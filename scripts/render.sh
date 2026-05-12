#!/usr/bin/env sh

set -u

if ! command -v quarto >/dev/null 2>&1; then
  printf '%s\n' "Quarto is not installed."
  printf '%s\n' "Install Quarto manually, then run:"
  printf '%s\n' "  bash scripts/render.sh"
  exit 1
fi

if [ ! -f manuscript/_quarto.yml ]; then
  printf '%s\n' "Missing manuscript/_quarto.yml"
  exit 1
fi

if grep -Eq '^[[:space:]]+pdf:' manuscript/_quarto.yml; then
  if ! command -v lualatex >/dev/null 2>&1; then
    printf '%s\n' "No TeX engine found for PDF rendering."
    printf '%s\n' "Install TinyTeX with 'quarto install tinytex' or install TeX Live, then rerun:"
    printf '%s\n' "  bash scripts/render.sh"
    exit 1
  fi
fi

quarto render manuscript
