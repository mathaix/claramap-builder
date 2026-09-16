import json
import os
import signal
import time
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'check_evidence.py'


class CheckEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'source'
        self.source.mkdir()
        (self.source / 'code.py').write_text('original')
        self.store = self.root / 'evidence'
        self.command = [sys.executable, '-c', 'print("verified")']

    def call(self, action='run', extra=(), command=None, env='local-v1'):
        return subprocess.run([sys.executable, str(SCRIPT), action, '--store', str(self.store),
            '--cwd', str(self.root), '--input', str(self.source), '--environment', env,
            *extra, '--', *(self.command if command is None else command)],
            capture_output=True, text=True, timeout=10)

    def records(self):
        return [json.loads(p.read_text()) for p in sorted(self.store.glob('*.json'))]

    def test_success_reuse_across_executors_and_reasoned_rerun(self):
        self.assertEqual(self.call().returncode, 0)
        self.assertEqual(self.call('status', ['--executor', 'qa']).returncode, 0)
        self.assertNotEqual(self.call(extra=['--executor', 'reviewer']).returncode, 0)
        self.assertEqual(len(self.records()), 1)
        self.assertEqual(self.call(extra=['--reason', 'independent repeat']).returncode, 0)
        records = self.records()
        self.assertEqual(len(records), 2)
        self.assertEqual(records[-1]['rerun_reason'], 'independent repeat')
        self.assertIn('verified', Path(records[0]['log_path']).read_text())
        self.assertGreaterEqual(records[0]['duration_seconds'], 0)

    def test_changed_added_deleted_and_environment_invalidate(self):
        self.assertEqual(self.call().returncode, 0)
        self.assertNotEqual(self.call('status', env='local-v2').returncode, 0)
        new = self.source / 'new.py'
        new.write_text('new')
        self.assertNotEqual(self.call('status').returncode, 0)
        new.unlink()
        self.assertEqual(self.call('status').returncode, 0)
        (self.source / 'code.py').write_text('changed')
        self.assertNotEqual(self.call('status').returncode, 0)
        (self.source / 'code.py').unlink()
        self.assertNotEqual(self.call('status').returncode, 0)

    def test_failure_and_missing_evidence_do_not_pass(self):
        self.assertNotEqual(self.call('status').returncode, 0)
        command = [sys.executable, '-c', 'raise SystemExit(7)']
        self.assertNotEqual(self.call(command=command).returncode, 0)
        self.assertEqual(self.records()[0]['exit_status'], 7)
        self.assertNotEqual(self.call('status', command=command).returncode, 0)

    def test_command_mutating_input_cannot_create_valid_evidence(self):
        command = [sys.executable, '-c', 'from pathlib import Path; Path("source/code.py").write_text("changed")']
        self.assertNotEqual(self.call(command=command).returncode, 0)
        self.assertEqual(self.records()[0]['state'], 'inputs_changed')
        self.assertNotEqual(self.call('status', command=command).returncode, 0)

    def test_timeout_does_not_pass(self):
        command = [sys.executable, '-c', 'import time; time.sleep(5)']
        self.assertNotEqual(self.call(extra=['--timeout', '0.05'], command=command).returncode, 0)
        self.assertEqual(self.records()[0]['state'], 'timed_out')
        self.assertNotEqual(self.call('status', command=command).returncode, 0)

    def test_store_inside_inputs_rejected_and_cache_ignored(self):
        self.store = self.source / 'evidence'
        self.assertNotEqual(self.call().returncode, 0)
        self.assertFalse(self.store.exists())
        self.store = self.root / 'evidence'
        self.assertEqual(self.call().returncode, 0)
        cache = self.source / '__pycache__'
        cache.mkdir()
        (cache / 'generated.pyc').write_bytes(b'ignored')
        self.assertEqual(self.call('status').returncode, 0)

    def test_missing_log_running_and_interrupted_records_do_not_pass(self):
        self.assertEqual(self.call().returncode, 0)
        path = next(self.store.glob('*.json'))
        record = json.loads(path.read_text())
        for state in ['running', 'interrupted']:
            record['state'] = state
            path.write_text(json.dumps(record))
            self.assertNotEqual(self.call('status').returncode, 0)
        record['state'] = 'passed'
        path.write_text(json.dumps(record))
        Path(record['log_path']).unlink()
        self.assertNotEqual(self.call('status').returncode, 0)

    def test_edited_log_and_legacy_record_without_hash_are_not_reusable(self):
        self.assertEqual(self.call().returncode, 0)
        record_path = next(self.store.glob('*.json'))
        record = json.loads(record_path.read_text())
        log_path = Path(record['log_path'])
        original = log_path.read_bytes()
        log_path.write_bytes(b'edited output')
        self.assertNotEqual(self.call('status').returncode, 0)
        log_path.write_bytes(original)
        self.assertEqual(self.call('status').returncode, 0)
        del record['log_sha256']
        record_path.write_text(json.dumps(record))
        self.assertNotEqual(self.call('status').returncode, 0)

    @unittest.skipUnless(os.name == 'posix', 'POSIX process-group cleanup')
    def test_sigterm_reaps_own_child_and_preserves_unrelated_process(self):
        pid_file = self.root / 'check.pid'
        command = [sys.executable, '-c',
            'import os, time; from pathlib import Path; '
            'Path("check.pid").write_text(str(os.getpid())); time.sleep(30)']
        unrelated = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(30)'])
        wrapper = subprocess.Popen([sys.executable, str(SCRIPT), 'run', '--store', str(self.store),
            '--cwd', str(self.root), '--input', str(self.source), '--environment', 'local-v1',
            '--', *command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        child_pid = None
        try:
            deadline = time.monotonic() + 5
            while not pid_file.exists() and time.monotonic() < deadline:
                time.sleep(0.01)
            self.assertTrue(pid_file.exists(), 'check child did not start')
            child_pid = int(pid_file.read_text())
            wrapper.send_signal(signal.SIGTERM)
            wrapper.communicate(timeout=5)
            self.assertNotEqual(wrapper.returncode, 0)
            record = self.records()[0]
            self.assertEqual(record['state'], 'interrupted')
            self.assertEqual(record['signal'], signal.SIGTERM)
            self.assertEqual(record['exit_status'], -signal.SIGKILL)
            with self.assertRaises(ProcessLookupError):
                os.kill(child_pid, 0)
            child_pid = None  # Reaped: never signal a potentially reused PID.
            self.assertIsNone(unrelated.poll())
            self.assertNotEqual(self.call('status', command=command).returncode, 0)
        finally:
            if wrapper.poll() is None:
                wrapper.kill()
                wrapper.communicate(timeout=5)
            if child_pid is not None:
                try:
                    os.kill(child_pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            unrelated.kill()
            unrelated.wait(timeout=5)

    def test_help_explains_evidence_scope(self):
        result = subprocess.run([sys.executable, str(SCRIPT), '--help'],
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0)
        self.assertIn('completeness cannot be inferred', result.stdout)

    def test_symlink_input_rejected(self):
        (self.source / 'link').symlink_to(self.source / 'code.py')
        self.assertNotEqual(self.call().returncode, 0)
        self.assertFalse(self.store.exists())


if __name__ == '__main__':
    unittest.main()
