from __future__ import annotations

import tempfile
import unittest
from pathlib import Path


from scripts.tests.helpers import add_scripts_to_path


add_scripts_to_path()

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

    def test_scaffold_fixture_has_verified_citation_for_strict_release_audit(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "bibliography").mkdir()
            (root / "manuscript").mkdir()
            (root / "bibliography" / "references.bib").write_text(
                "@misc{quartoPdfBasics,\n  title = {PDF Basics}\n}\n",
                encoding="utf-8",
            )
            (root / "manuscript" / "index.qmd").write_text(
                "PDF output depends on Quarto PDF basics [@quartoPdfBasics].\n",
                encoding="utf-8",
            )

            bibliography_keys = check_citations.parse_bib_keys(root / "bibliography" / "references.bib")
            manuscript_files = check_citations.iter_supported_files(
                [root / "manuscript"],
                check_citations.IGNORED_DIRS,
                check_citations.SUPPORTED_SUFFIXES,
            )
            manuscript_keys = set().union(*(check_citations.parse_citations(path) for path in manuscript_files))

        self.assertTrue(bibliography_keys)
        self.assertTrue(manuscript_keys)
        self.assertEqual(manuscript_keys - bibliography_keys, set())


if __name__ == "__main__":
    unittest.main()
