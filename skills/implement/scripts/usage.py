#!/usr/bin/env python3
"""Tokens per model: Codex attempts under a run dir, plus a Claude session transcript and its subagents."""
import argparse
import collections
import json
import os
from pathlib import Path

COLUMNS = ('input', 'cache_read', 'cache_write', 'output')


def codex(run):
    """Counters are session-cumulative, so the last attempt per session holds its total."""
    last = {}
    for path in sorted(run.rglob('attempt-*.json'), key=lambda p: (str(p.parent), int(p.stem.split('-')[-1]))):
        record = json.loads(path.read_text())
        usage = record.get('usage')
        if usage and record.get('session_id'):
            # Codex reports cached tokens inside input_tokens; split them out.
            last[record['session_id']] = (record['model'], {
                'input': usage['input_tokens'] - usage['cached_input_tokens'],
                'cache_read': usage['cached_input_tokens'], 'cache_write': 0,
                'output': usage['output_tokens']})
    return last.values()


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
    rows = list(codex(args.run) if args.run else []) + list(claude(args.session) if args.session else [])
    for model, usage in rows:
        for key in COLUMNS:
            totals[model][key] += usage[key]
    lines = ['| model | ' + ' | '.join(COLUMNS) + ' |', '| --- | ' + ' | '.join('---:' for _ in COLUMNS) + ' |']
    lines += [f'| {model} | ' + ' | '.join(f'{usage[c]:,}' for c in COLUMNS) + ' |' for model, usage in sorted(totals.items())]
    lines += ['', f'Sources: run={args.run or "none"}; session={args.session or "none"}.',
              'Tokens only; cost needs verified rates and billing mode.']
    report = '\n'.join(lines) + '\n'
    print(report, end='')
    if args.run:
        (args.run / 'usage.md').write_text(report)


if __name__ == '__main__':
    main()
