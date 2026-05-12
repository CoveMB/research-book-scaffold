#!/usr/bin/env python3
"""Check manuscript citekeys against bibliography/references.bib."""

from __future__ import annotations

import re
import sys
import argparse
from pathlib import Path


BIBLIOGRAPHY_PATH = Path("bibliography/references.bib")
DEFAULT_SCAN_ROOTS = [Path("manuscript")]
RESEARCH_NOTE_ROOTS = [Path("notes"), Path("research")]
IGNORED_DIRS = {".git", ".quarto", "_book", "vendor"}
SUPPORTED_SUFFIXES = {".md", ".qmd"}

BIB_ENTRY_RE = re.compile(r"@\s*([A-Za-z]+)\s*\{\s*([^,\s]+)", re.MULTILINE)
CITATION_BRACKET_RE = re.compile(r"\[([^\]]*@[^\]]*)\]")
CITEKEY_RE = re.compile(r"(?<![\w-])-?@([A-Za-z0-9_:.#$%&+?<>~/|-]+)")
IGNORED_BIB_TYPES = {"comment", "preamble", "string"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--include-notes",
        action="store_true",
        help="Also scan notes/ and research/ for citation keys.",
    )
    parser.add_argument(
        "--require-citations",
        action="store_true",
        help="Fail when no citations are found in scanned files.",
    )
    return parser.parse_args()


def scan_roots(include_notes: bool) -> list[Path]:
    if include_notes:
        return [*DEFAULT_SCAN_ROOTS, *RESEARCH_NOTE_ROOTS]
    return list(DEFAULT_SCAN_ROOTS)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def parse_bib_keys(path: Path) -> set[str]:
    if not path.exists():
        print(f"FAIL missing {path}")
        return set()
    text = read_text(path)
    keys: set[str] = set()
    for entry_type, key in BIB_ENTRY_RE.findall(text):
        if entry_type.lower() not in IGNORED_BIB_TYPES:
            keys.add(key.strip())
    return keys


def should_skip(path: Path) -> bool:
    return any(part in IGNORED_DIRS for part in path.parts)


def iter_manuscript_files(roots: list[Path]) -> list[Path]:
    files: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES and not should_skip(path):
                files.append(path)
    return sorted(files)


def parse_citations(path: Path) -> set[str]:
    text = read_text(path)
    keys: set[str] = set()
    for bracket_content in CITATION_BRACKET_RE.findall(text):
        for key in CITEKEY_RE.findall(bracket_content):
            keys.add(key.rstrip(".,;:"))
    return keys


def exit_code_for_findings(missing: list[str], manuscript_keys: set[str], require_citations: bool) -> int:
    if missing:
        return 1
    if require_citations and not manuscript_keys:
        return 1
    return 0


def main() -> int:
    args = parse_args()
    bibliography_keys = parse_bib_keys(BIBLIOGRAPHY_PATH)
    manuscript_files = iter_manuscript_files(scan_roots(args.include_notes))

    manuscript_keys_by_file: dict[Path, set[str]] = {
        path: parse_citations(path) for path in manuscript_files
    }
    manuscript_keys = set().union(*manuscript_keys_by_file.values()) if manuscript_keys_by_file else set()

    missing = sorted(manuscript_keys - bibliography_keys)
    unused = sorted(bibliography_keys - manuscript_keys)

    if missing:
        print("Missing bibliography entries:")
        for key in missing:
            locations = [
                str(path)
                for path, keys in manuscript_keys_by_file.items()
                if key in keys
            ]
            print(f"- {key}: {', '.join(locations)}")

    if unused:
        print("Unused bibliography keys:")
        for key in unused:
            print(f"- {key}")

    if args.require_citations and not manuscript_keys:
        print("FAIL no citations found in scanned files.")

    print(
        f"\nChecked {len(manuscript_files)} scanned file(s), "
        f"{len(manuscript_keys)} citation key(s), "
        f"{len(bibliography_keys)} bibliography key(s)."
    )

    return exit_code_for_findings(missing, manuscript_keys, args.require_citations)


if __name__ == "__main__":
    sys.exit(main())
