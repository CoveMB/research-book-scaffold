#!/usr/bin/env python3
"""Resilient local setup for the research writing scaffold."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

import install_external_skills
from project_config import (
    DEFAULT_ARS_REPO,
    DEFAULT_RBS_REPO,
    OBSIDIAN_CODEX_PLUGIN_ID,
    OBSIDIAN_DIR,
    OBSIDIAN_PLUGINS_DIR,
    REQUIRED_OBSIDIAN_PLUGIN_FILES,
    resolve_obsidian_vault_path,
)

DEFAULT_OBSIDIAN_REPO = "https://github.com/AKin-lvyifang/obsidian-codex"
CORE_TOOLS = ["git", "python3", "curl", "unzip"]
OPTIONAL_TOOLS = ["node", "npm", "codex", "quarto", "pandoc"]


@dataclass
class Report:
    installed: list[str] = field(default_factory=list)
    already_present: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    next_steps: list[str] = field(default_factory=list)

    def add(self, bucket: str, message: str) -> None:
        getattr(self, bucket).append(message)
        label = bucket.replace("_", " ").upper()
        print(f"{label}: {message}")

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
    parser.add_argument("--skip-codex", action="store_true")
    parser.add_argument("--skip-ars", action="store_true")
    parser.add_argument("--skip-rbs", action="store_true")
    parser.add_argument("--with-external-skills", action="store_true")
    parser.add_argument("--skip-obsidian-codex", action="store_true")
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
    parser.add_argument("--update", action="store_true")
    parser.add_argument("--no-update", action="store_true")
    return parser.parse_args(argv)


def run_command(
    command: list[str],
    report: Report,
    dry_run: bool,
    action: str,
    cwd: Path | None = None,
) -> bool:
    printable = " ".join(command)
    if dry_run:
        report.add("skipped", f"dry-run would run: {printable}")
        return True
    try:
        result = subprocess.run(command, cwd=cwd, check=False, text=True)
    except OSError as error:
        report.add("failed", f"{action}: {error}")
        return False
    if result.returncode == 0:
        report.add("installed", action)
        return True
    report.add("failed", f"{action}: command exited {result.returncode}: {printable}")
    return False


def command_exists(command: str) -> bool:
    return shutil.which(command) is not None


def ask_to_run(prompt: str, args: argparse.Namespace) -> bool:
    if args.dry_run:
        return True
    if args.yes:
        return True
    if not sys.stdin.isatty():
        return False
    answer = input(f"{prompt} [y/N] ").strip().lower()
    return answer in {"y", "yes"}


def detect_package_manager() -> str | None:
    for candidate in ["brew", "apt", "dnf", "pacman", "winget", "choco"]:
        if command_exists(candidate):
            return candidate
    return None


def package_install_command(manager: str, package_name: str) -> list[str] | None:
    brew_packages = {
        "git": ["brew", "install", "git"],
        "curl": ["brew", "install", "curl"],
        "unzip": ["brew", "install", "unzip"],
        "pandoc": ["brew", "install", "pandoc"],
        "quarto": ["brew", "install", "--cask", "quarto"],
    }
    apt_packages = {
        "git": ["apt", "install", "-y", "git"],
        "curl": ["apt", "install", "-y", "curl"],
        "unzip": ["apt", "install", "-y", "unzip"],
        "pandoc": ["apt", "install", "-y", "pandoc"],
    }
    dnf_packages = {
        "git": ["dnf", "install", "-y", "git"],
        "curl": ["dnf", "install", "-y", "curl"],
        "unzip": ["dnf", "install", "-y", "unzip"],
        "pandoc": ["dnf", "install", "-y", "pandoc"],
    }
    pacman_packages = {
        "git": ["pacman", "-S", "--noconfirm", "--needed", "git"],
        "curl": ["pacman", "-S", "--noconfirm", "--needed", "curl"],
        "unzip": ["pacman", "-S", "--noconfirm", "--needed", "unzip"],
        "pandoc": ["pacman", "-S", "--noconfirm", "--needed", "pandoc"],
    }
    winget_packages = {
        "git": ["winget", "install", "--id", "Git.Git", "-e"],
        "pandoc": ["winget", "install", "--id", "JohnMacFarlane.Pandoc", "-e"],
        "quarto": ["winget", "install", "--id", "Posit.Quarto", "-e"],
    }
    choco_packages = {
        "git": ["choco", "install", "git", "-y"],
        "curl": ["choco", "install", "curl", "-y"],
        "unzip": ["choco", "install", "unzip", "-y"],
        "pandoc": ["choco", "install", "pandoc", "-y"],
        "quarto": ["choco", "install", "quarto", "-y"],
    }
    package_maps = {
        "brew": brew_packages,
        "apt": apt_packages,
        "dnf": dnf_packages,
        "pacman": pacman_packages,
        "winget": winget_packages,
        "choco": choco_packages,
    }
    return package_maps.get(manager, {}).get(package_name)


def needs_sudo(manager: str) -> bool:
    return manager in {"apt", "dnf", "pacman"}


def maybe_install_system_package(
    package_name: str,
    args: argparse.Namespace,
    report: Report,
    optional: bool,
) -> None:
    if optional and not args.install_optional:
        report.add("skipped", f"{package_name} missing; optional install not requested")
        return
    if not optional and not args.install_system:
        report.add("skipped", f"{package_name} missing; system install not requested")
        return
    manager = detect_package_manager()
    if not manager:
        report.add("warnings", f"{package_name} missing; no supported package manager found")
        return
    command = package_install_command(manager, package_name)
    if command is None:
        report.add("warnings", f"{package_name} missing; {manager} install command not configured")
        return
    if needs_sudo(manager) and os.environ.get("ALLOW_SYSTEM_INSTALL") != "1":
        report.add("skipped", f"{package_name} missing; run manually with sudo: sudo {' '.join(command)}")
        return
    final_command = ["sudo", *command] if needs_sudo(manager) else command
    if ask_to_run(f"Install {package_name} with {manager}?", args):
        run_command(final_command, report, args.dry_run, f"installed {package_name}")
    else:
        report.add("skipped", f"{package_name} install not approved")


def check_packages(args: argparse.Namespace, report: Report) -> None:
    if args.skip_packages:
        report.add("skipped", "package checks skipped by flag")
        return

    for tool in CORE_TOOLS:
        if command_exists(tool):
            report.add("already_present", f"{tool} found")
        else:
            report.add("warnings", f"{tool} missing")
            maybe_install_system_package(tool, args, report, optional=False)

    for tool in OPTIONAL_TOOLS:
        if tool == "codex" and args.skip_codex:
            report.add("skipped", "codex check skipped by flag")
            continue
        if command_exists(tool):
            report.add("already_present", f"{tool} found")
            continue
        if tool == "codex":
            install_codex(args, report)
        elif tool in {"quarto", "pandoc"}:
            report.add("warnings", f"{tool} missing")
            maybe_install_system_package(tool, args, report, optional=True)
        else:
            report.add("warnings", f"{tool} missing")


def install_codex(args: argparse.Namespace, report: Report) -> None:
    if args.skip_codex:
        report.add("skipped", "codex install skipped by flag")
        return
    if not command_exists("npm"):
        report.add("skipped", "codex missing; npm missing, cannot install automatically")
        report.next_steps.append("Install Node/npm, then install @openai/codex if needed.")
        return
    command = ["npm", "i", "-g", "@openai/codex"]
    if ask_to_run("Install @openai/codex with npm?", args):
        run_command(command, report, args.dry_run, "installed @openai/codex")
    else:
        report.add("skipped", "@openai/codex install not approved")


def parse_front_matter(skill_file: Path) -> tuple[str | None, str | None, list[str]]:
    try:
        text = skill_file.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = skill_file.read_text(encoding="utf-8", errors="replace")
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


def vault_path_from_args(args: argparse.Namespace) -> Path:
    return resolve_obsidian_vault_path(args.obsidian_vault, os.environ.get("OBSIDIAN_VAULT"))


def latest_obsidian_release_zip_url() -> str:
    api_url = "https://api.github.com/repos/AKin-lvyifang/obsidian-codex/releases/latest"
    request = urllib.request.Request(api_url, headers={"Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    for asset in payload.get("assets", []):
        download_url = asset.get("browser_download_url", "")
        if download_url.endswith(".zip"):
            return download_url
    zipball_url = payload.get("zipball_url")
    if zipball_url:
        return zipball_url
    raise RuntimeError("No zip asset found for latest Obsidian plugin release")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_archive_checksum(path: Path, expected_sha256: str | None) -> None:
    if not expected_sha256:
        return
    actual_sha256 = sha256_file(path)
    if actual_sha256.lower() != expected_sha256.lower():
        raise RuntimeError(f"archive checksum mismatch: expected {expected_sha256}, got {actual_sha256}")


def safe_extract_zip(archive: zipfile.ZipFile, destination: Path) -> None:
    destination_root = destination.resolve()
    for member in archive.infolist():
        target = (destination / member.filename).resolve()
        if destination_root != target and destination_root not in target.parents:
            raise ValueError(f"unsafe archive path: {member.filename}")
    archive.extractall(destination)


def find_obsidian_plugin_root(extracted_dir: Path) -> Path | None:
    for path in extracted_dir.rglob("*"):
        if not path.is_dir():
            continue
        if REQUIRED_OBSIDIAN_PLUGIN_FILES.issubset({child.name for child in path.iterdir() if child.is_file()}):
            return path
    return None


def ensure_obsidian_plugin_parent(vault_path: Path, report: Report, dry_run: bool) -> Path | None:
    obsidian_dir = vault_path / OBSIDIAN_DIR
    plugins_dir = vault_path / OBSIDIAN_PLUGINS_DIR
    for directory in [obsidian_dir, plugins_dir]:
        if directory.exists():
            if not directory.is_dir():
                report.add("failed", f"{directory} exists but is not a directory")
                return None
            report.add("already_present", f"{directory} exists")
            continue
        if dry_run:
            report.add("skipped", f"dry-run would create {directory}")
            continue
        try:
            directory.mkdir(parents=True, exist_ok=True)
        except OSError as error:
            report.add("failed", f"could not create {directory}: {error}")
            return None
        report.add("installed", f"created {directory}")
    return plugins_dir


def replace_directory_atomically(source_dir: Path, destination_dir: Path) -> None:
    with tempfile.TemporaryDirectory(prefix=f".{destination_dir.name}-", dir=destination_dir.parent) as temp_dir:
        temp_path = Path(temp_dir)
        staged_dir = temp_path / destination_dir.name
        backup_dir = temp_path / f"{destination_dir.name}.backup"
        shutil.copytree(source_dir, staged_dir)
        if destination_dir.exists():
            shutil.move(str(destination_dir), backup_dir)
        try:
            shutil.move(str(staged_dir), destination_dir)
        except OSError:
            if backup_dir.exists() and not destination_dir.exists():
                shutil.move(str(backup_dir), destination_dir)
            raise


def obsidian_next_steps(include_read_only_test: bool) -> list[str]:
    steps = [
        "Restart Obsidian.",
        "Enable Community Plugins.",
        "Enable Codex for Obsidian.",
    ]
    if include_read_only_test:
        steps.append("Open the plugin sidebar and run a harmless read-only test first.")
    return steps


def install_obsidian_codex(args: argparse.Namespace, report: Report) -> None:
    if args.skip_obsidian_codex:
        report.add("skipped", "Obsidian plugin skipped by flag")
        return
    vault_path = vault_path_from_args(args)
    if not vault_path.exists():
        report.add("failed", f"Obsidian vault path missing: {vault_path}")
        return

    plugins_dir = ensure_obsidian_plugin_parent(vault_path, report, args.dry_run)
    if plugins_dir is None:
        return
    destination_dir = plugins_dir / OBSIDIAN_CODEX_PLUGIN_ID
    if destination_dir.exists() and not args.force:
        report.add("skipped", f"{destination_dir} exists; use --force to replace")
        return
    if args.dry_run:
        report.add("skipped", f"dry-run would download latest release from {DEFAULT_OBSIDIAN_REPO}/releases/latest")
        report.add("skipped", f"dry-run would install plugin to {destination_dir}")
        report.next_steps.extend(obsidian_next_steps(include_read_only_test=False))
        return

    try:
        with tempfile.TemporaryDirectory(prefix="obsidian-plugin-") as temp_dir:
            temp_path = Path(temp_dir)
            zip_url = args.obsidian_release_url or latest_obsidian_release_zip_url()
            archive_path = temp_path / "release.zip"
            urllib.request.urlretrieve(zip_url, archive_path)
            verify_archive_checksum(archive_path, args.obsidian_release_sha256)
            extract_dir = temp_path / "extract"
            extract_dir.mkdir()
            with zipfile.ZipFile(archive_path) as archive:
                safe_extract_zip(archive, extract_dir)
            plugin_root = find_obsidian_plugin_root(extract_dir)
            if plugin_root is None:
                report.add("failed", "Downloaded Obsidian plugin release does not contain expected files")
                return
            replace_directory_atomically(plugin_root, destination_dir)
    except (
        OSError,
        RuntimeError,
        ValueError,
        zipfile.BadZipFile,
        urllib.error.URLError,
        json.JSONDecodeError,
    ) as error:
        report.add("failed", f"Obsidian plugin install failed: {error}")
        return
    report.add("installed", f"installed Obsidian plugin to {destination_dir}")
    report.next_steps.extend(obsidian_next_steps(include_read_only_test=True))


def run_recommendations(args: argparse.Namespace, report: Report) -> None:
    report.next_steps.append("Run bash scripts/doctor.sh")
    report.next_steps.append("Run python3 scripts/check_external_skills.py")
    if not args.skip_obsidian_codex:
        report.next_steps.append("Run python3 scripts/check_obsidian_codex.py")
    report.next_steps.append("Run python3 scripts/check_citations.py")
    report.next_steps.append("Run python3 scripts/check_placeholders.py .")


def install_external_layer(args: argparse.Namespace, report: Report) -> None:
    if not args.with_external_skills:
        report.add("skipped", "external skills skipped; run install script or pass --with-external-skills")
        return

    external_args = argparse.Namespace(
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
        update=args.update,
        no_update=args.no_update,
    )
    external_report = install_external_skills.Report()
    install_external_skills.install_external(external_args, external_report)
    report.installed.extend(external_report.installed)
    report.already_present.extend(external_report.present)
    report.skipped.extend(external_report.skipped)
    report.failed.extend(external_report.failed)
    report.warnings.extend(external_report.warnings)


def main(argv: list[str]) -> int:
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
