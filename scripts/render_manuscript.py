#!/usr/bin/env python3
"""Render the Quarto manuscript with targeted preflight checks."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from project_config import change_to_project_root
from script_utils import read_text


MANUSCRIPT_DIR = Path("manuscript")
QUARTO_CONFIG = MANUSCRIPT_DIR / "_quarto.yml"
DEFAULT_PDF_ENGINE = "lualatex"
SUPPORTED_FORMATS = {"html", "pdf", "docx"}


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--to", choices=sorted(SUPPORTED_FORMATS), help="Render one output format.")
    return parser.parse_args(argv)


def configured_pdf_engine(config_text: str) -> str:
    for line in config_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("pdf-engine:"):
            value = stripped.split(":", 1)[1].strip().strip("\"'")
            return value or DEFAULT_PDF_ENGINE
    return DEFAULT_PDF_ENGINE


def pdf_format_enabled(config_text: str) -> bool:
    for line in config_text.splitlines():
        stripped = line.strip()
        if stripped == "pdf:" or stripped.startswith("pdf: "):
            return True
    return False


def requires_pdf_engine(output_format: str | None, config_text: str) -> bool:
    if output_format == "pdf":
        return True
    if output_format in {"html", "docx"}:
        return False
    return pdf_format_enabled(config_text)


def quarto_command(output_format: str | None) -> list[str]:
    command = ["quarto", "render", str(MANUSCRIPT_DIR)]
    if output_format:
        command.extend(["--to", output_format])
    return command


def check_preconditions(output_format: str | None) -> int:
    if not shutil.which("quarto"):
        print("Quarto is not installed.")
        print("Install Quarto manually, then run:")
        print("  bash scripts/render.sh")
        return 1

    if not QUARTO_CONFIG.is_file():
        print(f"Missing {QUARTO_CONFIG}")
        return 1

    config_text = read_text(QUARTO_CONFIG)
    if requires_pdf_engine(output_format, config_text):
        engine = configured_pdf_engine(config_text)
        if not shutil.which(engine):
            print(f"No TeX engine found for PDF rendering: {engine}.")
            print(
                "Install TinyTeX with 'quarto install tinytex --update-path' "
                "or install the configured TeX engine."
            )
            print(
                "On macOS, if TinyTeX is already installed, ensure "
                "$HOME/Library/TinyTeX/bin/universal-darwin is on PATH."
            )
            print("Then rerun:")
            print("  bash scripts/render.sh")
            return 1
    return 0


def main(argv: list[str]) -> int:
    change_to_project_root()
    args = parse_args(argv)
    preflight_exit = check_preconditions(args.to)
    if preflight_exit:
        return preflight_exit
    return subprocess.run(quarto_command(args.to), check=False).returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
