#!/usr/bin/env python3
"""Conservatively check wiki-style links in notes, manuscript, and research files."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOTS = [Path("notes"), Path("manuscript"), Path("research")]
IGNORED_DIRS = {".git", ".quarto", "_book", "vendor"}
SUPPORTED_SUFFIXES = {".md", ".qmd"}
WIKI_LINK_RE = re.compile(r"(?<!!)\[\[([^\]]+)\]\]")


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def should_skip(path: Path) -> bool:
    return any(part in IGNORED_DIRS for part in path.parts)


def iter_files() -> list[Path]:
    files: list[Path] = []
    for root in ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES and not should_skip(path):
                files.append(path)
    return sorted(files)


def normalize_link_target(raw_target: str) -> str:
    target = raw_target.split("|", 1)[0].split("#", 1)[0].strip()
    return target.strip()


def build_target_index(files: list[Path]) -> set[str]:
    targets: set[str] = set()
    for path in files:
        targets.add(path.stem)
        targets.add(path.name)
        targets.add(path.as_posix())
        for root in ROOTS:
            try:
                targets.add(path.relative_to(root).as_posix())
                targets.add(path.relative_to(root).with_suffix("").as_posix())
            except ValueError:
                continue
    return targets


def link_exists(target: str, source: Path, target_index: set[str]) -> bool:
    if not target or target.startswith("#"):
        return True
    candidate = Path(target)
    possible_targets = {
        target,
        candidate.name,
        candidate.stem,
        candidate.with_suffix("").as_posix() if candidate.suffix else target,
        f"{target}.md",
        f"{target}.qmd",
    }
    if possible_targets & target_index:
        return True
    if (source.parent / target).exists():
        return True
    if (source.parent / f"{target}.md").exists():
        return True
    if (source.parent / f"{target}.qmd").exists():
        return True
    return False


def scan_file(path: Path, target_index: set[str]) -> list[tuple[int, str]]:
    findings: list[tuple[int, str]] = []
    for line_number, line in enumerate(read_text(path).splitlines(), start=1):
        for raw_target in WIKI_LINK_RE.findall(line):
            target = normalize_link_target(raw_target)
            if not link_exists(target, path, target_index):
                findings.append((line_number, raw_target))
    return findings


def main() -> int:
    files = iter_files()
    target_index = build_target_index(files)
    findings: list[tuple[Path, int, str]] = []

    for path in files:
        for line_number, target in scan_file(path, target_index):
            findings.append((path, line_number, target))

    if findings:
        for path, line_number, target in findings:
            print(f"{path}:{line_number}: broken wiki link [[{target}]]")
        print(f"\nFound {len(findings)} broken internal link(s).")
        return 1

    print(f"No broken wiki links found in {len(files)} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
