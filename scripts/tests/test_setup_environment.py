from __future__ import annotations

import argparse
import contextlib
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import setup_environment


class SilentReport(setup_environment.Report):
    def add(self, bucket: str, message: str) -> None:
        getattr(self, bucket).append(message)


class SetupEnvironmentTests(unittest.TestCase):
    def test_default_obsidian_vault_is_project_root(self) -> None:
        args = setup_environment.parse_args(["--dry-run"])

        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = Path.cwd()
            try:
                os.chdir(temp_dir)

                vault_path = setup_environment.vault_path_from_args(args)
            finally:
                os.chdir(original_cwd)

        self.assertEqual(vault_path, Path(temp_dir).resolve())

    def test_default_setup_initializes_root_vault_without_nested_folder(self) -> None:
        args = setup_environment.parse_args(["--dry-run"])
        report = SilentReport()

        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = Path.cwd()
            try:
                os.chdir(temp_dir)

                setup_environment.install_obsidian_codex(args, report)
            finally:
                os.chdir(original_cwd)

        messages = report.skipped + report.installed + report.already_present
        self.assertTrue(any(".obsidian/plugins" in message for message in messages))
        self.assertFalse(any("obsidian-vault" in message for message in messages))

    def test_removed_obsidian_install_flag_is_rejected(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                setup_environment.parse_args(["--with-obsidian-codex"])

    def test_recommendations_skip_obsidian_check_when_plugin_skipped(self) -> None:
        args = setup_environment.parse_args(["--skip-obsidian-codex"])
        report = SilentReport()

        setup_environment.run_recommendations(args, report)

        self.assertNotIn("Run python3 scripts/check_obsidian_codex.py", report.next_steps)

    def test_external_layer_is_skipped_by_default(self) -> None:
        args = setup_environment.parse_args(["--dry-run"])
        args.with_external_skills = False
        report = SilentReport()

        setup_environment.install_external_layer(args, report)

        self.assertIn(
            "external skills skipped; run install script or pass --with-external-skills",
            report.skipped,
        )


if __name__ == "__main__":
    unittest.main()
