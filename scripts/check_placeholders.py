#!/usr/bin/env python3
"""Scan Markdown and Quarto files for unresolved placeholder markers."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


MARKERS = [
    re.compile(r"\bTODO\b", re.IGNORECASE),
    re.compile(r"\bFIXME\b", re.IGNORECASE),
    re.compile(r"citation needed", re.IGNORECASE),
    re.compile(r"\{\{\s*citation needed\s*\}\}", re.IGNORECASE),
    re.compile(r"\{\{\s*claim risk\s*\}\}", re.IGNORECASE),
    re.compile(r"\{\{\s*verify\s*\}\}", re.IGNORECASE),
    re.compile(r"\[(?!@)(?![ xX]\])([A-Za-z][^\]\n]{0,80})\](?!\()"),
]

DEFAULT_IGNORED_DIRS = {".git", ".quarto", "_book", "vendor", "plugins", "templates"}
SUPPORTED_SUFFIXES = {".md", ".qmd"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", default=["."], help="Files or folders to scan.")
    parser.add_argument(
        "--include-templates",
        action="store_true",
        help="Include templates/ in the scan.",
    )
    return parser.parse_args()


def should_skip(path: Path, include_templates: bool) -> bool:
    ignored_dirs = set(DEFAULT_IGNORED_DIRS)
    if include_templates:
        ignored_dirs.discard("templates")
    return any(part in ignored_dirs for part in path.parts)


def iter_files(paths: list[str], include_templates: bool) -> list[Path]:
    files: list[Path] = []
    for raw_path in paths:
        path = Path(raw_path)
        if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES:
            if not should_skip(path, include_templates):
                files.append(path)
        elif path.is_dir():
            for child in path.rglob("*"):
                if child.is_file() and child.suffix.lower() in SUPPORTED_SUFFIXES:
                    if not should_skip(child, include_templates):
                        files.append(child)
    return sorted(files)


def strip_fenced_code(line: str, in_fence: bool) -> tuple[str, bool]:
    stripped = line.lstrip()
    if stripped.startswith("```") or stripped.startswith("~~~"):
        return "", not in_fence
    if in_fence:
        return "", in_fence
    return line, in_fence


def scan_file(path: Path) -> list[tuple[int, str]]:
    findings: list[tuple[int, str]] = []
    in_fence = False
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()

    for line_number, line in enumerate(lines, start=1):
        scan_line, in_fence = strip_fenced_code(line, in_fence)
        if not scan_line:
            continue
        for marker in MARKERS:
            match = marker.search(scan_line)
            if match:
                findings.append((line_number, match.group(0)))
                break
    return findings


def main() -> int:
    args = parse_args()
    files = iter_files(args.paths, args.include_templates)
    all_findings: list[tuple[Path, int, str]] = []

    for path in files:
        for line_number, marker in scan_file(path):
            all_findings.append((path, line_number, marker))

    if all_findings:
        for path, line_number, marker in all_findings:
            print(f"{path}:{line_number}: {marker}")
        print(f"\nFound {len(all_findings)} unresolved placeholder marker(s).")
        return 1

    print(f"No unresolved placeholder markers found in {len(files)} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
