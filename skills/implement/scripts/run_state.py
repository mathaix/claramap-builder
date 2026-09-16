#!/usr/bin/env python3
"""Refresh observed recovery state without changing product files or Git metadata."""
import argparse
from datetime import datetime, timezone
import fcntl
import hashlib
import json
from pathlib import Path
import re
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


def plan_policy(previous, policy, reason):
    decision = previous.get('plan_review_decision')
    history = list(previous.get('plan_review_decisions', []))
    if reason is not None and policy is None:
        raise ValueError('--reason requires --plan-review')
    if policy is not None:
        new_choice = decision is None or decision['policy'] != policy
        if (new_choice or reason is not None) and not (reason and reason.strip()):
            raise ValueError('a new or changed --plan-review decision requires a nonempty --reason')
        if new_choice or reason is not None:
            decision = {'policy': policy, 'reason': reason.strip(),
                        'decided_at': datetime.now(timezone.utc).isoformat()}
            history.append(decision)
    # Existing runs keep their approval requirement until an explicit decision is recorded.
    required = decision is None or decision['policy'] == 'required'
    return required, decision, history


def refresh(run, worktree, next_action, completed, plan_review=None, reason=None):
    path = run / 'recovery.json'
    previous = json.loads(path.read_text()) if path.exists() else {}
    required, decision, decisions = plan_policy(previous, plan_review, reason)
    commits = dict(previous.get('completed', {}))
    for entry in completed:
        task, sha = entry.split('=', 1)
        commits[task] = git(worktree, 'rev-parse', '--verify', sha + '^{commit}')
    for task, sha in commits.items():
        subprocess.run(['git', '-C', str(worktree), 'merge-base', '--is-ancestor', sha, 'HEAD'], check=True)
    tasks = {p.name: worker_state(p) for p in sorted(run.glob('task-*')) if p.is_dir()}
    approved = []
    for snapshot in run.glob('review-*/plan-snapshot.json'):
        verdict = snapshot.with_name('verdict.md')
        saved = json.loads(snapshot.read_text())
        text = verdict.read_text() if verdict.exists() else ''
        if re.findall(r'^VERDICT: (\w+)\s*$', text, re.M) == ['APPROVE'] and re.findall(
                r'^ARTIFACT: ([0-9a-f]+)\s*$', text, re.M) == [saved['artifact']]:
            changed = [name for name, sha in saved['files'].items()
                       if not (run / name).exists() or hashlib.sha256((run / name).read_bytes()).hexdigest() != sha]
            approved.append({'review': snapshot.parent.name, 'artifact': saved['artifact'], 'changed_files': changed})
    matching = [p for p in approved if not p['changed_files']]
    state = {**previous, 'observed_at': datetime.now(timezone.utc).isoformat(), 'worktree': str(worktree),
             'head': git(worktree, 'rev-parse', 'HEAD'), 'branch': git(worktree, 'branch', '--show-current'),
             'git_status': git(worktree, 'status', '--porcelain=v1', '--untracked-files=all').splitlines(),
             'completed': commits, 'workers': tasks, 'plan_approvals': approved,
             'plan_ready': bool(matching), 'plan_review_required': required,
             'plan_review_decision': decision, 'plan_review_decisions': decisions,
             'execution_ready': not required or bool(matching), 'next_action': next_action,
             'note': 'Observed snapshot, not a live monitor. Execution ready concerns only the plan-review '
                     'requirement; it does not establish authorization, final review, check success, or readiness '
                     'to land. Worker exit does not imply review or check success.'}
    tmp = path.with_suffix('.json.tmp')
    tmp.write_text(json.dumps(state, indent=2) + '\n')
    tmp.replace(path)
    text = ['# Current recovery state', '', f"Observed: {state['observed_at']}",
            f"Worktree: `{worktree}`", f"Branch / HEAD: `{state['branch']}` / `{state['head']}`",
            f"Plan review required: {required}", f"Matching plan approval: {state['plan_ready']}",
            f"Execution ready (plan review only): {state['execution_ready']}", '', 'Next action: ' + next_action, '',
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
    parser.add_argument('--plan-review', choices=('required', 'not-required'),
                        help='record the coordinator decision; existing runs default to required')
    parser.add_argument('--reason', help='required for a new or changed plan-review decision')
    args = parser.parse_args()
    try:
        refresh(args.run.resolve(), args.worktree.resolve(), args.next_action, args.completed,
                args.plan_review, args.reason)
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        print(f'run_state: {exc}', file=sys.stderr)
        sys.exit(2)
