#!/usr/bin/env bash
set -euo pipefail

if ! command -v pg_dump >/dev/null 2>&1; then
  echo "pg_dump is required to run database backups" >&2
  exit 1
fi

python - <<'PY'
from app.utils.backup import pg_dump

pg_dump()
PY
