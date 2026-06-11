#!/usr/bin/env python3
"""Validate project-local Obsidian artifact files."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_SCRIPTS_ROOT = next(parent for parent in Path(__file__).resolve().parents if parent.name == "scripts")
_LIB_DIR = _SCRIPTS_ROOT / "lib"
if str(_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(_LIB_DIR))

from import_paths import configure_script_paths

configure_script_paths(__file__)

from script_utils import read_text


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="check_obsidian_artifacts.py",
        description=__doc__,
    )
    parser.add_argument("path", nargs="?", default=".", help="Project root or subtree to scan.")
    return parser.parse_args(argv)


def artifact_files(root: Path) -> list[Path]:
    if root.is_file():
        return [root] if root.suffix in {".base", ".canvas"} else []
    if not root.exists():
        return []
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix in {".base", ".canvas"} and "skill-plugins" not in path.parts
    )


def fail(message: str, failures: list[str]) -> None:
    print(f"FAIL {message}")
    failures.append(message)


def pass_message(message: str) -> None:
    print(f"PASS {message}")


def load_json_file(path: Path, failures: list[str]) -> dict[str, Any] | None:
    try:
        payload = json.loads(read_text(path))
    except json.JSONDecodeError as error:
        fail(f"canvas JSON invalid: {path}: {error}", failures)
        return None
    if not isinstance(payload, dict):
        fail(f"canvas root must be an object: {path}", failures)
        return None
    return payload


def validate_node_ids(path: Path, nodes: object, failures: list[str]) -> set[str]:
    if not isinstance(nodes, list):
        fail(f"canvas nodes must be a list: {path}", failures)
        return set()
    node_ids: set[str] = set()
    for index, node in enumerate(nodes):
        if not isinstance(node, dict):
            fail(f"canvas node {index} must be an object: {path}", failures)
            continue
        node_id = node.get("id")
        if not isinstance(node_id, str) or not node_id:
            fail(f"canvas node {index} missing string id: {path}", failures)
            continue
        if node_id in node_ids:
            fail(f"canvas duplicate node id {node_id}: {path}", failures)
            continue
        node_ids.add(node_id)
    return node_ids


def validate_edges(path: Path, edges: object, node_ids: set[str], failures: list[str]) -> None:
    if edges is None:
        return
    if not isinstance(edges, list):
        fail(f"canvas edges must be a list: {path}", failures)
        return
    for index, edge in enumerate(edges):
        if not isinstance(edge, dict):
            fail(f"canvas edge {index} must be an object: {path}", failures)
            continue
        edge_id = edge.get("id", index)
        for field_name in ("fromNode", "toNode"):
            node_id = edge.get(field_name)
            if not isinstance(node_id, str) or not node_id:
                fail(f"canvas edge {edge_id} missing {field_name}: {path}", failures)
                continue
            if node_id not in node_ids:
                fail(f"canvas edge {edge_id} references missing {field_name} {node_id}: {path}", failures)


def validate_canvas(path: Path, failures: list[str]) -> None:
    failure_count = len(failures)
    payload = load_json_file(path, failures)
    if payload is None:
        return
    node_ids = validate_node_ids(path, payload.get("nodes", []), failures)
    validate_edges(path, payload.get("edges", []), node_ids, failures)
    if len(failures) == failure_count:
        pass_message(f"canvas OK: {path}")


def yaml_module() -> object | None:
    try:
        import yaml  # type: ignore[import-not-found]
    except ImportError:
        return None
    return yaml


def validate_base_with_yaml(path: Path, text: str, failures: list[str], yaml: object) -> bool:
    try:
        payload = yaml.safe_load(text)  # type: ignore[attr-defined]
    except Exception as error:  # pragma: no cover - PyYAML may be absent locally.
        fail(f"base YAML invalid: {path}: {error}", failures)
        return False
    if not isinstance(payload, dict):
        fail(f"base root must be a mapping: {path}", failures)
        return False
    if not isinstance(payload.get("views"), list):
        fail(f"base views must be a list: {path}", failures)
        return False
    return True


def validate_base_without_yaml(path: Path, text: str, failures: list[str]) -> bool:
    if "\t" in text:
        fail(f"base contains tab indentation: {path}", failures)
        return False
    if not any(line.strip() == "views:" for line in text.splitlines()):
        fail(f"base missing top-level views section: {path}", failures)
        return False
    return True


def validate_base(path: Path, failures: list[str]) -> None:
    failure_count = len(failures)
    text = read_text(path)
    yaml = yaml_module()
    valid = validate_base_with_yaml(path, text, failures, yaml) if yaml else validate_base_without_yaml(path, text, failures)
    if valid and len(failures) == failure_count:
        pass_message(f"base OK: {path}")


def validate_artifact(path: Path, failures: list[str]) -> None:
    if path.suffix == ".canvas":
        validate_canvas(path, failures)
    elif path.suffix == ".base":
        validate_base(path, failures)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    root = Path(args.path)
    files = artifact_files(root)
    if not files:
        pass_message("no Obsidian artifact files found")
        return 0
    failures: list[str] = []
    for path in files:
        validate_artifact(path, failures)
    print(f"\nSummary: {len(failures)} fail")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
