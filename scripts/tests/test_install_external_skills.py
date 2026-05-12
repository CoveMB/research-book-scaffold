from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest import mock


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

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


if __name__ == "__main__":
    unittest.main()
