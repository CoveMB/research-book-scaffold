from __future__ import annotations

import contextlib
import io
import json
import os
import sys
from collections.abc import Callable, Iterator
from pathlib import Path


TESTS_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = TESTS_DIR.parent
SCRIPT_IMPORT_DIRS = [
    SCRIPTS_DIR / "lib",
    SCRIPTS_DIR / "research-writing",
    SCRIPTS_DIR / "operations" / "setup",
    SCRIPTS_DIR / "operations" / "health",
    SCRIPTS_DIR / "operations" / "vendors",
    SCRIPTS_DIR / "operations" / "obsidian",
]
REMOVED_EXTERNAL_REPO_FLAGS = ("--ars-repo", "--rbs-repo", "--subagent-orchestrator-repo", "--obsidian-skills-repo")


def add_path(path: Path) -> None:
    path_text = str(path)
    if path_text not in sys.path:
        sys.path.insert(0, path_text)


def add_scripts_to_path() -> None:
    add_path(SCRIPTS_DIR)
    for path in reversed(SCRIPT_IMPORT_DIRS):
        add_path(path)


def add_tests_to_path() -> None:
    add_path(TESTS_DIR)


def assert_parse_args_rejects(
    test_case: object,
    parse_args: Callable[[list[str]], object],
    argv: list[str],
) -> None:
    with contextlib.redirect_stderr(io.StringIO()):
        with test_case.assertRaises(SystemExit):
            parse_args(argv)


add_scripts_to_path()

import setup_environment
from project_config import CODEX_PANEL_PLUGIN_ID, REQUIRED_OBSIDIAN_PLUGIN_FILES


class SilentReport(setup_environment.Report):
    def add(self, bucket: str, message: str) -> None:
        getattr(self, bucket).append(message)


@contextlib.contextmanager
def working_directory(path: Path) -> Iterator[None]:
    original_cwd = Path.cwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(original_cwd)


def write_plugin_release(release_path: Path, manifest_id: str = CODEX_PANEL_PLUGIN_ID) -> None:
    assets_dir = release_path.parent / f"{release_path.stem}-assets"
    assets_dir.mkdir()
    plugin_files = {
        "manifest.json": json.dumps({"id": manifest_id}),
        "main.js": "module.exports = {};",
        "styles.css": "",
    }
    assets = []
    for file_name in sorted(REQUIRED_OBSIDIAN_PLUGIN_FILES):
        asset_path = assets_dir / file_name
        asset_path.write_text(plugin_files[file_name], encoding="utf-8")
        assets.append({"name": file_name, "browser_download_url": asset_path.as_uri()})
    release_path.write_text(json.dumps({"assets": assets}), encoding="utf-8")


def install_in_directory(work_dir: Path, args: object, report: setup_environment.Report) -> None:
    with working_directory(work_dir):
        setup_environment.install_codex_panel(args, report)
