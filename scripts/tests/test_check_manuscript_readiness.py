from __future__ import annotations

import unittest
from pathlib import Path


from scripts.tests.helpers import add_scripts_to_path


add_scripts_to_path()

import check_manuscript_readiness

ROOT = Path(__file__).resolve().parents[2]


class CheckManuscriptReadinessTests(unittest.TestCase):
    def test_scaffold_title_and_sample_files_block_release(self) -> None:
        config_text = """
book:
  title: "Untitled Scholarly Manuscript"
  chapters:
    - index.qmd
    - chapters/01-chapter-template.qmd
  appendices:
    - appendices/appendix-template.qmd
"""

        findings = check_manuscript_readiness.readiness_findings(config_text)

        self.assertEqual(
            findings,
            [
                "manuscript title is still Untitled Scholarly Manuscript",
                "sample chapter is still included in manuscript/_quarto.yml",
                "sample appendix is still included in manuscript/_quarto.yml",
            ],
        )

    def test_project_manuscript_without_scaffold_entries_passes(self) -> None:
        config_text = """
book:
  title: "Project Manuscript"
  chapters:
    - index.qmd
    - chapters/01-introduction.qmd
"""

        self.assertEqual(check_manuscript_readiness.readiness_findings(config_text), [])

    def test_default_scaffold_release_configuration_is_ready(self) -> None:
        config_text = (ROOT / "manuscript" / "_quarto.yml").read_text(encoding="utf-8")

        self.assertEqual(check_manuscript_readiness.readiness_findings(config_text), [])


if __name__ == "__main__":
    unittest.main()
