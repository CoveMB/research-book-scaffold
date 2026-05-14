from __future__ import annotations

import importlib
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


if __name__ == "__main__":
    unittest.main()
