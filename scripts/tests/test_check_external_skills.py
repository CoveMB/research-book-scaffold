from __future__ import annotations

import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import check_external_skills
from project_config import RBS_PLUGIN_JSON_NAME


class CheckExternalSkillsTests(unittest.TestCase):
    def test_dirty_submodule_status_is_actionable(self) -> None:
        status = " M .codex-plugin/plugin.json\n?? scratch.txt\n"

        self.assertEqual(
            check_external_skills.submodule_dirty_message("RBS", status),
            "RBS submodule has uncommitted changes: .codex-plugin/plugin.json, scratch.txt",
        )

    def test_expected_rbs_plugin_name_matches_upstream(self) -> None:
        self.assertEqual(RBS_PLUGIN_JSON_NAME, "scholarly-research-book")


if __name__ == "__main__":
    unittest.main()
