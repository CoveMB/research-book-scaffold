"""Local tool checks and optional package installation."""

from __future__ import annotations

import argparse
import os
import shutil
import sys

from script_utils import StatusReport, run_command


CORE_TOOLS = ["git", "python3", "curl", "unzip", "codex"]
OPTIONAL_TOOLS = ["node", "npm", "quarto", "pandoc"]


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
    package_maps = {
        "brew": {
            "git": ["brew", "install", "git"],
            "curl": ["brew", "install", "curl"],
            "unzip": ["brew", "install", "unzip"],
            "pandoc": ["brew", "install", "pandoc"],
            "quarto": ["brew", "install", "--cask", "quarto"],
        },
        "apt": {
            "git": ["apt", "install", "-y", "git"],
            "curl": ["apt", "install", "-y", "curl"],
            "unzip": ["apt", "install", "-y", "unzip"],
            "pandoc": ["apt", "install", "-y", "pandoc"],
        },
        "dnf": {
            "git": ["dnf", "install", "-y", "git"],
            "curl": ["dnf", "install", "-y", "curl"],
            "unzip": ["dnf", "install", "-y", "unzip"],
            "pandoc": ["dnf", "install", "-y", "pandoc"],
        },
        "pacman": {
            "git": ["pacman", "-S", "--noconfirm", "--needed", "git"],
            "curl": ["pacman", "-S", "--noconfirm", "--needed", "curl"],
            "unzip": ["pacman", "-S", "--noconfirm", "--needed", "unzip"],
            "pandoc": ["pacman", "-S", "--noconfirm", "--needed", "pandoc"],
        },
        "winget": {
            "git": ["winget", "install", "--id", "Git.Git", "-e"],
            "pandoc": ["winget", "install", "--id", "JohnMacFarlane.Pandoc", "-e"],
            "quarto": ["winget", "install", "--id", "Posit.Quarto", "-e"],
        },
        "choco": {
            "git": ["choco", "install", "git", "-y"],
            "curl": ["choco", "install", "curl", "-y"],
            "unzip": ["choco", "install", "unzip", "-y"],
            "pandoc": ["choco", "install", "pandoc", "-y"],
            "quarto": ["choco", "install", "quarto", "-y"],
        },
    }
    return package_maps.get(manager, {}).get(package_name)


def needs_sudo(manager: str) -> bool:
    return manager in {"apt", "dnf", "pacman"}


def maybe_install_system_package(
    package_name: str,
    args: argparse.Namespace,
    report: StatusReport,
    optional: bool,
) -> None:
    if optional and not args.install_optional:
        report.add("skipped", f"{package_name} missing; optional install not requested")
        return
    if not optional and not args.install_system:
        report.add("failed", f"{package_name} missing; system install not requested")
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


def install_codex(args: argparse.Namespace, report: StatusReport) -> None:
    if not command_exists("npm"):
        report.add("failed", "codex missing; npm missing, cannot install automatically")
        report.next_steps.append("Install Node/npm, then install @openai/codex.")
        return
    command = ["npm", "i", "-g", "@openai/codex"]
    if ask_to_run("Install @openai/codex with npm?", args):
        run_command(command, report, args.dry_run, "installed @openai/codex")
    else:
        report.add("failed", "@openai/codex install not approved")


def check_packages(args: argparse.Namespace, report: StatusReport) -> None:
    if args.skip_packages:
        report.add("skipped", "package checks skipped by flag")
        return

    for tool in CORE_TOOLS:
        if command_exists(tool):
            report.add("already_present", f"{tool} found")
        elif tool == "codex":
            report.add("warnings", "codex missing")
            install_codex(args, report)
        else:
            report.add("warnings", f"{tool} missing")
            maybe_install_system_package(tool, args, report, optional=False)

    for tool in OPTIONAL_TOOLS:
        if command_exists(tool):
            report.add("already_present", f"{tool} found")
        elif tool in {"quarto", "pandoc"}:
            report.add("warnings", f"{tool} missing")
            maybe_install_system_package(tool, args, report, optional=True)
        else:
            report.add("warnings", f"{tool} missing")
