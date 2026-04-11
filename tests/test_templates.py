import tempfile
import shutil
import unittest
from pathlib import Path

from brain.templates import create_entity, render_template

# Need real templates to test, so we copy from the project
PROJ_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = PROJ_ROOT / "templates"


class RenderTemplateTests(unittest.TestCase):
    def _setup_root(self, td):
        root = Path(td)
        shutil.copytree(TEMPLATE_DIR, root / "templates")
        return root

    def test_render_person(self):
        with tempfile.TemporaryDirectory() as td:
            root = self._setup_root(td)
            text = render_template(root, "person", "Alice Smith", tags=["friend"])
            self.assertIn("type: person", text)
            self.assertIn("# Alice Smith", text)
            self.assertIn("## Compiled Truth", text)
            self.assertIn("## Timeline (append-only)", text)
            self.assertIn("friend", text)

    def test_render_company(self):
        with tempfile.TemporaryDirectory() as td:
            root = self._setup_root(td)
            text = render_template(root, "company", "Acme Inc", tags=["ai", "startup"])
            self.assertIn("type: company", text)
            self.assertIn("# Acme Inc", text)

    def test_render_unknown_type_raises(self):
        with tempfile.TemporaryDirectory() as td:
            root = self._setup_root(td)
            with self.assertRaises(ValueError):
                render_template(root, "nonexistent", "Test")


class CreateEntityTests(unittest.TestCase):
    def _setup_root(self, td):
        root = Path(td)
        shutil.copytree(TEMPLATE_DIR, root / "templates")
        return root

    def test_create_person(self):
        with tempfile.TemporaryDirectory() as td:
            root = self._setup_root(td)
            path = create_entity(root, "person", "Bob", tags=["colleague"])
            self.assertTrue(path.exists())
            self.assertEqual(path.name, "Bob.md")
            self.assertEqual(path.parent.name, "people")
            content = path.read_text()
            self.assertIn("# Bob", content)

    def test_create_company(self):
        with tempfile.TemporaryDirectory() as td:
            root = self._setup_root(td)
            path = create_entity(root, "company", "Acme Corp")
            self.assertTrue(path.exists())
            self.assertEqual(path.parent.name, "companies")

    def test_no_overwrite_by_default(self):
        with tempfile.TemporaryDirectory() as td:
            root = self._setup_root(td)
            create_entity(root, "person", "Bob")
            with self.assertRaises(FileExistsError):
                create_entity(root, "person", "Bob")

    def test_force_overwrite(self):
        with tempfile.TemporaryDirectory() as td:
            root = self._setup_root(td)
            create_entity(root, "person", "Bob")
            path = create_entity(root, "person", "Bob", force=True)
            self.assertTrue(path.exists())


if __name__ == "__main__":
    unittest.main()
