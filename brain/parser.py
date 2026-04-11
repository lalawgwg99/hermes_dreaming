"""Parse brain entity files: frontmatter + compiled truth + timeline."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


@dataclass
class TimelineEntry:
    line_number: int
    raw: str
    date: str = ""
    event: str = ""
    source: str = ""
    has_source: bool = False


@dataclass
class Entity:
    path: Path
    entity_type: str  # person, company, idea, etc.
    bucket: str  # people, companies, ideas, etc.
    name: str  # filename stem or H1 title
    frontmatter: Dict[str, Any] = field(default_factory=dict)
    compiled_truth: List[str] = field(default_factory=list)
    timeline: List[TimelineEntry] = field(default_factory=list)
    has_frontmatter: bool = False
    has_compiled_truth: bool = False
    has_timeline: bool = False
    h1_title: str = ""


BUCKET_TO_TYPE = {
    "people": "person",
    "companies": "company",
    "ideas": "idea",
}

TYPE_TO_BUCKET = {v: k for k, v in BUCKET_TO_TYPE.items()}

TIMELINE_DATE_RE = re.compile(r"^- (\d{4}-\d{2}-\d{2})\s*[—–-]\s*(.+)$")
SOURCE_RE = re.compile(r"\(source:\s*(.+?)\)\s*$")


def parse_frontmatter(text: str) -> tuple[Dict[str, Any], str]:
    """Extract YAML frontmatter and remaining body."""
    if not text.startswith("---"):
        return {}, text

    end = text.find("\n---", 3)
    if end == -1:
        return {}, text

    fm_text = text[4:end]
    body = text[end + 4:].lstrip("\n")
    try:
        fm = yaml.safe_load(fm_text) or {}
    except yaml.YAMLError:
        fm = {}
    return fm, body


def parse_entity(path: Path, bucket: str) -> Entity:
    """Parse a single entity markdown file."""
    text = path.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)

    expected_type = BUCKET_TO_TYPE.get(bucket, bucket)
    entity = Entity(
        path=path,
        entity_type=expected_type,
        bucket=bucket,
        name=path.stem,
        frontmatter=fm,
        has_frontmatter=bool(fm),
    )

    lines = body.split("\n")
    section = None
    timeline_start = -1

    for i, line in enumerate(lines):
        # H1 title
        if line.startswith("# ") and not entity.h1_title:
            entity.h1_title = line[2:].strip()

        # Section headers
        if line.strip() == "## Compiled Truth":
            section = "compiled_truth"
            entity.has_compiled_truth = True
            continue
        if line.strip() == "## Timeline (append-only)":
            section = "timeline"
            entity.has_timeline = True
            timeline_start = i
            continue
        if line.startswith("## ") and section:
            section = None
            continue

        # Capture content
        if section == "compiled_truth" and line.strip():
            entity.compiled_truth.append(line.strip())
        elif section == "timeline" and line.startswith("- "):
            entry = TimelineEntry(
                line_number=i + 1,  # 1-indexed (relative to body)
                raw=line.strip(),
            )
            date_match = TIMELINE_DATE_RE.match(line.strip())
            if date_match:
                entry.date = date_match.group(1)
                entry.event = date_match.group(2)
            source_match = SOURCE_RE.search(line)
            if source_match:
                entry.source = source_match.group(1)
                entry.has_source = True
            entity.timeline.append(entry)

    return entity


def load_entities(root: Path) -> List[Entity]:
    """Load all entities from standard buckets."""
    entities = []
    for bucket in ("people", "companies", "ideas"):
        bucket_dir = root / bucket
        if not bucket_dir.is_dir():
            continue
        for path in sorted(bucket_dir.glob("*.md")):
            if path.name == "README.md":
                continue
            entities.append(parse_entity(path, bucket))
    return entities
