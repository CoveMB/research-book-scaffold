from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
END_TO_END_TESTS_ROOT = ROOT / "end-2-end-tests"
RUNBOOK = END_TO_END_TESTS_ROOT / "docs" / "end-to-end.md"
QA_REQUIREMENTS = END_TO_END_TESTS_ROOT / "docs" / "qa-environment-requirements.md"

sys.path.insert(0, str(ROOT / "scripts" / "lib"))

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
        for path in (ROOT / "scripts").rglob("*")
        if path.is_file()
        and path.suffix in {".py", ".sh"}
        and "tests" not in path.parts
        and "__pycache__" not in path.parts
    )


def previous_obsidian_agent_terms() -> list[str]:
    return [
        "obsidian-" + "codex",
        "Obsidian " + "Codex",
        "A" + "Kin-" + "lvy" + "ifang",
    ]


class ProductionReleaseQaDocTests(unittest.TestCase):
    def setUp(self) -> None:
        self.assertTrue(RUNBOOK.exists(), f"missing QA runbook: {RUNBOOK}")
        self.assertTrue(QA_REQUIREMENTS.exists(), f"missing QA requirements: {QA_REQUIREMENTS}")
        self.runbook_text = RUNBOOK.read_text(encoding="utf-8")
        self.qa_requirements_text = QA_REQUIREMENTS.read_text(encoding="utf-8")

    def test_runbook_lives_under_root_end_to_end_tests_folder(self) -> None:
        legacy_runbook_name = "15-production-" + "release-qa.md"
        legacy_nested_test_path = "test/" + "qa"

        self.assertIn("# Production Release QA Runbook", self.runbook_text)
        self.assertFalse((ROOT / "docs" / legacy_runbook_name).exists())
        self.assertFalse((ROOT / "test" / "qa").exists())
        self.assertFalse((ROOT / "test").exists())
        self.assertNotIn(legacy_nested_test_path, self.runbook_text)

    def test_runbook_mentions_every_make_target(self) -> None:
        for target in make_targets():
            self.assertIn(f"`make {target}`", self.runbook_text, target)

    def test_runbook_mentions_every_direct_script(self) -> None:
        for script_path in direct_script_paths():
            self.assertIn(f"`{script_path}`", self.runbook_text, script_path)

    def test_docs_and_qa_do_not_mention_previous_obsidian_agent_plugin(self) -> None:
        checked_paths = [
            ROOT / "AGENTS.md",
            ROOT / "README.md",
            ROOT / "Makefile",
            *sorted((ROOT / "docs").glob("*.md")),
            *sorted((END_TO_END_TESTS_ROOT / "docs").glob("*.md")),
        ]
        checked_text = "\n".join(path.read_text(encoding="utf-8") for path in checked_paths)

        for term in previous_obsidian_agent_terms():
            self.assertNotIn(term, checked_text)

    def test_runbook_mentions_external_skill_surfaces(self) -> None:
        for skill_name in project_config.ARS_SKILLS:
            self.assertIn(f"`ars-{skill_name}`", self.runbook_text)
        for skill_name in project_config.RBS_SKILLS:
            self.assertIn(f"`{skill_name}`", self.runbook_text)
        for skill_name in project_config.SUBAGENT_ORCHESTRATOR_SKILLS:
            self.assertIn(f"`{skill_name}`", self.runbook_text)

    def test_runbook_points_to_seed_tool_and_fixture_resources(self) -> None:
        self.assertIn("`end-2-end-tests/tools/seed_release_qa.py`", self.runbook_text)
        self.assertIn("`end-2-end-tests/fixtures/release_seed/`", self.runbook_text)
        self.assertIn("synthetic", self.runbook_text.lower())
        self.assertIn("not scholarly evidence", self.runbook_text.lower())

    def test_runbook_covers_scaffold_app_usability(self) -> None:
        expected_phrases = [
            "## Scaffold App Usability QA",
            "Codex Panel is installed by default setup unless `--skip-obsidian-panel` is used",
            "Obsidian opens the scaffold project root as a vault",
            "Codex Panel can run a bounded read-only prompt",
            "Reload plugins",
            "Codex Panel: Open panel",
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
            "Do not run `python3 end-2-end-tests/tools/seed_release_qa.py apply` from an authoring checkout",
            "Before refreshing `bibliography/references.bib`, confirm the disposable QA clone is clean",
            "`git diff -- bibliography/references.bib` shows only expected verified Zotero or Better BibTeX changes",
        ]
        for phrase in expected_phrases:
            self.assertIn(phrase, self.runbook_text)

    def test_runbook_includes_project_start_prompt_filling_qa(self) -> None:
        expected_phrases = [
            "## Project Start Script QA",
            "Run the guided initializer and fill every prompt",
            "Use synthetic QA answers",
            "`make start-project`",
            "`python3 scripts/start_project.py --dry-run --answers .qa-start-project.yml --non-interactive --skip-render`",
            "`python3 scripts/start_project.py --answers .qa-start-project.yml --non-interactive --skip-render`",
            "`python3 scripts/research-writing/check_manuscript_readiness.py`",
            "front/back matter files",
            "Do not use real private subject matter, source metadata, page numbers, quotations, or claims",
        ]
        for phrase in expected_phrases:
            self.assertIn(phrase, self.runbook_text)

    def test_vendor_update_is_not_in_routine_targeted_checks(self) -> None:
        targeted_start = self.runbook_text.index("Targeted script checks:")
        targeted_end = self.runbook_text.index("## Vendor Update QA")
        targeted_section = self.runbook_text[targeted_start:targeted_end]

        self.assertNotIn("bash scripts/operations/vendors/update-skills-vendors.sh --skip-checks", targeted_section)
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

    def test_standard_command_sequence_does_not_repeat_ci_aggregate(self) -> None:
        sequence_start = self.runbook_text.index("Standard command sequence:")
        sequence_end = self.runbook_text.index("Expected result:")
        sequence_section = self.runbook_text[sequence_start:sequence_end]

        self.assertNotIn("make ci", sequence_section)
        self.assertIn("`make ci` is the hosted-CI aggregate", self.runbook_text)
        self.assertNotIn(
            "`make doctor`, `make lint`, `make test`, `make audit`, `make release-audit`, and `make ci`",
            self.runbook_text,
        )

    def test_runbook_distinguishes_uninitialized_scaffold_from_release_ready_manuscript(self) -> None:
        self.assertIn("fresh uninitialized scaffold", self.runbook_text)
        self.assertIn("fails manuscript readiness", self.runbook_text)
        self.assertNotIn("for a fresh scaffold and for a production manuscript", self.runbook_text)

    def test_runbook_documents_tinytex_bibtex_obsidian_and_browser_qa_remediations(self) -> None:
        expected_phrases = [
            "`quarto install tinytex --update-path`",
            "`bibtex --version`",
            "`$HOME/Library/TinyTeX/bin/universal-darwin`",
            'PATH="$HOME/Library/TinyTeX/bin/universal-darwin:$PATH" make render-pdf',
            "Setup writes `.obsidian/community-plugins.json`",
            "`--register-obsidian-vault`",
            "Obsidian's app-level vault registry",
            "`codex-panel` is listed as enabled",
            "Download the latest Better BibTeX `.xpi`",
            "`python3 -m http.server --directory exports/html 4173`",
            "`http://127.0.0.1:4173/`",
        ]
        for phrase in expected_phrases:
            self.assertIn(phrase, self.runbook_text)

    def test_runbook_documents_zotero_api_quarto_warning_and_skill_smoke_tests(self) -> None:
        expected_phrases = [
            "`end-2-end-tests/docs/qa-environment-requirements.md` followed when API-based Zotero checks are in scope",
            "When API-based citation-library checks are in scope, follow `end-2-end-tests/docs/qa-environment-requirements.md`",
            "Identify at least one verified Zotero record or collection before claiming export QA",
            "Export QA is not skipped in normal citation-library QA",
            "record Better BibTeX availability and skip bibliography refresh",
            "Skill smoke tests are part of full release QA",
            "Loadability checks are not the same as live behavioral smoke tests",
            "No skill output is treated as scholarly evidence",
            "refusing to remove `site_libs` outside the project directory",
            "render internally, such as to `manuscript/_book`, then copy final artifacts into `exports/`",
            "unable to open database file",
        ]
        for phrase in expected_phrases:
            self.assertIn(phrase, self.runbook_text)

    def test_runbook_documents_template_placeholder_diagnostic(self) -> None:
        expected_phrases = [
            "Template placeholder diagnostic:",
            "`python3 scripts/research-writing/check_placeholders.py --include-templates templates` is expected to exit nonzero",
            "intentional template placeholders",
        ]
        for phrase in expected_phrases:
            self.assertIn(phrase, self.runbook_text)

    def test_qa_requirements_document_zotero_api_activation(self) -> None:
        expected_phrases = [
            "Routine writing does not require the Zotero local API",
            "Allow other applications on this computer to communicate with Zotero",
            "`http://localhost:23119/api/`",
            "A plain browser visit to the API root may show `Request not allowed`",
            "`git status --short`",
            "`git diff -- bibliography/references.bib`",
        ]
        for phrase in expected_phrases:
            self.assertIn(phrase, self.qa_requirements_text)

    def test_regular_docs_do_not_document_qa_only_zotero_api_activation(self) -> None:
        regular_docs_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (ROOT / "docs").glob("*.md")
        )

        qa_only_phrases = [
            "Allow other applications on this computer to communicate with Zotero",
            "http://localhost:23119/api/",
            "Zotero local API",
        ]
        for phrase in qa_only_phrases:
            self.assertNotIn(phrase, regular_docs_text)


if __name__ == "__main__":
    unittest.main()
