"""Dream Cycle — nightly brain maintenance."""
from __future__ import annotations

import subprocess
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Dict, List


def _get_recent_commits(root: Path, days: int = 1) -> List[str]:
    """Get commit messages from last N days."""
    since = (date.today() - timedelta(days=days)).isoformat()
    try:
        result = subprocess.run(
            ["git", "log", f"--since={since}", "--oneline", "--no-decorate"],
            cwd=root, capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            return [line.strip() for line in result.stdout.strip().split("\n") if line.strip()]
    except Exception:
        pass
    return []


def _get_inbox_items(root: Path) -> List[Dict[str, str]]:
    """List unprocessed inbox items."""
    inbox_dir = root / "inbox"
    items = []
    if inbox_dir.is_dir():
        for f in sorted(inbox_dir.glob("*.md")):
            if f.name == "README.md":
                continue
            # Read first line as title
            try:
                first_line = f.read_text(encoding="utf-8").split("\n")[0]
                title = first_line.lstrip("# ").strip() or f.stem
            except Exception:
                title = f.stem
            items.append({"file": f.name, "title": title})
    return items


def _get_recent_entities(root: Path) -> List[Dict[str, str]]:
    """List entities updated recently (by updated_at in frontmatter)."""
    from .parser import load_entities
    today = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()

    entities = load_entities(root)
    recent = []
    for e in entities:
        ua = str(e.frontmatter.get("updated_at", ""))
        if ua >= yesterday:
            recent.append({
                "name": e.name,
                "type": e.entity_type,
                "updated_at": ua,
                "file": str(e.path.relative_to(root)),
            })
    return recent


def run_dream_cycle(root: Path) -> Dict[str, Any]:
    """Run the dream cycle and generate a summary."""
    today = date.today().isoformat()

    commits = _get_recent_commits(root)
    inbox_items = _get_inbox_items(root)
    recent_entities = _get_recent_entities(root)

    # Build dream log
    lines = [
        f"# Dream Cycle — {today}",
        "",
        "## Recent Commits",
    ]
    if commits:
        for c in commits:
            lines.append(f"- {c}")
    else:
        lines.append("- (none)")

    lines.extend(["", "## Inbox Items"])
    if inbox_items:
        for item in inbox_items:
            lines.append(f"- `{item['file']}` — {item['title']}")
    else:
        lines.append("- (inbox empty)")

    lines.extend(["", "## Recently Updated Entities"])
    if recent_entities:
        for e in recent_entities:
            lines.append(f"- [{e['type']}] {e['name']} ({e['updated_at']})")
    else:
        lines.append("- (none)")

    lines.extend([
        "",
        "## Suggestions",
    ])
    if inbox_items:
        lines.append(f"- {len(inbox_items)} inbox items to sort")
    else:
        lines.append("- Inbox clear")

    content = "\n".join(lines) + "\n"

    # Write dream log
    dreams_dir = root / "meta" / "dreams"
    dreams_dir.mkdir(parents=True, exist_ok=True)
    dream_path = dreams_dir / f"{today}.md"
    dream_path.write_text(content, encoding="utf-8")

    return {
        "date": today,
        "dream_file": str(dream_path.relative_to(root)),
        "commits": len(commits),
        "inbox_items": len(inbox_items),
        "recent_entities": len(recent_entities),
    }
