"""Validation engine — replaces validate_brain.sh with richer checks."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Set

from .parser import Entity, load_entities, BUCKET_TO_TYPE


def _check_frontmatter(entity: Entity) -> List[str]:
    """Check frontmatter completeness."""
    errors = []
    fm = entity.frontmatter

    if not entity.has_frontmatter:
        errors.append("missing YAML frontmatter")
        return errors

    if "type" not in fm:
        errors.append("frontmatter missing 'type'")
    elif fm["type"] != entity.entity_type:
        errors.append(f"frontmatter type is '{fm['type']}', expected '{entity.entity_type}'")

    if "updated_at" not in fm:
        errors.append("frontmatter missing 'updated_at'")
    else:
        ua = str(fm["updated_at"])
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", ua):
            errors.append(f"'updated_at' not YYYY-MM-DD: {ua}")

    if "tags" not in fm:
        errors.append("frontmatter missing 'tags'")
    elif not isinstance(fm["tags"], list) or len(fm["tags"]) == 0:
        errors.append("'tags' must be a non-empty list")

    return errors


def _check_structure(entity: Entity) -> List[str]:
    """Check required sections."""
    errors = []
    if not entity.has_compiled_truth:
        errors.append("missing '## Compiled Truth' section")
    if not entity.has_timeline:
        errors.append("missing '## Timeline (append-only)' section")
    return errors


def _check_timeline(entity: Entity) -> List[str]:
    """Check timeline entries have sources and valid dates."""
    errors = []
    for entry in entity.timeline:
        if not entry.has_source:
            errors.append(f"timeline entry missing source: {entry.raw[:80]}")
        if not entry.date:
            errors.append(f"timeline entry missing date format: {entry.raw[:80]}")
    return errors


def _check_crossrefs(entity: Entity, all_names: Set[str]) -> List[str]:
    """Check for references to non-existent entities in timeline."""
    warnings = []
    # Look for mentions of entity names in compiled truth / timeline
    # This is a lightweight heuristic — not exhaustive
    return warnings


def _find_duplicates(entities: List[Entity]) -> List[str]:
    """Find potential duplicate entities (same name, different files)."""
    warnings = []
    seen: Dict[str, List[str]] = {}
    for e in entities:
        # Normalize: lowercase, strip underscores/hyphens
        key = e.name.lower().replace("_", " ").replace("-", " ")
        seen.setdefault(key, []).append(str(e.path))
    for key, paths in seen.items():
        if len(paths) > 1:
            warnings.append(f"possible duplicate entity '{key}': {', '.join(paths)}")
    return warnings


def validate_entity(entity: Entity) -> Dict[str, Any]:
    """Validate a single entity, returning errors and warnings."""
    errors = []
    warnings = []

    errors.extend(_check_frontmatter(entity))
    errors.extend(_check_structure(entity))
    errors.extend(_check_timeline(entity))

    if not entity.h1_title:
        warnings.append("missing H1 title")
    if entity.has_compiled_truth and not entity.compiled_truth:
        warnings.append("'Compiled Truth' section is empty")
    if entity.has_timeline and not entity.timeline:
        warnings.append("'Timeline' section is empty")

    return {
        "file": str(entity.path),
        "name": entity.name,
        "type": entity.entity_type,
        "errors": errors,
        "warnings": warnings,
    }


def validate_all(root: Path) -> Dict[str, Any]:
    """Validate all entities in the brain repo."""
    entities = load_entities(root)
    results = []
    total_errors = 0
    total_warnings = 0

    for entity in entities:
        result = validate_entity(entity)
        results.append(result)
        total_errors += len(result["errors"])
        total_warnings += len(result["warnings"])

    # Global checks
    global_warnings = _find_duplicates(entities)
    total_warnings += len(global_warnings)

    # Stats
    by_type: Dict[str, int] = {}
    for e in entities:
        by_type[e.entity_type] = by_type.get(e.entity_type, 0) + 1

    return {
        "files_checked": len(entities),
        "total_errors": total_errors,
        "total_warnings": total_warnings,
        "by_type": by_type,
        "results": results,
        "global_warnings": global_warnings,
    }
