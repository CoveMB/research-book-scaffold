from __future__ import annotations

import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import check_citations


class CheckCitationsTests(unittest.TestCase):
    def test_scan_roots_can_include_research_notes(self) -> None:
        self.assertEqual(check_citations.scan_roots(False), [Path("manuscript")])
        self.assertEqual(
            check_citations.scan_roots(True),
            [Path("manuscript"), Path("notes"), Path("research")],
        )

    def test_require_citations_fails_when_no_citations_exist(self) -> None:
        self.assertEqual(
            check_citations.exit_code_for_findings(missing=[], manuscript_keys=set(), require_citations=True),
            1,
        )


if __name__ == "__main__":
    unittest.main()
