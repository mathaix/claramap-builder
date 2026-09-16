#!/usr/bin/env python3
"""Export exact Git blobs into a disposable review directory, ignoring export attributes."""
import argparse
import json
import os
from pathlib import Path
import subprocess


def export(snapshot, destination, baseline=False):
    saved = json.loads(snapshot.read_text())
    tree = saved.get('review_base', saved['head']) if baseline else saved['tree']
    command = ['git', '-C', saved['worktree']]
    raw = subprocess.check_output(command + ['ls-tree', '-rz', tree])
    entries = []
    for item in raw.split(b'\0'):
        if not item:
            continue
        meta, name = item.split(b'\t', 1)
        mode, kind, oid = meta.decode().split()
        if kind != 'blob':
            raise ValueError('review copy needs explicit submodule handling: ' + os.fsdecode(name))
        entries.append((mode, oid, os.fsdecode(name)))
    payload = subprocess.check_output(command + ['cat-file', '--batch'],
                                     input=''.join(oid + '\n' for _, oid, _ in entries).encode())
    destination.mkdir(parents=True, exist_ok=False)
    pos = 0
    for mode, oid, name in entries:
        end = payload.index(b'\n', pos)
        header = payload[pos:end].split()
        if header[:2] != [oid.encode(), b'blob']:
            raise ValueError('unexpected Git blob response')
        size = int(header[2]); data = payload[end + 1:end + 1 + size]; pos = end + size + 2
        target = destination / name
        if destination.resolve() not in target.resolve().parents:
            raise ValueError('unsafe Git path')
        target.parent.mkdir(parents=True, exist_ok=True)
        if mode == '120000':
            link = os.fsdecode(data)
            if destination.resolve() not in (target.parent / link).resolve().parents:
                raise ValueError('symlink escapes review copy: ' + name)
            target.symlink_to(link)
        else:
            target.write_bytes(data)
            target.chmod(0o755 if mode == '100755' else 0o644)
    print(json.dumps({'copy': str(destination.resolve()), 'source_tree': tree,
                      'baseline': baseline, 'snapshot': str(snapshot.resolve())}))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('snapshot', type=Path)
    p.add_argument('destination', type=Path)
    p.add_argument('--baseline', action='store_true')
    a = p.parse_args()
    export(a.snapshot, a.destination, a.baseline)
