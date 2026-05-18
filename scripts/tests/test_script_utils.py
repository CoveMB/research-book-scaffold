from __future__ import annotations

import unittest
import tempfile
import io
from pathlib import Path
from unittest import mock


from scripts.tests.helpers import add_scripts_to_path


add_scripts_to_path()

import script_utils


class ScriptUtilsTests(unittest.TestCase):
    def test_status_report_print_summary_uses_standard_sections(self) -> None:
        report = script_utils.StatusReport()
        report.installed.append("created file")
        report.warnings.append("manual check needed")

        output = io.StringIO()
        with mock.patch("sys.stdout", output):
            report.print_summary("Example report")

        self.assertEqual(
            output.getvalue(),
            "\nExample report\n"
            "\nInstalled:\n"
            "- created file\n"
            "\nAlready present:\n"
            "- none\n"
            "\nSkipped:\n"
            "- none\n"
            "\nFailed:\n"
            "- none\n"
            "\nWarnings:\n"
            "- manual check needed\n"
            "\nNext manual steps:\n"
            "- none\n",
        )

    def test_run_command_required_prints_action_and_runs_command(self) -> None:
        result = mock.Mock(returncode=0)

        with (
            mock.patch.object(script_utils.subprocess, "run", return_value=result) as run_mock,
            mock.patch("builtins.print") as print_mock,
        ):
            script_utils.run_command_required(["python3", "--version"], "check Python")

        print_mock.assert_called_once_with("RUN check Python: python3 --version")
        run_mock.assert_called_once_with(["python3", "--version"], cwd=None, text=True, check=False)

    def test_run_command_required_raises_on_nonzero_exit(self) -> None:
        result = mock.Mock(returncode=2)

        with (
            mock.patch.object(script_utils.subprocess, "run", return_value=result),
            mock.patch("builtins.print"),
        ):
            with self.assertRaisesRegex(script_utils.CommandError, "check Python failed with exit code 2"):
                script_utils.run_command_required(["python3", "--bad-flag"], "check Python")

    def test_write_text_file_creates_parent_directories(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "nested" / "note.md"

            script_utils.write_text_file(path, "content\n")

            self.assertEqual(path.read_text(encoding="utf-8"), "content\n")

    def test_write_text_if_changed_reports_current_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "note.md"
            path.write_text("same\n", encoding="utf-8")
            report = script_utils.StatusReport()

            with mock.patch.object(report, "add") as add_mock:
                result = script_utils.write_text_if_changed(path, "same\n", report, "note")

        self.assertTrue(result)
        add_mock.assert_called_once_with("already_present", f"note current: {path}")

    def test_write_text_if_changed_respects_existing_file_without_force(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "note.md"
            path.write_text("old\n", encoding="utf-8")
            report = script_utils.StatusReport()

            with mock.patch.object(report, "add") as add_mock:
                result = script_utils.write_text_if_changed(path, "new\n", report, "note")

            self.assertEqual(path.read_text(encoding="utf-8"), "old\n")

        self.assertFalse(result)
        add_mock.assert_called_once_with("skipped", f"{path} exists; use --force to replace")


if __name__ == "__main__":
    unittest.main()
