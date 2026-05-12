"""Shared Git helpers for local repository scripts."""

from __future__ import annotations

import subprocess
from pathlib import Path


def git_stdout(command: list[str], cwd: Path | None = None) -> str | None:
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def has_git_checkout(path: Path) -> bool:
    return (path / ".git").exists()


def changed_paths_from_status(status_text: str) -> list[str]:
    return [line[3:].strip() for line in status_text.splitlines() if line.strip()]
