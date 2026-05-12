#!/usr/bin/env sh

set -u

SCRIPT_DIR=${0%/*}
if [ "$SCRIPT_DIR" = "$0" ]; then
  SCRIPT_DIR=.
fi
SCRIPT_DIR=$(CDPATH= cd -- "$SCRIPT_DIR" && pwd)
PROJECT_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)

python3 "$PROJECT_ROOT/scripts/render_manuscript.py" "$@"
