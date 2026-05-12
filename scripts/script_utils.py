"""Small shared helpers for repository scripts."""

from __future__ import annotations

import subprocess
import re
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path


DOCUMENT_SUFFIXES = {".md", ".qmd"}
DEFAULT_IGNORED_DIRS = {".git", ".quarto", "_book", "vendor"}
PLACEHOLDER_RE = re.compile(r"\{\{\s*[A-Za-z][A-Za-z0-9_ -]{0,80}\s*\}\}")


@dataclass
class StatusReport:
    installed: list[str] = field(default_factory=list)
    already_present: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    next_steps: list[str] = field(default_factory=list)

    def add(self, bucket: str, message: str) -> None:
        getattr(self, bucket).append(message)
        label = bucket.replace("_", " ").upper()
        print(f"{label}: {message}")

    def ok(self) -> bool:
        return not self.failed


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def replace_placeholders(text: str, replacements: dict[str, str]) -> str:
    def replace_match(match: re.Match[str]) -> str:
        raw_key = match.group(0).strip("{} ")
        return replacements.get(raw_key, match.group(0))

    return PLACEHOLDER_RE.sub(replace_match, text)


def should_skip_path(path: Path, ignored_dirs: set[str]) -> bool:
    return any(part in ignored_dirs for part in path.parts)


def ignored_dirs_with(extra: Iterable[str] = (), include: Iterable[str] = ()) -> set[str]:
    ignored = set(DEFAULT_IGNORED_DIRS)
    ignored.update(extra)
    ignored.difference_update(include)
    return ignored


def iter_supported_files(
    paths: Iterable[Path],
    ignored_dirs: set[str] | None = None,
    supported_suffixes: set[str] | None = None,
) -> list[Path]:
    ignored = ignored_dirs if ignored_dirs is not None else DEFAULT_IGNORED_DIRS
    suffixes = supported_suffixes if supported_suffixes is not None else DOCUMENT_SUFFIXES
    files: list[Path] = []
    for path in paths:
        if path.is_file() and path.suffix.lower() in suffixes and not should_skip_path(path, ignored):
            files.append(path)
            continue
        if path.is_dir():
            for child in path.rglob("*"):
                if child.is_file() and child.suffix.lower() in suffixes and not should_skip_path(child, ignored):
                    files.append(child)
    return sorted(files)


def run_command(
    command: list[str],
    report: StatusReport,
    dry_run: bool,
    action: str,
    cwd: Path | None = None,
    success_bucket: str = "installed",
) -> bool:
    printable = " ".join(command)
    if dry_run:
        report.add("skipped", f"dry-run would run: {printable}")
        return True
    try:
        result = subprocess.run(command, cwd=cwd, check=False, text=True)
    except OSError as error:
        report.add("failed", f"{action}: {error}")
        return False
    if result.returncode == 0:
        report.add(success_bucket, action)
        return True
    report.add("failed", f"{action}: command exited {result.returncode}: {printable}")
    return False
