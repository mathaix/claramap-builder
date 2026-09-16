import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/scaffold.py"

class CompactScaffoldTests(unittest.TestCase):
    def test_compact_creates_one_record_and_preserves_existing_run(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Path(temp) / "run"
            args = [sys.executable, str(SCRIPT), str(run), "--compact", "--title", "Fix inputs"]
            result = subprocess.run(args, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual([p.name for p in run.iterdir()], ["status.md"])
            (run / "status.md").write_text("owner decision")
            result = subprocess.run(args, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual((run / "status.md").read_text(), "owner decision")
