#!/usr/bin/env sh

set -u

SCRIPT_DIR=${SCRIPT_HELPER_DIR:-${0%/*}}
if [ "$SCRIPT_DIR" = "$0" ]; then
  SCRIPT_DIR=.
fi
SCRIPT_DIR=$(CDPATH= cd -- "$SCRIPT_DIR" && pwd)
PROJECT_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)

require_python3() {
  action=$1
  if ! command -v python3 >/dev/null 2>&1; then
    printf '%s\n' "python3 is required to ${action}."
    exit 1
  fi
}
