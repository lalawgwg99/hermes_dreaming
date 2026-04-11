#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$REPO_ROOT/meta/logs"
LOG_FILE="$LOG_DIR/gbrain-nightly.log"
TIMESTAMP="$(date '+%Y-%m-%d %H:%M:%S %Z')"
export PATH="$HOME/.bun/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

mkdir -p "$LOG_DIR"

if ! command -v gbrain >/dev/null 2>&1; then
  echo "[$TIMESTAMP] [WARN] gbrain not installed. Skipping nightly sync." >> "$LOG_FILE"
  exit 0
fi

{
  echo "[$TIMESTAMP] [INFO] Starting nightly sync..."
  gbrain sync --repo "$REPO_ROOT"
  gbrain embed --stale
  echo "[$TIMESTAMP] [INFO] Nightly sync completed."
} >> "$LOG_FILE" 2>&1
