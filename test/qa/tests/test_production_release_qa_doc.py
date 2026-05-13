from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RUNBOOK = ROOT / "test" / "qa" / "docs" / "production-release-qa.md"

sys.path.insert(0, str(ROOT / "scripts"))

import project_config  # noqa: E402


def make_targets() -> list[str]:
    text = (ROOT / "Makefile").read_text(encoding="utf-8")
    return [
        match.group(1)
        for match in re.finditer(r"^([A-Za-z0-9_-]+):", text, flags=re.MULTILINE)
        if not match.group(1).startswith(".")
    ]


def direct_script_paths() -> list[str]:
    return sorted(
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "scripts").iterdir()
        if path.is_file() and path.suffix in {".py", ".sh"}
    )


class ProductionReleaseQaDocTests(unittest.TestCase):
    def setUp(self) -> None:
        self.assertTrue(RUNBOOK.exists(), f"missing QA runbook: {RUNBOOK}")
        self.runbook_text = RUNBOOK.read_text(encoding="utf-8")

    def test_runbook_lives_under_root_test_folder(self) -> None:
        self.assertIn("# Production Release QA Runbook", self.runbook_text)
        self.assertFalse((ROOT / "docs" / "15-production-release-qa.md").exists())

    def test_runbook_mentions_every_make_target(self) -> None:
        for target in make_targets():
            self.assertIn(f"`make {target}`", self.runbook_text, target)

    def test_runbook_mentions_every_direct_script(self) -> None:
        for script_path in direct_script_paths():
            self.assertIn(f"`{script_path}`", self.runbook_text, script_path)

    def test_runbook_mentions_external_skill_surfaces(self) -> None:
        for skill_name in project_config.ARS_SKILLS:
            self.assertIn(f"`ars-{skill_name}`", self.runbook_text)
        for skill_name in project_config.RBS_SKILLS:
            self.assertIn(f"`{skill_name}`", self.runbook_text)
        for skill_name in project_config.SUBAGENT_ORCHESTRATOR_SKILLS:
            self.assertIn(f"`{skill_name}`", self.runbook_text)

    def test_runbook_points_to_seed_tool_and_fixture_resources(self) -> None:
        self.assertIn("`test/qa/tools/seed_release_qa.py`", self.runbook_text)
        self.assertIn("`test/qa/fixtures/release_seed/`", self.runbook_text)
        self.assertIn("synthetic", self.runbook_text.lower())
        self.assertIn("not scholarly evidence", self.runbook_text.lower())

    def test_runbook_covers_scaffold_app_usability(self) -> None:
        expected_phrases = [
            "## Scaffold App Usability QA",
            "Obsidian opens the scaffold project root as a vault",
            "Obsidian Codex can run a bounded read-only prompt",
            "Codex CLI runs from the scaffold project root",
            "Zotero and Better BibTeX can be used with `bibliography/references.bib`",
            "Quarto, Pandoc, and the configured TeX engine can render from the scaffold",
        ]
        for phrase in expected_phrases:
            self.assertIn(phrase, self.runbook_text)


if __name__ == "__main__":
    unittest.main()
