#!/usr/bin/env python3
"""Check Obsidian plugin installation without modifying files."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

from obsidian_agent import community_plugins_path, read_enabled_community_plugins
from project_config import (
    OBSIDIAN_CODEX_PLUGIN_ID,
    OBSIDIAN_DIR,
    OBSIDIAN_PLUGIN_DIR,
    REQUIRED_OBSIDIAN_PLUGIN_FILES,
    change_to_project_root,
    resolve_obsidian_vault_path,
)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="check_obsidian_codex.py",
        description=__doc__,
    )
    parser.add_argument(
        "vault",
        nargs="?",
        help="Obsidian vault path. Defaults to OBSIDIAN_VAULT or the project root.",
    )
    return parser.parse_args(argv)


def vault_path_from_args(args: argparse.Namespace) -> Path:
    return resolve_obsidian_vault_path(args.vault, os.environ.get("OBSIDIAN_VAULT"))


def check_cli() -> bool:
    executable = shutil.which("codex")
    if not executable:
        print("WARN codex CLI missing")
        return False
    print(f"PASS codex CLI found: {executable}")
    try:
        result = subprocess.run(
            [executable, "--version"],
            check=False,
            text=True,
            capture_output=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError) as error:
        print(f"WARN codex --version failed: {error}")
        return False
    if result.returncode == 0:
        version = result.stdout.strip() or result.stderr.strip()
        print(f"PASS codex --version: {version}")
        return True
    print(f"WARN codex --version exited {result.returncode}: {result.stderr.strip()}")
    return False


def check_community_plugins(obsidian_dir: Path) -> bool:
    plugins_path = community_plugins_path(obsidian_dir)
    if not plugins_path.exists():
        print("FAIL .obsidian/community-plugins.json missing; cannot confirm enablement")
        return False
    try:
        enabled_plugins = read_enabled_community_plugins(obsidian_dir)
    except RuntimeError as error:
        print(f"FAIL {error}")
        return False
    if OBSIDIAN_CODEX_PLUGIN_ID in enabled_plugins:
        print("PASS Obsidian plugin listed as enabled")
        return True
    else:
        print("FAIL Obsidian plugin is installed but not listed as enabled")
        return False


def main(argv: list[str] | None = None) -> int:
    change_to_project_root()
    args = parse_args(sys.argv[1:] if argv is None else argv)
    vault_path = vault_path_from_args(args)
    failures = 0

    if vault_path.exists() and vault_path.is_dir():
        print(f"PASS vault exists: {vault_path}")
    else:
        print(f"FAIL vault path missing: {vault_path}")
        check_cli()
        return 1

    obsidian_dir = vault_path / OBSIDIAN_DIR
    if obsidian_dir.exists() and obsidian_dir.is_dir():
        print(f"PASS Obsidian config exists: {obsidian_dir}")
    else:
        print(f"WARN Obsidian config missing: {obsidian_dir}")

    plugin_dir = vault_path / OBSIDIAN_PLUGIN_DIR
    if plugin_dir.exists() and plugin_dir.is_dir():
        print(f"PASS plugin directory exists: {plugin_dir}")
    else:
        print(f"FAIL plugin directory missing: {plugin_dir}")
        failures += 1

    for file_name in sorted(REQUIRED_OBSIDIAN_PLUGIN_FILES):
        file_path = plugin_dir / file_name
        if file_path.exists() and file_path.is_file():
            print(f"PASS {file_name} exists")
        else:
            print(f"FAIL {file_name} missing")
            failures += 1

    if obsidian_dir.exists() and not check_community_plugins(obsidian_dir):
        failures += 1
    if not check_cli():
        failures += 1

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
