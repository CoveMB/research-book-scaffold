from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class DocsConsistencyTests(unittest.TestCase):
    def test_setup_prerequisite_docs_do_not_require_curl_or_unzip(self) -> None:
        tooling = (ROOT / "docs/01-tooling.md").read_text(encoding="utf-8")
        runbook = (ROOT / "end-2-end-tests" / "docs" / "end-to-end.md").read_text(encoding="utf-8")
        prerequisites_start = runbook.index("## Prerequisites")
        fresh_clone_start = runbook.index("## Fresh Clone QA", prerequisites_start)
        prerequisites = runbook[prerequisites_start:fresh_clone_start]

        self.assertNotIn("| curl |", tooling)
        self.assertNotIn("| unzip |", tooling)
        self.assertNotIn("- `curl`", prerequisites)
        self.assertNotIn("- `unzip`", prerequisites)
        self.assertNotIn("curl --version", prerequisites)
        self.assertNotIn("unzip -v", prerequisites)

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
        setup_flow = "bash setup.sh\nmake doctor\nmake check-obsidian-codex\nmake check-obsidian-research-plugins\nmake audit"
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

    def test_agent_checks_cover_notes_and_obsidian_artifacts(self) -> None:
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

        self.assertIn("python3 scripts/research-writing/check_citations.py --include-notes", agents)
        self.assertIn("python3 scripts/operations/obsidian/check_obsidian_artifacts.py", agents)
        self.assertIn("when `.base` or `.canvas` files are created or changed", agents)

    def test_research_readme_lists_optional_obsidian_artifact_folders(self) -> None:
        research_readme = (ROOT / "research" / "README.md").read_text(encoding="utf-8")

        for path in ("views/", "canvases/", "web-ingest/"):
            with self.subTest(path=path):
                self.assertIn(path, research_readme)
        self.assertIn("docs/15-obsidian-skills.md", research_readme)

    def test_source_template_guidance_keeps_local_safety_rules_visible(self) -> None:
        templates_readme = (ROOT / "templates" / "README.md").read_text(encoding="utf-8")

        self.assertIn("Inspect the relevant upstream file before using it", templates_readme)
        self.assertIn("keep `skill-plugins/` unchanged", templates_readme)
        self.assertIn("local `AGENTS.md` source, citation, and evidence rules", templates_readme)

    def test_skill_plugins_readme_matches_current_setup_flow(self) -> None:
        readme = (ROOT / "skill-plugins" / "README.md").read_text(encoding="utf-8")

        self.assertIn("# Skill/Plugin Sources", readme)
        self.assertIn("Do not trust or run external source scripts until inspected.", readme)
        self.assertIn("`--skip-external-skills` is passed", readme)
        self.assertNotIn("vendored", readme)
        self.assertNotIn("--with-external-skills", readme)

    def test_native_ars_docs_cover_optional_install_and_guarded_migration(self) -> None:
        paths = [
            ROOT / "README.md",
            ROOT / "AGENTS.md",
            ROOT / "docs" / "12-external-skills-and-plugins.md",
            ROOT / "docs" / "13-academic-research-skills.md",
            ROOT / "end-2-end-tests" / "docs" / "end-to-end.md",
        ]
        combined = "\n".join(path.read_text(encoding="utf-8") for path in paths)

        self.assertIn("academic-research-skills-codex", combined)
        self.assertIn("academic-research-suite", combined)
        self.assertIn("925975e933a20893b81681d925a3404e3b7f73b7", combined)
        self.assertIn("81c7300b4066d233914563fc1c3f80512347b33c", combined)
        self.assertIn("optional", combined.lower())
        self.assertIn("uncommitted changes", combined)
        self.assertIn("divergent", combined)

        self.assertNotIn("ARS_INSTALLED.md", combined)


if __name__ == "__main__":
    unittest.main()
