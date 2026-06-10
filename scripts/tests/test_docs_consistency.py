from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class DocsConsistencyTests(unittest.TestCase):
    def test_obsidian_vault_is_documented_as_default_skippable_recommendation(self) -> None:
        tooling = (ROOT / "docs/01-tooling.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("| Obsidian project-root vault |", tooling)
        self.assertIn(
            "| Obsidian project-root vault | Project-root notes and local navigation | Recommended; setup default unless skipped |",
            tooling,
        )
        self.assertIn(
            "| Codex Panel Obsidian plugin | Agent work inside Obsidian | Recommended; setup default unless skipped |",
            tooling,
        )
        self.assertIn("--skip-obsidian-panel", readme)
        self.assertNotIn("| Obsidian or Markdown vault | Project-root notes and local navigation | Optional |", tooling)

    def test_new_user_setup_docs_include_obsidian_plugin_checks(self) -> None:
        setup_flow = "bash setup.sh\nmake check-obsidian-panel\nmake check-obsidian-research-plugins\nmake audit"
        docs = [
            ROOT / "README.md",
            ROOT / "docs" / "12-external-skills-and-plugins.md",
            ROOT / "docs" / "15-obsidian-skills.md",
        ]

        for path in docs:
            with self.subTest(path=path):
                self.assertIn(setup_flow, path.read_text(encoding="utf-8"))

    def test_end_to_end_codex_panel_qa_exercises_repo_scoped_skill_discovery(self) -> None:
        runbook = (ROOT / "end-2-end-tests" / "docs" / "end-to-end.md").read_text(encoding="utf-8")

        self.assertIn("Skill discovery smoke prompt", runbook)
        self.assertIn("$obsidian-research-markdown", runbook)
        self.assertIn("without manual repo marketplace plugin installation", runbook)


if __name__ == "__main__":
    unittest.main()
