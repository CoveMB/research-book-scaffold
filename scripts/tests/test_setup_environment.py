from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import setup_environment
from helpers import SilentReport, working_directory
from project_config import OBSIDIAN_PLUGINS_DIR


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
                setup_environment.install_obsidian_codex(args, report)

        messages = report.skipped + report.installed + report.already_present
        self.assertTrue(any(str(OBSIDIAN_PLUGINS_DIR) in message for message in messages))
        self.assertFalse(any("obsidian-vault" in message for message in messages))

    def test_removed_obsidian_install_flag_is_rejected(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                setup_environment.parse_args(["--with-obsidian-codex"])

    def test_skip_obsidian_agent_flag_is_rejected(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                setup_environment.parse_args(["--skip-obsidian-codex"])

    def test_recommendations_always_include_obsidian_agent_check(self) -> None:
        args = setup_environment.parse_args([])
        report = SilentReport()

        setup_environment.run_recommendations(args, report)

        self.assertIn("Run python3 scripts/check_obsidian_codex.py", report.next_steps)

    def test_obsidian_next_steps_add_read_only_test_only_after_install(self) -> None:
        dry_run_steps = setup_environment.obsidian_next_steps(include_read_only_test=False)
        installed_steps = setup_environment.obsidian_next_steps(include_read_only_test=True)

        self.assertNotIn("Open the plugin sidebar and run a harmless read-only test first.", dry_run_steps)
        self.assertIn("Open the plugin sidebar and run a harmless read-only test first.", installed_steps)

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
                "--rbs-ref",
                "main",
                "--no-rbs-plugin",
                "--no-update",
            ]
        )

        external_args = setup_environment.external_args_from_setup_args(args)

        self.assertTrue(external_args.dry_run)
        self.assertTrue(external_args.yes)
        self.assertTrue(external_args.force)
        self.assertTrue(external_args.skip_ars)
        self.assertEqual(external_args.rbs_ref, "main")
        self.assertTrue(external_args.no_rbs_plugin)
        self.assertTrue(external_args.no_update)


if __name__ == "__main__":
    unittest.main()
