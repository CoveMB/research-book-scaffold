from __future__ import annotations

import tempfile
import unittest
from pathlib import Path


from scripts.tests.helpers import add_scripts_to_path


add_scripts_to_path()

import check_manuscript_readiness

ROOT = Path(__file__).resolve().parents[2]


class CheckManuscriptReadinessTests(unittest.TestCase):
    def test_fixture_with_generic_scaffold_title_fails(self) -> None:
        config_text = """
book:
  title: "Research Scaffold Verification Manuscript"
  chapters:
    - index.qmd
"""

        findings = check_manuscript_readiness.readiness_findings(config_text)

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].path, Path("manuscript/_quarto.yml"))
        self.assertEqual(findings[0].line_number, 3)
        self.assertEqual(findings[0].context, 'title: "Research Scaffold Verification Manuscript"')
        self.assertIn("generic scaffold identity", findings[0].category)

    def test_fixture_with_generic_index_text_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manuscript_dir = root / "manuscript"
            manuscript_dir.mkdir()
            (manuscript_dir / "_quarto.yml").write_text(
                """
book:
  title: "Initialized Project"
  chapters:
    - index.qmd
""",
                encoding="utf-8",
            )
            (manuscript_dir / "index.qmd").write_text(
                "# Overview\n\nThis manuscript scaffold is generic.\n",
                encoding="utf-8",
            )

            findings = check_manuscript_readiness.scan_release_manuscript(root)

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].path, Path("manuscript/index.qmd"))
        self.assertEqual(findings[0].line_number, 3)
        self.assertEqual(findings[0].context, "This manuscript scaffold is generic.")

    def test_sample_files_in_release_config_block_release(self) -> None:
        config_text = """
book:
  title: "Initialized Project"
  chapters:
    - index.qmd
    - chapters/01-chapter-template.qmd
  appendices:
    - appendices/appendix-template.qmd
"""

        findings = check_manuscript_readiness.readiness_findings(config_text)

        self.assertEqual(
            [finding.phrase for finding in findings],
            [
                "chapters/01-chapter-template.qmd",
                "appendices/appendix-template.qmd",
            ],
        )

    def test_project_manuscript_without_scaffold_entries_passes(self) -> None:
        config_text = """
book:
  title: "A Real Initialized Manuscript"
  chapters:
    - index.qmd
    - chapters/01-introduction.qmd
"""

        self.assertEqual(check_manuscript_readiness.readiness_findings(config_text), [])

    def test_ordinary_todos_do_not_fail_readiness(self) -> None:
        findings = check_manuscript_readiness.scan_text(
            Path("manuscript/index.qmd"),
            "# Overview\n\nTODO: verify this claim after reviewing the source note.\n",
        )

        self.assertEqual(findings, [])

    def test_default_scaffold_release_configuration_is_not_ready(self) -> None:
        findings = check_manuscript_readiness.scan_release_manuscript(ROOT)

        self.assertTrue(any(finding.phrase == "Research Scaffold Verification Manuscript" for finding in findings))
        self.assertTrue(any(finding.phrase == "This manuscript scaffold is generic." for finding in findings))

    def test_error_output_is_actionable(self) -> None:
        finding = check_manuscript_readiness.scan_text(
            Path("manuscript/_quarto.yml"),
            'book:\n  title: "Research Scaffold Verification Manuscript"\n',
        )[0]

        output = check_manuscript_readiness.format_finding(finding)

        self.assertIn("manuscript/_quarto.yml:2", output)
        self.assertIn('title: "Research Scaffold Verification Manuscript"', output)
        self.assertIn("Fix:", output)
        self.assertIn("Replace", output)


if __name__ == "__main__":
    unittest.main()
