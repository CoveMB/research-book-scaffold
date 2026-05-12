#!/usr/bin/env sh

set -u

PASS_COUNT=0
WARN_COUNT=0
FAIL_COUNT=0

pass() {
  PASS_COUNT=$((PASS_COUNT + 1))
  printf 'PASS %s\n' "$1"
}

warn() {
  WARN_COUNT=$((WARN_COUNT + 1))
  printf 'WARN %s\n' "$1"
}

fail() {
  FAIL_COUNT=$((FAIL_COUNT + 1))
  printf 'FAIL %s\n' "$1"
}

check_command_required() {
  if command -v "$1" >/dev/null 2>&1; then
    pass "$1 found"
  else
    fail "$1 missing"
  fi
}

check_command_optional() {
  if command -v "$1" >/dev/null 2>&1; then
    pass "$1 found"
  else
    warn "$1 missing"
  fi
}

check_file_required() {
  if [ -f "$1" ]; then
    pass "$1 exists"
  else
    fail "$1 missing"
  fi
}

check_dir_required() {
  if [ -d "$1" ]; then
    pass "$1 exists"
  else
    fail "$1 missing"
  fi
}

check_command_required git
check_command_required python3
check_command_required curl
check_command_required unzip

check_command_optional node
check_command_optional npm
check_command_optional codex
check_command_optional quarto
check_command_optional pandoc

check_file_required bibliography/references.bib
check_file_required manuscript/_quarto.yml
check_dir_required .agents/skills
check_dir_required templates
check_dir_required notes
check_dir_required research

printf '\nSummary: %s pass, %s warn, %s fail\n' "$PASS_COUNT" "$WARN_COUNT" "$FAIL_COUNT"

if [ "$FAIL_COUNT" -gt 0 ]; then
  exit 1
fi

exit 0
