from __future__ import annotations

import argparse
import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import setup_environment


class SetupEnvironmentTests(unittest.TestCase):
    def test_external_layer_is_skipped_by_default(self) -> None:
        args = setup_environment.parse_args(["--dry-run"])
        args.with_external_skills = False
        report = setup_environment.Report()

        setup_environment.install_external_layer(args, report)

        self.assertIn(
            "external skills skipped; run install script or pass --with-external-skills",
            report.skipped,
        )


if __name__ == "__main__":
    unittest.main()
