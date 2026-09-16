#!/usr/bin/env python3
"""Install one skill from this collection without overwriting local work implicitly."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
import uuid


def install(name, skills_dir, replace=False):
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
    skills_dir.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f'.{name}-install-', dir=skills_dir))
    backup = None
    try:
        payload = staging / name
        shutil.copytree(source, payload, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.DS_Store'))
        if target.exists():
            backup_root = skills_dir.parent / '.skill-backups'
            backup_root.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
            backup = backup_root / f'{name}-{stamp}-{uuid.uuid4().hex[:8]}'
            target.rename(backup)
        try:
            payload.rename(target)
        except Exception:
            if backup is not None and not target.exists():
                backup.rename(target)
            raise
    finally:
        shutil.rmtree(staging)
    return {'skill': name, 'installed': str(target), 'backup': str(backup) if backup else None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('skill')
    parser.add_argument('--skills-dir', type=Path, default=Path.home() / '.claude/skills')
    parser.add_argument('--replace', action='store_true', help='Back up an existing installation before replacing it')
    args = parser.parse_args()
    try:
        print(json.dumps(install(args.skill, args.skills_dir, args.replace), indent=2))
    except (ValueError, OSError) as exc:
        parser.exit(2, f'install: {exc}\n')


if __name__ == '__main__':
    main()
