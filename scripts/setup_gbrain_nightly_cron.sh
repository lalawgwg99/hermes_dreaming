#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$REPO_ROOT/meta/logs"
LOG_FILE="$LOG_DIR/gbrain-nightly.log"
RUNNER="$REPO_ROOT/scripts/run_gbrain_nightly.sh"
CRON_SCHEDULE="${CRON_SCHEDULE:-30 2 * * *}"
CRON_MARKER="# hermes_dreaming_gbrain_nightly"

mkdir -p "$LOG_DIR"
chmod +x "$RUNNER"

CRON_CMD="/bin/bash -lc '\"$RUNNER\"'"
CRON_LINE="$CRON_SCHEDULE $CRON_CMD $CRON_MARKER"

CURRENT_CRON="$(crontab -l 2>/dev/null || true)"
FILTERED_CRON="$(printf '%s\n' "$CURRENT_CRON" | awk -v marker="$CRON_MARKER" 'index($0, marker) == 0')"

if [[ -n "$FILTERED_CRON" ]]; then
  NEW_CRON="$FILTERED_CRON"$'\n'"$CRON_LINE"
else
  NEW_CRON="$CRON_LINE"
fi

printf '%s\n' "$NEW_CRON" | crontab -

echo "[OK] Installed nightly gbrain cron job."
echo "[INFO] Schedule: $CRON_SCHEDULE"
echo "[INFO] Log file: $LOG_FILE"
if command -v gbrain >/dev/null 2>&1; then
  echo "[INFO] gbrain command found."
else
  echo "[WARN] gbrain command not found yet. Nightly job will skip until installed."
fi
echo "[INFO] Current matching entry:"
crontab -l | rg "hermes_dreaming_gbrain_nightly" || true
