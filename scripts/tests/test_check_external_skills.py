from __future__ import annotations

import contextlib
import io
import unittest
from pathlib import Path
from unittest import mock


from scripts.tests.helpers import add_scripts_to_path


add_scripts_to_path()

import check_external_skills
from project_config import RBS_PLUGIN_JSON_NAME, SUBAGENT_ORCHESTRATOR_PLUGIN_JSON_NAME


class CheckExternalSkillsTests(unittest.TestCase):
    def test_dirty_submodule_status_is_actionable(self) -> None:
        status = " M .codex-plugin/plugin.json\n?? scratch.txt\n"

        self.assertEqual(
            check_external_skills.submodule_dirty_message("RBS", status),
            "RBS submodule has uncommitted changes: .codex-plugin/plugin.json, scratch.txt",
        )

    def test_expected_rbs_plugin_name_matches_upstream(self) -> None:
        self.assertEqual(RBS_PLUGIN_JSON_NAME, "scholarly-research-book")

    def test_expected_subagent_orchestrator_plugin_name_matches_upstream(self) -> None:
        self.assertEqual(SUBAGENT_ORCHESTRATOR_PLUGIN_JSON_NAME, "subagent-orchestrator")

    def test_submodule_status_allows_new_working_tree_checkout(self) -> None:
        failures: list[str] = []
        failed_status = mock.Mock(returncode=1, stdout="")
        gitmodules_path = mock.Mock()
        gitmodules_path.exists.return_value = True

        with (
            mock.patch.object(check_external_skills, "GITMODULES_PATH", gitmodules_path),
            mock.patch.object(check_external_skills, "is_submodule_path", return_value=True),
            mock.patch.object(check_external_skills, "read_text", return_value="url = https://example.invalid/repo.git"),
            mock.patch.object(check_external_skills, "has_git_checkout", return_value=True),
            mock.patch.object(check_external_skills.subprocess, "run", return_value=failed_status),
        ):
            with contextlib.redirect_stdout(io.StringIO()):
                check_external_skills.check_submodule(
                    Path("vendor/example"),
                    "https://example.invalid/repo.git",
                    "Example",
                    failures,
                )

        self.assertEqual(failures, [])


if __name__ == "__main__":
    unittest.main()
