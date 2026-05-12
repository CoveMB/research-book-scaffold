#!/usr/bin/env python3
"""Check local tools and scaffold files."""

from __future__ import annotations

import sys
from pathlib import Path

from environment_checks import CORE_TOOLS, OPTIONAL_TOOLS, command_exists
from project_config import change_to_project_root


REQUIRED_FILES = [Path("bibliography/references.bib"), Path("manuscript/_quarto.yml")]
REQUIRED_DIRS = [Path(".agents/skills"), Path("templates"), Path("notes"), Path("research")]


def record(status: str, message: str, counts: dict[str, int]) -> None:
    counts[status] += 1
    print(f"{status.upper()} {message}")


def check_required_command(command: str, counts: dict[str, int]) -> None:
    if command_exists(command):
        record("pass", f"{command} found", counts)
    else:
        record("fail", f"{command} missing", counts)


def check_optional_command(command: str, counts: dict[str, int]) -> None:
    if command_exists(command):
        record("pass", f"{command} found", counts)
    else:
        record("warn", f"{command} missing", counts)


def check_file(path: Path, counts: dict[str, int]) -> None:
    if path.is_file():
        record("pass", f"{path} exists", counts)
    else:
        record("fail", f"{path} missing", counts)


def check_dir(path: Path, counts: dict[str, int]) -> None:
    if path.is_dir():
        record("pass", f"{path} exists", counts)
    else:
        record("fail", f"{path} missing", counts)


def main() -> int:
    change_to_project_root()
    counts = {"pass": 0, "warn": 0, "fail": 0}

    for command in CORE_TOOLS:
        check_required_command(command, counts)
    for command in OPTIONAL_TOOLS:
        check_optional_command(command, counts)
    for path in REQUIRED_FILES:
        check_file(path, counts)
    for path in REQUIRED_DIRS:
        check_dir(path, counts)

    print(f"\nSummary: {counts['pass']} pass, {counts['warn']} warn, {counts['fail']} fail")
    return 1 if counts["fail"] else 0


if __name__ == "__main__":
    sys.exit(main())
