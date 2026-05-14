#!/usr/bin/env sh

SCRIPT_ENTRY_DIR=${0%/*}
if [ "$SCRIPT_ENTRY_DIR" = "$0" ]; then
  SCRIPT_ENTRY_DIR=.
fi
SCRIPT_HELPER_DIR=$(CDPATH= cd -- "$SCRIPT_ENTRY_DIR/../lib" && pwd)
. "$SCRIPT_HELPER_DIR/script_env.sh"
require_python3 "render the manuscript"

python3 "$PROJECT_ROOT/scripts/research-writing/render_manuscript.py" "$@"
