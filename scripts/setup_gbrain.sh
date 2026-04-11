#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GBRAIN_GIT_URL="${GBRAIN_GIT_URL:-https://github.com/lalawgwg99/gbrain.git}"

echo "[INFO] Repo root: $REPO_ROOT"
echo "[INFO] gbrain source: $GBRAIN_GIT_URL"

if ! command -v bun >/dev/null 2>&1; then
  echo "[ERROR] bun is required but not installed."
  echo "Install bun first: https://bun.sh/docs/installation"
  exit 1
fi

if ! command -v gbrain >/dev/null 2>&1; then
  echo "[INFO] Installing gbrain from GitHub..."
  bun add -g "$GBRAIN_GIT_URL"
fi

if ! command -v gbrain >/dev/null 2>&1; then
  echo "[ERROR] gbrain command is still unavailable after install."
  echo "Try reopening your shell, then run: gbrain --help"
  exit 1
fi

echo "[INFO] gbrain detected: $(gbrain --version 2>/dev/null || echo unknown-version)"
echo
echo "[NEXT] 1) Initialize database connection:"
echo "       gbrain init --supabase"
echo
echo "[NEXT] 2) Import this brain repo:"
echo "       gbrain import \"$REPO_ROOT\" --no-embed"
echo
echo "[NEXT] 3) Backfill embeddings (optional):"
echo "       gbrain embed --stale"
echo
echo "[NEXT] 4) Query sanity check:"
echo "       gbrain query \"what changed recently in companies\""
echo
echo "[NEXT] 5) Ongoing sync command:"
echo "       gbrain sync --repo \"$REPO_ROOT\" && gbrain embed --stale"
