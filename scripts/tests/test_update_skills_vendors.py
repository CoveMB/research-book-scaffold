from __future__ import annotations

import contextlib
import io
import unittest
from pathlib import Path
from unittest import mock


from scripts.tests.helpers import add_scripts_to_path


add_scripts_to_path()

import update_skills_vendors
from project_config import ARS_VENDOR, RBS_VENDOR, SUBAGENT_ORCHESTRATOR_VENDOR, VENDOR_UPDATE_HEALTH_CHECKS


class UpdateSkillsVendorsTests(unittest.TestCase):
    def fake_git_stdout(self, command: list[str], cwd: Path | None = None) -> str:
        del cwd
        if command[-2:] == ["branch", "--show-current"]:
            return "main"
        return "abc123"

    def test_default_flow_updates_vendors_refreshes_integrations_and_runs_checks(self) -> None:
        args = update_skills_vendors.parse_args([])
        calls: list[tuple[str, ...]] = []

        def fake_run(command: list[str], action: str, cwd: Path | None = None) -> None:
            del action, cwd
            calls.append(tuple(command))

        with (
            mock.patch.object(update_skills_vendors, "run_checked", side_effect=fake_run),
            mock.patch.object(update_skills_vendors, "git_stdout_required", side_effect=self.fake_git_stdout),
            mock.patch.object(update_skills_vendors, "submodule_status", return_value=""),
        ):
            with contextlib.redirect_stdout(io.StringIO()):
                summaries = update_skills_vendors.update_skills_vendors(args)

        self.assertIn(("git", "fetch", "--all", "--prune"), calls)
        self.assertIn(("git", "submodule", "sync", "--", ARS_VENDOR.as_posix()), calls)
        self.assertIn(("git", "-C", ARS_VENDOR.as_posix(), "pull", "--ff-only"), calls)
        self.assertIn(("git", "submodule", "sync", "--", RBS_VENDOR.as_posix()), calls)
        self.assertIn(("git", "-C", RBS_VENDOR.as_posix(), "pull", "--ff-only"), calls)
        self.assertIn(("git", "submodule", "sync", "--", SUBAGENT_ORCHESTRATOR_VENDOR.as_posix()), calls)
        self.assertIn(("git", "-C", SUBAGENT_ORCHESTRATOR_VENDOR.as_posix(), "pull", "--ff-only"), calls)
        self.assertIn(
            (
                "python3",
                "scripts/install_external_skills.py",
                "--yes",
                "--force",
                "--no-update",
                "--preserve-vendor-checkouts",
            ),
            calls,
        )
        for check in VENDOR_UPDATE_HEALTH_CHECKS:
            self.assertIn(tuple(check.command), calls)
        self.assertEqual([summary.label for summary in summaries], ["ARS", "RBS", "Subagent Orchestrator"])

    def test_skip_flags_limit_vendor_refresh_scope(self) -> None:
        args = update_skills_vendors.parse_args(["--skip-ars", "--skip-checks"])
        calls: list[tuple[str, ...]] = []

        def fake_run(command: list[str], action: str, cwd: Path | None = None) -> None:
            del action, cwd
            calls.append(tuple(command))

        with (
            mock.patch.object(update_skills_vendors, "run_checked", side_effect=fake_run),
            mock.patch.object(update_skills_vendors, "git_stdout_required", side_effect=self.fake_git_stdout),
            mock.patch.object(update_skills_vendors, "submodule_status", return_value=""),
        ):
            with contextlib.redirect_stdout(io.StringIO()):
                summaries = update_skills_vendors.update_skills_vendors(args)

        self.assertNotIn(("git", "submodule", "sync", "--", ARS_VENDOR.as_posix()), calls)
        self.assertIn(("git", "submodule", "sync", "--", RBS_VENDOR.as_posix()), calls)
        self.assertIn(("git", "submodule", "sync", "--", SUBAGENT_ORCHESTRATOR_VENDOR.as_posix()), calls)
        self.assertIn(
            (
                "python3",
                "scripts/install_external_skills.py",
                "--yes",
                "--force",
                "--no-update",
                "--preserve-vendor-checkouts",
                "--skip-ars",
            ),
            calls,
        )
        for check in VENDOR_UPDATE_HEALTH_CHECKS:
            self.assertNotIn(tuple(check.command), calls)
        self.assertEqual([summary.label for summary in summaries], ["RBS", "Subagent Orchestrator"])

    def test_subagent_skip_flag_limits_vendor_refresh_scope(self) -> None:
        args = update_skills_vendors.parse_args(["--skip-ars", "--skip-rbs", "--skip-subagent-orchestrator"])

        with self.assertRaisesRegex(update_skills_vendors.UpdateError, "No vendors selected"):
            update_skills_vendors.vendor_specs(args)

    def test_dirty_vendor_fails_before_pull(self) -> None:
        args = update_skills_vendors.parse_args([])

        with (
            mock.patch.object(update_skills_vendors, "run_checked"),
            mock.patch.object(update_skills_vendors, "git_stdout_required", side_effect=self.fake_git_stdout),
            mock.patch.object(update_skills_vendors, "submodule_status", return_value=" M SKILL.md\n"),
        ):
            with contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaisesRegex(update_skills_vendors.UpdateError, "ARS vendor has uncommitted changes"):
                    update_skills_vendors.update_skills_vendors(args)


if __name__ == "__main__":
    unittest.main()
