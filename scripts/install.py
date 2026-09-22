#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Install both Claramap Builder skills, or select one explicitly."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import shutil
import tempfile
import uuid


BUNDLED_SKILLS = ('implement', 'improve-workflow')


def validate(name, skills_dir, replace):
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name):
        raise ValueError('skill name must use lowercase letters, numbers, and hyphens')
    source = Path(__file__).resolve().parents[1] / 'skills' / name
    if not (source / 'SKILL.md').is_file():
        raise ValueError(f'unknown skill: {name}')
    if source.is_symlink() or any(p.is_symlink() for p in source.rglob('*')):
        raise ValueError('skill source contains symlinks; inspect and install manually')
    skills_dir = skills_dir.expanduser().resolve()
    target = skills_dir / name
    if target == source or source in target.parents or target in source.parents:
        raise ValueError('installation must not replace or nest inside the collection source')
    if target.is_symlink():
        raise ValueError('destination is a symlink; inspect it before installing')
    if target.exists() and not target.is_dir():
        raise ValueError('destination exists and is not a directory')
    if target.exists() and not replace:
        raise ValueError(f'{target} already exists; use --replace to back it up and replace it')
    return source, target


def install_many(names, skills_dir, replace=False):
    # Validate every destination before changing any installed skill.
    plans = [(name, *validate(name, skills_dir, replace)) for name in names]
    skills_dir = skills_dir.expanduser().resolve()
    skills_dir.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix='.claramap-install-', dir=skills_dir))
    changes = []
    try:
        for name, source, target in plans:
            shutil.copytree(source, staging / name,
                            ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.DS_Store'))
        for name, source, target in plans:
            backup = None
            if target.exists():
                backup_root = skills_dir.parent / '.skill-backups'
                backup_root.mkdir(parents=True, exist_ok=True)
                stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
                backup = backup_root / f'{name}-{stamp}-{uuid.uuid4().hex[:8]}'
                target.rename(backup)
            changes.append((name, target, backup))
            (staging / name).rename(target)
    except Exception:
        for name, target, backup in reversed(changes):
            if target.exists():
                shutil.rmtree(target)
            if backup is not None:
                backup.rename(target)
        raise
    finally:
        shutil.rmtree(staging)
    return [{'skill': name, 'installed': str(target), 'backup': str(backup) if backup else None}
            for name, target, backup in changes]


def install(name, skills_dir, replace=False):
    return install_many((name,), skills_dir, replace)[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('skill', nargs='?', help='Install only this skill (default: both bundled skills)')
    parser.add_argument('--skills-dir', type=Path, default=Path.home() / '.claude/skills')
    parser.add_argument('--replace', action='store_true', help='Back up an existing installation before replacing it')
    args = parser.parse_args()
    try:
        result = (install(args.skill, args.skills_dir, args.replace) if args.skill else
                  install_many(BUNDLED_SKILLS, args.skills_dir, args.replace))
        print(json.dumps(result, indent=2))
    except (ValueError, OSError) as exc:
        parser.exit(2, f'install: {exc}\n')


if __name__ == '__main__':
    main()
