#!/usr/bin/env python3
"""Validate external skills and local plugin integration."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

_SCRIPTS_ROOT = next(parent for parent in Path(__file__).resolve().parents if parent.name == "scripts")
_LIB_DIR = _SCRIPTS_ROOT / "lib"
if str(_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(_LIB_DIR))

from import_paths import configure_script_paths

configure_script_paths(__file__)

from git_utils import changed_paths_from_status, git_stdout, has_git_checkout
from project_config import (
    ARS_SKILLS,
    EXTERNAL_PLUGIN_SPECS,
    EXTERNAL_VENDOR_SPECS,
    ExternalPluginSpec,
    GITMODULES_PATH,
    LEGACY_RBS_PLUGIN,
    PLUGIN_MARKETPLACE,
    RBS_PLUGIN_SPEC,
    SKILLS_DIR,
    SUBAGENT_ORCHESTRATOR_PLUGIN_SPEC,
    change_to_project_root,
)
from script_utils import read_text

OLD_ARS_REPO = "CoveMB/" + "academic-research-skills"
VENDOR_SPECS_BY_KEY = {spec.key: spec for spec in EXTERNAL_VENDOR_SPECS}
MARKETPLACE_PATHS_BY_NAME = {spec.marketplace_name: spec.plugin_path for spec in EXTERNAL_PLUGIN_SPECS}


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
    status_message = submodule_status_message(label, path, result.stdout, result.returncode)
    status_ok = result.returncode == 0 and str(path) in result.stdout and not status_message
    working_tree_checkout_ok = is_submodule_path(path) and has_git_checkout(path)
    if status_message:
        check(False, f"{label} submodule status OK", status_message, failures)
    else:
        check(
            status_ok or working_tree_checkout_ok,
            f"{label} submodule status OK",
            f"{label} submodule status failed",
            failures,
        )
    if path.exists():
        status_result = subprocess.run(["git", "status", "--short"], cwd=path, text=True, capture_output=True, check=False)
        if status_result.returncode == 0:
            message = submodule_dirty_message(label, status_result.stdout)
            check(not message, f"{label} submodule clean", message, failures)
        else:
            check(False, f"{label} submodule clean", f"{label} submodule status unavailable", failures)


def submodule_status_message(label: str, path: Path, status_text: str, returncode: int) -> str:
    if returncode != 0:
        return ""
    for raw_line in status_text.splitlines():
        line = raw_line.strip()
        if str(path) not in line:
            continue
        marker = line[0]
        if marker == "+":
            return f"{label} submodule pointer differs from parent index: {path}"
        if marker == "-":
            return f"{label} submodule is not initialized: {path}"
        if marker == "U":
            return f"{label} submodule has merge conflicts: {path}"
        return ""
    return ""


def submodule_dirty_message(label: str, status_text: str) -> str:
    changed_paths = changed_paths_from_status(status_text)
    if not changed_paths:
        return ""
    return f"{label} submodule has uncommitted changes: {', '.join(changed_paths)}"


def has_front_matter(path: Path) -> bool:
    text = read_text(path)
    return bool(re.match(r"\A---\s*\n.*?\n---\s*", text, flags=re.DOTALL))


def check_ars(failures: list[str], warnings: list[str]) -> None:
    spec = VENDOR_SPECS_BY_KEY["ars"]
    check_submodule(spec.path, spec.default_repo, spec.label, failures)
    check(spec.path.exists(), f"{spec.label} vendor exists: {spec.path}", f"{spec.label} vendor missing: {spec.path}", failures)
    origin = git_origin(spec.path)
    if origin:
        check("Imbad0202/academic-research-skills" in origin, f"ARS origin OK: {origin}", f"unexpected ARS origin: {origin}", failures)
    else:
        warn("ARS origin unavailable", warnings)
    check_skills_exist(spec.label, spec.path, ARS_SKILLS, failures, wrapper_prefix="ars-")


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


def check_plugin_json_name(plugin_json: Path, expected_name: str, label: str, failures: list[str]) -> None:
    check(plugin_json.exists(), f"{label} plugin.json exists", f"{label} plugin.json missing", failures)
    if not plugin_json.exists():
        return
    try:
        plugin_payload = json.loads(read_text(plugin_json))
    except json.JSONDecodeError as error:
        failures.append(f"{label} plugin.json invalid JSON: {error}")
        print(f"FAIL {label} plugin.json invalid JSON: {error}")
        return
    check(
        plugin_payload.get("name") == expected_name,
        f"{label} plugin name OK",
        f"{label} plugin name unexpected: {plugin_payload.get('name')}",
        failures,
    )


def check_plugin_vendor(plugin_spec: ExternalPluginSpec, failures: list[str]) -> None:
    check_plugin_json_name(
        plugin_spec.plugin_root / ".codex-plugin" / "plugin.json",
        plugin_spec.plugin_json_name,
        plugin_spec.label,
        failures,
    )
    check(
        plugin_spec.skills_root.exists(),
        f"{plugin_spec.label} vendor skills folder exists",
        f"{plugin_spec.label} vendor skills folder missing",
        failures,
    )
    check_skills_exist(plugin_spec.label, plugin_spec.skills_root, list(plugin_spec.skill_names), failures)


def check_rbs(failures: list[str], warnings: list[str]) -> None:
    spec = VENDOR_SPECS_BY_KEY["rbs"]
    check_submodule(spec.path, spec.default_repo, spec.label, failures)
    check(spec.path.exists(), f"{spec.label} vendor exists: {spec.path}", f"{spec.label} vendor missing: {spec.path}", failures)
    origin = git_origin(spec.path)
    if origin:
        check("CoveMB/research-book-skills" in origin, f"RBS origin OK: {origin}", f"unexpected RBS origin: {origin}", failures)
    else:
        warn("RBS origin unavailable", warnings)
    check_plugin_vendor(RBS_PLUGIN_SPEC, failures)
    check(not LEGACY_RBS_PLUGIN.exists(), "legacy RBS plugin copy absent", f"legacy RBS plugin copy should be removed: {LEGACY_RBS_PLUGIN}", failures)
    check((SKILLS_DIR / "RBS_INSTALLED.md").exists(), "RBS install report exists", "RBS install report missing", failures)


def check_subagent_orchestrator(failures: list[str], warnings: list[str]) -> None:
    spec = VENDOR_SPECS_BY_KEY["subagent-orchestrator"]
    check_submodule(spec.path, spec.default_repo, spec.label, failures)
    check(spec.path.exists(), f"{spec.label} vendor exists: {spec.path}", f"{spec.label} vendor missing: {spec.path}", failures)
    origin = git_origin(spec.path)
    if origin:
        check(
            "CoveMB/subagent-orchestration-plugin" in origin,
            f"Subagent Orchestrator origin OK: {origin}",
            f"unexpected Subagent Orchestrator origin: {origin}",
            failures,
        )
    else:
        warn("Subagent Orchestrator origin unavailable", warnings)
    check_plugin_vendor(SUBAGENT_ORCHESTRATOR_PLUGIN_SPEC, failures)
    check(
        (SKILLS_DIR / "SUBAGENT_ORCHESTRATOR_INSTALLED.md").exists(),
        "Subagent Orchestrator install report exists",
        "Subagent Orchestrator install report missing",
        failures,
    )


def check_marketplace_entry(
    plugins: list[object],
    plugin_name: str,
    expected_path: str,
    failures: list[str],
) -> None:
    entry = next(
        (plugin for plugin in plugins if isinstance(plugin, dict) and plugin.get("name") == plugin_name),
        None,
    )
    check(entry is not None, f"marketplace has {plugin_name} entry", f"marketplace missing {plugin_name} entry", failures)
    if not entry:
        return
    source = entry.get("source", {})
    if not isinstance(source, dict):
        check(False, f"marketplace source OK for {plugin_name}", f"marketplace source invalid for {plugin_name}", failures)
        return
    check(
        source.get("path") == expected_path,
        f"marketplace path OK for {plugin_name}",
        f"marketplace path unexpected for {plugin_name}: {source.get('path')}",
        failures,
    )


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
    if not isinstance(plugins, list):
        check(False, "marketplace plugin list OK", "marketplace plugins must be a list", failures)
        return
    for plugin_name, expected_path in MARKETPLACE_PATHS_BY_NAME.items():
        check_marketplace_entry(plugins, plugin_name, expected_path, failures)


def check_old_repo_reference(failures: list[str]) -> None:
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
    check_subagent_orchestrator(failures, warnings)
    check_marketplace(failures)
    check_old_repo_reference(failures)
    print(f"\nSummary: {len(failures)} fail, {len(warnings)} warn")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
