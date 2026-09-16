#!/usr/bin/env bash
set -euo pipefail
TASK_SKILL_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$TASK_SKILL_DIR/scripts/codex_task.py" "$@"
