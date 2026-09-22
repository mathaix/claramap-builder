import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.skills = Path(self.tmp.name) / 'skills'

    def call(self, name='implement', *extra):
        return subprocess.run([sys.executable, str(ROOT / 'scripts/install.py'), *([name] if name else []),
                               '--skills-dir', str(self.skills), *extra], text=True, capture_output=True)

    def test_install_includes_references_and_executable_wrapper(self):
        result = self.call()
        self.assertEqual(result.returncode, 0, result.stderr)
        target = self.skills / 'implement'
        self.assertTrue((target / 'SKILL.md').is_file())
        self.assertEqual((target / 'LICENSE').read_text(), (ROOT / 'LICENSE').read_text())
        self.assertTrue((target / 'references/specstory.md').is_file())
        self.assertTrue((target / 'assets/templates/requirements.md').is_file())
        self.assertEqual(json.loads((target / 'model-policy.json').read_text()),
                         json.loads((ROOT / 'skills/implement/model-policy.json').read_text()))
        self.assertTrue((target / 'codex_task.sh').stat().st_mode & 0o111)
        self.assertFalse((target / '.git').exists())
        smoke = subprocess.run([sys.executable, str(target / 'scripts/scaffold.py'),
                                str(Path(self.tmp.name) / 'work'), 'demo'], capture_output=True)
        self.assertEqual(smoke.returncode, 0)
        for script in ('review_gate.py', 'run_state.py'):
            smoke = subprocess.run([sys.executable, str(target / 'scripts' / script), '--help'],
                                   capture_output=True)
            self.assertEqual(smoke.returncode, 0, smoke.stderr)

    def test_improvement_skill_installs_independently_with_its_assets(self):
        result = self.call('improve-workflow')
        self.assertEqual(result.returncode, 0, result.stderr)
        target = self.skills / 'improve-workflow'
        self.assertTrue((target / 'SKILL.md').is_file())
        self.assertTrue((target / 'references/specstory.md').is_file())
        self.assertTrue((target / 'assets/workflow-feedback.png').is_file())
        self.assertEqual((target / 'LICENSE').read_text(), (ROOT / 'LICENSE').read_text())
        self.assertFalse((self.skills / 'implement').exists())

    def test_replace_backs_up_edits_and_preserves_other_skills(self):
        self.assertEqual(self.call().returncode, 0)
        target = self.skills / 'implement/SKILL.md'
        target.write_text('local changes')
        other = self.skills / 'another'; other.mkdir(); (other / 'keep').write_text('preserved')
        refused = self.call()
        self.assertNotEqual(refused.returncode, 0)
        self.assertEqual(target.read_text(), 'local changes')
        replaced = self.call('implement', '--replace')
        self.assertEqual(replaced.returncode, 0, replaced.stderr)
        backup = Path(json.loads(replaced.stdout)['backup'])
        self.assertEqual((backup / 'SKILL.md').read_text(), 'local changes')
        self.assertNotIn(self.skills, backup.parents)
        self.assertEqual((other / 'keep').read_text(), 'preserved')

    def test_rejects_traversal_missing_skill_and_symlink_destination(self):
        self.assertNotEqual(self.call('../implement').returncode, 0)
        self.assertNotEqual(self.call('does-not-exist').returncode, 0)
        self.skills.mkdir()
        outside = Path(self.tmp.name) / 'outside'; outside.mkdir()
        (outside / 'keep').write_text('untouched')
        (self.skills / 'implement').symlink_to(outside, target_is_directory=True)
        self.assertNotEqual(self.call('implement', '--replace').returncode, 0)
        self.assertEqual((outside / 'keep').read_text(), 'untouched')

    def test_refuses_replacing_collection_source(self):
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/install.py'), 'implement',
                                 '--skills-dir', str(ROOT / 'skills'), '--replace'], capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue((ROOT / 'skills/implement/SKILL.md').is_file())

    def test_default_installs_both_and_replacement_backs_up_both(self):
        result = self.call(None)
        self.assertEqual(result.returncode, 0, result.stderr)
        for name in ('implement', 'improve-workflow'):
            (self.skills / name / 'SKILL.md').write_text('local ' + name)
        result = self.call(None, '--replace')
        self.assertEqual(result.returncode, 0, result.stderr)
        records = json.loads(result.stdout)
        self.assertEqual({r['skill'] for r in records}, {'implement', 'improve-workflow'})
        for record in records:
            self.assertEqual((Path(record['backup']) / 'SKILL.md').read_text(),
                             'local ' + record['skill'])
            self.assertTrue((Path(record['installed']) / 'SKILL.md').is_file())

    def test_second_destination_conflict_leaves_first_uninstalled(self):
        self.assertEqual(self.call('improve-workflow').returncode, 0)
        result = self.call(None)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.skills / 'implement').exists())

    def test_failed_second_publish_restores_both_originals(self):
        import importlib.util
        from unittest.mock import patch
        spec = importlib.util.spec_from_file_location('installer', ROOT / 'scripts/install.py')
        installer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(installer)
        self.assertEqual(self.call(None).returncode, 0)
        for name in installer.BUNDLED_SKILLS:
            (self.skills / name / 'SKILL.md').write_text('local ' + name)
        original_rename = Path.rename

        def fail_second(path, target):
            if path.name == 'improve-workflow' and path.parent.name.startswith('.claramap-install-'):
                raise OSError('simulated publish failure')
            return original_rename(path, target)

        with patch.object(Path, 'rename', fail_second):
            with self.assertRaisesRegex(OSError, 'simulated'):
                installer.install_many(installer.BUNDLED_SKILLS, self.skills, replace=True)
        for name in installer.BUNDLED_SKILLS:
            self.assertEqual((self.skills / name / 'SKILL.md').read_text(), 'local ' + name)
