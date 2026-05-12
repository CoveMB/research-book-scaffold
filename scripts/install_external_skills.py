#!/usr/bin/env python3
"""Vendor external research skills and expose safe local integrations."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import shutil
from pathlib import Path

from project_config import (
    ARS_SKILLS,
    ARS_VENDOR,
    DEFAULT_ARS_REPO,
    DEFAULT_RBS_REPO,
    GITMODULES_PATH,
    MARKETPLACE_PLUGIN_PATH,
    PLUGIN_MARKETPLACE,
    RBS_MARKETPLACE_NAME,
    RBS_VENDOR,
    SKILLS_DIR,
    change_to_project_root,
)
from script_utils import StatusReport, run_command, read_text


class Report(StatusReport):
    pass


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--yes", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--skip-ars", action="store_true")
    parser.add_argument("--skip-rbs", action="store_true")
    parser.add_argument("--ars-repo", default=DEFAULT_ARS_REPO)
    parser.add_argument("--ars-ref")
    parser.add_argument("--rbs-repo", default=DEFAULT_RBS_REPO)
    parser.add_argument("--rbs-ref")
    parser.add_argument("--no-rbs-plugin", action="store_true")
    parser.add_argument("--update-mode", choices=["pinned", "remote"], default="pinned")
    parser.add_argument("--update", action="store_true")
    parser.add_argument("--no-update", action="store_true")
    return parser.parse_args(argv)


def run(command: list[str], report: Report, dry_run: bool, action: str, cwd: Path | None = None) -> bool:
    return run_command(command, report, dry_run, action, cwd=cwd)


def git_available(report: Report) -> bool:
    if shutil.which("git"):
        return True
    report.add("failed", "git missing; cannot vendor external repositories")
    return False


def should_update(args: argparse.Namespace) -> bool:
    return update_mode(args) == "remote"


def update_mode(args: argparse.Namespace) -> str:
    if args.update:
        return "remote"
    if args.no_update:
        return "pinned"
    return args.update_mode


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


def clone_or_update(repo_url: str, path: Path, ref: str | None, args: argparse.Namespace, report: Report, label: str) -> None:
    if not git_available(report):
        return
    if is_configured_submodule(path):
        report.add("present", f"{label} configured as Git submodule: {path}")
        sync_or_init_submodule(path, ref, args, report, label)
        return
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        ok = run(["git", "clone", repo_url, str(path)], report, args.dry_run, f"cloned {label}")
        if ok:
            checkout_ref(path, ref, report, args.dry_run, label)
        return
    report.add("present", f"{label} vendor exists: {path}")
    if not (path / ".git").exists():
        report.add("warnings", f"{path} exists but is not a Git checkout; update skipped")
        return
    if should_update(args):
        run(["git", "fetch", "--all", "--prune"], report, args.dry_run, f"fetched {label}", cwd=path)
        run(["git", "pull", "--ff-only"], report, args.dry_run, f"updated {label}", cwd=path)
    else:
        report.add("skipped", f"{label} update skipped")
    checkout_ref(path, ref, report, args.dry_run, label)


def commit_hash(path: Path) -> str:
    if not (path / ".git").exists():
        return "unknown"
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=path, text=True, capture_output=True, check=False)
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def write_if_changed(path: Path, text: str, args: argparse.Namespace, report: Report, label: str) -> bool:
    if path.exists() and path.read_text(encoding="utf-8", errors="replace") == text:
        report.add("present", f"{label} current: {path}")
        return True
    if path.exists() and not args.force:
        report.add("skipped", f"{path} exists; use --force to replace")
        return False
    if args.dry_run:
        report.add("skipped", f"dry-run would write {path}")
        return True
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    report.add("installed", f"wrote {label}: {path}")
    return True


def ars_skill_path(skill_name: str) -> Path:
    return ARS_VENDOR / skill_name / "SKILL.md"


def validate_ars(report: Report) -> bool:
    ok = True
    for skill_name in ARS_SKILLS:
        path = ars_skill_path(skill_name)
        if path.exists():
            report.add("present", f"ARS skill found: {path}")
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


def validate_rbs(report: Report) -> bool:
    required = [RBS_VENDOR / ".codex-plugin" / "plugin.json", RBS_VENDOR / "skills"]
    ok = True
    for path in required:
        if path.exists():
            report.add("present", f"RBS component found: {path}")
        else:
            report.add("failed", f"RBS component missing: {path}")
            ok = False
    return ok


def marketplace_text() -> str:
    payload = {
        "name": "local-research-workflow-plugins",
        "interface": {"displayName": "Local Research Workflow Plugins"},
        "plugins": [
            {
                "name": RBS_MARKETPLACE_NAME,
                "source": {"source": "local", "path": MARKETPLACE_PLUGIN_PATH},
                "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                "category": "Productivity",
            }
        ],
    }
    return json.dumps(payload, indent=2) + "\n"


def write_marketplace(args: argparse.Namespace, report: Report) -> bool:
    return write_if_changed(PLUGIN_MARKETPLACE, marketplace_text(), args, report, "plugin marketplace")


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
        args.ars_repo,
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
        args.rbs_repo,
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


def install_external(args: argparse.Namespace, report: Report) -> None:
    if args.update and args.no_update:
        report.add("failed", "choose either --update or --no-update, not both")
        return

    ars_wrappers: list[Path] = []
    plugin_exposed = False
    marketplace_written = False
    ars_ready = False
    rbs_ready = False

    if args.skip_ars:
        report.add("skipped", "ARS skipped")
    else:
        clone_or_update(args.ars_repo, ARS_VENDOR, args.ars_ref, args, report, "ARS")
        if ARS_VENDOR.exists() and validate_ars(report):
            ars_wrappers = create_ars_wrappers(args, report)
            ars_ready = bool(ars_wrappers)

    if args.skip_rbs:
        report.add("skipped", "RBS skipped")
    else:
        clone_or_update(args.rbs_repo, RBS_VENDOR, args.rbs_ref, args, report, "RBS")
        if RBS_VENDOR.exists() and validate_rbs(report):
            rbs_ready = True
            if args.no_rbs_plugin:
                report.add("skipped", "RBS marketplace exposure skipped by --no-rbs-plugin")
            else:
                plugin_exposed = True
                marketplace_written = write_marketplace(args, report)

    if ars_ready:
        write_ars_install_report(args, report, ars_wrappers)
    if rbs_ready:
        write_rbs_install_report(args, report, plugin_exposed, marketplace_written)

    report.add("warnings", "External repositories are untrusted until inspected")
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
