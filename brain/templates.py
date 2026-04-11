"""Template engine — create entities from templates."""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from typing import Dict, Optional

from .parser import BUCKET_TO_TYPE, TYPE_TO_BUCKET


TEMPLATE_DIR_NAME = "templates"

# Map entity type to template filename
TYPE_TO_TEMPLATE = {
    "person": "person.md",
    "company": "company.md",
    "idea": "idea.md",
    "meeting": "meeting.md",
    "media": "media.md",
    "original": "original.md",
    "learning": "learning.md",
    "health": "health.md",
    "finance": "finance.md",
}

# Map entity type to output bucket directory
TYPE_TO_DIR = {
    "person": "people",
    "company": "companies",
    "idea": "ideas",
    "meeting": "meetings",
    "media": "media",
    "original": "originals",
    "learning": "ideas",
    "health": "ideas",
    "finance": "ideas",
}


def _slugify(name: str) -> str:
    """Convert a name to a filename-safe slug."""
    slug = name.strip().replace(" ", "_")
    slug = re.sub(r"[^\w\-]", "", slug)
    return slug


def render_template(
    root: Path,
    entity_type: str,
    name: str,
    tags: Optional[list] = None,
    extra: Optional[Dict[str, str]] = None,
) -> str:
    """Render a template with the given values."""
    template_file = TYPE_TO_TEMPLATE.get(entity_type)
    if not template_file:
        raise ValueError(f"Unknown entity type: {entity_type}")

    template_path = root / TEMPLATE_DIR_NAME / template_file
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")

    text = template_path.read_text(encoding="utf-8")
    today = date.today().isoformat()

    # Replace common placeholders
    replacements = {
        "{{date}}": today,
        "{{name}}": name,
        "{{company}}": name,
        "{{idea}}": name,
        "{{meeting_title}}": name,
        "{{title}}": name,
        "{{topic}}": name,
        "{{metric_or_topic}}": name,
        "{{item}}": name,
        "{{tag1}}": (tags[0] if tags else "untagged"),
        "{{event}}": "Created",
        "{{source}}": "manual | brain add",
        "{{confidence}}": "confirmed",
    }

    if extra:
        for k, v in extra.items():
            replacements[f"{{{{{k}}}}}"] = v

    for placeholder, value in replacements.items():
        text = text.replace(placeholder, value)

    # Replace remaining tags if multiple
    if tags and len(tags) > 1:
        # Find the tags block and replace with full list
        tag_lines = "\n".join(f"  - {t}" for t in tags)
        text = re.sub(
            r"tags:\n\s+-\s+.+",
            f"tags:\n{tag_lines}",
            text,
            count=1,
        )

    return text


def create_entity(
    root: Path,
    entity_type: str,
    name: str,
    tags: Optional[list] = None,
    extra: Optional[Dict[str, str]] = None,
    force: bool = False,
) -> Path:
    """Create a new entity file from template. Returns the created path."""
    target_dir = TYPE_TO_DIR.get(entity_type)
    if not target_dir:
        raise ValueError(f"Unknown entity type: {entity_type}")

    slug = _slugify(name)
    if entity_type == "meeting":
        from datetime import date as d
        slug = f"{d.today().isoformat()}_{slug}"

    out_dir = root / target_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{slug}.md"

    if out_path.exists() and not force:
        raise FileExistsError(f"Entity already exists: {out_path}")

    content = render_template(root, entity_type, name, tags=tags, extra=extra)
    out_path.write_text(content, encoding="utf-8")
    return out_path
