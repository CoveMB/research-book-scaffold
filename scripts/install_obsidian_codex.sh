#!/usr/bin/env sh

SCRIPT_ENTRY_DIR=${0%/*}
if [ "$SCRIPT_ENTRY_DIR" = "$0" ]; then
  SCRIPT_ENTRY_DIR=.
fi
SCRIPT_HELPER_DIR="$SCRIPT_ENTRY_DIR"
. "$SCRIPT_ENTRY_DIR/script_env.sh"

cd "$PROJECT_ROOT" || exit 1
require_python3 "install the Obsidian plugin"

python3 "$PROJECT_ROOT/scripts/obsidian_agent.py" "$@"
