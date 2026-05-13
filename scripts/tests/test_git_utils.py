from __future__ import annotations

import unittest
from unittest import mock


from scripts.tests.helpers import add_scripts_to_path


add_scripts_to_path()

import git_utils


class GitUtilsTests(unittest.TestCase):
    def test_changed_paths_from_status_trims_status_columns(self) -> None:
        status_text = " M .codex-plugin/plugin.json\n?? scratch.txt\n"

        self.assertEqual(
            git_utils.changed_paths_from_status(status_text),
            [".codex-plugin/plugin.json", "scratch.txt"],
        )

    def test_git_stdout_required_returns_trimmed_stdout(self) -> None:
        result = mock.Mock(returncode=0, stdout="abc123\n")

        with mock.patch.object(git_utils.subprocess, "run", return_value=result) as run_mock:
            self.assertEqual(git_utils.git_stdout_required(["git", "rev-parse", "HEAD"]), "abc123")

        run_mock.assert_called_once_with(
            ["git", "rev-parse", "HEAD"],
            cwd=None,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_git_stdout_required_raises_on_failure(self) -> None:
        result = mock.Mock(returncode=128, stdout="")

        with mock.patch.object(git_utils.subprocess, "run", return_value=result):
            with self.assertRaisesRegex(git_utils.GitCommandError, "git command failed: git status"):
                git_utils.git_stdout_required(["git", "status"])


if __name__ == "__main__":
    unittest.main()
