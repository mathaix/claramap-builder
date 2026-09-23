import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/usage.py'


class UsageTests(unittest.TestCase):
    def test_sums_per_model_with_codex_cumulative_and_claude_dedupe(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            task = root / 'run/task-01'
            task.mkdir(parents=True)
            for n, total in ((1, 100), (2, 150)):  # same session: cumulative, keep the last
                (task / f'attempt-{n}.json').write_text(json.dumps({
                    'model': 'gpt-x', 'session_id': 's1',
                    'usage': {'input_tokens': total, 'cached_input_tokens': 40, 'output_tokens': 10}}))
            session = root / 'sess.jsonl'
            entry = {'message': {'id': 'm1', 'model': 'claude-a', 'usage': {
                'input_tokens': 5, 'cache_read_input_tokens': 20, 'cache_creation_input_tokens': 3, 'output_tokens': 7}}}
            session.write_text(json.dumps(entry) + '\n' + json.dumps(entry) + '\n')  # repeated block
            agents = root / 'sess/subagents'
            agents.mkdir(parents=True)
            (agents / 'agent-1.jsonl').write_text(json.dumps({'message': {'id': 'm2', 'model': 'claude-b', 'usage': {
                'input_tokens': 1, 'cache_read_input_tokens': 2, 'cache_creation_input_tokens': 0, 'output_tokens': 4}}}) + '\n')
            out = subprocess.run([sys.executable, str(SCRIPT), '--run', str(root / 'run'), '--session', str(session)],
                                 capture_output=True, text=True, check=True).stdout
            rows = {cells[1]: [c.replace(',', '') for c in cells[2:6]] for line in out.splitlines()
                    if line.startswith('| ') and (cells := [c.strip() for c in line.split('|')])[1] not in ('model', '---')}
            self.assertEqual(rows['gpt-x'], ['110', '40', '0', '10'])
            self.assertEqual(rows['claude-a'], ['5', '20', '3', '7'])
            self.assertEqual(rows['claude-b'], ['1', '2', '0', '4'])
            self.assertEqual((root / 'run/usage.md').read_text(), out)

    def test_defaults_to_current_claude_session(self):
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp) / 'home'
            work = Path(temp) / 'work'
            work.mkdir()
            project = home / '.claude/projects' / work.resolve().as_posix().replace('/', '-')
            project.mkdir(parents=True)
            (project / 'abc.jsonl').write_text(json.dumps({'message': {'id': 'm', 'model': 'claude-c', 'usage': {
                'input_tokens': 9, 'cache_read_input_tokens': 0, 'cache_creation_input_tokens': 0, 'output_tokens': 1}}}) + '\n')
            out = subprocess.run([sys.executable, str(SCRIPT)], cwd=work, capture_output=True, text=True, check=True,
                                 env={**os.environ, 'HOME': str(home), 'CLAUDE_CODE_SESSION_ID': 'abc'}).stdout
            self.assertIn('| claude-c | 9 | 0 | 0 | 1 |', out)

    def run_codex_report(self, root, attempts, unfinished=()):
        task = root / 'task-01'
        task.mkdir()
        for number, model, usage in attempts:
            (task / f'attempt-{number}.json').write_text(json.dumps({
                'model': model, 'session_id': 's1', 'usage': usage}))
        for number in unfinished:
            (task / f'events-{number}.jsonl').write_text('')
        env = {k: v for k, v in os.environ.items() if k != 'CLAUDE_CODE_SESSION_ID'}
        return subprocess.run([sys.executable, str(SCRIPT), '--run', str(root)],
                              capture_output=True, text=True, check=True, env=env).stdout

    def test_resume_attributes_numeric_attempt_deltas_to_their_models(self):
        with tempfile.TemporaryDirectory() as temp:
            out = self.run_codex_report(Path(temp), [
                (2, 'luna', {'input_tokens': 100, 'cached_input_tokens': 20, 'output_tokens': 10}),
                (10, 'terra', {'input_tokens': 150, 'cached_input_tokens': 30, 'output_tokens': 15}),
            ])
            self.assertIn('| luna | 80 | 20 | 0 | 10 |', out)
            self.assertIn('| terra | 40 | 10 | 0 | 5 |', out)

    def test_missing_claude_session_warns_in_saved_report(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            out = self.run_codex_report(root, [])
            self.assertIn('No Claude session detected or supplied', out)
            self.assertIn('--session <transcript.jsonl>', out)
            self.assertIn('not exact per-goal accounting', out)
            self.assertEqual((root / 'usage.md').read_text(), out)

    def test_missing_usage_does_not_assign_unknown_interval_to_next_model(self):
        with tempfile.TemporaryDirectory() as temp:
            out = self.run_codex_report(Path(temp), [
                (1, 'luna', {'input_tokens': 100, 'cached_input_tokens': 20, 'output_tokens': 10}),
                (2, 'terra', None),
                (3, 'sol', {'input_tokens': 150, 'cached_input_tokens': 30, 'output_tokens': 15}),
            ])
            self.assertIn('| luna | 80 | 20 | 0 | 10 |', out)
            self.assertIn('| unattributed Codex usage | 40 | 10 | 0 | 5 |', out)
            self.assertNotIn('| sol |', out)
            self.assertIn('attempt usage unknown', out)

    def test_counter_reset_omits_unknown_interval_then_uses_new_baseline(self):
        with tempfile.TemporaryDirectory() as temp:
            out = self.run_codex_report(Path(temp), [
                (1, 'luna', {'input_tokens': 100, 'cached_input_tokens': 20, 'output_tokens': 10}),
                (2, 'terra', {'input_tokens': 10, 'cached_input_tokens': 2, 'output_tokens': 1}),
                (3, 'terra', {'input_tokens': 30, 'cached_input_tokens': 5, 'output_tokens': 3}),
            ])
            self.assertIn('| luna | 80 | 20 | 0 | 10 |', out)
            self.assertIn('| terra | 17 | 3 | 0 | 2 |', out)
            self.assertIn('interval omitted', out)

    def test_unfinished_attempt_marks_later_delta_unattributed(self):
        with tempfile.TemporaryDirectory() as temp:
            out = self.run_codex_report(Path(temp), [
                (1, 'luna', {'input_tokens': 100, 'cached_input_tokens': 20, 'output_tokens': 10}),
                (3, 'terra', {'input_tokens': 150, 'cached_input_tokens': 30, 'output_tokens': 15}),
            ], unfinished=(2,))
            self.assertIn('| unattributed Codex usage | 40 | 10 | 0 | 5 |', out)
            self.assertNotIn('| terra |', out)
            self.assertIn('no final attempt record; usage unknown', out)
