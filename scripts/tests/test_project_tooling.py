from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
from scripts.tests.helpers import add_scripts_to_path


add_scripts_to_path()

import project_config


SCRIPT_LAYOUT = {
    "scripts/research-writing/new_from_template.py",
    "scripts/research-writing/check_citations.py",
    "scripts/research-writing/check_external_references.py",
    "scripts/research-writing/check_placeholders.py",
    "scripts/research-writing/check_broken_internal_links.py",
    "scripts/research-writing/check_manuscript_readiness.py",
    "scripts/research-writing/render_manuscript.py",
    "scripts/research-writing/render.sh",
    "scripts/operations/setup/setup_environment.py",
    "scripts/operations/setup/environment_checks.py",
    "scripts/operations/health/doctor.py",
    "scripts/operations/health/doctor.sh",
    "scripts/operations/skill_plugins/install_external_skills.py",
    "scripts/operations/skill_plugins/check_external_skills.py",
    "scripts/operations/skill_plugins/update_skill_plugins.py",
    "scripts/operations/skill_plugins/update-skill-plugins.sh",
    "scripts/operations/obsidian/obsidian_agent.py",
    "scripts/operations/obsidian/obsidian_research_plugins.py",
    "scripts/operations/obsidian/check_obsidian_panel.py",
    "scripts/operations/obsidian/check_obsidian_artifacts.py",
    "scripts/operations/obsidian/install_obsidian_panel.sh",
    "scripts/operations/obsidian/install_obsidian_research_plugins.sh",
    "scripts/lib/project_config.py",
    "scripts/lib/script_utils.py",
    "scripts/lib/git_utils.py",
    "scripts/lib/import_paths.py",
    "scripts/lib/script_env.sh",
}

OBSIDIAN_SKILL_WRAPPERS = {
    "obsidian-markdown": "obsidian-research-markdown",
    "obsidian-bases": "obsidian-research-bases",
    "json-canvas": "obsidian-research-canvas",
    "obsidian-cli": "obsidian-research-cli",
    "defuddle": "obsidian-research-defuddle",
}

SUBAGENT_ORCHESTRATOR_SKILL_WRAPPERS = {
    "using-subagent-orchestrator": "subagent-safe-using-subagent-orchestrator",
    "subagent-orchestrator": "subagent-safe-subagent-orchestrator",
}

CI_PYTHON_VERSION = "3.11"


class ProjectToolingTests(unittest.TestCase):
    def test_pyproject_declares_python_tooling_defaults(self) -> None:
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")

        self.assertIn("[tool.ruff]", pyproject)
        self.assertIn('target-version = "py311"', pyproject)
        self.assertNotIn("[tool.unittest]", pyproject)

    def test_external_source_specs_are_canonical(self) -> None:
        specs_by_key = {spec.key: spec for spec in project_config.EXTERNAL_SOURCE_SPECS}

        self.assertEqual(specs_by_key["ars"].label, "ARS")
        self.assertEqual(specs_by_key["ars"].path, project_config.ARS_SOURCE)
        self.assertEqual(specs_by_key["ars"].default_repo, project_config.DEFAULT_ARS_REPO)
        self.assertEqual(specs_by_key["rbs"].label, "RBS")
        self.assertEqual(specs_by_key["rbs"].path, project_config.RBS_SOURCE)
        self.assertEqual(specs_by_key["rbs"].default_repo, project_config.DEFAULT_RBS_REPO)
        self.assertEqual(specs_by_key["subagent-orchestrator"].label, "Subagent Orchestrator")
        self.assertEqual(
            specs_by_key["subagent-orchestrator"].path,
            project_config.SUBAGENT_ORCHESTRATOR_SOURCE,
        )
        self.assertEqual(
            specs_by_key["subagent-orchestrator"].default_repo,
            project_config.DEFAULT_SUBAGENT_ORCHESTRATOR_REPO,
        )
        self.assertEqual(specs_by_key["obsidian-skills"].label, "Obsidian Skills")
        self.assertEqual(specs_by_key["obsidian-skills"].path, project_config.OBSIDIAN_SKILLS_SOURCE)
        self.assertEqual(
            specs_by_key["obsidian-skills"].default_repo,
            project_config.DEFAULT_OBSIDIAN_SKILLS_REPO,
        )
        self.assertEqual(
            project_config.OBSIDIAN_SKILLS,
            ["obsidian-markdown", "obsidian-bases", "json-canvas", "obsidian-cli", "defuddle"],
        )
        self.assertEqual(project_config.OBSIDIAN_SKILL_WRAPPERS, OBSIDIAN_SKILL_WRAPPERS)
        self.assertEqual(
            project_config.RBS_SKILL_WRAPPERS,
            {skill_name: f"rbs-{skill_name}" for skill_name in project_config.RBS_SKILLS},
        )
        self.assertEqual(
            project_config.SUBAGENT_ORCHESTRATOR_SKILL_WRAPPERS,
            SUBAGENT_ORCHESTRATOR_SKILL_WRAPPERS,
        )

    def test_repo_scoped_skill_manifest_matches_skill_directories(self) -> None:
        skill_files = (ROOT / project_config.SKILLS_DIR).glob("*/SKILL.md")
        actual_skill_names = {skill_file.parent.name for skill_file in skill_files}
        expected_skill_names = set(project_config.REPO_SCOPED_SKILL_NAMES)

        self.assertEqual(len(project_config.REPO_SCOPED_SKILL_NAMES), len(expected_skill_names))
        self.assertEqual(actual_skill_names, expected_skill_names)

    def test_obsidian_safety_wrappers_exist_with_frontmatter_and_contract(self) -> None:
        for upstream_name, wrapper_name in OBSIDIAN_SKILL_WRAPPERS.items():
            with self.subTest(wrapper=wrapper_name):
                upstream_path = project_config.OBSIDIAN_SKILLS_SOURCE / "skills" / upstream_name / "SKILL.md"
                wrapper_path = ROOT / project_config.SKILLS_DIR / wrapper_name / "SKILL.md"

                self.assertTrue(wrapper_path.exists(), wrapper_path)
                text = wrapper_path.read_text(encoding="utf-8")

                self.assertTrue(text.startswith("---\n"))
                self.assertIn("\n---\n", text[4:])
                self.assertIn(f"name: {wrapper_name}", text)
                self.assertIn("description:", text)
                self.assertIn(upstream_name, text)
                self.assertIn(upstream_path.as_posix(), text)
                self.assertIn("Read the upstream `SKILL.md` before use.", text)
                self.assertIn("AGENTS.md", text)
                self.assertIn("citation workflow", text)
                self.assertIn("evidence rules", text)
                self.assertIn("folder responsibilities", text)
                self.assertIn("## Allowed Reads", text)
                self.assertIn("## Allowed Writes", text)
                self.assertIn("## Forbidden Actions", text)
                self.assertIn("## Validation Steps", text)
                self.assertIn("## Failure Modes", text)

    def test_rbs_safety_wrappers_exist_with_frontmatter_and_contract(self) -> None:
        for upstream_name, wrapper_name in project_config.RBS_SKILL_WRAPPERS.items():
            with self.subTest(wrapper=wrapper_name):
                upstream_path = project_config.RBS_SOURCE / "skills" / upstream_name / "SKILL.md"
                wrapper_path = ROOT / project_config.SKILLS_DIR / wrapper_name / "SKILL.md"

                self.assertTrue(wrapper_path.exists(), wrapper_path)
                text = wrapper_path.read_text(encoding="utf-8")

                self.assertTrue(text.startswith("---\n"))
                self.assertIn(f"name: {wrapper_name}", text)
                self.assertIn("description:", text)
                self.assertIn(upstream_path.as_posix(), text)
                self.assertIn("local scaffold rules win", text)
                self.assertIn("Do not invent citations or claims", text)
                self.assertIn("source notes", text)
                self.assertIn("claim ledgers", text)
                self.assertIn("audits", text)
                self.assertIn("bibliography checks", text)
                self.assertIn("workflow guidance, not evidence", text)

    def test_rbs_config_exposes_all_external_plugin_skills(self) -> None:
        source_skill_names = {
            skill_file.parent.name
            for skill_file in (ROOT / project_config.RBS_PLUGIN_SPEC.skills_root).glob("*/SKILL.md")
        }

        self.assertEqual(set(project_config.RBS_SKILLS), source_skill_names)

    def test_subagent_safety_wrappers_exist_with_guarded_contract(self) -> None:
        for upstream_name, wrapper_name in project_config.SUBAGENT_ORCHESTRATOR_SKILL_WRAPPERS.items():
            with self.subTest(wrapper=wrapper_name):
                upstream_path = (
                    project_config.SUBAGENT_ORCHESTRATOR_PLUGIN_SPEC.skills_root / upstream_name / "SKILL.md"
                )
                wrapper_path = ROOT / project_config.SKILLS_DIR / wrapper_name / "SKILL.md"

                self.assertTrue(wrapper_path.exists(), wrapper_path)
                text = wrapper_path.read_text(encoding="utf-8")

                self.assertTrue(text.startswith("---\n"))
                self.assertIn(f"name: {wrapper_name}", text)
                self.assertIn("description:", text)
                self.assertIn(upstream_path.as_posix(), text)
                self.assertIn("bounded orchestration materially helps", text)
                self.assertIn("not use automatically for every research task", text)
                self.assertIn("Subagent output is not evidence", text)
                self.assertIn("no global hooks, global agents, or global config", text)
                self.assertIn("project, citation, manuscript, audit, and skill/plugin source rules win", text)

    def test_external_plugin_specs_are_canonical(self) -> None:
        specs_by_key = {spec.source_key: spec for spec in project_config.EXTERNAL_PLUGIN_SPECS}

        self.assertEqual(specs_by_key["rbs"].marketplace_name, project_config.RBS_MARKETPLACE_NAME)
        self.assertEqual(specs_by_key["rbs"].plugin_path, project_config.MARKETPLACE_PLUGIN_PATH)
        self.assertEqual(specs_by_key["rbs"].skills_root, project_config.RBS_SOURCE / "skills")
        self.assertEqual(specs_by_key["subagent-orchestrator"].marketplace_name, "subagent-orchestrator")
        self.assertEqual(
            specs_by_key["subagent-orchestrator"].plugin_root,
            project_config.SUBAGENT_ORCHESTRATOR_PLUGIN_ROOT,
        )

    def test_scripts_are_grouped_by_use_case(self) -> None:
        for relative_path in sorted(SCRIPT_LAYOUT):
            self.assertTrue((ROOT / relative_path).exists(), relative_path)

    def test_subagent_make_target_skips_other_external_sources(self) -> None:
        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")

        self.assertIn("--skip-ars --skip-rbs --skip-obsidian-skills", makefile)

    def test_makefile_exposes_obsidian_artifact_check(self) -> None:
        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")

        self.assertIn("check-obsidian-artifacts", makefile)
        self.assertIn("python3 scripts/operations/obsidian/check_obsidian_artifacts.py", makefile)

    def test_makefile_exposes_obsidian_research_plugin_commands(self) -> None:
        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")

        self.assertIn("check-obsidian-research-plugins", makefile)
        self.assertIn("python3 scripts/operations/obsidian/obsidian_research_plugins.py check", makefile)
        self.assertIn("install-obsidian-research-plugins", makefile)
        self.assertIn("bash scripts/operations/obsidian/install_obsidian_research_plugins.sh", makefile)

    def test_makefile_obsidian_targets_pin_project_root_vault(self) -> None:
        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")

        self.assertIn(
            "check-obsidian-panel:\n"
            "\tpython3 scripts/operations/obsidian/check_obsidian_panel.py .",
            makefile,
        )
        self.assertIn(
            "check-obsidian-research-plugins:\n"
            "\tpython3 scripts/operations/obsidian/obsidian_research_plugins.py check .",
            makefile,
        )
        self.assertIn(
            "install-obsidian-panel:\n"
            "\tbash scripts/operations/obsidian/install_obsidian_panel.sh --obsidian-vault .",
            makefile,
        )
        self.assertIn(
            "install-obsidian-research-plugins:\n"
            "\tbash scripts/operations/obsidian/install_obsidian_research_plugins.sh --obsidian-vault .",
            makefile,
        )

    def test_ci_target_uses_hosted_safe_checks_without_placeholder_gate(self) -> None:
        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
        workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

        self.assertIn(
            "ci: lint test check-citations check-links check-external-skills check-obsidian-artifacts",
            makefile,
        )
        self.assertIn("audit: test check-placeholders", makefile)
        self.assertNotIn("ci: lint audit", makefile)
        self.assertNotIn("ci: lint release-audit", makefile)
        self.assertNotIn("make check-placeholders", workflow)

    def test_pre_commit_hooks_do_not_run_placeholder_check(self) -> None:
        pre_commit_config = (ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")
        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")

        self.assertNotIn("make-check-placeholders", pre_commit_config)
        self.assertIn("scaffold-audit: test check-placeholders", makefile)
        self.assertIn("audit: scaffold-audit", makefile)
        self.assertIn("release-audit: test check-placeholders", makefile)

    def test_manuscript_readiness_is_not_required_for_base_scaffold_audits(self) -> None:
        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")

        self.assertIn(
            "release-audit: test check-placeholders check-citations-strict check-links "
            "check-external-skills check-obsidian-artifacts",
            makefile,
        )
        self.assertIn("manuscript-release-audit: release-audit check-manuscript-readiness", makefile)
        self.assertNotIn("release-audit: test check-placeholders check-citations-strict check-links check-manuscript-readiness", makefile)

    def test_github_workflow_uses_descriptive_scaffold_check_steps(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

        expected_steps = [
            "Check out repository and skill/plugin submodules",
            f"Set up Python {CI_PYTHON_VERSION}",
            "Show Python, Git, and Make versions",
            "Compile-check Python scripts and QA tools",
            "Run script and end-to-end tests",
            "Check manuscript citations against bibliography",
            "Check wiki-style internal links",
            "Validate external skill integration",
            "Validate Obsidian artifact files",
        ]
        for step_name in expected_steps:
            with self.subTest(step_name=step_name):
                self.assertIn(f"- name: {step_name}", workflow)

        self.assertIn("uses: actions/checkout@v6", workflow)
        self.assertIn("uses: actions/setup-python@v6", workflow)
        self.assertNotIn("Run CI checks", workflow)

    def test_github_workflow_uses_single_declared_python_floor(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

        self.assertIn(f"name: Scaffold QA (Python {CI_PYTHON_VERSION})", workflow)
        self.assertIn(f'python-version: "{CI_PYTHON_VERSION}"', workflow)
        self.assertNotIn("strategy:", workflow)
        self.assertNotIn("matrix:", workflow)
        self.assertNotIn("matrix.python-version", workflow)
        self.assertNotIn('- "3.12"', workflow)
        self.assertNotIn('- "3.13"', workflow)

    def test_gitignore_keeps_vault_defaults_and_plugin_config_trackable(self) -> None:
        gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")

        self.assertNotIn(".obsidian/plugins/codex-panel/", gitignore)
        self.assertNotIn(".obsidian/plugins/obsidian-zotero-desktop-connector/", gitignore)
        self.assertNotIn(".obsidian/plugins/obsidian-pandoc-reference-list/", gitignore)
        self.assertIn(".pandoc/", gitignore)
        self.assertNotIn(".obsidian/community-plugins.json", gitignore)

    def test_ieee_csl_is_tracked_and_used_by_default_quarto_config(self) -> None:
        ieee_csl = ROOT / "bibliography" / "csl" / "ieee.csl"
        quarto_config = (ROOT / "manuscript" / "_quarto.yml").read_text(encoding="utf-8")

        self.assertTrue(ieee_csl.is_file())
        self.assertIn("http://www.zotero.org/styles/ieee", ieee_csl.read_text(encoding="utf-8"))
        self.assertIn("csl: ../bibliography/csl/ieee.csl", quarto_config)

    def test_obsidian_manual_refresh_docs_include_force(self) -> None:
        docs = (ROOT / "docs" / "15-obsidian-skills.md").read_text(encoding="utf-8")
        scripts_readme = (ROOT / "scripts" / "README.md").read_text(encoding="utf-8")
        expected = (
            "python3 scripts/operations/skill_plugins/install_external_skills.py --yes "
            "--force --skip-ars --skip-rbs --skip-subagent-orchestrator --preserve-skill-plugin-checkouts"
        )

        self.assertIn(expected, docs)
        self.assertIn(expected, scripts_readme)


if __name__ == "__main__":
    unittest.main()
