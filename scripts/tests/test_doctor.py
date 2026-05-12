from __future__ import annotations

import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import doctor


class DoctorTests(unittest.TestCase):
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
