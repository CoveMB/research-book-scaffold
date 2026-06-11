#!/usr/bin/env python3
"""Check local tools and scaffold files."""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS_ROOT = next(parent for parent in Path(__file__).resolve().parents if parent.name == "scripts")
_LIB_DIR = _SCRIPTS_ROOT / "lib"
if str(_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(_LIB_DIR))

from import_paths import configure_script_paths

configure_script_paths(__file__)

from environment_checks import (
    CORE_TOOLS,
    MINIMUM_PYTHON_VERSION_TEXT,
    OPTIONAL_TOOLS,
    command_exists,
    command_runs,
    python3_meets_minimum,
)
from git_utils import git_stdout
from project_config import change_to_project_root


REQUIRED_FILES = [Path("bibliography/references.bib"), Path("manuscript/_quarto.yml")]
REQUIRED_DIRS = [Path(".agents/skills"), Path("templates"), Path("notes"), Path("research")]
VERSION_CHECK_COMMANDS = {"codex": ["codex", "--version"]}


def record(status: str, message: str, counts: dict[str, int]) -> None:
    counts[status] += 1
    print(f"{status.upper()} {message}")


def check_required_command(command: str, counts: dict[str, int]) -> None:
    if not command_exists(command):
        record("fail", f"{command} missing", counts)
        return
    if command == "python3":
        if python3_meets_minimum():
            record("pass", f"python3 {MINIMUM_PYTHON_VERSION_TEXT}+ found", counts)
        else:
            record("fail", f"python3 {MINIMUM_PYTHON_VERSION_TEXT}+ required", counts)
        return
    version_command = VERSION_CHECK_COMMANDS.get(command)
    if version_command and not command_runs(version_command):
        record("warn", f"{command} found but version check failed", counts)
        return
    record("pass", f"{command} found", counts)


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


def branch_tracking_status(
    current_branch: str | None,
    upstream: str | None,
    divergence: tuple[int, int] | None,
) -> tuple[str, str]:
    if not current_branch:
        return "warn", "git repository is detached; check out intended branch before work"
    if not upstream:
        return "warn", f"git branch {current_branch} has no upstream configured"
    if divergence is None:
        return "warn", f"git branch {current_branch} tracking status unavailable"

    behind_count, ahead_count = divergence
    if ahead_count and behind_count:
        return (
            "warn",
            f"git branch {current_branch} has diverged from {upstream}: "
            f"{ahead_count} ahead, {behind_count} behind",
        )
    if ahead_count:
        return "warn", f"git branch {current_branch} is {ahead_count} commit(s) ahead of {upstream}"
    if behind_count:
        return "warn", f"git branch {current_branch} is {behind_count} commit(s) behind {upstream}"
    return "pass", f"git branch {current_branch} tracks {upstream} and is up to date"


def current_branch_tracking_status() -> tuple[str, str]:
    current_branch = git_stdout(["git", "branch", "--show-current"])
    upstream = git_stdout(["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"])
    divergence_text = git_stdout(["git", "rev-list", "--left-right", "--count", "@{u}...HEAD"]) if upstream else None
    divergence = None
    if divergence_text:
        left, right = divergence_text.split()
        divergence = (int(left), int(right))
    return branch_tracking_status(current_branch, upstream, divergence)


def check_git_branch_tracking(counts: dict[str, int]) -> None:
    status, message = current_branch_tracking_status()
    record(status, message, counts)


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
    if command_exists("git"):
        check_git_branch_tracking(counts)

    print(f"\nSummary: {counts['pass']} pass, {counts['warn']} warn, {counts['fail']} fail")
    return 1 if counts["fail"] else 0


if __name__ == "__main__":
    sys.exit(main())
