#!/usr/bin/env python3
"""Validate external skills and local plugin integration."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

from git_utils import changed_paths_from_status, git_stdout, has_git_checkout
from project_config import (
    ARS_SKILLS,
    ARS_VENDOR,
    DEFAULT_ARS_REPO,
    DEFAULT_RBS_REPO,
    GITMODULES_PATH,
    LEGACY_RBS_PLUGIN,
    MARKETPLACE_PLUGIN_PATH,
    PLUGIN_MARKETPLACE,
    RBS_MARKETPLACE_NAME,
    RBS_PLUGIN_JSON_NAME,
    RBS_SKILLS,
    RBS_VENDOR,
    SKILLS_DIR,
    change_to_project_root,
)
from script_utils import read_text

OLD_ARS_REPO = "CoveMB/" + "academic-research-skills"


def check(condition: bool, success: str, failure: str, failures: list[str]) -> None:
    if condition:
        print(f"PASS {success}")
    else:
        print(f"FAIL {failure}")
        failures.append(failure)


def warn(message: str, warnings: list[str]) -> None:
    print(f"WARN {message}")
    warnings.append(message)


def git_origin(path: Path) -> str:
    if not has_git_checkout(path):
        return ""
    return git_stdout(["git", "remote", "get-url", "origin"], cwd=path) or ""


def is_submodule_path(path: Path) -> bool:
    if not GITMODULES_PATH.exists():
        return False
    text = read_text(GITMODULES_PATH)
    return f"path = {path.as_posix()}" in text


def check_submodule(path: Path, expected_url: str, label: str, failures: list[str]) -> None:
    check(GITMODULES_PATH.exists(), ".gitmodules exists", ".gitmodules missing", failures)
    check(is_submodule_path(path), f"{label} path registered in .gitmodules", f"{label} path missing from .gitmodules", failures)
    if GITMODULES_PATH.exists():
        text = read_text(GITMODULES_PATH)
        check(expected_url in text, f"{label} URL registered in .gitmodules", f"{label} URL missing from .gitmodules", failures)
    result = subprocess.run(["git", "submodule", "status", "--", str(path)], text=True, capture_output=True, check=False)
    check(result.returncode == 0 and str(path) in result.stdout, f"{label} submodule status OK", f"{label} submodule status failed", failures)
    if path.exists():
        status_result = subprocess.run(["git", "status", "--short"], cwd=path, text=True, capture_output=True, check=False)
        if status_result.returncode == 0:
            message = submodule_dirty_message(label, status_result.stdout)
            check(not message, f"{label} submodule clean", message, failures)
        else:
            check(False, f"{label} submodule clean", f"{label} submodule status unavailable", failures)


def submodule_dirty_message(label: str, status_text: str) -> str:
    changed_paths = changed_paths_from_status(status_text)
    if not changed_paths:
        return ""
    return f"{label} submodule has uncommitted changes: {', '.join(changed_paths)}"


def has_front_matter(path: Path) -> bool:
    text = read_text(path)
    return bool(re.match(r"\A---\s*\n.*?\n---\s*", text, flags=re.DOTALL))


def check_ars(failures: list[str], warnings: list[str]) -> None:
    check_submodule(ARS_VENDOR, DEFAULT_ARS_REPO, "ARS", failures)
    check(ARS_VENDOR.exists(), f"ARS vendor exists: {ARS_VENDOR}", f"ARS vendor missing: {ARS_VENDOR}", failures)
    origin = git_origin(ARS_VENDOR)
    if origin:
        check("Imbad0202/academic-research-skills" in origin, f"ARS origin OK: {origin}", f"unexpected ARS origin: {origin}", failures)
    else:
        warn("ARS origin unavailable", warnings)
    check_skills_exist("ARS", ARS_VENDOR, ARS_SKILLS, failures, wrapper_prefix="ars-")


def check_skills_exist(
    label: str,
    vendor_root: Path,
    skill_names: list[str],
    failures: list[str],
    wrapper_prefix: str | None = None,
) -> None:
    for skill_name in skill_names:
        upstream = vendor_root / skill_name / "SKILL.md"
        check(upstream.exists(), f"{label} upstream skill exists: {upstream}", f"{label} upstream skill missing: {upstream}", failures)
        if not wrapper_prefix:
            continue
        wrapper = SKILLS_DIR / f"{wrapper_prefix}{skill_name}" / "SKILL.md"
        expected_name = f"{wrapper_prefix}{skill_name}"
        check(wrapper.exists(), f"{label} wrapper exists: {wrapper}", f"{label} wrapper missing: {wrapper}", failures)
        if wrapper.exists():
            text = read_text(wrapper)
            check(has_front_matter(wrapper), f"{label} wrapper front matter OK: {wrapper}", f"{label} wrapper missing front matter: {wrapper}", failures)
            check(f"name: {expected_name}" in text, f"{label} wrapper name OK: {expected_name}", f"{label} wrapper name missing: {wrapper}", failures)
            check(str(upstream) in text, f"{label} wrapper points upstream: {wrapper}", f"{label} wrapper does not point upstream: {wrapper}", failures)
            check("Claude" in text and "Do not execute vendored scripts" in text, f"{label} wrapper warning OK: {wrapper}", f"{label} wrapper warning missing: {wrapper}", failures)
    if label == "ARS":
        check((SKILLS_DIR / "ARS_INSTALLED.md").exists(), "ARS install report exists", "ARS install report missing", failures)


def check_rbs(failures: list[str], warnings: list[str]) -> None:
    check_submodule(RBS_VENDOR, DEFAULT_RBS_REPO, "RBS", failures)
    check(RBS_VENDOR.exists(), f"RBS vendor exists: {RBS_VENDOR}", f"RBS vendor missing: {RBS_VENDOR}", failures)
    origin = git_origin(RBS_VENDOR)
    if origin:
        check("CoveMB/research-book-skills" in origin, f"RBS origin OK: {origin}", f"unexpected RBS origin: {origin}", failures)
    else:
        warn("RBS origin unavailable", warnings)
    check((RBS_VENDOR / ".codex-plugin" / "plugin.json").exists(), "RBS vendor plugin.json exists", "RBS vendor plugin.json missing", failures)
    if (RBS_VENDOR / ".codex-plugin" / "plugin.json").exists():
        try:
            plugin_payload = json.loads(read_text(RBS_VENDOR / ".codex-plugin" / "plugin.json"))
        except json.JSONDecodeError as error:
            failures.append(f"RBS plugin.json invalid JSON: {error}")
            print(f"FAIL RBS plugin.json invalid JSON: {error}")
        else:
            check(
                plugin_payload.get("name") == RBS_PLUGIN_JSON_NAME,
                "RBS plugin name OK",
                f"RBS plugin name unexpected: {plugin_payload.get('name')}",
                failures,
            )
    check((RBS_VENDOR / "skills").exists(), "RBS vendor skills folder exists", "RBS vendor skills folder missing", failures)
    check_skills_exist("RBS", RBS_VENDOR / "skills", RBS_SKILLS, failures)
    check(not LEGACY_RBS_PLUGIN.exists(), "legacy RBS plugin copy absent", f"legacy RBS plugin copy should be removed: {LEGACY_RBS_PLUGIN}", failures)
    check((SKILLS_DIR / "RBS_INSTALLED.md").exists(), "RBS install report exists", "RBS install report missing", failures)


def check_marketplace(failures: list[str]) -> None:
    check(PLUGIN_MARKETPLACE.exists(), f"marketplace exists: {PLUGIN_MARKETPLACE}", f"marketplace missing: {PLUGIN_MARKETPLACE}", failures)
    if not PLUGIN_MARKETPLACE.exists():
        return
    try:
        payload = json.loads(read_text(PLUGIN_MARKETPLACE))
    except json.JSONDecodeError as error:
        failures.append(f"marketplace invalid JSON: {error}")
        print(f"FAIL marketplace invalid JSON: {error}")
        return
    plugins = payload.get("plugins", [])
    entry = next((plugin for plugin in plugins if plugin.get("name") == RBS_MARKETPLACE_NAME), None)
    check(entry is not None, f"marketplace has {RBS_MARKETPLACE_NAME} entry", f"marketplace missing {RBS_MARKETPLACE_NAME} entry", failures)
    if entry:
        source = entry.get("source", {})
        check(source.get("path") == MARKETPLACE_PLUGIN_PATH, "marketplace path OK", f"marketplace path unexpected: {source.get('path')}", failures)


def check_old_repo_reference(failures: list[str], warnings: list[str]) -> None:
    ignored_parts = {"__pycache__", ".git"}
    roots = [Path("README.md"), Path("AGENTS.md"), Path("docs"), Path("scripts"), Path("config"), Path(".agents")]
    matches: list[Path] = []
    for root in roots:
        if root.is_file():
            files = [root]
        elif root.exists():
            files = [path for path in root.rglob("*") if path.is_file() and not (ignored_parts & set(path.parts))]
        else:
            files = []
        for path in files:
            if OLD_ARS_REPO in read_text(path):
                matches.append(path)
    if matches:
        for path in matches:
            print(f"FAIL old ARS repo reference remains: {path}")
        failures.append("old ARS repo reference remains")
    else:
        print("PASS no old ARS repo references in local docs/scripts")


def main() -> int:
    change_to_project_root()
    failures: list[str] = []
    warnings: list[str] = []
    check_ars(failures, warnings)
    check_rbs(failures, warnings)
    check_marketplace(failures)
    check_old_repo_reference(failures, warnings)
    print(f"\nSummary: {len(failures)} fail, {len(warnings)} warn")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
