#!/usr/bin/env sh

SCRIPT_ENTRY_DIR=${0%/*}
if [ "$SCRIPT_ENTRY_DIR" = "$0" ]; then
  SCRIPT_ENTRY_DIR=.
fi
SCRIPT_HELPER_DIR=$(CDPATH= cd -- "$SCRIPT_ENTRY_DIR/../../lib" && pwd)
. "$SCRIPT_HELPER_DIR/script_env.sh"

cd "$PROJECT_ROOT" || exit 1
require_python3 "update skill vendors"

python3 "$PROJECT_ROOT/scripts/operations/vendors/update_skills_vendors.py" "$@"
