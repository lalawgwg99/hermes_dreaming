"""Quick inbox capture."""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path


def _slug_from_text(text: str, max_len: int = 40) -> str:
    """Generate a filename slug from text."""
    # Take first meaningful words
    words = re.sub(r"[^\w\s]", "", text).split()[:6]
    slug = "_".join(w.lower() for w in words)
    return slug[:max_len] if slug else "note"


def capture_inbox(root: Path, text: str, source: str = "manual") -> Path:
    """Write text to inbox/ as a dated markdown file."""
    today = date.today().isoformat()
    slug = _slug_from_text(text)
    inbox_dir = root / "inbox"
    inbox_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{today}_{slug}.md"
    path = inbox_dir / filename

    # Avoid overwriting
    counter = 1
    while path.exists():
        filename = f"{today}_{slug}_{counter}.md"
        path = inbox_dir / filename
        counter += 1

    content = f"# {text[:80]}\n\n{text}\n\n---\n- {today} — Captured (source: {source} | confidence: tentative)\n"
    path.write_text(content, encoding="utf-8")
    return path
