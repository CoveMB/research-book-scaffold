from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNBOOK = ROOT / "test" / "docs" / "end-to-end.md"

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
        legacy_runbook_name = "15-production-" + "release-qa.md"
        legacy_nested_test_path = "test/" + "qa"

        self.assertIn("# Production Release QA Runbook", self.runbook_text)
        self.assertFalse((ROOT / "docs" / legacy_runbook_name).exists())
        self.assertFalse((ROOT / "test" / "qa").exists())
        self.assertNotIn(legacy_nested_test_path, self.runbook_text)

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
        self.assertIn("`test/tools/seed_release_qa.py`", self.runbook_text)
        self.assertIn("`test/fixtures/release_seed/`", self.runbook_text)
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

    def test_runbook_requires_clean_clone_before_mutating_seed_and_zotero_steps(self) -> None:
        expected_phrases = [
            "The disposable QA clone must be clean before applying the seed",
            "`git status --short` prints no tracked or untracked project changes",
            "Do not run `python3 test/tools/seed_release_qa.py apply` from an authoring checkout",
            "Before refreshing `bibliography/references.bib`, confirm the disposable QA clone is clean",
            "`git diff -- bibliography/references.bib` shows only expected verified Zotero or Better BibTeX changes",
        ]
        for phrase in expected_phrases:
            self.assertIn(phrase, self.runbook_text)

    def test_vendor_update_is_not_in_routine_targeted_checks(self) -> None:
        targeted_start = self.runbook_text.index("Targeted script checks:")
        targeted_end = self.runbook_text.index("## Vendor Update QA")
        targeted_section = self.runbook_text[targeted_start:targeted_end]

        self.assertNotIn("bash scripts/update-skills-vendors.sh --skip-checks", targeted_section)
        self.assertIn("## Vendor Update QA", self.runbook_text)
        self.assertIn("Only run this section when the release intentionally updates vendored skill repositories.", self.runbook_text)

    def test_render_qa_is_scoped_to_export_targets(self) -> None:
        expected_phrases = [
            "Run this section only when export or render QA is in scope.",
            "If render tooling is out of scope, record Quarto, Pandoc, or TeX as skipped with release impact.",
            "Missing Quarto, Pandoc, or TeX is a blocker only for releases that claim rendered artifacts.",
        ]
        for phrase in expected_phrases:
            self.assertIn(phrase, self.runbook_text)

    def test_runbook_documents_tinytex_bibtex_obsidian_and_browser_qa_remediations(self) -> None:
        expected_phrases = [
            "`quarto install tinytex --update-path`",
            "`bibtex --version`",
            "`$HOME/Library/TinyTeX/bin/universal-darwin`",
            "Setup writes `.obsidian/community-plugins.json`",
            "Download the latest Better BibTeX `.xpi`",
            "`python3 -m http.server --directory exports/html 4173`",
            "`http://127.0.0.1:4173/`",
        ]
        for phrase in expected_phrases:
            self.assertIn(phrase, self.runbook_text)


if __name__ == "__main__":
    unittest.main()
