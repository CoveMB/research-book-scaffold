#!/usr/bin/env sh

set -u

if ! command -v python3 >/dev/null 2>&1; then
  printf '%s\n' "python3 is required to install the Obsidian plugin."
  exit 1
fi

python3 scripts/setup_environment.py --with-obsidian-codex "$@"
