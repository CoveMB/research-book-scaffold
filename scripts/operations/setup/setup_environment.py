#!/usr/bin/env python3
"""Single entrypoint for local setup of the research writing scaffold."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SCRIPTS_ROOT = next(parent for parent in Path(__file__).resolve().parents if parent.name == "scripts")
_LIB_DIR = _SCRIPTS_ROOT / "lib"
if str(_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(_LIB_DIR))

from import_paths import configure_script_paths

configure_script_paths(__file__)

import install_external_skills
import obsidian_research_plugins
from environment_checks import check_packages
from obsidian_agent import (
    install_codex_panel,
    obsidian_next_steps,
    vault_path_from_args,
)
from project_config import (
    SETUP_RECOMMENDED_CHECKS,
    change_to_project_root,
)
from script_utils import StatusReport, read_text


class Report(StatusReport):
    def print_summary(self) -> None:
        super().print_summary("Final setup report")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--yes", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--skip-packages", action="store_true")
    parser.add_argument("--skip-ars", action="store_true")
    parser.add_argument("--skip-rbs", action="store_true")
    parser.add_argument("--skip-subagent-orchestrator", action="store_true")
    parser.add_argument("--skip-obsidian-skills", action="store_true")
    parser.add_argument("--skip-obsidian-panel", action="store_true")
    parser.add_argument(
        "--skip-external-skills",
        action="store_true",
        help="Skip vendored external skill initialization and local wrapper refresh.",
    )
    parser.add_argument(
        "--with-external-skills",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    parser.add_argument("--obsidian-vault")
    parser.add_argument("--obsidian-release-url")
    parser.add_argument("--obsidian-release-sha256")
    parser.add_argument("--zotero-integration-release-url")
    parser.add_argument("--pandoc-reference-list-release-url")
    parser.add_argument("--qmd-as-md-release-url")
    parser.add_argument("--skip-obsidian-research-plugins", action="store_true")
    parser.add_argument(
        "--register-obsidian-vault",
        action="store_true",
        help="Register the vault path in Obsidian's app-level vault registry.",
    )
    parser.add_argument("--obsidian-registry-path", help=argparse.SUPPRESS)
    parser.add_argument("--install-optional", action="store_true")
    parser.add_argument("--install-system", action="store_true")
    parser.add_argument("--ars-ref")
    parser.add_argument("--rbs-ref")
    parser.add_argument("--subagent-orchestrator-ref")
    parser.add_argument("--obsidian-skills-ref")
    parser.add_argument("--no-rbs-plugin", action="store_true")
    parser.add_argument("--no-subagent-orchestrator-plugin", action="store_true")
    update_group = parser.add_mutually_exclusive_group()
    update_group.add_argument("--update", action="store_true", help="Update configured external skills from remotes.")
    update_group.add_argument("--no-update", action="store_true", help="Use pinned or current external skill checkouts.")
    return parser.parse_args(argv)


def parse_front_matter(skill_file: Path) -> tuple[str | None, str | None, list[str]]:
    text = read_text(skill_file)
    issues: list[str] = []
    if not text.startswith("---\n"):
        return None, None, ["missing YAML front matter"]
    end_index = text.find("\n---", 4)
    if end_index == -1:
        return None, None, ["unterminated YAML front matter"]
    front_matter = text[4:end_index]
    name = None
    description = None
    for line in front_matter.splitlines():
        if line.startswith("name:"):
            name = line.split(":", 1)[1].strip().strip("\"'")
        if line.startswith("description:"):
            description = line.split(":", 1)[1].strip().strip("\"'")
    if not name:
        issues.append("missing front matter name")
    if not description:
        issues.append("missing front matter description")
    return name, description, issues


def validate_local_skills(target_dir: Path, report: Report, dry_run: bool) -> None:
    if target_dir.exists():
        report.add("already_present", f"{target_dir} exists")
    else:
        if dry_run:
            report.add("skipped", f"dry-run would create {target_dir}")
            return
        else:
            target_dir.mkdir(parents=True, exist_ok=True)
            report.add("installed", f"created {target_dir}")

    for child in sorted(path for path in target_dir.iterdir() if path.is_dir()):
        skill_file = child / "SKILL.md"
        if not skill_file.exists():
            report.add("warnings", f"{child} missing SKILL.md")
            continue
        _name, _description, issues = parse_front_matter(skill_file)
        if issues:
            report.add("warnings", f"{skill_file}: {', '.join(issues)}")
        else:
            report.add("already_present", f"{skill_file} valid")


def recommended_checks(args: argparse.Namespace) -> list[str]:
    checks = [check.shell_text() for check in SETUP_RECOMMENDED_CHECKS]
    if args.skip_obsidian_panel:
        checks = [check for check in checks if check != "python3 scripts/operations/obsidian/check_obsidian_panel.py"]
    if args.skip_obsidian_research_plugins:
        checks = [
            check
            for check in checks
            if check != "python3 scripts/operations/obsidian/obsidian_research_plugins.py check"
        ]
    return checks


def run_recommendations(args: argparse.Namespace, report: Report) -> None:
    report.next_steps.extend(f"Run {check}" for check in recommended_checks(args))
    if args.skip_obsidian_panel:
        report.next_steps.append("Run make install-obsidian-panel when Obsidian/Codex Panel coverage is needed")
    if args.skip_obsidian_research_plugins:
        report.next_steps.append(
            "Run make install-obsidian-research-plugins when Zotero/Pandoc/QMD Obsidian coverage is needed"
        )


def external_args_from_setup_args(args: argparse.Namespace) -> argparse.Namespace:
    return argparse.Namespace(
        dry_run=args.dry_run,
        yes=args.yes,
        force=args.force,
        skip_ars=args.skip_ars,
        skip_rbs=args.skip_rbs,
        skip_subagent_orchestrator=args.skip_subagent_orchestrator,
        skip_obsidian_skills=args.skip_obsidian_skills,
        ars_ref=args.ars_ref,
        rbs_ref=args.rbs_ref,
        subagent_orchestrator_ref=args.subagent_orchestrator_ref,
        obsidian_skills_ref=args.obsidian_skills_ref,
        no_rbs_plugin=args.no_rbs_plugin,
        no_subagent_orchestrator_plugin=args.no_subagent_orchestrator_plugin,
        update=args.update,
        no_update=args.no_update,
        preserve_vendor_checkouts=False,
    )


def install_external_layer(args: argparse.Namespace, report: Report) -> None:
    if args.skip_external_skills:
        report.add("skipped", "external skills skipped by --skip-external-skills")
        return

    external_args = external_args_from_setup_args(args)
    external_report = install_external_skills.Report()
    install_external_skills.install_external(external_args, external_report)
    report.installed.extend(external_report.installed)
    report.already_present.extend(external_report.already_present)
    report.skipped.extend(external_report.skipped)
    report.failed.extend(external_report.failed)
    report.warnings.extend(external_report.warnings)


def install_obsidian_panel_layer(args: argparse.Namespace, report: Report) -> None:
    if args.skip_obsidian_panel:
        report.add("skipped", "Codex Panel setup skipped by --skip-obsidian-panel")
        return
    install_codex_panel(args, report)


def install_research_plugins(args: argparse.Namespace, report: Report) -> None:
    obsidian_research_plugins.install_research_plugins(args, report)


def install_obsidian_research_plugin_layer(args: argparse.Namespace, report: Report) -> None:
    if args.skip_obsidian_research_plugins:
        report.add("skipped", "Obsidian research plugin setup skipped by --skip-obsidian-research-plugins")
        return
    install_research_plugins(args, report)


def main(argv: list[str]) -> int:
    change_to_project_root()
    args = parse_args(argv)
    report = Report()

    if args.dry_run:
        print("Dry run: no files, packages, repos, or plugins will be changed.\n")

    check_packages(args, report)
    validate_local_skills(Path(".agents/skills"), report, args.dry_run)
    install_external_layer(args, report)
    install_obsidian_panel_layer(args, report)
    install_obsidian_research_plugin_layer(args, report)
    run_recommendations(args, report)
    report.print_summary()
    return 1 if report.failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
