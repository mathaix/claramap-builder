import json
import os
import signal
import shutil
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

SKILL = Path(__file__).resolve().parents[1]
FAKE = r'''#!/usr/bin/env python3
import json, os, subprocess, sys, time
from pathlib import Path
args = sys.argv[1:]
Path(os.environ['FAKE_ARGS']).write_text(json.dumps(args))
if os.environ.get('FAKE_FAIL'):
    print('startup diagnostic', file=sys.stderr)
    sys.exit(int(os.environ['FAKE_FAIL']))
if os.environ.get('FAKE_SLEEP'):
    time.sleep(2)
print(json.dumps({'type':'thread.started','thread_id':'abc-123'}), flush=True)
if os.environ.get('FAKE_HOLD'):
    time.sleep(float(os.environ['FAKE_HOLD']))
if os.environ.get('FAKE_HELPER_DIR'):
    helper = """import os, sys, time
from pathlib import Path
root = Path(sys.argv[1])
(root / 'ready').write_text(str(os.getpid()))
deadline = time.monotonic() + 15
while not (root / 'release').exists() and time.monotonic() < deadline:
    time.sleep(0.01)
(root / 'done').touch()
"""
    subprocess.Popen([sys.executable, '-c', helper, os.environ['FAKE_HELPER_DIR']],
                     close_fds=False, stdin=subprocess.DEVNULL,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    while not (Path(os.environ['FAKE_HELPER_DIR']) / 'ready').exists():
        time.sleep(0.01)
if os.environ.get('FAKE_TURN_FAIL'):
    print(json.dumps({'type':'turn.failed','error':'fake failure'}))
    sys.exit(0)
print(json.dumps({'type':'item.completed','item':{'type':'agent_message','text':'Outcome: IMPLEMENTED'}}))
print(json.dumps({'type':'turn.completed','usage':{'input_tokens':100,'cached_input_tokens':30,'output_tokens':20}}))
'''


class Helpers(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bin = self.root / 'bin'
        self.bin.mkdir()
        (self.bin / 'codex').write_text(FAKE)
        (self.bin / 'codex').chmod(0o755)
        self.work = self.root / 'work'
        self.work.mkdir()
        self.env = {**os.environ, 'IMPLEMENT_ROOT': str(self.root / 'runs'),
                    'FAKE_ARGS': str(self.root / 'args.json'),
                    'PATH': str(self.bin) + os.pathsep + os.environ['PATH']}
        self.env.pop('IMPLEMENT_MODEL', None)
        self.env.pop('IMPLEMENT_EFFORT', None)

    def call(self, script, *args, env=None):
        return subprocess.run([sys.executable, str(SKILL / 'scripts' / script), *map(str, args)],
                              env=env or self.env, input='task prompt', text=True, capture_output=True)

    def worker(self, *args, **kwargs):
        return self.call('codex_task.py', *args, **kwargs)

    def test_run_resume_model_and_immutable_attempts(self):
        first = self.worker('run', self.work, 'project/task-01')
        self.assertEqual(first.returncode, 0, first.stderr)
        state = self.root / 'runs/project/task-01'
        original = (state / 'events-1.jsonl').read_bytes()
        # Config defaults differ in the real incident; explicit -m must be present.
        resumed = self.worker('resume', 'project/task-01')
        self.assertEqual(resumed.returncode, 0, resumed.stderr)
        args = json.loads((self.root / 'args.json').read_text())
        self.assertIn('resume', args)
        self.assertEqual(args[args.index('-m') + 1], 'gpt-5.6-luna')
        self.assertEqual((state / 'events-1.jsonl').read_bytes(), original)
        self.assertTrue((state / 'prompt-2.md').exists())
        duplicate = self.worker('run', self.work, 'project/task-01')
        self.assertNotEqual(duplicate.returncode, 0)
        self.assertEqual((state / 'events-1.jsonl').read_bytes(), original)
        report = json.loads(self.worker('cost', 'project').stdout)
        self.assertEqual(report['structured_total_tokens'], 120)
        self.assertEqual(report['structured_usage']['cached_input_tokens'], 30)

    def test_task_model_choice_explicit_reassessment_and_resume_pin(self):
        for i, model in enumerate(('gpt-5.6-luna', 'gpt-5.6-terra', 'gpt-5.6-sol')):
            slug = f'project/task-{i}'
            result = self.worker('run', self.work, slug,
                env={**self.env, 'IMPLEMENT_MODEL': model, 'IMPLEMENT_EFFORT': 'medium'})
            self.assertEqual(result.returncode, 0, result.stderr)
            state = self.root / 'runs' / slug
            self.assertEqual(json.loads((state / 'attempt-1.json').read_text())['model'], model)
            result = self.worker('resume', slug,
                env={**self.env, 'IMPLEMENT_MODEL': 'gpt-5.6-sol', 'IMPLEMENT_EFFORT': 'high'})
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(self.worker('resume', slug).returncode, 0)
            final = json.loads((state / 'attempt-3.json').read_text())
            self.assertEqual((final['model'], final['effort']), ('gpt-5.6-sol', 'high'))
            self.assertEqual(json.loads((state / 'attempt-1.json').read_text())['model'], model)

    def test_astra_excluded_for_new_and_resumed_workers(self):
        denied = self.worker('run', self.work, 'project/denied',
            env={**self.env, 'IMPLEMENT_MODEL': 'gpt-6-astra'})
        self.assertNotEqual(denied.returncode, 0)
        self.assertIn('excluded by owner policy', denied.stderr)
        self.assertFalse((self.root / 'args.json').exists())
        self.assertEqual(self.worker('run', self.work, 'project/task-01').returncode, 0)
        state = self.root / 'runs/project/task-01'
        settings = json.dumps({'model': 'gpt-6-astra', 'effort': 'high'})
        (state / 'worker.json').write_text(settings)
        (self.root / 'args.json').unlink()
        denied = self.worker('resume', 'project/task-01')
        self.assertNotEqual(denied.returncode, 0)
        self.assertFalse((self.root / 'args.json').exists())
        self.assertEqual((state / 'worker.json').read_text(), settings)
        result = self.worker('resume', 'project/task-01',
            env={**self.env, 'IMPLEMENT_MODEL': 'gpt-5.6-sol', 'IMPLEMENT_EFFORT': 'high'})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((state / 'attempt-2.json').exists())

    def test_startup_exit_and_diagnostics_preserved(self):
        result = self.worker('run', self.work, 'project/task-01',
                             env={**self.env, 'FAKE_FAIL': '42'})
        self.assertEqual(result.returncode, 42)
        self.assertIn('startup diagnostic', result.stderr)
        state = self.root / 'runs/project/task-01'
        self.assertFalse((state / 'session.id').exists())
        self.assertEqual(json.loads((state / 'attempt-1.json').read_text())['codex_exit_code'], 42)
        report = json.loads(self.worker('cost').stdout)
        self.assertEqual(report['unknown_attempts'], 1)

    def test_policy_file_controls_defaults_allowlist_and_saved_resume(self):
        installed = self.root / 'installed'
        shutil.copytree(SKILL, installed)
        path = installed / 'model-policy.json'
        policy = json.loads(path.read_text())
        policy.update(allowed_models=['test-worker', 'next-worker'],
                      default_model='test-worker', default_effort='high')
        path.write_text(json.dumps(policy))

        def call(*args, env=None):
            return subprocess.run([sys.executable, str(installed / 'scripts/codex_task.py'), *map(str, args)],
                                  env=env or self.env, input='brief', text=True, capture_output=True)

        result = call('run', self.work, 'custom/code')
        self.assertEqual(result.returncode, 0, result.stderr)
        state = self.root / 'runs/custom/code'
        self.assertEqual(json.loads((state / 'worker.json').read_text()),
                         {'model': 'test-worker', 'effort': 'high'})
        policy.update(default_model='next-worker', default_effort='low')
        path.write_text(json.dumps(policy))
        self.assertEqual(call('resume', 'custom/code').returncode, 0)
        attempt = json.loads((state / 'attempt-2.json').read_text())
        self.assertEqual((attempt['model'], attempt['effort']), ('test-worker', 'high'))
        denied = call('resume', 'custom/code', env={**self.env, 'IMPLEMENT_MODEL': 'unlisted'})
        self.assertNotEqual(denied.returncode, 0)
        self.assertFalse((state / 'attempt-3.json').exists())
        policy['allowed_models'] = []
        path.write_text(json.dumps(policy))
        self.assertNotEqual(call('run', self.work, 'custom/invalid').returncode, 0)
        self.assertFalse((self.root / 'runs/custom/invalid/events-1.jsonl').exists())

    def test_large_prompt_startup_exit_preserved(self):
        result = subprocess.run([sys.executable, str(SKILL / 'scripts/codex_task.py'),
                                 'run', str(self.work), 'project/task-01'],
                                env={**self.env, 'FAKE_FAIL': '42'}, input='x' * 1000000,
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 42, result.stderr)
        state = self.root / 'runs/project/task-01'
        self.assertEqual(json.loads((state / 'attempt-1.json').read_text())['codex_exit_code'], 42)

    def test_legacy_resume_and_nested_cost_unknown(self):
        state = self.root / 'runs/project/task-01'
        state.mkdir(parents=True)
        (state / 'workdir').write_text(str(self.work))
        (state / 'session.id').write_text('abc-123')
        (state / 'transcript-1.txt').write_text('model: gpt-5.6-luna\nreasoning effort: high\n')
        (state / 'transcript-3.txt').write_text('preserve gap')
        (state / 'cost.tsv').write_text('date\ttranscript-1.txt\t123\ndate\ttranscript-3.txt\tunknown\n')
        result = self.worker('resume', 'project/task-01')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((state / 'events-4.jsonl').exists())
        self.assertEqual((state / 'transcript-3.txt').read_text(), 'preserve gap')
        report = json.loads(self.worker('cost', 'project').stdout)
        self.assertEqual(report['legacy_reported_tokens_sum'], 123)
        self.assertEqual(report['unknown_attempts'], 1)
        self.assertEqual(report['structured_total_tokens'], 120)

    def test_resume_without_model_metadata_refused(self):
        state = self.root / 'runs/project/task-01'
        state.mkdir(parents=True)
        (state / 'workdir').write_text(str(self.work))
        (state / 'session.id').write_text('abc-123')
        result = self.worker('resume', 'project/task-01')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('unknown original model/effort', result.stderr)
        self.assertFalse((self.root / 'args.json').exists())
        result = self.worker('resume', 'project/task-01',
                             env={**self.env, 'IMPLEMENT_MODEL': 'gpt-5.6-luna', 'IMPLEMENT_EFFORT': 'high'})
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_traversal_rejected(self):
        result = self.worker('run', self.work, '../escape')
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.root / 'escape').exists())

    def test_concurrent_resume_refused(self):
        self.assertEqual(self.worker('run', self.work, 'project/task-01').returncode, 0)
        (self.root / 'args.json').unlink()
        command = [sys.executable, str(SKILL / 'scripts/codex_task.py'), 'resume', 'project/task-01']
        with subprocess.Popen(command, env={**self.env, 'FAKE_SLEEP': '1'}, stdin=subprocess.DEVNULL,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as proc:
            for _ in range(100):
                if (self.root / 'args.json').exists():
                    break
                time.sleep(0.01)
            result = self.worker('resume', 'project/task-01')
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('already running', result.stderr)
            proc.communicate(timeout=5)
            self.assertEqual(proc.returncode, 0)

    def test_cumulative_usage_deltas_and_counter_decrease(self):
        state = self.root / 'runs/project/task-01'
        state.mkdir(parents=True)
        for n, total in enumerate([100, 180, 250, 200], 1):
            (state / f'attempt-{n}.json').write_text(json.dumps({
                'attempt': n, 'session_id': 'same-session',
                'usage': {'input_tokens': total, 'cached_input_tokens': 0, 'output_tokens': 0}}))
        report = json.loads(self.worker('cost', 'project').stdout)
        self.assertEqual(report['structured_total_tokens'], 250)
        self.assertEqual([a['usage_delta']['input_tokens'] for a in report['attempts'][:3]], [100, 80, 70])
        self.assertEqual(report['unknown_attempts'], 1)
        self.assertTrue(report['warnings'])

    def test_recover_missing_session_from_partial_events(self):
        state = self.root / 'runs/project/task-01'
        state.mkdir(parents=True)
        (state / 'workdir').write_text(str(self.work))
        (state / 'worker.json').write_text(json.dumps({'model': 'gpt-5.6-luna', 'effort': 'high'}))
        old = '{"type":"thread.started","thread_id":"abc-123"}\n{"partial"'
        (state / 'events-1.jsonl').write_text(old)
        result = self.worker('resume', 'project/task-01')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((state / 'session.id').read_text().strip(), 'abc-123')
        self.assertEqual((state / 'events-1.jsonl').read_text(), old)
        self.assertTrue((state / 'attempt-2.json').exists())
        self.assertEqual(json.loads(self.worker('cost', 'project').stdout)['unknown_attempts'], 1)

    def test_conflicting_session_recovery_refused(self):
        self.assertEqual(self.worker('run', self.work, 'project/task-01').returncode, 0)
        state = self.root / 'runs/project/task-01'
        (state / 'events-2.jsonl').write_text('{"type":"thread.started","thread_id":"other"}\n')
        result = self.worker('resume', 'project/task-01')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('conflicting session', result.stderr)
        self.assertEqual((state / 'session.id').read_text().strip(), 'abc-123')

    def start_held_worker(self, hold='3'):
        command = [sys.executable, str(SKILL / 'scripts/codex_task.py'),
                   'run', str(self.work), 'project/task-01']
        proc = subprocess.Popen(command, env={**self.env, 'FAKE_HOLD': hold},
                                stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        state = self.root / 'runs/project/task-01'
        for _ in range(300):
            if (state / 'session.id').exists():
                return proc, state
            if proc.poll() is not None:
                self.fail(proc.communicate())
            time.sleep(0.01)
        proc.kill()
        proc.communicate()
        self.fail('session identity was not persisted while worker running')

    def test_graceful_interrupt_preserves_identity_and_attempt(self):
        proc, state = self.start_held_worker('20')
        self.assertFalse((state / 'attempt-1.json').exists())
        proc.send_signal(signal.SIGTERM)
        proc.communicate(timeout=5)
        self.assertEqual(proc.returncode, 143)
        self.assertEqual(json.loads((state / 'attempt-1.json').read_text())['wrapper_exit_code'], 143)
        self.assertEqual(self.worker('resume', 'project/task-01').returncode, 0)

    def test_orphan_worker_retains_lock_after_wrapper_kill(self):
        proc, state = self.start_held_worker()
        proc.kill()
        proc.communicate(timeout=5)
        result = self.worker('resume', 'project/task-01')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('already running', result.stderr)
        # Wait for the fake child to exit; do not signal arbitrary process IDs.
        for _ in range(100):
            result = self.worker('resume', 'project/task-01')
            if result.returncode == 0:
                break
            self.assertIn('already running', result.stderr)
            time.sleep(0.05)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((state / 'attempt-1.json').exists())
        self.assertTrue((state / 'attempt-2.json').exists())

    def test_completed_worker_releases_lock_while_helper_survives(self):
        for failure in (False, True):
            with self.subTest(failure=failure):
                helper = self.root / ('helper-failed' if failure else 'helper-ok')
                helper.mkdir()
                slug = 'project/' + helper.name
                env = {**self.env, 'FAKE_HELPER_DIR': str(helper)}
                if failure:
                    env['FAKE_TURN_FAIL'] = '1'
                try:
                    result = self.worker('run', self.work, slug, env=env)
                    self.assertEqual(result.returncode, 2 if failure else 0, result.stderr)
                    self.assertTrue((helper / 'ready').exists())
                    self.assertFalse((helper / 'done').exists())
                    state = self.root / 'runs' / slug
                    self.assertTrue((state / 'attempt-1.json').exists())
                    resumed = self.worker('resume', slug)
                    self.assertEqual(resumed.returncode, 0, resumed.stderr)
                    self.assertTrue((state / 'attempt-2.json').exists())
                    self.assertFalse((helper / 'done').exists())
                finally:
                    (helper / 'release').touch()
                    for _ in range(300):
                        if (helper / 'done').exists():
                            break
                        time.sleep(0.01)
                    self.assertTrue((helper / 'done').exists(), 'fake helper did not exit')

    def test_review_copy_cannot_disturb_original_index(self):
        self.prepare_repo()
        review = self.root / 'review'
        self.assertEqual(self.call('review_gate.py', 'snapshot', self.work, review).returncode, 0)
        (self.work / '.gitattributes').write_text('new export-ignore\nfile export-subst\n')
        self.git('add', '.gitattributes')
        review = self.root / 'review-with-attributes'
        self.assertEqual(self.call('review_gate.py', 'snapshot', self.work, review).returncode, 0)
        before = self.git('write-tree')
        copy = self.root / 'copy'
        baseline = self.root / 'baseline'
        self.assertEqual(self.call('review_copy.py', review / 'snapshot.json', copy).returncode, 0)
        self.assertEqual((copy / 'new').read_text(), 'new content\n')
        self.assertFalse((copy / '.git').exists())
        (copy / 'file').write_text('reviewer test modified copy')
        self.assertEqual(self.git('write-tree'), before)
        self.assertEqual((self.work / 'file').read_text(), 'two\n')
        self.assertEqual(self.call('review_copy.py', review / 'snapshot.json', baseline, '--baseline').returncode, 0)
        self.assertEqual((baseline / 'file').read_text(), 'one\n')

    def test_recovery_observes_actual_head_and_dirty_tree(self):
        self.prepare_repo()
        run = self.root / 'run'
        args = ('run_state.py', run, self.work, '--next-action', 'inspect partial changes', '--completed', 'T00=HEAD')
        result = self.call(*args)
        self.assertEqual(result.returncode, 0, result.stderr)
        record = json.loads(result.stdout)
        self.assertEqual(record['head'], self.git('rev-parse', 'HEAD'))
        self.assertTrue(record['git_status'])
        (self.work / 'file').write_text('unstaged content')
        current = json.loads(self.call(*args).stdout)
        self.assertIn('MM file', current['git_status'])
        self.git('reset', '--', 'file')
        self.assertIn(' M file', json.loads(self.call(*args).stdout)['git_status'])
        self.assertEqual(json.loads((run / 'recovery.json').read_text())['next_action'], 'inspect partial changes')

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.work), *args], stderr=subprocess.PIPE).decode().strip()

    def prepare_repo(self):
        self.git('init')
        self.git('config', 'user.email', 'test@example.invalid')
        self.git('config', 'user.name', 'Test')
        (self.work / 'file').write_text('one\n')
        self.git('add', 'file')
        self.git('-c', 'core.hooksPath=/dev/null', 'commit', '-m', 'baseline')
        (self.work / 'file').write_text('two\n')
        (self.work / 'new').write_text('new content\n')
        self.git('add', 'file', 'new')

    def test_review_rejects_same_stat_different_content(self):
        self.prepare_repo()
        review = self.root / 'review'
        result = self.call('review_gate.py', 'snapshot', self.work, review)
        self.assertEqual(result.returncode, 0, result.stderr)
        manifest = json.loads((review / 'snapshot.json').read_text())
        self.assertIn('new content', (review / 'diff.patch').read_text())
        (review / 'verdict.md').write_text('VERDICT: CHANGES\nTREE: ' + manifest['tree'] + '\n')
        self.assertNotEqual(self.call('review_gate.py', 'verify', self.work, review).returncode, 0)
        (review / 'verdict.md').write_text('VERDICT: APPROVE\nTREE: ' + manifest['tree'] + '\n')
        self.assertEqual(self.call('review_gate.py', 'verify', self.work, review).returncode, 0)
        before = self.git('diff', '--cached', '--stat')
        (self.work / 'file').write_text('six\n')
        self.git('add', 'file')
        self.assertEqual(self.git('diff', '--cached', '--stat'), before)
        self.assertNotEqual(self.call('review_gate.py', 'verify', self.work, review).returncode, 0)

    def test_review_rejects_unstaged_and_new_untracked(self):
        self.prepare_repo()
        review = self.root / 'review'
        self.assertEqual(self.call('review_gate.py', 'snapshot', self.work, review).returncode, 0)
        tree = json.loads((review / 'snapshot.json').read_text())['tree']
        (review / 'verdict.md').write_text('VERDICT: APPROVE\nTREE: ' + tree + '\n')
        (self.work / 'surprise').write_text('unexpected')
        self.assertNotEqual(self.call('review_gate.py', 'verify', self.work, review).returncode, 0)
        (self.work / 'file').write_text('unstaged')
        self.assertNotEqual(self.call('review_gate.py', 'snapshot', self.work, self.root / 'review2').returncode, 0)


if __name__ == '__main__':
    unittest.main()
