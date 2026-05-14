#!/usr/bin/env python3
"""Update vendored skill repositories and refresh local integrations."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

_SCRIPTS_ROOT = next(parent for parent in Path(__file__).resolve().parents if parent.name == "scripts")
_LIB_DIR = _SCRIPTS_ROOT / "lib"
if str(_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(_LIB_DIR))

from import_paths import configure_script_paths

configure_script_paths(__file__)

from git_utils import GitCommandError, git_stdout_required, has_git_checkout
from project_config import EXTERNAL_VENDOR_SPECS, VENDOR_UPDATE_HEALTH_CHECKS, ExternalVendorSpec, change_to_project_root
from script_utils import CommandError, run_command_required as run_checked


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
    parser.add_argument("--skip-subagent-orchestrator", action="store_true", help="Skip Subagent Orchestrator.")
    parser.add_argument("--skip-checks", action="store_true", help="Skip post-update health checks.")
    return parser.parse_args(argv)


def vendor_specs(args: argparse.Namespace) -> list[ExternalVendorSpec]:
    skipped_keys = {
        key
        for key, should_skip in {
            "ars": args.skip_ars,
            "rbs": args.skip_rbs,
            "subagent-orchestrator": args.skip_subagent_orchestrator,
        }.items()
        if should_skip
    }
    vendors = [vendor for vendor in EXTERNAL_VENDOR_SPECS if vendor.key not in skipped_keys]
    if not vendors:
        raise UpdateError("No vendors selected; remove one skip flag.")
    return vendors


def submodule_status(path: Path) -> str:
    return git_stdout_required(["git", "-C", path.as_posix(), "status", "--short"])


def fail_if_dirty(vendor: ExternalVendorSpec) -> None:
    status = submodule_status(vendor.path)
    if status:
        raise UpdateError(f"{vendor.label} vendor has uncommitted changes:\n{status}")


def ensure_vendor_branch(vendor: ExternalVendorSpec) -> None:
    path = vendor.path.as_posix()
    current_branch = git_stdout_required(["git", "-C", path, "branch", "--show-current"])
    if current_branch == vendor.branch:
        return
    if current_branch:
        raise UpdateError(
            f"{vendor.label} vendor is on {current_branch}; expected {vendor.branch}. "
            "Check out the intended vendor branch first."
        )
    try:
        run_checked(["git", "-C", path, "checkout", vendor.branch], f"checkout {vendor.label} branch {vendor.branch}")
    except CommandError:
        run_checked(
            ["git", "-C", path, "checkout", "--track", f"origin/{vendor.branch}"],
            f"track {vendor.label} branch {vendor.branch}",
        )


def short_ref(ref: str) -> str:
    return ref[:12] if len(ref) > 12 else ref


def update_vendor(vendor: ExternalVendorSpec) -> VendorUpdate:
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
    old_ref = git_stdout_required(["git", "-C", path, "rev-parse", "HEAD"])
    run_checked(["git", "-C", path, "pull", "--ff-only"], f"fast-forward {vendor.label}")
    fail_if_dirty(vendor)
    new_ref = git_stdout_required(["git", "-C", path, "rev-parse", "HEAD"])
    return VendorUpdate(vendor.label, vendor.path, old_ref, new_ref)


def refresh_command(args: argparse.Namespace) -> list[str]:
    command = [
        "python3",
        "scripts/operations/vendors/install_external_skills.py",
        "--yes",
        "--force",
        "--no-update",
        "--preserve-vendor-checkouts",
    ]
    if args.skip_ars:
        command.append("--skip-ars")
    if args.skip_rbs:
        command.append("--skip-rbs")
    if args.skip_subagent_orchestrator:
        command.append("--skip-subagent-orchestrator")
    return command


def refresh_integrations(args: argparse.Namespace) -> None:
    run_checked(refresh_command(args), "refresh local skill integrations")


def run_health_checks(args: argparse.Namespace) -> None:
    if args.skip_checks:
        print("SKIP post-update checks")
        return
    for check in VENDOR_UPDATE_HEALTH_CHECKS:
        run_checked(list(check.command), check.action)


def print_summary(summaries: list[VendorUpdate]) -> None:
    print("\nUpdated vendors:")
    for summary in summaries:
        print(f"- {summary.label}: {short_ref(summary.old_ref)} -> {short_ref(summary.new_ref)} ({summary.path})")


def update_skills_vendors(args: argparse.Namespace) -> list[VendorUpdate]:
    current_branch = git_stdout_required(["git", "branch", "--show-current"])
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
    except (CommandError, GitCommandError, UpdateError) as error:
        print(f"FAIL {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
