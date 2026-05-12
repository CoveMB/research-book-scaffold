from __future__ import annotations

import sys
import tempfile
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

    def test_empty_non_strict_scan_warns_without_failing(self) -> None:
        self.assertEqual(
            check_citations.no_citation_warning(manuscript_keys=set(), require_citations=False),
            "WARN no citations found; release-audit requires at least one verified citation.",
        )
        self.assertIsNone(check_citations.no_citation_warning(manuscript_keys={"smith2024"}, require_citations=False))
        self.assertIsNone(check_citations.no_citation_warning(manuscript_keys=set(), require_citations=True))

    def test_parse_citations_finds_bare_pandoc_citations(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "chapter.qmd"
            path.write_text("This claim follows @smith2024 and [@doe2023].\n", encoding="utf-8")

            keys = check_citations.parse_citations(path)

        self.assertEqual(keys, {"smith2024", "doe2023"})

    def test_duplicate_bibliography_keys_are_reported(self) -> None:
        text = "@book{smith2024,\n}\n@article{smith2024,\n}\n@string{ignored = \"x\"}\n"

        self.assertEqual(check_citations.duplicate_bib_keys(text), ["smith2024"])


if __name__ == "__main__":
    unittest.main()
