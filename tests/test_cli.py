import json
import subprocess
import sys
import tempfile
import shutil
import unittest
from pathlib import Path

PROJ_ROOT = Path(__file__).resolve().parents[1]


class CLITests(unittest.TestCase):
    def run_cli(self, *args, root=None):
        cmd_root = root or str(PROJ_ROOT)
        return subprocess.run(
            [sys.executable, "-m", "brain.cli", "--root", cmd_root, *args],
            cwd=PROJ_ROOT,
            text=True,
            capture_output=True,
        )

    # --- validate ---
    def test_validate_passes(self):
        proc = self.run_cli("validate")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("OK", proc.stdout)

    def test_validate_json(self):
        proc = self.run_cli("validate", "--json")
        self.assertEqual(proc.returncode, 0)
        payload = json.loads(proc.stdout)
        self.assertIn("files_checked", payload)
        self.assertIn("total_errors", payload)

    # --- status ---
    def test_status_text(self):
        proc = self.run_cli("status")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("Brain:", proc.stdout)
        self.assertIn("Files:", proc.stdout)
        self.assertIn("Entities:", proc.stdout)

    def test_status_json(self):
        proc = self.run_cli("status", "--json")
        self.assertEqual(proc.returncode, 0)
        payload = json.loads(proc.stdout)
        self.assertIn("total_files", payload)
        self.assertIn("by_bucket", payload)

    # --- search ---
    def test_search_finds_entity(self):
        proc = self.run_cli("search", "Amazon")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("Amazon", proc.stdout)

    def test_search_no_results(self):
        proc = self.run_cli("search", "zzz_nonexistent_zzz")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("No results", proc.stdout)

    def test_search_json(self):
        proc = self.run_cli("search", "Amazon", "--json")
        self.assertEqual(proc.returncode, 0)
        payload = json.loads(proc.stdout)
        self.assertIsInstance(payload, list)
        self.assertGreater(len(payload), 0)

    # --- add ---
    def test_add_creates_entity(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            shutil.copytree(PROJ_ROOT / "templates", root / "templates")
            (root / "meta").mkdir()
            proc = self.run_cli("add", "person", "Test User", "--tags", "test", root=str(root))
            self.assertEqual(proc.returncode, 0)
            self.assertIn("Created:", proc.stdout)
            self.assertTrue((root / "people" / "Test_User.md").exists())

    def test_add_no_overwrite(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            shutil.copytree(PROJ_ROOT / "templates", root / "templates")
            (root / "meta").mkdir()
            self.run_cli("add", "person", "Dupe", root=str(root))
            proc = self.run_cli("add", "person", "Dupe", root=str(root))
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("Already exists", proc.stdout)

    # --- inbox ---
    def test_inbox_capture(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "meta").mkdir()
            (root / "templates").mkdir()
            proc = self.run_cli("inbox", "test note content", root=str(root))
            self.assertEqual(proc.returncode, 0)
            self.assertIn("Captured:", proc.stdout)
            inbox_files = list((root / "inbox").glob("*.md"))
            self.assertEqual(len(inbox_files), 1)

    # --- timeline ---
    def test_timeline_shows_entries(self):
        proc = self.run_cli("timeline", "Amazon")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("Amazon", proc.stdout)
        self.assertIn("source:", proc.stdout)

    def test_timeline_not_found(self):
        proc = self.run_cli("timeline", "nonexistent_entity_xyz")
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("not found", proc.stdout.lower())

    def test_timeline_json(self):
        proc = self.run_cli("timeline", "Amazon", "--json")
        self.assertEqual(proc.returncode, 0)
        payload = json.loads(proc.stdout)
        self.assertIn("entries", payload)

    # --- dream ---
    def test_dream_runs(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "meta").mkdir()
            (root / "meta" / "dreams").mkdir()
            (root / "templates").mkdir()
            (root / "inbox").mkdir()
            proc = self.run_cli("dream", root=str(root))
            self.assertEqual(proc.returncode, 0)
            self.assertIn("Dream Cycle", proc.stdout)

    def test_dream_json(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "meta").mkdir()
            (root / "meta" / "dreams").mkdir()
            (root / "templates").mkdir()
            proc = self.run_cli("dream", "--json", root=str(root))
            self.assertEqual(proc.returncode, 0)
            payload = json.loads(proc.stdout)
            self.assertIn("date", payload)
            self.assertIn("dream_file", payload)


if __name__ == "__main__":
    unittest.main()
