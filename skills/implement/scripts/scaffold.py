#!/usr/bin/env python3
"""Create specs/<slug>/ in the product repo from the bundled templates; never overwrite."""
import argparse
from pathlib import Path

FILES = ('requirements.md', 'design.md', 'tasks.md')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('worktree', type=Path)
    parser.add_argument('slug', help='feature folder name, also the run slug under ~/.claude/implement')
    parser.add_argument('--title', default='Untitled feature')
    args = parser.parse_args()
    if len(Path(args.slug).parts) != 1 or args.slug in ('.', '..'):
        parser.error('slug must be a single folder name')
    templates = Path(__file__).resolve().parents[1] / 'assets/templates'
    target = args.worktree / 'specs' / args.slug
    target.mkdir(parents=True, exist_ok=False)
    for name in FILES:
        (target / name).write_text((templates / name).read_text().replace('{{TITLE}}', args.title))
    print(target)


if __name__ == '__main__':
    main()
