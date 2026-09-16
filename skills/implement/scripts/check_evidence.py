#!/usr/bin/env python3
"""Run a bounded check and retain evidence tied to explicitly declared inputs."""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import uuid

IGNORED = {'.git', '__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache', '.cache'}


def timestamp():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def fingerprint(paths):
    """Hash names and contents; new/deleted files invalidate directory evidence."""
    digest = hashlib.sha256()

    def add(value):
        data = value if isinstance(value, bytes) else value.encode()
        digest.update(len(data).to_bytes(8, 'big'))
        digest.update(data)

    def visit(path):
        if path.is_symlink():
            raise ValueError(f'symlink input is unsupported; declare its real target: {path}')
        add(str(path))
        if path.is_dir():
            add('directory')
            for child in sorted(path.iterdir()):
                if child.name not in IGNORED:
                    visit(child)
        elif path.is_file():
            add('file')
            # Executable-bit changes can alter the check as well as file contents.
            add(str(path.stat().st_mode & 0o111))
            with path.open('rb') as stream:
                while chunk := stream.read(1024 * 1024):
                    add(chunk)
        else:
            raise ValueError(f'input is missing or is not a regular file/directory: {path}')

    for path in paths:
        visit(path)
    return digest.hexdigest()


def write_record(path, record):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(record, indent=2) + '\n')
    temporary.replace(path)


def latest_record(store, identity):
    matches = []
    for path in store.glob('*.json'):
        try:
            record = json.loads(path.read_text())
            if record.get('identity') == identity:
                matches.append(record)
        except (OSError, ValueError):
            continue
    return max(matches, key=lambda item: item.get('started_at', ''), default=None)


def log_hash(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def valid(record, current):
    if not (record and record.get('state') == 'passed'
            and record.get('exit_status') == 0
            and record.get('before') == current == record.get('after')
            and record.get('log_sha256')):
        return False
    try:
        return log_hash(Path(record['log_path'])) == record['log_sha256']
    except (OSError, KeyError, TypeError):
        return False


def stop_process(process):
    # Once reaped, a PID can be reused; never signal that former process group.
    if process.returncode is not None:
        return
    if os.name == 'posix':
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    else:
        process.kill()
    process.wait()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, epilog=(
        'Evidence covers ONLY declared inputs. Declare relevant source directories, '
        'dependency lockfiles and configuration; completeness cannot be inferred. '
        'Environment is a non-secret label, never an environment dump: change the label '
        'when runtime/dependency/service assumptions change. Live services and external '
        'state require fresh checks. Do not put secrets in commands or check output. '
        'Stores must be outside input directories. Symlink inputs are rejected. '
        'Ignored directory entries: ' + ', '.join(sorted(IGNORED)) + '. '
        'Before/after fingerprints detect persistent changes during execution, not '
        'changes reverted before completion; use an immutable review copy for isolation.'))
    parser.add_argument('action', choices=['run', 'status'])
    parser.add_argument('--store', required=True, type=Path)
    parser.add_argument('--cwd', type=Path, default=Path.cwd())
    parser.add_argument('--input', action='append', required=True, dest='inputs')
    parser.add_argument('--environment', required=True, help='Non-secret runtime/configuration identity')
    parser.add_argument('--executor', default='orchestrator', help='Agent/role label, excluded from reuse identity')
    parser.add_argument('--timeout', type=float, default=600, help='Maximum seconds, default 600')
    parser.add_argument('--reason', help='Required to repeat an already valid successful check')
    # Parse the command after -- separately so CLI options remain unambiguous.
    arguments = list(sys.argv[1:] if argv is None else argv)
    try:
        separator = arguments.index('--')
    except ValueError:
        if '--help' in arguments or '-h' in arguments:
            parser.print_help()
            return 0
        parser.error('provide the check command after -- (argv only, no shell)')
    args = parser.parse_args(arguments[:separator])
    command = arguments[separator + 1:]
    if not command:
        parser.error('check command is empty')
    if not 0 < args.timeout < float('inf'):
        parser.error('--timeout must be finite and positive')
    cwd = args.cwd.resolve()
    store = args.store.resolve()
    declared = [cwd / value for value in args.inputs]
    if any(path.is_symlink() for path in declared):
        parser.error('symlink inputs are unsupported; declare their real targets')
    paths = sorted({path.resolve() for path in declared})
    for path in paths:
        if path == store or path in store.parents:
            parser.error('evidence store must be outside every declared input')
    identity = {'command': command, 'cwd': str(cwd), 'inputs': [str(p) for p in paths],
                'environment': args.environment}
    try:
        before = fingerprint(paths)
    except (OSError, ValueError) as exc:
        print(json.dumps({'state': 'invalid_inputs', 'error': str(exc)}))
        return 1
    previous = latest_record(store, identity)
    reusable = valid(previous, before)
    if args.action == 'status':
        print(json.dumps({'state': 'reusable' if reusable else 'not_reusable',
                          'record': previous.get('id') if previous else None,
                          'record_state': previous.get('state') if previous else None}))
        return 0 if reusable else 1
    if reusable and not (args.reason and args.reason.strip()):
        parser.error('successful unchanged evidence exists; reuse it or supply --reason for rerun')
    store.mkdir(parents=True, exist_ok=True)
    run_id = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '-' + uuid.uuid4().hex[:8]
    log_path = store / (run_id + '.log')
    record_path = store / (run_id + '.json')
    record = {'id': run_id, 'identity': identity, 'executor': args.executor,
              'started_at': timestamp(), 'state': 'running', 'before': before,
              'after': None, 'exit_status': None, 'log_path': str(log_path),
              'timeout_seconds': args.timeout, 'rerun_reason': args.reason}
    write_record(record_path, record)
    started = time.monotonic()
    process = None
    received_signal = None
    handling_check = True

    def interrupt_check(signum, _frame):
        nonlocal received_signal
        if received_signal is None:
            received_signal = signum
        # Defer interruption while Popen constructs its child so we retain the
        # handle and can reap it. Repeated signals must not interrupt cleanup.
        if handling_check and process is not None:
            raise KeyboardInterrupt

    old_handlers = {sig: signal.signal(sig, interrupt_check)
                    for sig in (signal.SIGINT, signal.SIGTERM)}
    try:
        with log_path.open('xb') as output:
            if received_signal is not None:
                raise KeyboardInterrupt
            process = subprocess.Popen(command, cwd=cwd, stdout=output, stderr=subprocess.STDOUT,
                                       start_new_session=(os.name == 'posix'))
            if received_signal is not None:
                raise KeyboardInterrupt
            record['exit_status'] = process.wait(timeout=args.timeout)
            record['state'] = 'passed' if record['exit_status'] == 0 else 'failed'
    except subprocess.TimeoutExpired:
        handling_check = False
        stop_process(process)
        record.update(state='timed_out', exit_status=process.returncode)
    except KeyboardInterrupt:
        handling_check = False
        if process is not None:
            stop_process(process)
        record.update(state='interrupted', exit_status=process.returncode if process else None)
    except OSError as exc:
        record.update(state='failed', error=str(exc))
    finally:
        handling_check = False
        for sig, handler in old_handlers.items():
            signal.signal(sig, handler)
    if received_signal is not None:
        record.update(state='interrupted', signal=received_signal)
    try:
        record['after'] = fingerprint(paths)
        if record['before'] != record['after']:
            record['state'] = 'inputs_changed'
    except (OSError, ValueError) as exc:
        record.update(state='inputs_changed', error=str(exc))
    try:
        record['log_sha256'] = log_hash(log_path)
    except OSError as exc:
        record.update(state='failed', error=str(exc))
    record.update(finished_at=timestamp(), duration_seconds=round(time.monotonic() - started, 3))
    write_record(record_path, record)
    print(json.dumps({'state': record['state'], 'record_path': str(record_path), 'log_path': str(log_path)}))
    return 0 if valid(record, before) else 1


if __name__ == '__main__':
    sys.exit(main())
