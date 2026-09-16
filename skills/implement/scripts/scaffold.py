#!/usr/bin/env python3
"""Create a new personal run from bundled templates; never overwrite a run."""
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run_dir', type=Path)
    parser.add_argument('--title', default='Untitled implementation')
    parser.add_argument('--compact', action='store_true', help='Create only a concise status/acceptance record')
    args = parser.parse_args()
    templates = Path(__file__).resolve().parents[1] / 'assets/templates'
    args.run_dir.mkdir(parents=True, exist_ok=False)
    if args.compact:
        (args.run_dir / 'status.md').write_text(
            '# ' + args.title + '\n\n'
            'Outcome / acceptance criteria: record here or link the existing specification.\n'
            'Authorization / constraints: preserve the owner instructions and repository rules.\n'
            'Baseline / worktree: record inspected Git state and known failures.\n'
            'Plan-review choice / reason: record with run_state.py before execution.\n\n'
            '## Work and evidence\n\n'
            'Record concrete tasks, assigned checks, results, and open findings as needed.\n'
            'Reuse valid evidence; explain repeated checks. Final independent review required.\n\n'
            '## Next action\n\n'
            'Record the next runnable action; refresh recovery state at transitions.\n')
        print(args.run_dir)
        return
    for name in ('spec.md', 'plan.md', 'tasks.md', 'status.md'):
        (args.run_dir / name).write_text(
            (templates / name).read_text().replace('{{TITLE}}', args.title))
    print(args.run_dir)


if __name__ == '__main__':
    main()
