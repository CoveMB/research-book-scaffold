#!/usr/bin/env python3
"""Check whether scaffold manuscript entries still block release readiness."""

from __future__ import annotations

import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

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


@dataclass(frozen=True)
class ForbiddenScaffoldPhrase:
    phrase: str
    category: str
    suggested_fix: str


@dataclass(frozen=True)
class ReadinessFinding:
    path: Path
    line_number: int
    phrase: str
    category: str
    context: str
    suggested_fix: str


FORBIDDEN_SCAFFOLD_PHRASES: tuple[ForbiddenScaffoldPhrase, ...] = (
    ForbiddenScaffoldPhrase(
        "Research Scaffold Verification Manuscript",
        "generic scaffold identity not replaced",
        "Replace the scaffold manuscript title in manuscript/_quarto.yml with the real project title.",
    ),
    ForbiddenScaffoldPhrase(
        "Untitled Scholarly Manuscript",
        "generic scaffold identity not replaced",
        "Replace the scaffold manuscript title in manuscript/_quarto.yml with the real project title.",
    ),
    ForbiddenScaffoldPhrase(
        "This manuscript scaffold is generic.",
        "generic scaffold identity not replaced",
        "Replace manuscript/index.qmd with project-specific front matter or overview prose.",
    ),
    ForbiddenScaffoldPhrase(
        "Replace this page with project-level front matter",
        "generic scaffold identity not replaced",
        "Replace manuscript/index.qmd with project-specific front matter or overview prose.",
    ),
    ForbiddenScaffoldPhrase(
        "Use citations only after the citekey exists in",
        "generic scaffold identity not replaced",
        "Replace scaffold citation guidance with project-specific manuscript prose.",
    ),
    ForbiddenScaffoldPhrase(
        "PDF output depends on a local TeX distribution",
        "generic scaffold identity not replaced",
        "Replace scaffold verification prose with project-specific manuscript prose.",
    ),
    ForbiddenScaffoldPhrase(
        "Use this file for generic front matter",
        "generic scaffold identity not replaced",
        "Replace scaffold front matter guidance with real front matter, or remove the file from manuscript/_quarto.yml.",
    ),
    ForbiddenScaffoldPhrase(
        "Use this file for references to appendices",
        "generic scaffold identity not replaced",
        "Replace scaffold back matter guidance with real back matter, or remove the file from manuscript/_quarto.yml.",
    ),
    ForbiddenScaffoldPhrase(
        "chapters/01-chapter-template.qmd",
        "sample manuscript file still included",
        "Remove the sample chapter from manuscript/_quarto.yml or replace it with a real chapter path.",
    ),
    ForbiddenScaffoldPhrase(
        "appendices/appendix-template.qmd",
        "sample manuscript file still included",
        "Remove the sample appendix from manuscript/_quarto.yml or replace it with a real appendix path.",
    ),
    ForbiddenScaffoldPhrase(
        "This sample chapter shows the expected shape of a chapter file",
        "sample manuscript text still included",
        "Replace sample chapter text with verified project manuscript prose.",
    ),
    ForbiddenScaffoldPhrase(
        "This sample appendix shows where supporting material can live",
        "sample manuscript text still included",
        "Replace sample appendix text with verified project appendix prose.",
    ),
    ForbiddenScaffoldPhrase(
        "Replace this sample with project material before using the manuscript as a real draft",
        "sample manuscript text still included",
        "Replace sample appendix text with verified project appendix prose.",
    ),
)


def strip_yaml_list_entry(line: str) -> str | None:
    stripped = line.strip()
    if not stripped.startswith("-"):
        return None
    value = stripped[1:].split("#", maxsplit=1)[0].strip()
    return value.strip("\"'") or None


def referenced_qmd_files(config_text: str) -> list[Path]:
    files: list[Path] = []
    for line in config_text.splitlines():
        value = strip_yaml_list_entry(line)
        if value is None or not value.endswith(".qmd"):
            continue
        path = Path(value)
        if path.is_absolute() or ".." in path.parts:
            continue
        files.append(path)
    return files


def unique_paths(paths: Sequence[Path]) -> list[Path]:
    unique: list[Path] = []
    seen: set[Path] = set()
    for path in paths:
        if path in seen:
            continue
        unique.append(path)
        seen.add(path)
    return unique


def display_path(project_root: Path, path: Path) -> Path:
    try:
        return path.relative_to(project_root)
    except ValueError:
        return path


def scan_text(path: Path, text: str) -> list[ReadinessFinding]:
    findings: list[ReadinessFinding] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for forbidden_phrase in FORBIDDEN_SCAFFOLD_PHRASES:
            if forbidden_phrase.phrase not in line:
                continue
            findings.append(
                ReadinessFinding(
                    path=path,
                    line_number=line_number,
                    phrase=forbidden_phrase.phrase,
                    category=forbidden_phrase.category,
                    context=line.strip(),
                    suggested_fix=forbidden_phrase.suggested_fix,
                )
            )
            break
    return findings


def readiness_findings(config_text: str) -> list[ReadinessFinding]:
    return scan_text(QUARTO_CONFIG, config_text)


def release_manuscript_paths(project_root: Path, config_text: str) -> list[Path]:
    included_files = [project_root / MANUSCRIPT_DIR / path for path in referenced_qmd_files(config_text)]
    return unique_paths([project_root / QUARTO_CONFIG, *included_files])


def scan_release_manuscript(project_root: Path) -> list[ReadinessFinding]:
    config_path = project_root / QUARTO_CONFIG
    config_text = read_text(config_path)
    findings: list[ReadinessFinding] = []
    for path in release_manuscript_paths(project_root, config_text):
        if not path.is_file():
            continue
        findings.extend(scan_text(display_path(project_root, path), read_text(path)))
    return findings


def format_finding(finding: ReadinessFinding) -> str:
    return (
        f"{finding.path}:{finding.line_number}: {finding.category}: {finding.phrase}\n"
        f"  Context: {finding.context}\n"
        f"  Fix: {finding.suggested_fix}"
    )


def main() -> int:
    change_to_project_root()
    if not QUARTO_CONFIG.is_file():
        print(f"FAIL missing {QUARTO_CONFIG}")
        return 1

    findings = scan_release_manuscript(Path("."))
    if findings:
        print("Manuscript release-readiness blockers:")
        for finding in findings:
            print(format_finding(finding))
        print(f"\nFound {len(findings)} generic scaffold manuscript blocker(s).")
        return 1

    print("No generic scaffold manuscript text found in release manuscript files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
