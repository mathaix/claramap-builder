import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/scaffold.py"


class ScaffoldTests(unittest.TestCase):
    def test_creates_spec_folder_in_repo_and_never_overwrites(self):
        with tempfile.TemporaryDirectory() as temp:
            work = Path(temp) / "work"
            args = [sys.executable, str(SCRIPT), str(work), "fix-inputs", "--title", "Fix inputs"]
            result = subprocess.run(args, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            spec = work / "specs/fix-inputs"
            self.assertEqual(sorted(p.name for p in spec.iterdir()), ["design.md", "requirements.md", "tasks.md"])
            requirements = (spec / "requirements.md").read_text()
            self.assertIn("# Fix inputs", requirements)
            self.assertIn("THE SYSTEM SHALL", requirements)
            (spec / "requirements.md").write_text("owner decision")
            self.assertNotEqual(subprocess.run(args, capture_output=True).returncode, 0)
            self.assertEqual((spec / "requirements.md").read_text(), "owner decision")
            bad = subprocess.run([sys.executable, str(SCRIPT), str(work), "../escape"], capture_output=True)
            self.assertNotEqual(bad.returncode, 0)
            self.assertFalse((Path(temp) / "specs").exists())
