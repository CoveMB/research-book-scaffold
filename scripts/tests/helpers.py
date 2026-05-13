from __future__ import annotations

import contextlib
import json
import os
import sys
import zipfile
from collections.abc import Iterator
from pathlib import Path


TESTS_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = TESTS_DIR.parent


def add_path(path: Path) -> None:
    path_text = str(path)
    if path_text not in sys.path:
        sys.path.insert(0, path_text)


def add_scripts_to_path() -> None:
    add_path(SCRIPTS_DIR)


def add_tests_to_path() -> None:
    add_path(TESTS_DIR)


add_scripts_to_path()

import setup_environment
from project_config import OBSIDIAN_CODEX_PLUGIN_ID, REQUIRED_OBSIDIAN_PLUGIN_FILES


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


def write_plugin_release(archive_path: Path) -> None:
    plugin_files = {
        "manifest.json": json.dumps({"id": OBSIDIAN_CODEX_PLUGIN_ID}),
        "main.js": "module.exports = {};",
        "styles.css": "",
    }
    with zipfile.ZipFile(archive_path, "w") as archive:
        for file_name in sorted(REQUIRED_OBSIDIAN_PLUGIN_FILES):
            archive.writestr(f"plugin/{file_name}", plugin_files[file_name])


def install_in_directory(work_dir: Path, args: object, report: setup_environment.Report) -> None:
    with working_directory(work_dir):
        setup_environment.install_obsidian_codex(args, report)
