"""Exercise recovery state and integrated review using real temporary Git repos."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SKILL = Path(__file__).resolve().parents[1]


class ReviewAndRecovery(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.work = self.root / 'work'
        self.work.mkdir()
        self.run = self.root / 'run'
        self.git('init')
        self.git('config', 'user.email', 'test@example.invalid')
        self.git('config', 'user.name', 'Test')
        (self.work / 'file').write_text('baseline\n')
        self.commit('baseline')
        self.base = self.git('rev-parse', 'HEAD')

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.work), *args],
                                       stderr=subprocess.PIPE).decode().strip()

    def commit(self, message):
        self.git('add', '.')
        self.git('-c', 'core.hooksPath=/dev/null', 'commit', '-m', message)

    def call(self, script, *args):
        return subprocess.run([sys.executable, str(SKILL / 'scripts' / script), *map(str, args)],
                              capture_output=True, text=True)

    def recovery(self, *args):
        return self.call('run_state.py', self.run, self.work, '--next-action', 'implement', *args)

    def read_ok(self, result):
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def approve(self, review):
        saved = json.loads((review / 'snapshot.json').read_text())
        (review / 'verdict.md').write_text('VERDICT: APPROVE\nTREE: ' + saved['tree'] + '\n')

    def test_recovery_creates_run_dir_and_preserves_existing_keys(self):
        (self.run / 'nested').mkdir(parents=True)
        (self.run / 'recovery.json').write_text(json.dumps({
            'completed': {'T00': self.base}, 'evidence': ['unchanged-report.md'],
            'plan_ready': True, 'execution_ready': True, 'plan_approvals': [{'review': 'review-1'}],
            'plan_review_required': False, 'plan_review_decision': {'policy': 'not-required'}}))
        state = self.read_ok(self.recovery())
        for stale in ('plan_ready', 'execution_ready', 'plan_approvals', 'plan_review_required', 'plan_review_decision'):
            self.assertNotIn(stale, state)
        self.assertNotIn('plan_ready', (self.run / 'recovery.json').read_text())
        self.assertEqual(state['completed'], {'T00': self.base})
        self.assertEqual(state['evidence'], ['unchanged-report.md'])
        self.assertEqual(state['head'], self.base)
        self.assertIn('Next action: implement', (self.run / 'recovery.md').read_text())
        fresh = self.root / 'fresh'
        self.read_ok(self.call('run_state.py', fresh, self.work, '--next-action', 'start'))
        self.assertTrue((fresh / 'recovery.md').is_file())

    def test_recovery_discovers_arbitrary_and_nested_worker_names(self):
        for name in ('diagnosis', 'checks/database'):
            worker = self.run / name
            worker.mkdir(parents=True)
            (worker / 'workdir').write_text(str(self.work))
            (worker / 'events-1.jsonl').write_text('')
            (worker / 'attempt-1.json').write_text('{"wrapper_exit_code": 0}')
        (self.run / 'task-legacy').mkdir()
        state = self.read_ok(self.recovery())
        self.assertEqual(state['workers'], {
            'diagnosis': 'exited_pending_verification',
            'checks/database': 'exited_pending_verification',
            'task-legacy': 'legacy_or_not_started'})

    def test_completed_commit_ancestry_is_enforced_and_not_erased(self):
        self.git('checkout', '-b', 'unrelated')
        (self.work / 'other').write_text('other branch')
        self.commit('other')
        other = self.git('rev-parse', 'HEAD')
        self.git('checkout', '--detach', self.base)
        self.run.mkdir()
        (self.run / 'recovery.json').write_text(json.dumps({'completed': {'T01': other}}))
        before = (self.run / 'recovery.json').read_bytes()
        result = self.recovery()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((self.run / 'recovery.json').read_bytes(), before)

    def test_integrated_snapshot_includes_committed_and_staged_changes_and_exports_base(self):
        (self.work / 'committed').write_text('committed work\n')
        self.commit('implemented')
        head = self.git('rev-parse', 'HEAD')
        (self.work / 'staged').write_text('staged work\n')
        self.git('add', 'staged')
        review = self.root / 'review'
        self.read_ok(self.call('review_gate.py', 'snapshot', self.work, review, '--base', self.base))
        saved = json.loads((review / 'snapshot.json').read_text())
        self.assertEqual(saved['head'], head)
        self.assertEqual(saved['review_base'], self.base)
        patch = (review / 'diff.patch').read_text()
        self.assertIn('+committed work', patch)
        self.assertIn('+staged work', patch)
        self.approve(review)
        self.assertEqual(self.call('review_gate.py', 'verify', self.work, review).returncode, 0)
        baseline = self.root / 'baseline'
        self.read_ok(self.call('review_copy.py', review / 'snapshot.json', baseline, '--baseline'))
        self.assertFalse((baseline / 'committed').exists())
        self.assertFalse((baseline / 'staged').exists())
        copy = self.root / 'copy'
        self.read_ok(self.call('review_copy.py', review / 'snapshot.json', copy))
        self.assertEqual((copy / 'committed').read_text(), 'committed work\n')
        self.assertEqual((copy / 'staged').read_text(), 'staged work\n')
        (self.work / 'staged').write_text('edited work\n')
        self.git('add', 'staged')
        self.assertNotEqual(self.call('review_gate.py', 'verify', self.work, review).returncode, 0)

    def test_changed_base_manifest_is_rejected(self):
        (self.work / 'file').write_text('committed\n')
        self.commit('implementation')
        review = self.root / 'review'
        self.read_ok(self.call('review_gate.py', 'snapshot', self.work, review, '--base', self.base))
        self.approve(review)
        manifest = review / 'snapshot.json'
        saved = json.loads(manifest.read_text())
        saved['review_base'] = saved['head']
        saved['review_base_tree'] = self.git('rev-parse', saved['head'] + '^{tree}')
        manifest.write_text(json.dumps(saved))
        result = self.call('review_gate.py', 'verify', self.work, review)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('does not match its base and tree', result.stderr)

    def test_edited_patch_with_updated_digest_still_must_match_git_objects(self):
        (self.work / 'file').write_text('implementation\n')
        self.commit('implementation')
        review = self.root / 'review'
        self.read_ok(self.call('review_gate.py', 'snapshot', self.work, review, '--base', self.base))
        self.approve(review)
        data = b'edited review patch\n'
        (review / 'diff.patch').write_bytes(data)
        manifest = review / 'snapshot.json'
        saved = json.loads(manifest.read_text())
        saved['patch_sha256']['diff.patch'] = hashlib.sha256(data).hexdigest()
        manifest.write_text(json.dumps(saved))
        result = self.call('review_gate.py', 'verify', self.work, review)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('does not match its base and tree', result.stderr)

    def test_integrated_merge_snapshot_keeps_both_parent_patches(self):
        self.git('checkout', '-b', 'side')
        (self.work / 'side').write_text('side change\n')
        self.commit('side')
        side = self.git('rev-parse', 'HEAD')
        self.git('checkout', '-b', 'topic', self.base)
        (self.work / 'topic').write_text('topic change\n')
        self.commit('topic')
        self.git('merge', '--no-commit', '--no-ff', side)
        review = self.root / 'review'
        self.read_ok(self.call('review_gate.py', 'snapshot', self.work, review, '--base', self.base))
        saved = json.loads((review / 'snapshot.json').read_text())
        self.assertEqual(set(saved['patch_sha256']), {'diff.patch', 'parent-1.patch', 'parent-2.patch'})
        self.assertIn('+side change', (review / 'parent-1.patch').read_text())
        self.assertIn('+topic change', (review / 'parent-2.patch').read_text())
        self.approve(review)
        self.assertEqual(self.call('review_gate.py', 'verify', self.work, review).returncode, 0)

    def test_default_snapshot_still_uses_head_and_invalid_base_is_non_mutating(self):
        (self.work / 'committed').write_text('already committed\n')
        self.commit('implementation')
        (self.work / 'staged').write_text('pending\n')
        self.git('add', 'staged')
        review = self.root / 'review'
        self.read_ok(self.call('review_gate.py', 'snapshot', self.work, review))
        self.assertNotIn('already committed', (review / 'diff.patch').read_text())
        self.assertNotIn('review_base', json.loads((review / 'snapshot.json').read_text()))
        self.approve(review)
        self.assertEqual(self.call('review_gate.py', 'verify', self.work, review).returncode, 0)
        invalid = self.root / 'invalid'
        self.assertNotEqual(self.call('review_gate.py', 'snapshot', self.work, invalid,
                                     '--base', 'does-not-exist').returncode, 0)
        self.assertFalse(invalid.exists())
        self.assertNotEqual(self.call('review_gate.py', 'verify', self.work, review,
                                     '--base', self.base).returncode, 0)


if __name__ == '__main__':
    unittest.main()
