#!/usr/bin/env python3
"""Refresh observed recovery state without changing product files or Git metadata."""
import argparse
from datetime import datetime, timezone
import fcntl
import json
from pathlib import Path
import subprocess
import sys


def git(worktree, *args):
    return subprocess.check_output(['git', '--no-optional-locks', '-C', str(worktree), *args],
                                   stderr=subprocess.PIPE).decode().rstrip('\n')


def worker_state(directory):
    lock = directory / '.lock'
    if lock.exists():
        with lock.open('r') as f:
            try:
                fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                return 'running'
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)
    events = list(directory.glob('events-*.jsonl'))
    if not events:
        return 'legacy_or_not_started'
    latest = max(events, key=lambda p: int(p.stem.split('-')[-1]))
    attempt = directory / latest.name.replace('events-', 'attempt-').replace('.jsonl', '.json')
    if not attempt.exists():
        return 'interrupted_without_final_record'
    record = json.loads(attempt.read_text())
    return 'exited_pending_verification' if record.get('wrapper_exit_code') == 0 else 'interrupted_or_failed'


def refresh(run, worktree, next_action, completed):
    run.mkdir(parents=True, exist_ok=True)
    path = run / 'recovery.json'
    previous = json.loads(path.read_text()) if path.exists() else {}
    # Plan-approval fields from the retired hash gate are never recalculated; drop them.
    previous = {k: v for k, v in previous.items() if not k.startswith('plan_') and k != 'execution_ready'}
    commits = dict(previous.get('completed', {}))
    for entry in completed:
        task, sha = entry.split('=', 1)
        commits[task] = git(worktree, 'rev-parse', '--verify', sha + '^{commit}')
    for task, sha in commits.items():
        subprocess.run(['git', '-C', str(worktree), 'merge-base', '--is-ancestor', sha, 'HEAD'], check=True)
    # The wrapper accepts nested slugs with arbitrary names. Its workdir file
    # identifies workers; retain discovery of old task-* directories as well.
    directories = {p.parent for p in run.rglob('workdir') if p.is_file()}
    directories.update(p for p in run.glob('task-*') if p.is_dir())
    tasks = {str(p.relative_to(run)): worker_state(p) for p in sorted(directories)}
    state = {**previous, 'observed_at': datetime.now(timezone.utc).isoformat(), 'worktree': str(worktree),
             'head': git(worktree, 'rev-parse', 'HEAD'), 'branch': git(worktree, 'branch', '--show-current'),
             'git_status': git(worktree, 'status', '--porcelain=v1', '--untracked-files=all').splitlines(),
             'completed': commits, 'workers': tasks, 'next_action': next_action,
             'note': 'Observed snapshot, not a live monitor. Worker exit does not imply review or check success.'}
    tmp = path.with_suffix('.json.tmp')
    tmp.write_text(json.dumps(state, indent=2) + '\n')
    tmp.replace(path)
    text = ['# Current recovery state', '', f"Observed: {state['observed_at']}",
            f"Worktree: `{worktree}`", f"Branch / HEAD: `{state['branch']}` / `{state['head']}`",
            '', 'Next action: ' + next_action, '',
            'Completed commits: ' + (', '.join(f'{k}={v[:12]}' for k, v in commits.items()) or 'none recorded'), '',
            '| Worker | Observed state |', '| --- | --- |']
    text += [f'| {k} | {v} |' for k, v in tasks.items()]
    text += ['', 'Product worktree changes:', '```', *state['git_status'], '```', '', state['note']]
    (run / 'recovery.md').write_text('\n'.join(text) + '\n')
    print(json.dumps(state, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    parser.add_argument('worktree', type=Path)
    parser.add_argument('--next-action', required=True)
    parser.add_argument('--completed', action='append', default=[], metavar='TASK=COMMIT')
    args = parser.parse_args()
    try:
        refresh(args.run.resolve(), args.worktree.resolve(), args.next_action, args.completed)
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        print(f'run_state: {exc}', file=sys.stderr)
        sys.exit(2)
