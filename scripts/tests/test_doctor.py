from __future__ import annotations

import contextlib
import io
import unittest
from unittest import mock


from scripts.tests.helpers import add_scripts_to_path


add_scripts_to_path()

import doctor


class DoctorTests(unittest.TestCase):
    def test_doctor_succeeds_when_curl_and_unzip_are_missing(self) -> None:
        output = io.StringIO()

        with (
            contextlib.redirect_stdout(output),
            mock.patch.object(doctor, "change_to_project_root"),
            mock.patch.object(doctor, "check_file"),
            mock.patch.object(doctor, "check_dir"),
            mock.patch.object(doctor, "check_git_branch_tracking"),
            mock.patch.object(doctor, "command_runs", return_value=True),
            mock.patch.object(doctor, "python3_meets_minimum", return_value=True),
            mock.patch.object(
                doctor,
                "command_exists",
                side_effect=lambda command: command not in {"curl", "unzip"},
            ),
        ):
            self.assertEqual(doctor.main(), 0)

        self.assertNotIn("curl", output.getvalue())
        self.assertNotIn("unzip", output.getvalue())

    def test_doctor_still_fails_when_git_is_missing(self) -> None:
        output = io.StringIO()

        with (
            contextlib.redirect_stdout(output),
            mock.patch.object(doctor, "change_to_project_root"),
            mock.patch.object(doctor, "check_file"),
            mock.patch.object(doctor, "check_dir"),
            mock.patch.object(doctor, "check_git_branch_tracking"),
            mock.patch.object(doctor, "command_runs", return_value=True),
            mock.patch.object(doctor, "python3_meets_minimum", return_value=True),
            mock.patch.object(
                doctor,
                "command_exists",
                side_effect=lambda command: command not in {"git", "curl", "unzip"},
            ),
        ):
            self.assertEqual(doctor.main(), 1)

        self.assertIn("FAIL git missing", output.getvalue())
        self.assertNotIn("curl", output.getvalue())
        self.assertNotIn("unzip", output.getvalue())

    def test_required_command_warns_when_version_check_fails(self) -> None:
        counts = {"pass": 0, "warn": 0, "fail": 0}

        with (
            mock.patch.object(doctor, "command_exists", return_value=True),
            mock.patch.object(doctor, "command_runs", return_value=False),
            mock.patch.object(doctor, "record") as record_mock,
        ):
            doctor.check_required_command("codex", counts)

        record_mock.assert_called_once_with("warn", "codex found but version check failed", counts)

    def test_required_python_fails_when_version_is_too_old(self) -> None:
        counts = {"pass": 0, "warn": 0, "fail": 0}

        with (
            mock.patch.object(doctor, "command_exists", return_value=True),
            mock.patch.object(doctor, "python3_meets_minimum", return_value=False),
            mock.patch.object(doctor, "record") as record_mock,
        ):
            doctor.check_required_command("python3", counts)

        record_mock.assert_called_once_with("fail", "python3 3.11+ required", counts)

    def test_branch_without_upstream_reports_warning(self) -> None:
        self.assertEqual(
            doctor.branch_tracking_status("main", None, None),
            ("warn", "git branch main has no upstream configured"),
        )

    def test_ahead_branch_reports_warning(self) -> None:
        self.assertEqual(
            doctor.branch_tracking_status("main", "origin/main", (0, 3)),
            ("warn", "git branch main is 3 commit(s) ahead of origin/main"),
        )

    def test_clean_tracked_branch_reports_pass(self) -> None:
        self.assertEqual(
            doctor.branch_tracking_status("main", "origin/main", (0, 0)),
            ("pass", "git branch main tracks origin/main and is up to date"),
        )


if __name__ == "__main__":
    unittest.main()
