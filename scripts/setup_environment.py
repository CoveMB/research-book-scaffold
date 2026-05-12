#!/usr/bin/env python3
"""Single entrypoint for local setup of the research writing scaffold."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import install_external_skills
from environment_checks import check_packages
from obsidian_agent import (
    install_obsidian_codex,
    obsidian_next_steps,
    safe_extract_zip,
    sha256_file,
    vault_path_from_args,
)
from project_config import DEFAULT_ARS_REPO, DEFAULT_RBS_REPO, change_to_project_root
from script_utils import StatusReport, read_text


class Report(StatusReport):
    def print_summary(self) -> None:
        print("\nFinal setup report")
        sections = [
            ("Installed", self.installed),
            ("Already present", self.already_present),
            ("Skipped", self.skipped),
            ("Failed", self.failed),
            ("Warnings", self.warnings),
            ("Next manual steps", self.next_steps),
        ]
        for title, values in sections:
            print(f"\n{title}:")
            if not values:
                print("- none")
            else:
                for value in values:
                    print(f"- {value}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--yes", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--skip-packages", action="store_true")
    parser.add_argument("--skip-ars", action="store_true")
    parser.add_argument("--skip-rbs", action="store_true")
    parser.add_argument("--with-external-skills", action="store_true")
    parser.add_argument("--obsidian-vault")
    parser.add_argument("--obsidian-release-url")
    parser.add_argument("--obsidian-release-sha256")
    parser.add_argument("--install-optional", action="store_true")
    parser.add_argument("--install-system", action="store_true")
    parser.add_argument("--ars-repo", default=DEFAULT_ARS_REPO)
    parser.add_argument("--ars-ref")
    parser.add_argument("--rbs-repo", default=DEFAULT_RBS_REPO)
    parser.add_argument("--rbs-ref")
    parser.add_argument("--no-rbs-plugin", action="store_true")
    parser.add_argument("--update-mode", choices=["pinned", "remote"], default="pinned")
    parser.add_argument("--update", action="store_true")
    parser.add_argument("--no-update", action="store_true")
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


def run_recommendations(args: argparse.Namespace, report: Report) -> None:
    report.next_steps.append("Run bash scripts/doctor.sh")
    report.next_steps.append("Run python3 scripts/check_external_skills.py")
    report.next_steps.append("Run python3 scripts/check_obsidian_codex.py")
    report.next_steps.append("Run python3 scripts/check_citations.py")
    report.next_steps.append("Run python3 scripts/check_placeholders.py .")


def external_args_from_setup_args(args: argparse.Namespace) -> argparse.Namespace:
    return argparse.Namespace(
        dry_run=args.dry_run,
        yes=args.yes,
        force=args.force,
        skip_ars=args.skip_ars,
        skip_rbs=args.skip_rbs,
        ars_repo=args.ars_repo,
        ars_ref=args.ars_ref,
        rbs_repo=args.rbs_repo,
        rbs_ref=args.rbs_ref,
        no_rbs_plugin=args.no_rbs_plugin,
        update_mode=args.update_mode,
        update=args.update,
        no_update=args.no_update,
    )


def install_external_layer(args: argparse.Namespace, report: Report) -> None:
    if not args.with_external_skills:
        report.add("skipped", "external skills skipped; run install script or pass --with-external-skills")
        return

    external_args = external_args_from_setup_args(args)
    external_report = install_external_skills.Report()
    install_external_skills.install_external(external_args, external_report)
    report.installed.extend(external_report.installed)
    report.already_present.extend(external_report.already_present)
    report.skipped.extend(external_report.skipped)
    report.failed.extend(external_report.failed)
    report.warnings.extend(external_report.warnings)


def main(argv: list[str]) -> int:
    change_to_project_root()
    args = parse_args(argv)
    report = Report()

    if args.dry_run:
        print("Dry run: no files, packages, repos, or plugins will be changed.\n")

    check_packages(args, report)
    validate_local_skills(Path(".agents/skills"), report, args.dry_run)
    install_external_layer(args, report)
    install_obsidian_codex(args, report)
    run_recommendations(args, report)
    report.print_summary()
    return 1 if report.failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
