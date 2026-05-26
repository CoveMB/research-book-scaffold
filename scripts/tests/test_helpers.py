from __future__ import annotations

import importlib
import argparse
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class HelpersTests(unittest.TestCase):
    def test_helpers_import_adds_script_import_directories_to_path(self) -> None:
        helpers = importlib.import_module("scripts.tests.helpers")

        self.assertEqual(helpers.SCRIPTS_DIR, ROOT / "scripts")
        self.assertIn(str(ROOT / "scripts"), sys.path)
        self.assertIn(str(ROOT / "scripts" / "lib"), sys.path)
        self.assertIn(str(ROOT / "scripts" / "research-writing"), sys.path)
        self.assertIn(str(ROOT / "scripts" / "operations" / "setup"), sys.path)

    def test_removed_external_repo_flags_are_shared(self) -> None:
        helpers = importlib.import_module("scripts.tests.helpers")

        self.assertEqual(
            helpers.REMOVED_EXTERNAL_REPO_FLAGS,
            ("--ars-repo", "--rbs-repo", "--subagent-orchestrator-repo", "--obsidian-skills-repo"),
        )

    def test_assert_parse_args_rejects_requires_system_exit(self) -> None:
        helpers = importlib.import_module("scripts.tests.helpers")

        def parse_args(argv: list[str]) -> argparse.Namespace:
            parser = argparse.ArgumentParser()
            parser.add_argument("--known")
            return parser.parse_args(argv)

        helpers.assert_parse_args_rejects(self, parse_args, ["--unknown"])

    def test_assert_parse_args_rejects_fails_when_args_are_accepted(self) -> None:
        helpers = importlib.import_module("scripts.tests.helpers")

        def parse_args(argv: list[str]) -> argparse.Namespace:
            parser = argparse.ArgumentParser()
            parser.add_argument("--known")
            return parser.parse_args(argv)

        with self.assertRaises(AssertionError):
            helpers.assert_parse_args_rejects(self, parse_args, ["--known", "value"])


if __name__ == "__main__":
    unittest.main()
