#!/usr/bin/env python3
"""Capture/verify the exact staged or integrated review artifact; does not commit or run tests."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args], stderr=subprocess.PIPE)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def state(repo):
    if git(repo, 'diff', '--name-only', '--diff-filter=U').strip():
        raise ValueError('unresolved conflicts')
    if git(repo, 'diff', '--no-ext-diff', '--no-textconv', '--ignore-submodules=none', '--name-only').strip():
        raise ValueError('unstaged tracked changes; checks would not see the reviewed tree')
    head = git(repo, 'rev-parse', 'HEAD').decode().strip()
    tree = git(repo, 'write-tree').decode().strip()
    merge_file = Path(git(repo, 'rev-parse', '--git-path', 'MERGE_HEAD').decode().strip())
    if not merge_file.is_absolute():
        merge_file = repo / merge_file
    parents = [head] + (merge_file.read_text().splitlines() if merge_file.exists() else [])
    untracked = {}
    for raw in git(repo, 'ls-files', '--others', '--exclude-standard', '-z').split(b'\0'):
        if not raw:
            continue
        name = raw.decode('utf-8', 'surrogateescape')
        path = repo / name
        if path.is_symlink():
            content = b'symlink:' + os.fsencode(os.readlink(path))
        elif path.is_file():
            content = b'file:' + path.read_bytes()
        else:
            raise ValueError(f'untracked nested repository or directory needs explicit isolation: {name}')
        untracked[name] = digest(content)
    return {'head': head, 'tree': tree, 'parents': parents, 'untracked': untracked}


def patch_bases(current):
    bases = {'diff.patch': current.get('review_base', current['parents'][0])}
    # Retain comparisons against both merge parents even for an integrated review.
    for index, parent in enumerate(current['parents']):
        if index or (len(current['parents']) > 1 and bases['diff.patch'] != parent):
            bases[f'parent-{index + 1}.patch'] = parent
    return bases


def patch(repo, base, tree):
    return git(repo, 'diff', '--no-ext-diff', '--no-textconv', '--ignore-submodules=none',
               '--binary', '--full-index', base, tree)


def snapshot(repo, directory, base=None):
    current = state(repo)
    if base is not None:
        current['review_base'] = git(repo, 'rev-parse', '--verify', '--end-of-options',
                                     base + '^{commit}').decode().strip()
        current['review_base_tree'] = git(repo, 'rev-parse',
                                         current['review_base'] + '^{tree}').decode().strip()
    if directory == repo or repo in directory.parents:
        raise ValueError('review records must be outside the product worktree')
    directory.mkdir(parents=True, exist_ok=False)
    patches = {}
    for name, parent in patch_bases(current).items():
        data = patch(repo, parent, current['tree'])
        (directory / name).write_bytes(data)
        patches[name] = digest(data)
    current['patch_sha256'] = patches
    current['worktree'] = str(repo)
    (directory / 'snapshot.json').write_text(json.dumps(current, indent=2) + '\n')
    print(json.dumps({'tree': current['tree'], 'snapshot': str(directory / 'snapshot.json')}))


def verify(repo, directory):
    saved = json.loads((directory / 'snapshot.json').read_text())
    if saved['worktree'] != str(repo):
        raise ValueError('different worktree')
    current = state(repo)
    for key in current:
        if current[key] != saved[key]:
            raise ValueError(f'{key} changed since review; obtain a new review')
    if 'review_base' in saved:
        base = saved['review_base']
        if git(repo, 'rev-parse', '--verify', '--end-of-options', base + '^{commit}').decode().strip() != base:
            raise ValueError('review base is not an immutable commit identity')
        if git(repo, 'rev-parse', base + '^{tree}').decode().strip() != saved['review_base_tree']:
            raise ValueError('review base tree changed')
    bases = patch_bases(saved)
    if set(saved['patch_sha256']) != set(bases):
        raise ValueError('review patch set changed')
    for name, base in bases.items():
        expected = saved['patch_sha256'][name]
        if (digest((directory / name).read_bytes()) != expected
                or digest(patch(repo, base, saved['tree'])) != expected):
            raise ValueError('review patch changed or does not match its base and tree')
    verdict = (directory / 'verdict.md').read_text()
    if re.findall(r'^VERDICT: (\w+)\s*$', verdict, re.M) != ['APPROVE']:
        raise ValueError('reviewer has not returned an unambiguous APPROVE')
    if re.findall(r'^TREE: ([0-9a-f]+)\s*$', verdict, re.M) != [saved['tree']]:
        raise ValueError('approval does not name this tree')
    print('APPROVED_UNCHANGED ' + saved['tree'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('snapshot', 'verify'))
    parser.add_argument('worktree', type=Path)
    parser.add_argument('review_dir', type=Path)
    parser.add_argument('--base', help='snapshot: commit to compare with the staged tree (integrated review)')
    args = parser.parse_args()
    if args.base is not None and args.mode != 'snapshot':
        parser.error('--base is only valid with snapshot')
    if args.mode == 'snapshot':
        snapshot(args.worktree.resolve(), args.review_dir.resolve(), args.base)
    else:
        verify(args.worktree.resolve(), args.review_dir.resolve())


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        print(f'review_gate: {exc}', file=sys.stderr)
        sys.exit(2)
