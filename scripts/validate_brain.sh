#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="${1:-.}"
EXIT_CODE=0
CHECKED=0

validate_frontmatter() {
  local file="$1"
  local expected_type="$2"
  local first_line
  first_line="$(head -n 1 "$file" || true)"

  if [[ "$first_line" != "---" ]]; then
    echo "[ERROR] Missing YAML frontmatter start '---': $file"
    EXIT_CODE=1
    return
  fi

  local fm
  fm="$(
    awk '
      NR == 1 && $0 == "---" { in_fm=1; next }
      in_fm && $0 == "---" { exit }
      in_fm { print }
    ' "$file"
  )"

  if [[ -z "$fm" ]]; then
    echo "[ERROR] Empty frontmatter block: $file"
    EXIT_CODE=1
    return
  fi

  if ! printf '%s\n' "$fm" | rg -q '^type:\s+'; then
    echo "[ERROR] Missing frontmatter field 'type': $file"
    EXIT_CODE=1
  fi

  if ! printf '%s\n' "$fm" | rg -q '^updated_at:\s+[0-9]{4}-[0-9]{2}-[0-9]{2}$'; then
    echo "[ERROR] Missing or invalid 'updated_at' (YYYY-MM-DD): $file"
    EXIT_CODE=1
  fi

  if ! printf '%s\n' "$fm" | rg -q '^tags:\s*$'; then
    echo "[ERROR] Missing frontmatter field 'tags': $file"
    EXIT_CODE=1
  fi

  if ! printf '%s\n' "$fm" | rg -q '^\s*-\s+\S+'; then
    echo "[ERROR] 'tags' must include at least one list item: $file"
    EXIT_CODE=1
  fi

  if ! printf '%s\n' "$fm" | rg -q "^type:\\s+${expected_type}$"; then
    echo "[ERROR] Frontmatter 'type' must be '${expected_type}': $file"
    EXIT_CODE=1
  fi
}

check_file() {
  local file="$1"
  local expected_type="$2"
  CHECKED=$((CHECKED + 1))
  validate_frontmatter "$file" "$expected_type"

  if ! rg -q '^## Compiled Truth$' "$file"; then
    echo "[ERROR] Missing '## Compiled Truth': $file"
    EXIT_CODE=1
  fi

  if ! rg -q '^## Timeline \(append-only\)$' "$file"; then
    echo "[ERROR] Missing '## Timeline (append-only)': $file"
    EXIT_CODE=1
    return
  fi

  local source_issues
  source_issues="$(
    awk '
      /^## Timeline \(append-only\)$/ { in_timeline=1; next }
      /^## / && in_timeline { in_timeline=0 }
      in_timeline && /^- / && $0 !~ /\(source: / { print NR ":" $0 }
    ' "$file"
  )"

  if [[ -n "$source_issues" ]]; then
    echo "[ERROR] Timeline entries missing source in $file"
    echo "$source_issues"
    EXIT_CODE=1
  fi
}

for bucket in people companies ideas; do
  dir="$ROOT_DIR/$bucket"
  [[ -d "$dir" ]] || continue
  case "$bucket" in
    people) entity_type="person" ;;
    companies) entity_type="company" ;;
    ideas) entity_type="idea" ;;
    *) entity_type="unknown" ;;
  esac

  while IFS= read -r file; do
    check_file "$file" "$entity_type"
  done < <(find "$dir" -type f -name "*.md" ! -name "README.md" | sort)
done

if [[ "$CHECKED" -eq 0 ]]; then
  echo "[WARN] No entity files found under people/ companies/ ideas/."
else
  echo "[OK] Validated $CHECKED files."
fi

exit "$EXIT_CODE"
