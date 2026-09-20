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
