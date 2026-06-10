#!/usr/bin/env python3
"""Render the Quarto manuscript with targeted preflight checks."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Callable

_SCRIPTS_ROOT = next(parent for parent in Path(__file__).resolve().parents if parent.name == "scripts")
_LIB_DIR = _SCRIPTS_ROOT / "lib"
if str(_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(_LIB_DIR))

from import_paths import configure_script_paths
from project_config import change_to_project_root
from script_utils import read_text

configure_script_paths(__file__)

MANUSCRIPT_DIR = Path("manuscript")
QUARTO_CONFIG = MANUSCRIPT_DIR / "_quarto.yml"
QUARTO_OUTPUT_DIR = MANUSCRIPT_DIR / "_book"
DEFAULT_PDF_ENGINE = "lualatex"
SUPPORTED_FORMATS = {"html", "pdf", "docx"}
EXPORT_DIRS = {
    "html": Path("exports/html"),
    "pdf": Path("exports/pdf"),
    "docx": Path("exports/docx"),
}


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


def replace_directory(source: Path, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination)
    (destination / ".gitkeep").write_text("\n", encoding="utf-8")


def copy_rendered_files(source: Path, destination: Path, suffix: str, required: bool) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    for stale_file in destination.glob(f"*{suffix}"):
        stale_file.unlink()
    rendered_files = sorted(source.glob(f"*{suffix}"))
    if required and not rendered_files:
        raise FileNotFoundError(f"no rendered {suffix} file found in {source}")
    for rendered_file in rendered_files:
        shutil.copy2(rendered_file, destination / rendered_file.name)


def mirror_render_outputs(output_format: str | None, project_root: Path = Path(".")) -> None:
    source = project_root / QUARTO_OUTPUT_DIR
    if not source.is_dir():
        raise FileNotFoundError(f"Quarto output directory not found: {source}")

    if output_format in {None, "html"}:
        replace_directory(source, project_root / EXPORT_DIRS["html"])
    if output_format in {None, "pdf"}:
        copy_rendered_files(source, project_root / EXPORT_DIRS["pdf"], ".pdf", required=output_format == "pdf")
    if output_format in {None, "docx"}:
        copy_rendered_files(source, project_root / EXPORT_DIRS["docx"], ".docx", required=output_format == "docx")


def check_preconditions(output_format: str | None) -> int:
    if not shutil.which("quarto"):
        print("Quarto is not installed.")
        print("Install Quarto manually, then run:")
        print("  bash scripts/research-writing/render.sh")
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
            print("  bash scripts/research-writing/render.sh")
            return 1
    return 0


def run_citation_preflight(
    command_runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> int:
    return command_runner(
        [sys.executable, "scripts/research-writing/check_citations.py"],
        check=False,
    ).returncode


def main(argv: list[str]) -> int:
    change_to_project_root()
    args = parse_args(argv)
    preflight_exit = check_preconditions(args.to)
    if preflight_exit:
        return preflight_exit
    citation_exit = run_citation_preflight()
    if citation_exit:
        return citation_exit
    render = subprocess.run(quarto_command(args.to), check=False)
    if render.returncode:
        return render.returncode
    try:
        mirror_render_outputs(args.to)
    except OSError as error:
        print(f"Failed to mirror rendered output into exports/: {error}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
