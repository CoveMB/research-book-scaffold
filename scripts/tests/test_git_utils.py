from __future__ import annotations

import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import git_utils


class GitUtilsTests(unittest.TestCase):
    def test_changed_paths_from_status_trims_status_columns(self) -> None:
        status_text = " M .codex-plugin/plugin.json\n?? scratch.txt\n"

        self.assertEqual(
            git_utils.changed_paths_from_status(status_text),
            [".codex-plugin/plugin.json", "scratch.txt"],
        )


if __name__ == "__main__":
    unittest.main()
