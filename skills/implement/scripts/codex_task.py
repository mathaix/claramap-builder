#!/usr/bin/env python3
"""Resumable Codex worker with immutable attempts and recursive usage reporting."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time


def model_policy():
    policy = json.loads((Path(__file__).resolve().parents[1] / 'model-policy.json').read_text())
    if policy['default_model'] not in policy['allowed_models']:
        raise ValueError('model-policy.json default_model must be one of allowed_models')
    return policy


def task_path(root, slug):
    parts = Path(slug).parts
    if not parts or Path(slug).is_absolute() or any(p in ('.', '..') for p in parts):
        raise ValueError('slug must be a relative path without traversal')
    path = (root / slug).resolve()
    if path == root or root not in path.parents:
        raise ValueError('slug escapes run root')
    return path


def field(text, label):
    match = re.search(r'^' + re.escape(label) + r': (.+)$', text, re.M)
    return match[1].strip() if match else None


def read_optional(path):
    return path.read_text().strip() if path.exists() else None


def usage_report(root, slug=None):
    scope = task_path(root, slug) if slug else root
    if not scope.is_dir():
        raise ValueError(f'no run directory: {scope}')
    structured = {'input_tokens': 0, 'cached_input_tokens': 0, 'output_tokens': 0}
    unknown = 0
    legacy_total = 0
    records = []
    new_attempts = set()
    sessions = {}
    warnings = []
    paths = sorted(scope.rglob('attempt-*.json'),
                   key=lambda p: (str(p.parent), int(p.stem.split('-')[-1])))
    for path in paths:
        record = json.loads(path.read_text())
        new_attempts.add((path.parent, record['attempt']))
        usage = record.get('usage')
        sid = record.get('session_id')
        delta = None
        if usage is None or not sid:
            unknown += 1
        else:
            previous = sessions.get(sid, dict.fromkeys(structured, 0))
            if any(usage.get(k, 0) < previous[k] for k in structured):
                unknown += 1
                warnings.append(f'{path}: cumulative counter decreased; delta unknown')
            else:
                delta = {k: usage.get(k, 0) - previous[k] for k in structured}
                for key in structured:
                    structured[key] += delta[key]
                sessions[sid] = {k: usage.get(k, 0) for k in structured}
        records.append({'task': str(path.parent.relative_to(root)), **record,
                        'usage_semantics': 'session_cumulative', 'usage_delta': delta})
    # Interrupted attempts without a final record remain visible as unknown usage.
    for path in scope.rglob('events-*.jsonl'):
        number = int(path.stem.split('-')[-1])
        if (path.parent, number) not in new_attempts:
            unknown += 1
            records.append({'task': str(path.parent.relative_to(root)),
                            'attempt': number, 'usage': None,
                            'state': 'unfinished_or_interrupted'})
    # Old cost.tsv rows are preserved. Only text observations are summed here;
    # their billing/cumulative semantics cannot be reconstructed reliably.
    for path in sorted(scope.rglob('cost.tsv')):
        for line in path.read_text().splitlines():
            columns = line.split('\t')
            if len(columns) < 3:
                continue
            match = re.fullmatch(r'transcript-(\d+)\.txt', columns[1])
            if not match or (path.parent, int(match[1])) in new_attempts:
                continue
            transcript = path.parent / columns[1]
            raw = transcript.read_text() if transcript.exists() else ''
            token_text = columns[2].replace(',', '')
            count = int(token_text) if token_text.isdigit() else None
            unknown += count is None
            legacy_total += count or 0
            records.append({'task': str(path.parent.relative_to(root)),
                            'attempt': int(match[1]), 'format': 'legacy_text',
                            'model': field(raw, 'model'), 'reported_tokens': count})
    result = {'attempts': records, 'structured_usage': structured,
              'structured_total_tokens': structured['input_tokens'] + structured['output_tokens'],
              'legacy_reported_tokens_sum': legacy_total, 'unknown_attempts': unknown,
              'cost_usd': None, 'warnings': warnings,
              'note': 'Legacy counters are observations, not verified incremental billing. '
                      'Structured totals use session-cumulative deltas; the first observed counter may include earlier session usage. Reviewer/coordinator usage is separate. Cached input is included in input.'}
    print(json.dumps(result, indent=2))


def execute(root, mode, slug, workdir=None):
    directory = task_path(root, slug)
    if mode == 'run':
        workdir = Path(workdir).resolve()
        if not workdir.is_dir():
            raise ValueError(f'no workdir: {workdir}')
        directory.mkdir(parents=True, exist_ok=False)
        (directory / 'workdir').write_text(str(workdir) + '\n')
    elif not directory.is_dir():
        raise ValueError(f'no task: {slug}')
    with (directory / '.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError('task already running; do not resume concurrently') from None
        result = execute_locked(directory, mode, lock.fileno())
        # All worker work and attempt records are finished. Closing our copy alone
        # leaves the flock held by helpers that inherited the descriptor; explicit
        # unlock releases it for every copy of this open file description.
        # Do not unlock on an unexpected exception: a worker may still be alive.
        # SIGKILL also leaves the inherited lock protecting a surviving worker.
        fcntl.flock(lock, fcntl.LOCK_UN)
        return result


def recover_session(directory):
    saved = read_optional(directory / 'session.id')
    ids = set()
    for path in directory.glob('events-*.jsonl'):
        for line in path.read_text(errors='replace').splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get('type') == 'thread.started':
                sid = event.get('thread_id')
                if isinstance(sid, str) and re.fullmatch(r'[A-Za-z0-9-]+', sid):
                    ids.add(sid)
    if saved:
        ids.add(saved)
    if len(ids) > 1:
        raise ValueError('conflicting session IDs; inspect events before recovery')
    sid = next(iter(ids), None)
    if sid and not saved:
        (directory / 'session.id').write_text(sid + '\n')
    return sid


def execute_locked(directory, mode, lock_fd):
    workdir = Path((directory / 'workdir').read_text().strip())
    if not workdir.is_dir():
        raise ValueError(f'no workdir: {workdir}')
    legacy = read_optional(directory / 'transcript-1.txt') or ''
    settings = directory / 'worker.json'
    saved = json.loads(settings.read_text()) if settings.exists() else {}
    model = (os.environ.get('IMPLEMENT_MODEL') or saved.get('model')
             or field(legacy, 'model'))
    effort = (os.environ.get('IMPLEMENT_EFFORT') or saved.get('effort')
              or field(legacy, 'reasoning effort'))
    if mode == 'resume' and (not model or not effort):
        raise ValueError('unknown original model/effort; inspect history and explicitly set '
                         'IMPLEMENT_MODEL and IMPLEMENT_EFFORT before resuming')
    policy = model_policy()
    model = model or policy['default_model']
    allowed_models = policy['allowed_models']
    if model not in allowed_models:
        raise ValueError(f'worker model {model!r} is excluded by owner policy; '
                         f'choose explicitly from {", ".join(allowed_models)} in model-policy.json')
    effort = effort or policy['default_effort']
    sid = recover_session(directory)
    if mode == 'resume' and not sid:
        raise ValueError('no session.id; inspect the failed attempt and use a new task slug')
    if sid and not re.fullmatch(r'[A-Za-z0-9-]+', sid):
        raise ValueError('invalid session.id')
    (directory / 'worker.json').write_text(json.dumps({'model': model, 'effort': effort}) + '\n')
    numbers = [int(m[1]) for p in directory.iterdir()
               if (m := re.fullmatch(r'(?:transcript|events|attempt|prompt)-(\d+)\.(?:txt|jsonl|json|md)', p.name))]
    number = max(numbers, default=0) + 1
    events_path = directory / f'events-{number}.jsonl'
    stderr_path = directory / f'stderr-{number}.log'
    transcript = directory / f'transcript-{number}.txt'
    prompt = sys.stdin.buffer.read()
    (directory / f'prompt-{number}.md').write_bytes(prompt)
    cmd = ['codex', 'exec', '-s', 'workspace-write', '-c', f'model_reasoning_effort={effort}']
    if mode == 'resume':
        cmd += ['resume', '-m', model, '--json', '--skip-git-repo-check', sid, '-']
    else:
        cmd += ['-m', model, '--json', '--skip-git-repo-check', '-C', str(workdir), '-']
    started = time.time()
    returncode = 127
    interrupted = None
    process = None

    def stop(signum, _frame):
        nonlocal interrupted
        interrupted = signum
        if process is not None:
            try:
                os.killpg(process.pid, signum)
            except ProcessLookupError:
                pass

    previous = {sig: signal.signal(sig, stop) for sig in (signal.SIGINT, signal.SIGTERM)}
    try:
        with events_path.open('xb') as output, stderr_path.open('xb') as errors, (directory / f'prompt-{number}.md').open('rb') as prompt_input:
            try:
                process = subprocess.Popen(cmd, cwd=workdir, stdin=prompt_input,
                                           stdout=subprocess.PIPE, stderr=errors, start_new_session=True,
                                           pass_fds=(lock_fd,))
                # Persist identity at thread start, not only after the turn exits.
                for line in process.stdout:
                    output.write(line)
                    output.flush()
                    try:
                        event = json.loads(line)
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        continue
                    if event.get('type') == 'thread.started':
                        new_sid = event.get('thread_id')
                        if isinstance(new_sid, str) and re.fullmatch(r'[A-Za-z0-9-]+', new_sid):
                            if sid and new_sid != sid:
                                stop(signal.SIGTERM, None)
                            else:
                                (directory / 'session.id').write_text(new_sid + '\n')
                process.stdout.close()
                process.wait()
                returncode = process.returncode
            except OSError as exc:
                errors.write((str(exc) + '\n').encode())
    finally:
        for sig, handler in previous.items():
            signal.signal(sig, handler)
    if returncode < 0:
        returncode = 128 - returncode
    if interrupted:
        returncode = 128 + interrupted
    messages = []
    usages = []
    failed_events = []
    parsed_sid = None
    for line in events_path.read_text(errors='replace').splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue
        if event.get('type') == 'thread.started':
            parsed_sid = event.get('thread_id')
        if event.get('type') == 'turn.completed' and isinstance(event.get('usage'), dict):
            usages.append(event['usage'])
        if event.get('type') in ('turn.failed', 'error'):
            failed_events.append(event)
        item = event.get('item', {})
        if event.get('type') == 'item.completed' and item.get('type') == 'agent_message':
            messages.append(item.get('text', ''))
    if parsed_sid and (not sid or parsed_sid == sid):
        (directory / 'session.id').write_text(parsed_sid + '\n')
    elif parsed_sid and parsed_sid != sid:
        failed_events.append({'error': 'resumed thread ID changed; original session.id preserved'})
    keys = ('input_tokens', 'cached_input_tokens', 'output_tokens')
    usage = None
    if usages and all(all(isinstance(u.get(k), int) and u[k] >= 0 for k in keys) for u in usages):
        usage = {k: usages[-1][k] for k in keys}
    wrapper_code = returncode
    if not returncode and (not parsed_sid or not messages or failed_events or not usages):
        wrapper_code = 2  # Preserve the actual process status separately.
    record = {'attempt': number, 'format': 'jsonl', 'model': model, 'effort': effort,
              'session_id': parsed_sid or sid, 'started_at_unix': started,
              'elapsed_seconds': round(time.time() - started, 3),
              'codex_exit_code': returncode, 'wrapper_exit_code': wrapper_code,
              'usage': usage, 'usage_semantics': 'session_cumulative', 'errors': failed_events}
    (directory / f'attempt-{number}.json').write_text(json.dumps(record, indent=2) + '\n')
    transcript.write_text('model: ' + model + '\n' + '\n\n'.join(messages) +
                          '\n\nSTDERR:\n' + stderr_path.read_text(errors='replace'))
    print(messages[-1] if messages else 'No agent result; inspect the attempt diagnostics.')
    print(f'\nmodel={model} codex_exit={returncode} wrapper_exit={wrapper_code}')
    print(f'Artifacts: {directory} (attempt {number})')
    if wrapper_code:
        print(stderr_path.read_text(errors='replace')[-4000:], file=sys.stderr)
        for event in failed_events:
            print(json.dumps(event), file=sys.stderr)
    return wrapper_code


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='mode', required=True)
    run = sub.add_parser('run')
    run.add_argument('workdir')
    run.add_argument('slug')
    resume = sub.add_parser('resume')
    resume.add_argument('slug')
    cost = sub.add_parser('cost')
    cost.add_argument('slug', nargs='?')
    args = parser.parse_args()
    root = Path(os.environ.get('IMPLEMENT_ROOT', '~/.claude/implement')).expanduser().resolve()
    if args.mode == 'cost':
        usage_report(root, args.slug)
        return 0
    return execute(root, args.mode, args.slug, getattr(args, 'workdir', None))


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, OSError, KeyError) as exc:
        print(f'codex_task: {exc}', file=sys.stderr)
        sys.exit(2)
