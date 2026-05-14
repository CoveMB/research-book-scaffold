#!/usr/bin/env python3
"""Conservatively check wiki-style links in notes, manuscript, and research files."""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

_SCRIPTS_ROOT = next(parent for parent in Path(__file__).resolve().parents if parent.name == "scripts")
_LIB_DIR = _SCRIPTS_ROOT / "lib"
if str(_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(_LIB_DIR))

from import_paths import configure_script_paths
from project_config import change_to_project_root
from script_utils import DEFAULT_IGNORED_DIRS, DOCUMENT_SUFFIXES, iter_supported_files, read_text

configure_script_paths(__file__)

ROOTS = [Path("notes"), Path("manuscript"), Path("research")]
IGNORED_DIRS = set(DEFAULT_IGNORED_DIRS)
SUPPORTED_SUFFIXES = set(DOCUMENT_SUFFIXES)
WIKI_LINK_RE = re.compile(r"(?<!!)\[\[([^\]]+)\]\]")


@dataclass(frozen=True)
class LinkStatus:
    kind: str
    matches: tuple[Path, ...] = ()


def iter_files() -> list[Path]:
    return iter_supported_files(ROOTS, IGNORED_DIRS, SUPPORTED_SUFFIXES)


def normalize_link_target(raw_target: str) -> str:
    target = raw_target.split("|", 1)[0].split("#", 1)[0].strip()
    return target.strip()


def add_target(targets: dict[str, set[Path]], key: str, path: Path) -> None:
    targets.setdefault(key, set()).add(path)


def build_target_index(files: list[Path]) -> dict[str, set[Path]]:
    targets: dict[str, set[Path]] = {}
    for path in files:
        add_target(targets, path.stem, path)
        add_target(targets, path.name, path)
        add_target(targets, path.as_posix(), path)
        for root in ROOTS:
            try:
                add_target(targets, path.relative_to(root).as_posix(), path)
                add_target(targets, path.relative_to(root).with_suffix("").as_posix(), path)
            except ValueError:
                continue
    return targets


def link_status(target: str, source: Path, target_index: dict[str, set[Path]]) -> LinkStatus:
    if not target or target.startswith("#"):
        return LinkStatus("ok")
    candidate = Path(target)
    possible_targets = {
        target,
        candidate.name,
        candidate.stem,
        candidate.with_suffix("").as_posix() if candidate.suffix else target,
        f"{target}.md",
        f"{target}.qmd",
    }
    matches = {
        match
        for possible_target in possible_targets
        for match in target_index.get(possible_target, set())
    }
    local_matches = {
        path
        for path in [
            source.parent / target,
            source.parent / f"{target}.md",
            source.parent / f"{target}.qmd",
        ]
        if path.exists()
    }
    matches.update(local_matches)
    if not matches:
        return LinkStatus("missing")
    if len(matches) > 1 and "/" not in target:
        return LinkStatus("ambiguous", tuple(sorted(matches)))
    return LinkStatus("ok", tuple(sorted(matches)))


def scan_file(path: Path, target_index: dict[str, set[Path]]) -> list[tuple[int, str, LinkStatus]]:
    findings: list[tuple[int, str, LinkStatus]] = []
    for line_number, line in enumerate(read_text(path).splitlines(), start=1):
        for raw_target in WIKI_LINK_RE.findall(line):
            target = normalize_link_target(raw_target)
            status = link_status(target, path, target_index)
            if status.kind != "ok":
                findings.append((line_number, raw_target, status))
    return findings


def main() -> int:
    change_to_project_root()
    files = iter_files()
    target_index = build_target_index(files)
    findings: list[tuple[Path, int, str, LinkStatus]] = []

    for path in files:
        for line_number, target, status in scan_file(path, target_index):
            findings.append((path, line_number, target, status))

    if findings:
        for path, line_number, target, status in findings:
            if status.kind == "ambiguous":
                matches = ", ".join(match.as_posix() for match in status.matches)
                print(f"{path}:{line_number}: ambiguous wiki link [[{target}]] matches: {matches}")
            else:
                print(f"{path}:{line_number}: broken wiki link [[{target}]]")
        print(f"\nFound {len(findings)} broken internal link(s).")
        return 1

    print(f"No broken wiki links found in {len(files)} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
