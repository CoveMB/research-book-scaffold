#!/usr/bin/env sh

SCRIPT_ENTRY_DIR=${0%/*}
if [ "$SCRIPT_ENTRY_DIR" = "$0" ]; then
  SCRIPT_ENTRY_DIR=.
fi
SCRIPT_HELPER_DIR=$(CDPATH= cd -- "$SCRIPT_ENTRY_DIR/../../lib" && pwd)
. "$SCRIPT_HELPER_DIR/script_env.sh"

cd "$PROJECT_ROOT" || exit 1
require_python3 "install Obsidian research plugins"

python3 "$PROJECT_ROOT/scripts/operations/obsidian/obsidian_research_plugins.py" install "$@"
