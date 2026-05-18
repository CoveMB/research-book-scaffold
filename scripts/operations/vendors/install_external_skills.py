#!/usr/bin/env python3
"""Vendor external research skills and expose safe local integrations."""

from __future__ import annotations

import argparse
import json
import sys
import shutil
from pathlib import Path

_SCRIPTS_ROOT = next(parent for parent in Path(__file__).resolve().parents if parent.name == "scripts")
_LIB_DIR = _SCRIPTS_ROOT / "lib"
if str(_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(_LIB_DIR))

from import_paths import configure_script_paths

configure_script_paths(__file__)

from git_utils import git_stdout, has_git_checkout
from project_config import (
    ARS_SKILLS,
    ARS_VENDOR,
    DEFAULT_ARS_REPO,
    DEFAULT_RBS_REPO,
    DEFAULT_SUBAGENT_ORCHESTRATOR_REPO,
    ExternalPluginSpec,
    GITMODULES_PATH,
    PLUGIN_MARKETPLACE,
    PROJECT_ROOT,
    RBS_PLUGIN_SPEC,
    RBS_VENDOR,
    SKILLS_DIR,
    SUBAGENT_ORCHESTRATOR_PLUGIN_ROOT,
    SUBAGENT_ORCHESTRATOR_PLUGIN_SPEC,
    SUBAGENT_ORCHESTRATOR_VENDOR,
    change_to_project_root,
)
from script_utils import StatusReport, run_command, read_text, write_text_if_changed


Report = StatusReport


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--yes", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--skip-ars", action="store_true")
    parser.add_argument("--skip-rbs", action="store_true")
    parser.add_argument("--skip-subagent-orchestrator", action="store_true")
    parser.add_argument("--ars-ref")
    parser.add_argument("--rbs-ref")
    parser.add_argument("--subagent-orchestrator-ref")
    parser.add_argument("--no-rbs-plugin", action="store_true")
    parser.add_argument("--no-subagent-orchestrator-plugin", action="store_true")
    update_group = parser.add_mutually_exclusive_group()
    update_group.add_argument("--update", action="store_true", help="Update configured vendors from their remotes.")
    update_group.add_argument("--no-update", action="store_true", help="Use pinned or current vendor checkouts.")
    parser.add_argument(
        "--preserve-vendor-checkouts",
        action="store_true",
        help="Refresh wrappers and reports without changing configured submodule checkouts.",
    )
    return parser.parse_args(argv)


def run(command: list[str], report: Report, dry_run: bool, action: str, cwd: Path | None = None) -> bool:
    return run_command(command, report, dry_run, action, cwd=cwd)


def git_available(report: Report) -> bool:
    if shutil.which("git"):
        return True
    report.add("failed", "git missing; cannot vendor external repositories")
    return False


def should_update(args: argparse.Namespace) -> bool:
    return bool(args.update)


def checkout_ref(path: Path, ref: str | None, report: Report, dry_run: bool, label: str) -> None:
    if ref:
        run(["git", "checkout", ref], report, dry_run, f"checked out {label} ref {ref}", cwd=path)


def is_configured_submodule(path: Path) -> bool:
    if not GITMODULES_PATH.exists():
        return False
    text = read_text(GITMODULES_PATH)
    return f"path = {path.as_posix()}" in text


def sync_or_init_submodule(path: Path, ref: str | None, args: argparse.Namespace, report: Report, label: str) -> None:
    if not git_available(report):
        return
    run(["git", "submodule", "sync", "--", str(path)], report, args.dry_run, f"synced {label} submodule")
    run(["git", "submodule", "update", "--init", "--recursive", "--", str(path)], report, args.dry_run, f"initialized {label} submodule")
    if should_update(args):
        run(["git", "submodule", "update", "--remote", "--merge", "--", str(path)], report, args.dry_run, f"updated {label} submodule from remote")
    else:
        report.add("skipped", f"{label} remote submodule update skipped; using pinned commit")
    checkout_ref(path, ref, report, args.dry_run, label)


def clone_or_update(path: Path, ref: str | None, args: argparse.Namespace, report: Report, label: str) -> None:
    if not git_available(report):
        return
    if is_configured_submodule(path):
        report.add("already_present", f"{label} configured as Git submodule: {path}")
        if args.preserve_vendor_checkouts:
            report.add("skipped", f"{label} submodule checkout preserved")
            return
        sync_or_init_submodule(path, ref, args, report, label)
        return
    report.add("failed", f"{label} vendor path is not configured as a Git submodule: {path}")


def commit_hash(path: Path) -> str:
    if not has_git_checkout(path):
        return "unknown"
    return git_stdout(["git", "rev-parse", "HEAD"], cwd=path) or "unknown"


def write_if_changed(path: Path, text: str, args: argparse.Namespace, report: Report, label: str) -> bool:
    return write_text_if_changed(path, text, report, label, dry_run=args.dry_run, force=args.force)


def ars_skill_path(skill_name: str) -> Path:
    return ARS_VENDOR / skill_name / "SKILL.md"


def validate_ars(report: Report) -> bool:
    ok = True
    for skill_name in ARS_SKILLS:
        path = ars_skill_path(skill_name)
        if path.exists():
            report.add("already_present", f"ARS skill found: {path}")
        else:
            report.add("failed", f"ARS skill missing: {path}")
            ok = False
    return ok


def ars_wrapper_text(skill_name: str) -> str:
    wrapper_name = f"ars-{skill_name}"
    upstream_path = ars_skill_path(skill_name).as_posix()
    return f"""---
name: {wrapper_name}
description: Use this wrapper to consult the vendored Academic Research Skills `{skill_name}` workflow after reading and validating the upstream instructions.
---

# {wrapper_name}

## Purpose

Use the vendored `{skill_name}` workflow as external guidance for academic research discipline.

## Upstream source

Read this file before using the wrapper:

```text
{upstream_path}
```

## Rules

- The upstream repository is Claude Code oriented.
- Do not assume Claude-specific slash commands, hooks, subagents, plugin commands, or API-key assumptions work here.
- Do not execute vendored scripts automatically.
- Do not edit upstream files under `vendor/academic-research-skills/`.
- Verify citations, claims, page numbers, and source metadata independently.
- Keep local scaffold skills as the primary safety layer.

## Output

Summarize which upstream guidance was used, what evidence was checked, and what uncertainty remains.
"""


def create_ars_wrappers(args: argparse.Namespace, report: Report) -> list[Path]:
    wrapper_paths: list[Path] = []
    for skill_name in ARS_SKILLS:
        wrapper_dir = SKILLS_DIR / f"ars-{skill_name}"
        wrapper_path = wrapper_dir / "SKILL.md"
        if write_if_changed(wrapper_path, ars_wrapper_text(skill_name), args, report, f"ARS wrapper {skill_name}"):
            wrapper_paths.append(wrapper_path)
    return wrapper_paths


def plugin_component_paths(plugin_spec: ExternalPluginSpec) -> list[Path]:
    return [
        plugin_spec.plugin_root / ".codex-plugin" / "plugin.json",
        plugin_spec.skills_root,
        *(plugin_spec.skills_root / skill_name / "SKILL.md" for skill_name in plugin_spec.skill_names),
    ]


def validate_plugin_components(plugin_spec: ExternalPluginSpec, report: Report) -> bool:
    ok = True
    for path in plugin_component_paths(plugin_spec):
        if path.exists():
            report.add("already_present", f"{plugin_spec.label} component found: {path}")
        elif path.name == "SKILL.md":
            report.add("failed", f"{plugin_spec.label} skill missing: {path}")
            ok = False
        else:
            report.add("failed", f"{plugin_spec.label} component missing: {path}")
            ok = False
    return ok


def validate_rbs(report: Report) -> bool:
    return validate_plugin_components(RBS_PLUGIN_SPEC, report)


def validate_subagent_orchestrator(report: Report) -> bool:
    return validate_plugin_components(SUBAGENT_ORCHESTRATOR_PLUGIN_SPEC, report)


def marketplace_entry(name: str, plugin_path: str) -> dict[str, object]:
    return {
        "name": name,
        "source": {"source": "local", "path": plugin_path},
        "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
        "category": "Productivity",
    }


def configured_marketplace_entries(
    include_rbs: bool,
    include_subagent_orchestrator: bool,
) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    if include_rbs:
        entries.append(marketplace_entry(RBS_PLUGIN_SPEC.marketplace_name, RBS_PLUGIN_SPEC.plugin_path))
    if include_subagent_orchestrator:
        entries.append(
            marketplace_entry(
                SUBAGENT_ORCHESTRATOR_PLUGIN_SPEC.marketplace_name,
                SUBAGENT_ORCHESTRATOR_PLUGIN_SPEC.plugin_path,
            )
        )
    return entries


def plugin_name(plugin: object) -> str | None:
    if not isinstance(plugin, dict):
        return None
    name = plugin.get("name")
    return name if isinstance(name, str) else None


def existing_marketplace_plugins(path: Path) -> list[object]:
    if not path.exists():
        return []
    try:
        payload = json.loads(read_text(path))
    except json.JSONDecodeError:
        return []
    plugins = payload.get("plugins", [])
    return plugins if isinstance(plugins, list) else []


def merge_marketplace_entries(
    existing_plugins: list[object],
    desired_plugins: list[dict[str, object]],
    remove_plugin_names: set[str],
) -> list[object]:
    desired_names = {plugin["name"] for plugin in desired_plugins if isinstance(plugin.get("name"), str)}
    merged = [
        plugin
        for plugin in existing_plugins
        if plugin_name(plugin) not in desired_names and plugin_name(plugin) not in remove_plugin_names
    ]
    merged.extend(desired_plugins)
    return merged


def marketplace_text(
    include_rbs: bool = True,
    include_subagent_orchestrator: bool = True,
    existing_plugins: list[object] | None = None,
    remove_plugin_names: set[str] | None = None,
) -> str:
    desired_plugins = configured_marketplace_entries(include_rbs, include_subagent_orchestrator)
    plugins = merge_marketplace_entries(existing_plugins or [], desired_plugins, remove_plugin_names or set())
    payload = {
        "name": "local-research-workflow-plugins",
        "interface": {"displayName": "Local Research Workflow Plugins"},
        "plugins": plugins,
    }
    return json.dumps(payload, indent=2) + "\n"


def write_marketplace(
    args: argparse.Namespace,
    report: Report,
    include_rbs: bool,
    include_subagent_orchestrator: bool,
    remove_plugin_names: set[str] | None = None,
) -> bool:
    return write_if_changed(
        PLUGIN_MARKETPLACE,
        marketplace_text(
            include_rbs,
            include_subagent_orchestrator,
            existing_marketplace_plugins(PLUGIN_MARKETPLACE),
            remove_plugin_names or set(),
        ),
        args,
        report,
        "plugin marketplace",
    )


def report_text(
    title: str,
    repo_url: str,
    ref: str | None,
    commit: str,
    vendor_path: Path,
    wrapper_paths: list[Path],
    plugin_path: Path | None,
    marketplace_path: Path | None,
    license_note: str,
    warnings: list[str],
) -> str:
    lines = [
        f"# {title}",
        "",
        f"- Repo: `{repo_url}`",
        f"- Ref: `{ref or 'default branch'}`",
        f"- Commit: `{commit}`",
        f"- Vendor path: `{vendor_path.as_posix()}`",
        f"- License note: {license_note}",
        "",
        "## Wrappers",
    ]
    if wrapper_paths:
        lines.extend(f"- `{path.as_posix()}`" for path in wrapper_paths)
    else:
        lines.append("- none")
    if plugin_path:
        lines.extend(["", "## Plugin", f"- Plugin source path: `{plugin_path.as_posix()}`"])
    if marketplace_path:
        lines.append(f"- Marketplace path: `{marketplace_path.as_posix()}`")
    lines.extend(["", "## Warnings"])
    if warnings:
        lines.extend(f"- {warning}" for warning in warnings)
    else:
        lines.append("- Review upstream files before use.")
    lines.append("")
    return "\n".join(lines)


def write_ars_install_report(args: argparse.Namespace, report: Report, ars_wrappers: list[Path]) -> None:
    ars_report = report_text(
        "Installed Academic Research Skills",
        DEFAULT_ARS_REPO,
        args.ars_ref,
        commit_hash(ARS_VENDOR),
        ARS_VENDOR,
        ars_wrappers,
        None,
        None,
        "CC-BY-NC-4.0. Confirm license compatibility before commercial use.",
        ["Upstream is Claude Code oriented.", "Do not run Claude-specific commands here."],
    )
    write_if_changed(SKILLS_DIR / "ARS_INSTALLED.md", ars_report, args, report, "ARS install report")


def write_rbs_install_report(args: argparse.Namespace, report: Report, plugin_exposed: bool, marketplace_written: bool) -> None:
    rbs_report = report_text(
        "Installed Research Book Skills",
        DEFAULT_RBS_REPO,
        args.rbs_ref,
        commit_hash(RBS_VENDOR),
        RBS_VENDOR,
        [],
        RBS_VENDOR if plugin_exposed else None,
        PLUGIN_MARKETPLACE if marketplace_written else None,
        "MIT.",
        ["Do not run vendored scripts automatically.", "Use the plugin as extended capability."],
    )
    write_if_changed(SKILLS_DIR / "RBS_INSTALLED.md", rbs_report, args, report, "RBS install report")


def write_subagent_orchestrator_install_report(
    args: argparse.Namespace,
    report: Report,
    plugin_exposed: bool,
    marketplace_written: bool,
) -> None:
    install_report = report_text(
        "Installed Subagent Orchestrator",
        DEFAULT_SUBAGENT_ORCHESTRATOR_REPO,
        args.subagent_orchestrator_ref,
        commit_hash(SUBAGENT_ORCHESTRATOR_VENDOR),
        SUBAGENT_ORCHESTRATOR_VENDOR,
        [],
        SUBAGENT_ORCHESTRATOR_PLUGIN_ROOT if plugin_exposed else None,
        PLUGIN_MARKETPLACE if marketplace_written else None,
        "MIT.",
        [
            "Execution-shape helper only; not evidence.",
            "Project rules, citation rules, manuscript rules, audit rules, and vendor rules win.",
            "Installer runs only after project-scoped boundary checks.",
        ],
    )
    write_if_changed(
        SKILLS_DIR / "SUBAGENT_ORCHESTRATOR_INSTALLED.md",
        install_report,
        args,
        report,
        "Subagent Orchestrator install report",
    )


def subagent_orchestrator_install_command() -> list[str]:
    return [
        "bash",
        (SUBAGENT_ORCHESTRATOR_VENDOR / "install.sh").as_posix(),
        "--scope",
        "project",
        "--repo-root",
        PROJECT_ROOT.as_posix(),
        "--from-vendor",
        (PROJECT_ROOT / SUBAGENT_ORCHESTRATOR_VENDOR).as_posix(),
        "--available-only",
        "--link-skills",
        "--with-repo-marketplace",
    ]


def status_summary(status_text: str) -> str:
    return ", ".join(line.strip() for line in status_text.splitlines() if line.strip())


def subagent_orchestrator_installer_boundary(report: Report) -> bool:
    install_script = SUBAGENT_ORCHESTRATOR_VENDOR / "install.sh"
    if not install_script.exists():
        report.add("failed", f"Subagent Orchestrator installer missing: {install_script}")
        return False
    if not is_configured_submodule(SUBAGENT_ORCHESTRATOR_VENDOR):
        report.add("failed", f"Subagent Orchestrator vendor is not a configured submodule: {SUBAGENT_ORCHESTRATOR_VENDOR}")
        return False
    if not has_git_checkout(SUBAGENT_ORCHESTRATOR_VENDOR):
        report.add("failed", f"Subagent Orchestrator vendor is not a Git checkout: {SUBAGENT_ORCHESTRATOR_VENDOR}")
        return False
    origin = git_stdout(["git", "remote", "get-url", "origin"], cwd=SUBAGENT_ORCHESTRATOR_VENDOR) or ""
    if "CoveMB/subagent-orchestration-plugin" not in origin:
        report.add("failed", f"Subagent Orchestrator origin unexpected: {origin or 'unknown'}")
        return False
    status = git_stdout(["git", "status", "--short"], cwd=SUBAGENT_ORCHESTRATOR_VENDOR) or ""
    if status:
        report.add("failed", f"Subagent Orchestrator vendor has uncommitted changes: {status_summary(status)}")
        return False
    return True


def install_subagent_orchestrator(args: argparse.Namespace, report: Report) -> bool:
    if not subagent_orchestrator_installer_boundary(report):
        return False
    return run(
        subagent_orchestrator_install_command(),
        report,
        args.dry_run,
        "installed Subagent Orchestrator project-scoped integration",
    )


def install_external(args: argparse.Namespace, report: Report) -> None:
    ars_wrappers: list[Path] = []
    plugin_exposed = False
    subagent_plugin_exposed = False
    marketplace_written = False
    remove_plugin_names: set[str] = set()
    ars_ready = False
    rbs_ready = False
    subagent_ready = False

    if args.skip_ars:
        report.add("skipped", "ARS skipped")
    else:
        clone_or_update(ARS_VENDOR, args.ars_ref, args, report, "ARS")
        if ARS_VENDOR.exists() and validate_ars(report):
            ars_wrappers = create_ars_wrappers(args, report)
            ars_ready = bool(ars_wrappers)

    if args.skip_rbs:
        report.add("skipped", "RBS skipped")
    else:
        clone_or_update(RBS_VENDOR, args.rbs_ref, args, report, "RBS")
        if RBS_VENDOR.exists() and validate_rbs(report):
            rbs_ready = True
            if args.no_rbs_plugin:
                report.add("skipped", "RBS marketplace exposure skipped by --no-rbs-plugin")
                remove_plugin_names.add(RBS_PLUGIN_SPEC.marketplace_name)
            else:
                plugin_exposed = True

    if args.skip_subagent_orchestrator:
        report.add("skipped", "Subagent Orchestrator skipped")
    else:
        clone_or_update(
            SUBAGENT_ORCHESTRATOR_VENDOR,
            args.subagent_orchestrator_ref,
            args,
            report,
            "Subagent Orchestrator",
        )
        if SUBAGENT_ORCHESTRATOR_VENDOR.exists() and validate_subagent_orchestrator(report):
            if args.no_subagent_orchestrator_plugin:
                subagent_ready = True
                report.add(
                    "skipped",
                    "Subagent Orchestrator marketplace exposure skipped by --no-subagent-orchestrator-plugin",
                )
                remove_plugin_names.add(SUBAGENT_ORCHESTRATOR_PLUGIN_SPEC.marketplace_name)
            else:
                subagent_plugin_exposed = install_subagent_orchestrator(args, report)
                subagent_ready = subagent_plugin_exposed

    if plugin_exposed or subagent_plugin_exposed or remove_plugin_names:
        marketplace_written = write_marketplace(
            args,
            report,
            plugin_exposed,
            subagent_plugin_exposed,
            remove_plugin_names,
        )

    if ars_ready:
        write_ars_install_report(args, report, ars_wrappers)
    if rbs_ready:
        write_rbs_install_report(args, report, plugin_exposed, marketplace_written)
    if subagent_ready:
        write_subagent_orchestrator_install_report(args, report, subagent_plugin_exposed, marketplace_written)

    report.add("warnings", "External repositories are untrusted until inspected")
    if subagent_plugin_exposed and args.dry_run:
        report.add("warnings", "Dry run only; Subagent Orchestrator installer was not executed")
    elif subagent_plugin_exposed:
        report.add("warnings", "Only the bounded Subagent Orchestrator project installer was executed")
    else:
        report.add("warnings", "Vendored scripts were not executed")


def main(argv: list[str]) -> int:
    change_to_project_root()
    args = parse_args(argv)
    report = Report()
    if args.dry_run:
        print("Dry run: no external repositories, wrappers, plugins, or reports will be changed.\n")
    install_external(args, report)
    return 1 if report.failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
