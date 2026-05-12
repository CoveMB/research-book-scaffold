#!/usr/bin/env sh

SCRIPT_ENTRY_DIR=${0%/*}
if [ "$SCRIPT_ENTRY_DIR" = "$0" ]; then
  SCRIPT_ENTRY_DIR=.
fi
SCRIPT_HELPER_DIR="$SCRIPT_ENTRY_DIR/scripts"
. "$SCRIPT_ENTRY_DIR/scripts/script_env.sh"

cd "$PROJECT_ROOT" || exit 1
require_python3 "run setup"

python3 scripts/setup_environment.py "$@"
