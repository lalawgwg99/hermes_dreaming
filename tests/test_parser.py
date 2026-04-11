import tempfile
import unittest
from pathlib import Path

from brain.parser import parse_frontmatter, parse_entity, load_entities, BUCKET_TO_TYPE


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

MINIMAL_PERSON = """\
---
type: person
updated_at: 2026-04-10
tags:
  - friend
---

# Alice

## Compiled Truth
- Role: tester

## Timeline (append-only)
- 2026-04-10 — Met at conference (source: meeting | conf | 2026-04-10)
- 2026-04-11 — Follow-up call (source: chat | Telegram | 2026-04-11)
"""

NO_FRONTMATTER = """\
# BadEntity

## Compiled Truth
- something

## Timeline (append-only)
- 2026-04-11 — Event (source: manual)
"""

MISSING_SOURCE = """\
---
type: idea
updated_at: 2026-04-11
tags:
  - draft
---

# Bad Idea

## Compiled Truth
- Thesis: testing

## Timeline (append-only)
- 2026-04-11 — First entry (source: manual)
- 2026-04-12 — Missing source entry
"""


class FrontmatterTests(unittest.TestCase):
    def test_parse_valid(self):
        fm, body = parse_frontmatter(VALID_COMPANY)
        self.assertEqual(fm["type"], "company")
        self.assertIn("TestCo", body)

    def test_parse_no_frontmatter(self):
        fm, body = parse_frontmatter(NO_FRONTMATTER)
        self.assertEqual(fm, {})
        self.assertIn("BadEntity", body)


class EntityParseTests(unittest.TestCase):
    def _write_entity(self, td, bucket, name, content):
        d = Path(td) / bucket
        d.mkdir(parents=True, exist_ok=True)
        p = d / f"{name}.md"
        p.write_text(content, encoding="utf-8")
        return p

    def test_parse_company(self):
        with tempfile.TemporaryDirectory() as td:
            p = self._write_entity(td, "companies", "TestCo", VALID_COMPANY)
            entity = parse_entity(p, "companies")
            self.assertEqual(entity.entity_type, "company")
            self.assertEqual(entity.h1_title, "TestCo")
            self.assertTrue(entity.has_frontmatter)
            self.assertTrue(entity.has_compiled_truth)
            self.assertTrue(entity.has_timeline)
            self.assertEqual(len(entity.timeline), 1)
            self.assertTrue(entity.timeline[0].has_source)

    def test_parse_person_multiple_timeline(self):
        with tempfile.TemporaryDirectory() as td:
            p = self._write_entity(td, "people", "Alice", MINIMAL_PERSON)
            entity = parse_entity(p, "people")
            self.assertEqual(entity.entity_type, "person")
            self.assertEqual(len(entity.timeline), 2)
            self.assertEqual(entity.timeline[0].date, "2026-04-10")
            self.assertEqual(entity.timeline[1].date, "2026-04-11")

    def test_parse_missing_source(self):
        with tempfile.TemporaryDirectory() as td:
            p = self._write_entity(td, "ideas", "bad", MISSING_SOURCE)
            entity = parse_entity(p, "ideas")
            self.assertEqual(len(entity.timeline), 2)
            self.assertTrue(entity.timeline[0].has_source)
            self.assertFalse(entity.timeline[1].has_source)

    def test_parse_no_frontmatter(self):
        with tempfile.TemporaryDirectory() as td:
            p = self._write_entity(td, "ideas", "bad", NO_FRONTMATTER)
            entity = parse_entity(p, "ideas")
            self.assertFalse(entity.has_frontmatter)


class LoadEntitiesTests(unittest.TestCase):
    def test_load_from_multiple_buckets(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "companies").mkdir()
            (root / "companies" / "TestCo.md").write_text(VALID_COMPANY)
            (root / "people").mkdir()
            (root / "people" / "Alice.md").write_text(MINIMAL_PERSON)
            (root / "ideas").mkdir()
            (root / "ideas" / "README.md").write_text("# ideas\n")

            entities = load_entities(root)
            self.assertEqual(len(entities), 2)
            types = {e.entity_type for e in entities}
            self.assertEqual(types, {"person", "company"})

    def test_load_empty(self):
        with tempfile.TemporaryDirectory() as td:
            entities = load_entities(Path(td))
            self.assertEqual(len(entities), 0)


if __name__ == "__main__":
    unittest.main()
