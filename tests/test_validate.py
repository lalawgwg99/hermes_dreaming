import tempfile
import unittest
from pathlib import Path

from brain.parser import parse_entity
from brain.validate import validate_entity, validate_all


VALID_COMPANY = """\
---
type: company
updated_at: 2026-04-11
tags:
  - tech
---

# TestCo

## Compiled Truth
- What it does: testing

## Timeline (append-only)
- 2026-04-11 — Created (source: manual | test)
"""

BAD_FRONTMATTER = """\
---
type: wrong_type
updated_at: not-a-date
---

# BadFM

## Compiled Truth
- something

## Timeline (append-only)
- 2026-04-11 — Event (source: manual)
"""

MISSING_SECTIONS = """\
---
type: person
updated_at: 2026-04-11
tags:
  - test
---

# NoSections

Just some text.
"""

MISSING_SOURCE_IN_TIMELINE = """\
---
type: idea
updated_at: 2026-04-11
tags:
  - draft
---

# Missing Source

## Compiled Truth
- Thesis: test

## Timeline (append-only)
- 2026-04-11 — Has source (source: manual)
- 2026-04-12 — No source here
"""


class ValidateEntityTests(unittest.TestCase):
    def _make_entity(self, td, bucket, name, content):
        d = Path(td) / bucket
        d.mkdir(parents=True, exist_ok=True)
        p = d / f"{name}.md"
        p.write_text(content, encoding="utf-8")
        return parse_entity(p, bucket)

    def test_valid_entity_no_errors(self):
        with tempfile.TemporaryDirectory() as td:
            entity = self._make_entity(td, "companies", "TestCo", VALID_COMPANY)
            result = validate_entity(entity)
            self.assertEqual(result["errors"], [])

    def test_bad_frontmatter(self):
        with tempfile.TemporaryDirectory() as td:
            entity = self._make_entity(td, "companies", "Bad", BAD_FRONTMATTER)
            result = validate_entity(entity)
            errors = result["errors"]
            self.assertTrue(any("type" in e for e in errors))
            self.assertTrue(any("updated_at" in e or "date" in e for e in errors))
            self.assertTrue(any("tags" in e for e in errors))

    def test_missing_sections(self):
        with tempfile.TemporaryDirectory() as td:
            entity = self._make_entity(td, "people", "NoSec", MISSING_SECTIONS)
            result = validate_entity(entity)
            errors = result["errors"]
            self.assertTrue(any("Compiled Truth" in e for e in errors))
            self.assertTrue(any("Timeline" in e for e in errors))

    def test_missing_source_in_timeline(self):
        with tempfile.TemporaryDirectory() as td:
            entity = self._make_entity(td, "ideas", "Bad", MISSING_SOURCE_IN_TIMELINE)
            result = validate_entity(entity)
            errors = result["errors"]
            self.assertTrue(any("source" in e for e in errors))
            # Only one entry missing source
            source_errors = [e for e in errors if "source" in e.lower()]
            self.assertEqual(len(source_errors), 1)


class ValidateAllTests(unittest.TestCase):
    def test_validate_all_clean(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "companies").mkdir()
            (root / "companies" / "TestCo.md").write_text(VALID_COMPANY)
            result = validate_all(root)
            self.assertEqual(result["total_errors"], 0)
            self.assertEqual(result["files_checked"], 1)

    def test_validate_all_with_errors(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "people").mkdir()
            (root / "people" / "Bad.md").write_text(MISSING_SECTIONS)
            result = validate_all(root)
            self.assertGreater(result["total_errors"], 0)

    def test_validate_empty_repo(self):
        with tempfile.TemporaryDirectory() as td:
            result = validate_all(Path(td))
            self.assertEqual(result["files_checked"], 0)
            self.assertEqual(result["total_errors"], 0)


if __name__ == "__main__":
    unittest.main()
