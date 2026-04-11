"""Brain status — stats and overview."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from .parser import load_entities


ALL_BUCKETS = ("people", "companies", "ideas", "meetings", "media", "originals", "inbox")


def count_files(root: Path) -> Dict[str, int]:
    """Count markdown files per bucket."""
    counts = {}
    for bucket in ALL_BUCKETS:
        bucket_dir = root / bucket
        if not bucket_dir.is_dir():
            counts[bucket] = 0
            continue
        files = [f for f in bucket_dir.glob("*.md") if f.name != "README.md"]
        counts[bucket] = len(files)
    return counts


def brain_status(root: Path) -> Dict[str, Any]:
    """Compute full brain status."""
    counts = count_files(root)
    total = sum(counts.values())

    entities = load_entities(root)
    timeline_entries = sum(len(e.timeline) for e in entities)

    # Recent activity: entities sorted by updated_at
    recent = []
    for e in entities:
        ua = e.frontmatter.get("updated_at", "")
        recent.append({
            "name": e.name,
            "type": e.entity_type,
            "updated_at": str(ua),
            "file": str(e.path.relative_to(root)),
        })
    recent.sort(key=lambda r: r["updated_at"], reverse=True)

    # Tags summary
    all_tags: Dict[str, int] = {}
    for e in entities:
        for tag in e.frontmatter.get("tags", []) or []:
            all_tags[tag] = all_tags.get(tag, 0) + 1

    return {
        "total_files": total,
        "by_bucket": counts,
        "entities": len(entities),
        "timeline_entries": timeline_entries,
        "tags": dict(sorted(all_tags.items(), key=lambda x: -x[1])),
        "recent": recent[:10],
    }
