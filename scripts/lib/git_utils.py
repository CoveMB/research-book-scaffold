"""Shared Git helpers for local repository scripts."""

from __future__ import annotations

import subprocess
from pathlib import Path
from urllib.parse import urlparse


class GitCommandError(RuntimeError):
    """Raised when a required Git command fails."""


def git_stdout(command: list[str], cwd: Path | None = None) -> str | None:
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def git_stdout_required(command: list[str], cwd: Path | None = None) -> str:
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise GitCommandError(f"git command failed: {' '.join(command)}")
    return result.stdout.strip()


def has_git_checkout(path: Path) -> bool:
    return (path / ".git").exists()


def changed_paths_from_status(status_text: str) -> list[str]:
    return [line[3:].strip() for line in status_text.splitlines() if line.strip()]


def github_repository_from_path(path: str) -> str | None:
    parts = [part for part in path.strip("/").split("/") if part]
    if len(parts) != 2:
        return None
    owner, repository = parts
    if repository.endswith(".git"):
        repository = repository[:-4]
    if not owner or not repository:
        return None
    return f"{owner.lower()}/{repository.lower()}"


def github_repository_from_url(url: str) -> str | None:
    value = url.strip()
    if not value:
        return None
    if value.startswith("git@github.com:"):
        return github_repository_from_path(value.split(":", 1)[1])
    parsed = urlparse(value)
    if parsed.hostname != "github.com":
        return None
    return github_repository_from_path(parsed.path)


def github_repositories_match(actual_url: str, expected_url: str) -> bool:
    expected = github_repository_from_url(expected_url)
    actual = github_repository_from_url(actual_url)
    return bool(expected and actual and actual == expected)
