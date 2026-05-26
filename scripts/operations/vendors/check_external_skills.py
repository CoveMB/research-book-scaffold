#!/usr/bin/env python3
"""Validate external skills and local plugin integration."""

from __future__ import annotations

import configparser
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

from git_utils import (
    changed_paths_from_status,
    git_stdout,
    github_repositories_match,
    has_git_checkout,
)
from project_config import (
    ARS_SKILLS,
    EXTERNAL_PLUGIN_SPECS,
    EXTERNAL_VENDOR_SPECS,
    ExternalPluginSpec,
    GITMODULES_PATH,
    LEGACY_RBS_PLUGIN,
    OBSIDIAN_SKILLS,
    OBSIDIAN_SKILL_WRAPPERS,
    PLUGIN_MARKETPLACE,
    RBS_PLUGIN_SPEC,
    RBS_SKILL_WRAPPERS,
    REPO_SCOPED_SKILL_NAMES,
    SKILLS_DIR,
    SUBAGENT_ORCHESTRATOR_SKILL_WRAPPERS,
    SUBAGENT_ORCHESTRATOR_PLUGIN_SPEC,
    change_to_project_root,
)
from script_utils import read_text

OLD_ARS_REPO = "CoveMB/" + "academic-research-skills"
FRONT_MATTER_PATTERN = re.compile(r"\A---\s*\n(?P<body>.*?)\n---\s*", flags=re.DOTALL)
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
    return path.as_posix() in gitmodule_urls_by_path()


def gitmodule_urls_by_path() -> dict[str, list[str]]:
    if not GITMODULES_PATH.exists():
        return {}
    parser = configparser.ConfigParser(interpolation=None)
    try:
        parser.read_string(read_text(GITMODULES_PATH))
    except configparser.Error:
        return {}
    urls_by_path: dict[str, list[str]] = {}
    for section in parser.sections():
        path = parser.get(section, "path", fallback="").strip()
        url = parser.get(section, "url", fallback="").strip()
        if path:
            urls_by_path.setdefault(path, [])
            if url:
                urls_by_path[path].append(url)
    return urls_by_path


def gitmodule_has_expected_github_repo(path: Path, expected_url: str) -> bool:
    return any(
        github_repositories_match(actual_url, expected_url)
        for actual_url in gitmodule_urls_by_path().get(path.as_posix(), [])
    )


def check_origin(origin: str, expected_url: str, label: str, failures: list[str]) -> None:
    check(
        github_repositories_match(origin, expected_url),
        f"{label} origin OK: {origin}",
        f"unexpected {label} origin: {origin}",
        failures,
    )


def check_submodule(path: Path, expected_url: str, label: str, failures: list[str]) -> None:
    check(GITMODULES_PATH.exists(), ".gitmodules exists", ".gitmodules missing", failures)
    check(is_submodule_path(path), f"{label} path registered in .gitmodules", f"{label} path missing from .gitmodules", failures)
    if GITMODULES_PATH.exists():
        check(
            gitmodule_has_expected_github_repo(path, expected_url),
            f"{label} URL registered in .gitmodules",
            f"{label} URL missing from .gitmodules",
            failures,
        )
    result = subprocess.run(["git", "submodule", "status", "--", str(path)], text=True, capture_output=True, check=False)
    status_message = submodule_status_message(label, path, result.stdout, result.returncode)
    status_ok = result.returncode == 0 and str(path) in result.stdout and not status_message
    if status_message:
        check(False, f"{label} submodule status OK", status_message, failures)
    else:
        check(
            status_ok,
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


def front_matter_fields(text: str) -> dict[str, str]:
    match = FRONT_MATTER_PATTERN.match(text)
    if not match:
        return {}
    fields: dict[str, str] = {}
    for line in match.group("body").splitlines():
        key, separator, value = line.partition(":")
        if separator and key.strip():
            fields[key.strip()] = value.strip()
    return fields


def has_front_matter(path: Path) -> bool:
    return bool(front_matter_fields(read_text(path)))


def repo_skill_directories(skills_dir: Path) -> set[str]:
    if not skills_dir.exists():
        return set()
    return {path.name for path in skills_dir.iterdir() if path.is_dir()}


def check_repo_skill_front_matter(skill_name: str, skill_file: Path, failures: list[str]) -> None:
    front_matter = front_matter_fields(read_text(skill_file))
    check(
        bool(front_matter),
        f"repo-scoped skill front matter OK: {skill_name}",
        f"repo-scoped skill missing front matter: {skill_name}",
        failures,
    )
    if not front_matter:
        return
    check(
        front_matter.get("name") == skill_name,
        f"repo-scoped skill name OK: {skill_name}",
        f"repo-scoped skill front matter name mismatch: {skill_name}",
        failures,
    )
    check(
        bool(front_matter.get("description")),
        f"repo-scoped skill description OK: {skill_name}",
        f"repo-scoped skill description missing: {skill_name}",
        failures,
    )


def check_repo_scoped_skill_inventory(failures: list[str]) -> None:
    expected_skill_names = set(REPO_SCOPED_SKILL_NAMES)
    actual_skill_names = repo_skill_directories(SKILLS_DIR)

    for skill_name in sorted(expected_skill_names - actual_skill_names):
        check(
            False,
            f"repo-scoped skill exists: {skill_name}",
            f"repo-scoped skill missing: {skill_name}",
            failures,
        )

    for skill_name in sorted(actual_skill_names - expected_skill_names):
        check(
            False,
            f"repo-scoped skill configured: {skill_name}",
            f"repo-scoped skill directory not configured: {skill_name}",
            failures,
        )

    for skill_name in sorted(expected_skill_names & actual_skill_names):
        skill_file = SKILLS_DIR / skill_name / "SKILL.md"
        check(True, f"repo-scoped skill exists: {skill_name}", f"repo-scoped skill missing: {skill_name}", failures)
        check(
            skill_file.exists(),
            f"repo-scoped skill file exists: {skill_name}",
            f"repo-scoped skill file missing: {skill_name}",
            failures,
        )
        if not skill_file.exists():
            continue
        check_repo_skill_front_matter(skill_name, skill_file, failures)

    check(
        len(REPO_SCOPED_SKILL_NAMES) == len(expected_skill_names),
        "repo-scoped skill manifest has unique names",
        "repo-scoped skill manifest has duplicate names",
        failures,
    )


def wrapper_name_for_skill(
    skill_name: str,
    wrapper_prefix: str | None = None,
    wrapper_names_by_skill: dict[str, str] | None = None,
) -> str | None:
    if wrapper_names_by_skill:
        return wrapper_names_by_skill.get(skill_name)
    if wrapper_prefix:
        return f"{wrapper_prefix}{skill_name}"
    return None


def check_wrapper_contract(
    label: str,
    wrapper: Path,
    upstream: Path,
    expected_name: str,
    required_fragments: tuple[str, ...],
    failures: list[str],
    safety_failure: str | None = None,
) -> None:
    check(wrapper.exists(), f"{label} wrapper exists: {wrapper}", f"{label} wrapper missing: {wrapper}", failures)
    if not wrapper.exists():
        return
    text = read_text(wrapper)
    front_matter = front_matter_fields(text)
    check(bool(front_matter), f"{label} wrapper front matter OK: {wrapper}", f"{label} wrapper missing front matter: {wrapper}", failures)
    check(
        front_matter.get("name") == expected_name,
        f"{label} wrapper name OK: {expected_name}",
        f"{label} wrapper name mismatch: {wrapper}",
        failures,
    )
    check(
        wrapper.parent.name == expected_name,
        f"{label} wrapper directory name OK: {expected_name}",
        f"{label} wrapper directory name mismatch: {wrapper}",
        failures,
    )
    check(
        bool(front_matter.get("description")),
        f"{label} wrapper description OK: {wrapper}",
        f"{label} wrapper description missing: {wrapper}",
        failures,
    )
    check(
        str(upstream) in text,
        f"{label} wrapper points upstream: {wrapper}",
        f"{label} wrapper does not point upstream: {wrapper}",
        failures,
    )
    missing_fragments = [fragment for fragment in required_fragments if fragment not in text]
    failure_message = safety_failure or f"{label} wrapper warning missing: {wrapper}"
    check(
        not missing_fragments,
        f"{label} wrapper warning OK: {wrapper}",
        failure_message,
        failures,
    )


def check_skill_wrappers(
    label: str,
    upstream_root: Path,
    skill_names: list[str],
    failures: list[str],
    required_fragments: tuple[str, ...],
    wrapper_prefix: str | None = None,
    wrapper_names_by_skill: dict[str, str] | None = None,
    safety_failure_label: str | None = None,
) -> None:
    for skill_name in skill_names:
        wrapper_name = wrapper_name_for_skill(skill_name, wrapper_prefix, wrapper_names_by_skill)
        if not wrapper_name:
            continue
        upstream = upstream_root / skill_name / "SKILL.md"
        wrapper = SKILLS_DIR / wrapper_name / "SKILL.md"
        safety_failure = f"{safety_failure_label}: {wrapper}" if safety_failure_label else None
        check_wrapper_contract(label, wrapper, upstream, wrapper_name, required_fragments, failures, safety_failure)


def check_ars(failures: list[str], warnings: list[str]) -> None:
    spec = VENDOR_SPECS_BY_KEY["ars"]
    check_submodule(spec.path, spec.default_repo, spec.label, failures)
    check(spec.path.exists(), f"{spec.label} vendor exists: {spec.path}", f"{spec.label} vendor missing: {spec.path}", failures)
    origin = git_origin(spec.path)
    if origin:
        check_origin(origin, spec.default_repo, "ARS", failures)
    else:
        warn("ARS origin unavailable", warnings)
    check_skills_exist(spec.label, spec.path, ARS_SKILLS, failures)
    check_all_vendor_skills_configured(spec.label, spec.path, ARS_SKILLS, failures)
    check_skill_wrappers(
        spec.label,
        spec.path,
        ARS_SKILLS,
        failures,
        ("local scaffold", "Do not execute vendored scripts automatically."),
        wrapper_prefix="ars-",
    )
    check((SKILLS_DIR / "ARS_INSTALLED.md").exists(), "ARS install report exists", "ARS install report missing", failures)


def check_skills_exist(
    label: str,
    vendor_root: Path,
    skill_names: list[str],
    failures: list[str],
) -> None:
    for skill_name in skill_names:
        upstream = vendor_root / skill_name / "SKILL.md"
        check(upstream.exists(), f"{label} upstream skill exists: {upstream}", f"{label} upstream skill missing: {upstream}", failures)


def vendor_skill_names(vendor_root: Path) -> set[str]:
    if not vendor_root.exists():
        return set()
    return {skill_file.parent.name for skill_file in vendor_root.glob("*/SKILL.md")}


def check_all_vendor_skills_configured(
    label: str,
    vendor_root: Path,
    configured_skill_names: list[str],
    failures: list[str],
) -> None:
    missing_from_config = sorted(vendor_skill_names(vendor_root) - set(configured_skill_names))
    check(
        not missing_from_config,
        f"{label} vendor skills all configured",
        f"{label} vendor skills missing from wrapper config: {', '.join(missing_from_config)}",
        failures,
    )


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
        check_origin(origin, spec.default_repo, "RBS", failures)
    else:
        warn("RBS origin unavailable", warnings)
    check_plugin_vendor(RBS_PLUGIN_SPEC, failures)
    check_all_vendor_skills_configured(
        "RBS",
        RBS_PLUGIN_SPEC.skills_root,
        list(RBS_PLUGIN_SPEC.skill_names),
        failures,
    )
    check_skill_wrappers(
        "RBS",
        RBS_PLUGIN_SPEC.skills_root,
        list(RBS_PLUGIN_SPEC.skill_names),
        failures,
        (
            "local scaffold rules win",
            "Do not invent citations or claims",
            "workflow guidance, not evidence",
        ),
        wrapper_names_by_skill=RBS_SKILL_WRAPPERS,
    )
    check(not LEGACY_RBS_PLUGIN.exists(), "legacy RBS plugin copy absent", f"legacy RBS plugin copy should be removed: {LEGACY_RBS_PLUGIN}", failures)
    check((SKILLS_DIR / "RBS_INSTALLED.md").exists(), "RBS install report exists", "RBS install report missing", failures)


def check_subagent_orchestrator(failures: list[str], warnings: list[str]) -> None:
    spec = VENDOR_SPECS_BY_KEY["subagent-orchestrator"]
    check_submodule(spec.path, spec.default_repo, spec.label, failures)
    check(spec.path.exists(), f"{spec.label} vendor exists: {spec.path}", f"{spec.label} vendor missing: {spec.path}", failures)
    origin = git_origin(spec.path)
    if origin:
        check_origin(origin, spec.default_repo, "Subagent Orchestrator", failures)
    else:
        warn("Subagent Orchestrator origin unavailable", warnings)
    check_plugin_vendor(SUBAGENT_ORCHESTRATOR_PLUGIN_SPEC, failures)
    check_all_vendor_skills_configured(
        "Subagent Orchestrator",
        SUBAGENT_ORCHESTRATOR_PLUGIN_SPEC.skills_root,
        list(SUBAGENT_ORCHESTRATOR_PLUGIN_SPEC.skill_names),
        failures,
    )
    check_skill_wrappers(
        "Subagent Orchestrator",
        SUBAGENT_ORCHESTRATOR_PLUGIN_SPEC.skills_root,
        list(SUBAGENT_ORCHESTRATOR_PLUGIN_SPEC.skill_names),
        failures,
        (
            "bounded orchestration materially helps",
            "not use automatically for every research task",
            "Subagent output is not evidence",
            "no global hooks, global agents, or global config",
            "project, citation, manuscript, audit, and vendor rules win",
        ),
        wrapper_names_by_skill=SUBAGENT_ORCHESTRATOR_SKILL_WRAPPERS,
        safety_failure_label="Subagent Orchestrator wrapper safety wording missing",
    )
    check(
        (SKILLS_DIR / "SUBAGENT_ORCHESTRATOR_INSTALLED.md").exists(),
        "Subagent Orchestrator install report exists",
        "Subagent Orchestrator install report missing",
        failures,
    )


def check_obsidian_skills(failures: list[str], warnings: list[str]) -> None:
    spec = VENDOR_SPECS_BY_KEY["obsidian-skills"]
    check_submodule(spec.path, spec.default_repo, spec.label, failures)
    check(spec.path.exists(), f"{spec.label} vendor exists: {spec.path}", f"{spec.label} vendor missing: {spec.path}", failures)
    origin = git_origin(spec.path)
    if origin:
        check_origin(origin, spec.default_repo, "Obsidian Skills", failures)
    else:
        warn("Obsidian Skills origin unavailable", warnings)
    check_skills_exist(spec.label, spec.path / "skills", OBSIDIAN_SKILLS, failures)
    check_all_vendor_skills_configured(spec.label, spec.path / "skills", OBSIDIAN_SKILLS, failures)
    check_skill_wrappers(
        spec.label,
        spec.path / "skills",
        OBSIDIAN_SKILLS,
        failures,
        ("AGENTS.md", "Do not execute vendored scripts automatically."),
        wrapper_names_by_skill=OBSIDIAN_SKILL_WRAPPERS,
    )
    check(
        (SKILLS_DIR / "OBSIDIAN_SKILLS_INSTALLED.md").exists(),
        "Obsidian Skills install report exists",
        "Obsidian Skills install report missing",
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
    check_repo_scoped_skill_inventory(failures)
    check_ars(failures, warnings)
    check_rbs(failures, warnings)
    check_subagent_orchestrator(failures, warnings)
    check_obsidian_skills(failures, warnings)
    check_marketplace(failures)
    check_old_repo_reference(failures)
    print(f"\nSummary: {len(failures)} fail, {len(warnings)} warn")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
