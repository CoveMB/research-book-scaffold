from __future__ import annotations

import unittest
from pathlib import Path
from unittest import mock


from scripts.tests.helpers import add_scripts_to_path


add_scripts_to_path()

import install_external_skills


class SilentReport(install_external_skills.Report):
    def add(self, bucket: str, message: str) -> None:
        getattr(self, bucket).append(message)


class InstallExternalSkillsTests(unittest.TestCase):
    def test_preserve_vendor_checkouts_does_not_reset_configured_submodule(self) -> None:
        args = install_external_skills.parse_args(["--preserve-vendor-checkouts"])
        report = SilentReport()

        with (
            mock.patch.object(install_external_skills, "git_available", return_value=True),
            mock.patch.object(install_external_skills, "is_configured_submodule", return_value=True),
            mock.patch.object(install_external_skills, "run") as run_mock,
        ):
            install_external_skills.clone_or_update(
                "https://example.invalid/repo.git",
                Path("vendor/example"),
                None,
                args,
                report,
                "Example",
            )

        run_mock.assert_not_called()
        self.assertEqual(report.already_present, ["Example configured as Git submodule: vendor/example"])
        self.assertEqual(report.skipped, ["Example submodule checkout preserved"])

    def test_subagent_orchestrator_installer_is_project_scoped_and_available_only(self) -> None:
        command = install_external_skills.subagent_orchestrator_install_command()

        self.assertIn("--scope", command)
        self.assertEqual(command[command.index("--scope") + 1], "project")
        self.assertIn("--available-only", command)
        self.assertIn("--link-skills", command)
        self.assertIn("--with-repo-marketplace", command)
        self.assertNotIn("--activate-gate", command)
        self.assertNotIn("--with-project-agents", command)


if __name__ == "__main__":
    unittest.main()
