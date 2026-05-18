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


if __name__ == "__main__":
    unittest.main()
