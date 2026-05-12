#!/usr/bin/env sh

set -u

SCRIPT_DIR=${0%/*}
if [ "$SCRIPT_DIR" = "$0" ]; then
  SCRIPT_DIR=.
fi
SCRIPT_DIR=$(CDPATH= cd -- "$SCRIPT_DIR" && pwd)
PROJECT_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
cd "$PROJECT_ROOT" || exit 1

if ! command -v python3 >/dev/null 2>&1; then
  printf '%s\n' "python3 is required to update skill vendors."
  exit 1
fi

python3 "$PROJECT_ROOT/scripts/update_skills_vendors.py" "$@"
