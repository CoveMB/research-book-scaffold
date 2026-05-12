#!/usr/bin/env sh

set -u

SCRIPT_DIR=${0%/*}
if [ "$SCRIPT_DIR" = "$0" ]; then
  SCRIPT_DIR=.
fi
SCRIPT_DIR=$(CDPATH= cd -- "$SCRIPT_DIR" && pwd)
cd "$SCRIPT_DIR" || exit 1

if ! command -v python3 >/dev/null 2>&1; then
  printf '%s\n' "python3 is required to run setup."
  printf '%s\n' "Install Python 3 with your system package manager, then rerun:"
  printf '%s\n' "  sh setup.sh"
  exit 1
fi

python3 scripts/setup_environment.py "$@"
