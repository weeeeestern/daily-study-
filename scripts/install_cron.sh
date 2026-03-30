#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
CRON_TMP="$(mktemp)"

crontab -l 2>/dev/null > "$CRON_TMP" || true

if ! grep -Fq "generate_daily.py" "$CRON_TMP"; then
  printf 'CRON_TZ=Asia/Seoul\n0 9 * * * cd %q && %q scripts/generate_daily.py >> logs/gen.log 2>&1\n' "$REPO_DIR" "$PYTHON_BIN" >> "$CRON_TMP"
fi

if ! grep -Fq "push_if_done.py" "$CRON_TMP"; then
  printf '0 23 * * * cd %q && %q scripts/push_if_done.py >> logs/push.log 2>&1\n' "$REPO_DIR" "$PYTHON_BIN" >> "$CRON_TMP"
fi

crontab "$CRON_TMP"
rm -f "$CRON_TMP"
echo "Installed cron entries for daily-study"
