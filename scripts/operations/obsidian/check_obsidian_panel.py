#!/usr/bin/env python3
"""Check Codex Panel Obsidian installation without modifying files."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

_SCRIPTS_ROOT = next(parent for parent in Path(__file__).resolve().parents if parent.name == "scripts")
_LIB_DIR = _SCRIPTS_ROOT / "lib"
if str(_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(_LIB_DIR))

from import_paths import configure_script_paths

configure_script_paths(__file__)

from obsidian_agent import (
    codex_panel_settings_path,
    community_plugins_path,
    is_valid_codex_path,
    read_codex_panel_settings,
    read_enabled_community_plugins,
    validate_plugin_manifest,
)
from project_config import (
    CODEX_PANEL_PLUGIN_ID,
    OBSIDIAN_DIR,
    OBSIDIAN_PLUGIN_DIR,
    REQUIRED_OBSIDIAN_PLUGIN_FILES,
    change_to_project_root,
    resolve_obsidian_vault_path,
)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="check_obsidian_panel.py",
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


def command_output(result: subprocess.CompletedProcess[str]) -> str:
    return result.stdout.strip() or result.stderr.strip()


def run_codex_command(command: list[str], label: str) -> bool:
    try:
        result = subprocess.run(
            command,
            check=False,
            text=True,
            capture_output=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError) as error:
        print(f"FAIL {label} failed: {error}")
        return False
    if result.returncode == 0:
        output = command_output(result)
        if output:
            print(f"PASS {label}: {output}")
        else:
            print(f"PASS {label}")
        return True
    output = command_output(result)
    suffix = f": {output}" if output else ""
    print(f"FAIL {label} exited {result.returncode}{suffix}")
    return False


def configured_codex_path(plugin_dir: Path) -> Path | None:
    settings_path = codex_panel_settings_path(plugin_dir)
    if not settings_path.exists():
        print(f"FAIL {settings_path} missing")
        return None
    try:
        settings = read_codex_panel_settings(plugin_dir)
    except RuntimeError as error:
        print(f"FAIL {error}")
        return None
    codex_path = settings.get("codexPath")
    if not isinstance(codex_path, str) or not codex_path:
        print(f"FAIL {settings_path} missing codexPath")
        return None
    if not Path(codex_path).is_absolute():
        print(f"FAIL configured codexPath is not absolute: {codex_path}")
        return None
    if not is_valid_codex_path(codex_path):
        print(f"FAIL configured codexPath missing or not executable: {codex_path}")
        return None
    print(f"PASS configured codexPath exists: {codex_path}")
    return Path(codex_path)


def check_cli(plugin_dir: Path) -> bool:
    codex_path = configured_codex_path(plugin_dir)
    if codex_path is None:
        return False
    version_ok = run_codex_command([str(codex_path), "--version"], "codex --version")
    app_server_ok = run_codex_command([str(codex_path), "app-server", "--help"], "codex app-server --help")
    return version_ok and app_server_ok


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
    if CODEX_PANEL_PLUGIN_ID in enabled_plugins:
        print("PASS Obsidian plugin listed as enabled")
        return True
    print("FAIL Obsidian plugin is installed but not listed as enabled")
    return False


def check_manifest(plugin_dir: Path) -> bool:
    try:
        validate_plugin_manifest(plugin_dir)
    except RuntimeError as error:
        print(f"FAIL {error}")
        return False
    print(f"PASS manifest id is {CODEX_PANEL_PLUGIN_ID}")
    return True


def main(argv: list[str] | None = None) -> int:
    change_to_project_root()
    args = parse_args(sys.argv[1:] if argv is None else argv)
    vault_path = vault_path_from_args(args)
    failures = 0

    if vault_path.exists() and vault_path.is_dir():
        print(f"PASS vault exists: {vault_path}")
    else:
        print(f"FAIL vault path missing: {vault_path}")
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

    if plugin_dir.exists() and not check_manifest(plugin_dir):
        failures += 1
    if obsidian_dir.exists() and not check_community_plugins(obsidian_dir):
        failures += 1
    if plugin_dir.exists() and not check_cli(plugin_dir):
        failures += 1

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
