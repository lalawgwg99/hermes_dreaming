"""brain CLI — hermes_dreaming knowledge operating system."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__


def _find_root(start: Path = None) -> Path:
    """Find brain root by looking for meta/ directory."""
    p = start or Path.cwd()
    for candidate in [p] + list(p.parents):
        if (candidate / "meta").is_dir() and (candidate / "templates").is_dir():
            return candidate
    return p


def cmd_validate(args) -> int:
    from .validate import validate_all
    root = Path(args.root)
    result = validate_all(root)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if result["total_errors"] == 0 and result["total_warnings"] == 0:
            print(f"OK — {result['files_checked']} files, 0 errors")
        else:
            for r in result["results"]:
                if r["errors"] or r["warnings"]:
                    print(f"\n{r['file']}:")
                    for e in r["errors"]:
                        print(f"  [ERROR] {e}")
                    for w in r["warnings"]:
                        print(f"  [WARN]  {w}")
            for w in result.get("global_warnings", []):
                print(f"\n[WARN] {w}")
            print(f"\n{result['files_checked']} files, {result['total_errors']} errors, {result['total_warnings']} warnings")

        # Always show stats
        by_type = result.get("by_type", {})
        if by_type:
            parts = [f"{count} {typ}" for typ, count in sorted(by_type.items())]
            print(f"  ({', '.join(parts)})")

    return 1 if result["total_errors"] > 0 else 0


def cmd_status(args) -> int:
    from .status import brain_status
    root = Path(args.root)
    result = brain_status(root)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Brain: {root.name}")
        print(f"Files: {result['total_files']}")
        by_bucket = result["by_bucket"]
        for bucket, count in by_bucket.items():
            if count > 0:
                print(f"  {bucket}: {count}")
        print(f"Entities: {result['entities']}")
        print(f"Timeline entries: {result['timeline_entries']}")

        if result["tags"]:
            top_tags = list(result["tags"].items())[:10]
            tag_str = ", ".join(f"{t}({c})" for t, c in top_tags)
            print(f"Top tags: {tag_str}")

        if result["recent"]:
            print(f"\nRecent:")
            for r in result["recent"][:5]:
                print(f"  [{r['type']}] {r['name']} ({r['updated_at']})")

    return 0


def cmd_add(args) -> int:
    from .templates import create_entity
    root = Path(args.root)
    tags = [t.strip() for t in args.tags.split(",")] if args.tags else None

    try:
        path = create_entity(
            root=root,
            entity_type=args.type,
            name=args.name,
            tags=tags,
            force=args.force,
        )
        print(f"Created: {path.relative_to(root)}")
        return 0
    except FileExistsError as e:
        print(f"Already exists: {e}")
        print("Use --force to overwrite")
        return 1
    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {e}")
        return 1


def cmd_search(args) -> int:
    from .search import search_entities
    root = Path(args.root)
    results = search_entities(root, args.query, bucket=args.bucket)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        if not results:
            print(f"No results for '{args.query}'")
            return 0
        for r in results[:20]:
            print(f"  [{r['bucket']}] {r['name']} (score: {r['score']})")
            print(f"    {r['file']}")
            for line in r["matches"][:2]:
                print(f"    > {line[:100]}")
    return 0


def cmd_inbox(args) -> int:
    from .inbox import capture_inbox
    root = Path(args.root)
    text = " ".join(args.text)
    if not text.strip():
        print("Provide text to capture")
        return 1
    path = capture_inbox(root, text, source=args.source or "manual")
    print(f"Captured: {path.relative_to(root)}")
    return 0


def cmd_dream(args) -> int:
    from .dream import run_dream_cycle
    root = Path(args.root)
    result = run_dream_cycle(root)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Dream Cycle — {result['date']}")
        print(f"  Commits: {result['commits']}")
        print(f"  Inbox items: {result['inbox_items']}")
        print(f"  Recent entities: {result['recent_entities']}")
        print(f"  Log: {result['dream_file']}")
    return 0


def cmd_timeline(args) -> int:
    from .parser import parse_entity, BUCKET_TO_TYPE
    root = Path(args.root)

    # Find entity by name across buckets
    found = None
    for bucket in ("people", "companies", "ideas"):
        bucket_dir = root / bucket
        if not bucket_dir.is_dir():
            continue
        for path in bucket_dir.glob("*.md"):
            if path.name == "README.md":
                continue
            if path.stem.lower().replace("_", " ") == args.entity.lower().replace("_", " "):
                found = parse_entity(path, bucket)
                break
        if found:
            break

    if not found:
        print(f"Entity not found: {args.entity}")
        return 1

    if args.json:
        entries = [{"date": e.date, "event": e.event, "source": e.source, "raw": e.raw} for e in found.timeline]
        payload = {"entity": found.name, "type": found.entity_type, "entries": entries}
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"{found.h1_title or found.name} [{found.entity_type}]")
        if not found.timeline:
            print("  (no timeline entries)")
        else:
            for entry in found.timeline:
                print(f"  {entry.raw}")
    return 0


def build_parser():
    p = argparse.ArgumentParser(prog="brain", description="hermes_dreaming knowledge operating system")
    p.add_argument("--version", action="version", version=f"brain {__version__}")
    p.add_argument("--root", default=None, help="brain repo root (auto-detected if omitted)")

    sub = p.add_subparsers(dest="cmd", required=True)

    # validate
    p_val = sub.add_parser("validate", help="validate all entities")
    p_val.add_argument("--json", action="store_true")
    p_val.set_defaults(func=cmd_validate)

    # status
    p_status = sub.add_parser("status", help="brain overview and stats")
    p_status.add_argument("--json", action="store_true")
    p_status.set_defaults(func=cmd_status)

    # add
    p_add = sub.add_parser("add", help="create entity from template")
    p_add.add_argument("type", choices=["person", "company", "idea", "meeting", "media", "original", "learning", "health", "finance"])
    p_add.add_argument("name", help="entity name")
    p_add.add_argument("--tags", help="comma-separated tags")
    p_add.add_argument("--force", action="store_true", help="overwrite existing")
    p_add.set_defaults(func=cmd_add)

    # search
    p_search = sub.add_parser("search", help="search across entities")
    p_search.add_argument("query", help="search query")
    p_search.add_argument("--bucket", help="limit to specific bucket")
    p_search.add_argument("--json", action="store_true")
    p_search.set_defaults(func=cmd_search)

    # inbox
    p_inbox = sub.add_parser("inbox", help="quick capture to inbox")
    p_inbox.add_argument("text", nargs="+", help="text to capture")
    p_inbox.add_argument("--source", help="source label (default: manual)")
    p_inbox.set_defaults(func=cmd_inbox)

    # dream
    p_dream = sub.add_parser("dream", help="run dream cycle")
    p_dream.add_argument("--json", action="store_true")
    p_dream.set_defaults(func=cmd_dream)

    # timeline
    p_tl = sub.add_parser("timeline", help="show entity timeline")
    p_tl.add_argument("entity", help="entity name (filename stem)")
    p_tl.add_argument("--json", action="store_true")
    p_tl.set_defaults(func=cmd_timeline)

    return p


def main():
    parser = build_parser()
    args = parser.parse_args()

    # Auto-detect root
    if args.root is None:
        args.root = str(_find_root())

    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
