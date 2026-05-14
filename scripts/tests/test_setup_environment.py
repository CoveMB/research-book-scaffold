from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path


from scripts.tests.helpers import SilentReport, working_directory

import setup_environment
from project_config import OBSIDIAN_PLUGINS_DIR, SETUP_RECOMMENDED_CHECKS


class SetupEnvironmentTests(unittest.TestCase):
    def test_default_obsidian_vault_is_project_root(self) -> None:
        args = setup_environment.parse_args(["--dry-run"])

        with tempfile.TemporaryDirectory() as temp_dir:
            with working_directory(Path(temp_dir)):
                vault_path = setup_environment.vault_path_from_args(args)

        self.assertEqual(vault_path, Path(temp_dir).resolve())

    def test_default_setup_initializes_root_vault_without_nested_folder(self) -> None:
        args = setup_environment.parse_args(["--dry-run"])
        report = SilentReport()

        with tempfile.TemporaryDirectory() as temp_dir:
            with working_directory(Path(temp_dir)):
                setup_environment.install_codex_panel(args, report)

        messages = report.skipped + report.installed + report.already_present
        self.assertTrue(any(str(OBSIDIAN_PLUGINS_DIR) in message for message in messages))
        self.assertFalse(any("obsidian-vault" in message for message in messages))

    def test_removed_subagent_install_flag_is_rejected(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                setup_environment.parse_args(["--install-subagent-orchestrator"])

    def test_update_conflict_is_rejected_during_argparse(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                setup_environment.parse_args(["--update", "--no-update"])

    def test_missing_local_skills_directory_dry_run_does_not_crash(self) -> None:
        report = SilentReport()

        with tempfile.TemporaryDirectory() as temp_dir:
            setup_environment.validate_local_skills(Path(temp_dir) / "missing-skills", report, dry_run=True)

        self.assertTrue(any("dry-run would create" in message for message in report.skipped))

    def test_recommendations_always_include_obsidian_agent_check(self) -> None:
        report = SilentReport()

        setup_environment.run_recommendations(report)

        self.assertIn("Run python3 scripts/operations/obsidian/check_obsidian_panel.py", report.next_steps)

    def test_recommendations_follow_configured_check_manifest(self) -> None:
        report = SilentReport()

        setup_environment.run_recommendations(report)

        self.assertEqual(
            report.next_steps,
            [f"Run {check.shell_text()}" for check in SETUP_RECOMMENDED_CHECKS],
        )

    def test_obsidian_next_steps_add_read_only_test_only_after_install(self) -> None:
        dry_run_steps = setup_environment.obsidian_next_steps(include_read_only_test=False)
        installed_steps = setup_environment.obsidian_next_steps(include_read_only_test=True)

        self.assertNotIn("Run a harmless read-only prompt first.", dry_run_steps)
        self.assertIn("Run a harmless read-only prompt first.", installed_steps)
        self.assertIn("Run the command palette action Codex Panel: Open panel.", installed_steps)

    def test_external_layer_is_skipped_by_default(self) -> None:
        args = setup_environment.parse_args(["--dry-run"])
        args.with_external_skills = False
        report = SilentReport()

        setup_environment.install_external_layer(args, report)

        self.assertIn(
            "external skills skipped; run install script or pass --with-external-skills",
            report.skipped,
        )

    def test_external_args_are_mapped_from_setup_args(self) -> None:
        args = setup_environment.parse_args(
            [
                "--dry-run",
                "--yes",
                "--force",
                "--skip-ars",
                "--skip-subagent-orchestrator",
                "--rbs-ref",
                "main",
                "--subagent-orchestrator-ref",
                "main",
                "--no-rbs-plugin",
                "--no-subagent-orchestrator-plugin",
                "--no-update",
            ]
        )

        external_args = setup_environment.external_args_from_setup_args(args)

        self.assertTrue(external_args.dry_run)
        self.assertTrue(external_args.yes)
        self.assertTrue(external_args.force)
        self.assertTrue(external_args.skip_ars)
        self.assertTrue(external_args.skip_subagent_orchestrator)
        self.assertEqual(external_args.rbs_ref, "main")
        self.assertEqual(external_args.subagent_orchestrator_ref, "main")
        self.assertTrue(external_args.no_rbs_plugin)
        self.assertTrue(external_args.no_subagent_orchestrator_plugin)
        self.assertTrue(external_args.no_update)
        self.assertFalse(external_args.preserve_vendor_checkouts)


if __name__ == "__main__":
    unittest.main()
