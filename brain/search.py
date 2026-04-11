"""Full-text search across brain entities."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from .parser import load_entities, Entity


ALL_BUCKETS = ("people", "companies", "ideas", "meetings", "media", "originals", "inbox")


def _score_match(text: str, query: str, is_name: bool = False) -> int:
    """Simple scoring: higher = better match."""
    lower_text = text.lower()
    lower_query = query.lower()

    if lower_query == lower_text:
        return 100 if is_name else 50
    if lower_query in lower_text:
        return 80 if is_name else 30
    # Word-level match
    words = lower_query.split()
    hits = sum(1 for w in words if w in lower_text)
    if hits == 0:
        return 0
    return int(hits / len(words) * (60 if is_name else 20))


def search_entities(root: Path, query: str, bucket: Optional[str] = None) -> List[Dict[str, Any]]:
    """Search across all entity files. Returns sorted results."""
    results = []

    buckets = [bucket] if bucket else list(ALL_BUCKETS)

    for b in buckets:
        bucket_dir = root / b
        if not bucket_dir.is_dir():
            continue
        for path in sorted(bucket_dir.glob("*.md")):
            if path.name == "README.md":
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except Exception:
                continue

            name = path.stem.replace("_", " ")
            name_score = _score_match(name, query, is_name=True)
            body_score = _score_match(text, query, is_name=False)
            score = max(name_score, body_score)

            if score == 0:
                continue

            # Extract matching lines for context
            matching_lines = []
            for line in text.split("\n"):
                if query.lower() in line.lower():
                    matching_lines.append(line.strip())
                    if len(matching_lines) >= 3:
                        break

            results.append({
                "file": str(path.relative_to(root)),
                "name": name,
                "bucket": b,
                "score": score,
                "matches": matching_lines,
            })

    results.sort(key=lambda r: -r["score"])
    return results
