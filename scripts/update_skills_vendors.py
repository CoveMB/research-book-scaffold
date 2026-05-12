#!/usr/bin/env python3
"""Update vendored skill repositories and refresh local integrations."""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from git_utils import has_git_checkout
from project_config import ARS_VENDOR, RBS_VENDOR, change_to_project_root


@dataclass(frozen=True)
class VendorSpec:
    label: str
    path: Path
    branch: str = "main"


@dataclass(frozen=True)
class VendorUpdate:
    label: str
    path: Path
    old_ref: str
    new_ref: str


class UpdateError(RuntimeError):
    """Raised when a vendor update cannot safely continue."""


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-ars", action="store_true", help="Skip Academic Research Skills.")
    parser.add_argument("--skip-rbs", action="store_true", help="Skip Research Book Skills.")
    parser.add_argument("--skip-checks", action="store_true", help="Skip post-update health checks.")
    return parser.parse_args(argv)


def vendor_specs(args: argparse.Namespace) -> list[VendorSpec]:
    vendors = []
    if not args.skip_ars:
        vendors.append(VendorSpec("ARS", ARS_VENDOR))
    if not args.skip_rbs:
        vendors.append(VendorSpec("RBS", RBS_VENDOR))
    if not vendors:
        raise UpdateError("No vendors selected; remove one skip flag.")
    return vendors


def run_checked(command: list[str], action: str, cwd: Path | None = None) -> None:
    print(f"RUN {action}: {' '.join(command)}")
    result = subprocess.run(command, cwd=cwd, text=True, check=False)
    if result.returncode != 0:
        raise UpdateError(f"{action} failed with exit code {result.returncode}")


def git_stdout(command: list[str], cwd: Path | None = None) -> str:
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise UpdateError(f"git command failed: {' '.join(command)}")
    return result.stdout.strip()


def submodule_status(path: Path) -> str:
    return git_stdout(["git", "-C", path.as_posix(), "status", "--short"])


def fail_if_dirty(vendor: VendorSpec) -> None:
    status = submodule_status(vendor.path)
    if status:
        raise UpdateError(f"{vendor.label} vendor has uncommitted changes:\n{status}")


def ensure_vendor_branch(vendor: VendorSpec) -> None:
    path = vendor.path.as_posix()
    current_branch = git_stdout(["git", "-C", path, "branch", "--show-current"])
    if current_branch == vendor.branch:
        return
    if current_branch:
        raise UpdateError(
            f"{vendor.label} vendor is on {current_branch}; expected {vendor.branch}. "
            "Check out the intended vendor branch first."
        )
    try:
        run_checked(["git", "-C", path, "checkout", vendor.branch], f"checkout {vendor.label} branch {vendor.branch}")
    except UpdateError:
        run_checked(
            ["git", "-C", path, "checkout", "--track", f"origin/{vendor.branch}"],
            f"track {vendor.label} branch {vendor.branch}",
        )


def short_ref(ref: str) -> str:
    return ref[:12] if len(ref) > 12 else ref


def update_vendor(vendor: VendorSpec) -> VendorUpdate:
    path = vendor.path.as_posix()
    run_checked(["git", "submodule", "sync", "--", path], f"sync {vendor.label} submodule")
    if not has_git_checkout(vendor.path):
        run_checked(
            ["git", "submodule", "update", "--init", "--recursive", "--", path],
            f"initialize {vendor.label} submodule",
        )
    fail_if_dirty(vendor)
    run_checked(["git", "-C", path, "fetch", "--prune"], f"fetch {vendor.label} remote")
    ensure_vendor_branch(vendor)
    old_ref = git_stdout(["git", "-C", path, "rev-parse", "HEAD"])
    run_checked(["git", "-C", path, "pull", "--ff-only"], f"fast-forward {vendor.label}")
    fail_if_dirty(vendor)
    new_ref = git_stdout(["git", "-C", path, "rev-parse", "HEAD"])
    return VendorUpdate(vendor.label, vendor.path, old_ref, new_ref)


def refresh_command(args: argparse.Namespace) -> list[str]:
    command = [
        "python3",
        "scripts/install_external_skills.py",
        "--yes",
        "--force",
        "--no-update",
        "--preserve-vendor-checkouts",
    ]
    if args.skip_ars:
        command.append("--skip-ars")
    if args.skip_rbs:
        command.append("--skip-rbs")
    return command


def refresh_integrations(args: argparse.Namespace) -> None:
    run_checked(refresh_command(args), "refresh local skill integrations")


def run_health_checks(args: argparse.Namespace) -> None:
    if args.skip_checks:
        print("SKIP post-update checks")
        return
    run_checked(["python3", "scripts/check_external_skills.py"], "check external skill integrations")
    run_checked(["bash", "scripts/doctor.sh"], "run repository doctor")


def print_summary(summaries: list[VendorUpdate]) -> None:
    print("\nUpdated vendors:")
    for summary in summaries:
        print(f"- {summary.label}: {short_ref(summary.old_ref)} -> {short_ref(summary.new_ref)} ({summary.path})")


def update_skills_vendors(args: argparse.Namespace) -> list[VendorUpdate]:
    current_branch = git_stdout(["git", "branch", "--show-current"])
    if not current_branch:
        raise UpdateError("Parent repository is detached; check out intended branch first.")
    print(f"Branch: {current_branch}")
    run_checked(["git", "status", "--short", "--branch"], "show parent repository status")
    run_checked(["git", "fetch", "--all", "--prune"], "fetch parent repository refs")
    summaries = [update_vendor(vendor) for vendor in vendor_specs(args)]
    refresh_integrations(args)
    run_health_checks(args)
    run_checked(["git", "status", "--short", "--branch"], "show final parent repository status")
    print_summary(summaries)
    return summaries


def main(argv: list[str]) -> int:
    change_to_project_root()
    args = parse_args(argv)
    try:
        update_skills_vendors(args)
    except UpdateError as error:
        print(f"FAIL {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
