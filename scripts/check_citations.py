#!/usr/bin/env python3
"""Check manuscript citekeys against bibliography/references.bib."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from project_config import change_to_project_root
from script_utils import DEFAULT_IGNORED_DIRS, DOCUMENT_SUFFIXES, iter_supported_files, read_text

BIBLIOGRAPHY_PATH = Path("bibliography/references.bib")
DEFAULT_SCAN_ROOTS = [Path("manuscript")]
RESEARCH_NOTE_ROOTS = [Path("notes"), Path("research")]
IGNORED_DIRS = set(DEFAULT_IGNORED_DIRS)
SUPPORTED_SUFFIXES = set(DOCUMENT_SUFFIXES)

BIB_ENTRY_RE = re.compile(r"@\s*([A-Za-z]+)\s*\{\s*([^,\s]+)", re.MULTILINE)
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
    parser.add_argument(
        "--show-unused",
        action="store_true",
        help="Print bibliography keys that are not cited in scanned files.",
    )
    return parser.parse_args()


def scan_roots(include_notes: bool) -> list[Path]:
    if include_notes:
        return [*DEFAULT_SCAN_ROOTS, *RESEARCH_NOTE_ROOTS]
    return list(DEFAULT_SCAN_ROOTS)


def bib_key_entries(text: str) -> list[str]:
    return [
        key.strip()
        for entry_type, key in BIB_ENTRY_RE.findall(text)
        if entry_type.lower() not in IGNORED_BIB_TYPES
    ]


def duplicate_bib_keys(text: str) -> list[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for key in bib_key_entries(text):
        if key in seen:
            duplicates.add(key)
        seen.add(key)
    return sorted(duplicates)


def parse_bib_keys(path: Path) -> set[str]:
    if not path.exists():
        print(f"FAIL missing {path}")
        return set()
    return set(bib_key_entries(read_text(path)))


def iter_manuscript_files(roots: list[Path]) -> list[Path]:
    return iter_supported_files(roots, IGNORED_DIRS, SUPPORTED_SUFFIXES)


def parse_citations(path: Path) -> set[str]:
    text = read_text(path)
    return {key.rstrip(".,;:") for key in CITEKEY_RE.findall(text)}


def exit_code_for_findings(
    missing: list[str],
    manuscript_keys: set[str],
    require_citations: bool,
    duplicate_keys: list[str] | None = None,
) -> int:
    if missing or duplicate_keys:
        return 1
    if require_citations and not manuscript_keys:
        return 1
    return 0


def main() -> int:
    change_to_project_root()
    args = parse_args()
    bibliography_text = read_text(BIBLIOGRAPHY_PATH) if BIBLIOGRAPHY_PATH.exists() else ""
    bibliography_keys = parse_bib_keys(BIBLIOGRAPHY_PATH)
    duplicate_keys = duplicate_bib_keys(bibliography_text)
    manuscript_files = iter_manuscript_files(scan_roots(args.include_notes))

    manuscript_keys_by_file: dict[Path, set[str]] = {
        path: parse_citations(path) for path in manuscript_files
    }
    manuscript_keys = set().union(*manuscript_keys_by_file.values()) if manuscript_keys_by_file else set()

    missing = sorted(manuscript_keys - bibliography_keys)
    unused = sorted(bibliography_keys - manuscript_keys)

    if duplicate_keys:
        print("Duplicate bibliography keys:")
        for key in duplicate_keys:
            print(f"- {key}")

    if missing:
        print("Missing bibliography entries:")
        for key in missing:
            locations = [
                str(path)
                for path, keys in manuscript_keys_by_file.items()
                if key in keys
            ]
            print(f"- {key}: {', '.join(locations)}")

    if args.show_unused and unused:
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

    return exit_code_for_findings(missing, manuscript_keys, args.require_citations, duplicate_keys)


if __name__ == "__main__":
    sys.exit(main())
