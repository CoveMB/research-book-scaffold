"""Import path setup for scripts that are executed by file path."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_IMPORT_DIRS = (
    "lib",
    "research-writing",
    "operations/setup",
    "operations/health",
    "operations/vendors",
    "operations/obsidian",
)


def scripts_root_for(file_path: str | Path) -> Path:
    for parent in Path(file_path).resolve().parents:
        if parent.name == "scripts":
            return parent
    raise RuntimeError(f"Could not find scripts root for {file_path}")


def prepend_path_once(path: Path) -> None:
    path_text = str(path)
    if path_text not in sys.path:
        sys.path.insert(0, path_text)


def configure_script_paths(file_path: str | Path) -> Path:
    scripts_root = scripts_root_for(file_path)
    for relative_path in reversed(SCRIPT_IMPORT_DIRS):
        prepend_path_once(scripts_root / relative_path)
    return scripts_root
