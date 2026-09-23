#!/usr/bin/env python3
"""Tokens per model: Codex attempts under a run dir, plus a Claude session transcript and its subagents."""
import argparse
import collections
import json
import os
from pathlib import Path

COLUMNS = ('input', 'cache_read', 'cache_write', 'output')


def codex(run, warnings=None):
    """Attribute cumulative-counter deltas to attempts, retaining unknown intervals."""
    if warnings is None:
        warnings = []
    keys = ('input_tokens', 'cached_input_tokens', 'output_tokens')
    previous = {}
    gaps = set()
    directory_gaps = set()
    paths = sorted(run.rglob('attempt-*.json'),
                   key=lambda p: (str(p.parent), int(p.stem.split('-')[-1])))
    records = {(p.parent, int(p.stem.split('-')[-1])) for p in paths}
    unfinished = [p for p in sorted(run.rglob('events-*.jsonl'))
                  if (p.parent, int(p.stem.split('-')[-1])) not in records]
    last_attempt = {}
    rows = []
    for path in paths:
        number = int(path.stem.split('-')[-1])
        if any(p.parent == path.parent and last_attempt.get(path.parent, 0)
               < int(p.stem.split('-')[-1]) < number for p in unfinished):
            directory_gaps.add(path.parent)
        last_attempt[path.parent] = number
        record = json.loads(path.read_text())
        usage = record.get('usage')
        sid = record.get('session_id')
        valid = (isinstance(usage, dict)
                 and all(type(usage.get(k)) is int and usage[k] >= 0 for k in keys)
                 and usage['cached_input_tokens'] <= usage['input_tokens'])
        if not sid or not valid:
            warnings.append(f'{path}: missing session identity or valid usage; attempt usage unknown.')
            if sid:
                gaps.add(sid)
            else:
                directory_gaps.add(path.parent)
            continue
        baseline = previous.get(sid, dict.fromkeys(keys, 0))
        delta = {k: usage[k] - baseline[k] for k in keys}
        previous[sid] = {k: usage[k] for k in keys}
        if any(v < 0 for v in delta.values()) or delta['cached_input_tokens'] > delta['input_tokens']:
            warnings.append(f'{path}: cumulative counters reset or became inconsistent; '
                            'interval omitted, using this observation as the next baseline.')
            gaps.discard(sid)
            directory_gaps.discard(path.parent)
            continue
        model = record.get('model')
        if sid in gaps or path.parent in directory_gaps or not model:
            model = 'unattributed Codex usage'
            warnings.append(f'{path}: interval spans missing usage/identity or model; '
                            'its known cumulative delta cannot be assigned to a model.')
        gaps.discard(sid)
        directory_gaps.discard(path.parent)
        rows.append((model, {
            'input': delta['input_tokens'] - delta['cached_input_tokens'],
            'cache_read': delta['cached_input_tokens'], 'cache_write': 0,
            'output': delta['output_tokens']}))
    for path in unfinished:
        warnings.append(f'{path}: no final attempt record; usage unknown.')
    return rows


def claude(transcript):
    """One usage per message id; streamed content blocks repeat the same usage."""
    seen = {}
    for path in [transcript, *sorted(transcript.with_suffix('').glob('subagents/agent-*.jsonl'))]:
        for line in path.open():
            try:
                message = json.loads(line).get('message') or {}
            except ValueError:
                continue
            usage = message.get('usage') if isinstance(message, dict) else None
            if usage and message.get('model'):
                seen[message.get('id')] = (message['model'], {
                    'input': usage.get('input_tokens', 0),
                    'cache_read': usage.get('cache_read_input_tokens', 0),
                    'cache_write': usage.get('cache_creation_input_tokens', 0),
                    'output': usage.get('output_tokens', 0)})
    return seen.values()


def current_session():
    """Claude Code's transcript for this session: ~/.claude/projects/<cwd with / as ->/<id>.jsonl."""
    session_id = os.environ.get('CLAUDE_CODE_SESSION_ID')
    if not session_id:
        return None
    # ponytail: mirrors Claude Code's path encoding as observed; revisit if it changes.
    project = Path.home() / '.claude/projects' / Path.cwd().as_posix().replace('/', '-')
    path = project / f'{session_id}.jsonl'
    return path if path.is_file() else None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, help='run directory with Codex attempt records; report also saved there as usage.md')
    parser.add_argument('--session', type=Path, default=current_session(),
                        help='Claude session .jsonl (default: this session); its subagents/ folder is included')
    args = parser.parse_args()
    if not (args.run or args.session):
        parser.error('give --run and/or --session (no current Claude session detected)')
    totals = collections.defaultdict(lambda: dict.fromkeys(COLUMNS, 0))
    warnings = []
    if args.run and not args.session:
        warnings.append('No Claude session detected or supplied; coordinator and Claude subagent '
                        'usage is not included. Pass --session <transcript.jsonl> for that coverage.')
    rows = list(codex(args.run, warnings) if args.run else []) + list(claude(args.session) if args.session else [])
    for model, usage in rows:
        for key in COLUMNS:
            totals[model][key] += usage[key]
    lines = ['| model | ' + ' | '.join(COLUMNS) + ' |', '| --- | ' + ' | '.join('---:' for _ in COLUMNS) + ' |']
    lines += [f'| {model} | ' + ' | '.join(f'{usage[c]:,}' for c in COLUMNS) + ' |' for model, usage in sorted(totals.items())]
    lines += ['', f'Sources: run={args.run or "none"}; session={args.session or "none"}.',
              'Coverage: recorded session usage, not exact per-goal accounting. Claude includes the '
              'full supplied/detected session and available subagent transcripts. The first Codex '
              'counter may include earlier session work and is attributed to its recorded model.',
              'Sessions may span multiple goals; missing records and uncaptured agents are not zero usage.',
              'Tokens only; cost needs verified rates and billing mode.']
    if warnings:
        lines += ['', 'Coverage warnings:', '', *('- ' + warning for warning in warnings)]
    report = '\n'.join(lines) + '\n'
    print(report, end='')
    if args.run:
        (args.run / 'usage.md').write_text(report)


if __name__ == '__main__':
    main()
