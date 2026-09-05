from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
from scripts.tests.helpers import add_scripts_to_path


add_scripts_to_path()

import project_config
import install_external_skills


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

EXPECTED_ARS_SKILLS = (
    "deep-research",
    "academic-paper",
    "academic-paper-reviewer",
    "academic-pipeline",
)
EXPECTED_RBS_SKILLS = (
    "research-intent-router",
    "dyslexia-research-companion",
    "dictation-to-research-notes",
    "reading-load-reducer",
    "dyslexia-friendly-prose-editor",
    "research-book-orchestrator",
    "scholarly-research-agenda",
    "systematic-source-discovery",
    "discovery-runner-deduper",
    "annotation-to-source-note",
    "extraction-table-builder",
    "literature-review-mapper",
    "annotated-bibliography-builder",
    "methodology-source-auditor",
    "claim-evidence-ledger",
    "claim-traceability-graph",
    "argument-architecture",
    "counterargument-peer-review",
    "chapter-architecture",
    "scholarly-prose-editor",
    "citation-integrity-auditor",
    "figure-table-integrity-auditor",
    "scholarly-integrity-gate",
    "ai-human-workflow-log",
    "rights-privacy-release-auditor",
    "manuscript-continuity-editor",
    "case-study-integration",
    "book-proposal-scholarship",
    "book-comps-verifier",
)
EXPECTED_RBS_WRAPPERS = tuple((skill_name, f"rbs-{skill_name}") for skill_name in EXPECTED_RBS_SKILLS)
EXPECTED_OBSIDIAN_WRAPPERS = (
    ("obsidian-markdown", "obsidian-research-markdown"),
    ("obsidian-bases", "obsidian-research-bases"),
    ("json-canvas", "obsidian-research-canvas"),
    ("obsidian-cli", "obsidian-research-cli"),
    ("defuddle", "obsidian-research-defuddle"),
)

CI_PYTHON_VERSION = "3.11"


class ProjectToolingTests(unittest.TestCase):
    def test_pyproject_declares_python_tooling_defaults(self) -> None:
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")

        self.assertIn("[project.optional-dependencies]", pyproject)
        self.assertIn('dev = ["ruff==0.15.16", "pyright==1.1.410"]', pyproject)
        self.assertIn("[build-system]", pyproject)
        self.assertIn('build-backend = "setuptools.build_meta"', pyproject)
        self.assertIn("[tool.setuptools]", pyproject)
        self.assertIn("packages = []", pyproject)
        self.assertIn("[tool.ruff]", pyproject)
        self.assertIn('target-version = "py311"', pyproject)
        self.assertIn("[tool.ruff.lint]", pyproject)
        self.assertIn('ignore = ["E402"]', pyproject)
        self.assertIn("[tool.pyright]", pyproject)
        self.assertIn('pythonVersion = "3.11"', pyproject)
        self.assertIn('typeCheckingMode = "standard"', pyproject)
        self.assertIn('include = ["scripts", "end-2-end-tests/tools", "end-2-end-tests/tests"]', pyproject)
        self.assertIn('extraPaths = [', pyproject)
        self.assertIn('"scripts/lib"', pyproject)
        self.assertIn('"scripts/research-writing"', pyproject)
        self.assertIn('"scripts/operations/health"', pyproject)
        self.assertIn('"scripts/operations/obsidian"', pyproject)
        self.assertIn('"scripts/operations/setup"', pyproject)
        self.assertIn('"scripts/operations/skill_plugins"', pyproject)
        self.assertNotIn("[tool.unittest]", pyproject)

    def test_external_source_specs_are_canonical(self) -> None:
        specs_by_key = {spec.key: spec for spec in project_config.EXTERNAL_SOURCE_SPECS}

        self.assertEqual(specs_by_key["ars"].label, "ARS")
        self.assertEqual(specs_by_key["ars"].path, project_config.ARS_SOURCE)
        self.assertEqual(specs_by_key["ars"].default_repo, project_config.DEFAULT_ARS_REPO)
        self.assertEqual(specs_by_key["rbs"].label, "RBS")
        self.assertEqual(specs_by_key["rbs"].path, project_config.RBS_SOURCE)
        self.assertEqual(specs_by_key["rbs"].default_repo, project_config.DEFAULT_RBS_REPO)
        self.assertEqual(specs_by_key["obsidian-skills"].label, "Obsidian Skills")
        self.assertEqual(specs_by_key["obsidian-skills"].path, project_config.OBSIDIAN_SKILLS_SOURCE)
        self.assertEqual(
            specs_by_key["obsidian-skills"].default_repo,
            project_config.DEFAULT_OBSIDIAN_SKILLS_REPO,
        )
        self.assertEqual(
            tuple(project_config.ARS_SKILLS),
            EXPECTED_ARS_SKILLS,
        )
        self.assertEqual(
            tuple(project_config.RBS_SKILLS),
            EXPECTED_RBS_SKILLS,
        )
        self.assertEqual(tuple(project_config.RBS_SKILL_WRAPPERS.items()), EXPECTED_RBS_WRAPPERS)
        self.assertEqual(
            tuple(project_config.OBSIDIAN_SKILLS),
            tuple(skill_name for skill_name, _ in EXPECTED_OBSIDIAN_WRAPPERS),
        )
        self.assertEqual(tuple(project_config.OBSIDIAN_SKILL_WRAPPERS.items()), EXPECTED_OBSIDIAN_WRAPPERS)
    def test_repo_scoped_skill_manifest_matches_skill_directories(self) -> None:
        skill_files = (ROOT / project_config.SKILLS_DIR).glob("*/SKILL.md")
        actual_skill_names = {skill_file.parent.name for skill_file in skill_files}
        expected_skill_names = set(project_config.REPO_SCOPED_SKILL_NAMES)

        self.assertEqual(len(project_config.REPO_SCOPED_SKILL_NAMES), len(expected_skill_names))
        self.assertEqual(actual_skill_names, expected_skill_names)

    def test_external_wrappers_preserve_frontmatter_and_generated_parity(self) -> None:
        def front_matter(text: str) -> str:
            return text[: text.index("\n---\n", 4) + 5]

        wrappers: list[tuple[str, str, str]] = []
        wrappers.extend(
            (
                f"ars-{skill_name}",
                (
                    "---\n"
                    f"name: ars-{skill_name}\n"
                    "description: Use this wrapper to consult the external Academic Research Skills "
                    f"`{skill_name}` workflow after reading and validating the upstream instructions.\n"
                    "---\n"
                ),
                install_external_skills.ars_wrapper_text(skill_name),
            )
            for skill_name in EXPECTED_ARS_SKILLS
        )
        wrappers.extend(
            (
                wrapper_name,
                (
                    "---\n"
                    f"name: {wrapper_name}\n"
                    "description: Use when the external Research Book Skills "
                    f"`{skill_name}` guidance is needed through the local scaffold safety wrapper.\n"
                    "---\n"
                ),
                install_external_skills.rbs_wrapper_text(skill_name),
            )
            for skill_name, wrapper_name in EXPECTED_RBS_WRAPPERS
        )
        wrappers.extend(
            (
                wrapper_name,
                (
                    "---\n"
                    f"name: {wrapper_name}\n"
                    "description: Use when the external Obsidian Skills "
                    f"`{skill_name}` guidance is needed for a research vault while preserving local citation, evidence, and folder rules.\n"
                    "---\n"
                ),
                install_external_skills.obsidian_wrapper_text(skill_name, wrapper_name),
            )
            for skill_name, wrapper_name in EXPECTED_OBSIDIAN_WRAPPERS
        )

        self.assertEqual(len(wrappers), 38)
        for wrapper_name, expected_front_matter, expected_text in wrappers:
            with self.subTest(wrapper=wrapper_name):
                wrapper_path = ROOT / project_config.SKILLS_DIR / wrapper_name / "SKILL.md"
                text = wrapper_path.read_text(encoding="utf-8")
                self.assertEqual(front_matter(text), expected_front_matter)
                self.assertEqual(text, expected_text)

    def test_representative_external_wrappers_load_read_only(self) -> None:
        expected_wrappers = {
            "ars-academic-paper": "skill-plugins/academic-research-skills/academic-paper/SKILL.md",
            "rbs-claim-evidence-ledger": "skill-plugins/research-book-skills/skills/claim-evidence-ledger/SKILL.md",
            "obsidian-research-markdown": "skill-plugins/obsidian-skills/skills/obsidian-markdown/SKILL.md",
        }

        for wrapper_name, upstream_path in expected_wrappers.items():
            with self.subTest(wrapper=wrapper_name):
                wrapper_path = ROOT / project_config.SKILLS_DIR / wrapper_name / "SKILL.md"
                text = wrapper_path.read_text(encoding="utf-8")
                self.assertIn(f"# {wrapper_name}\n", text)
                self.assertIn(f"Read `{upstream_path}` before use.", text)

    def test_rbs_config_exposes_all_external_plugin_skills(self) -> None:
        source_skill_names = {
            skill_file.parent.name
            for skill_file in (ROOT / project_config.RBS_PLUGIN_SPEC.skills_root).glob("*/SKILL.md")
        }

        self.assertEqual(set(project_config.RBS_SKILLS), source_skill_names)

    def test_external_plugin_specs_are_canonical(self) -> None:
        specs_by_key = {spec.source_key: spec for spec in project_config.EXTERNAL_PLUGIN_SPECS}

        self.assertEqual(specs_by_key["rbs"].marketplace_name, project_config.RBS_MARKETPLACE_NAME)
        self.assertEqual(specs_by_key["rbs"].plugin_path, project_config.MARKETPLACE_PLUGIN_PATH)
        self.assertEqual(specs_by_key["rbs"].skills_root, project_config.RBS_SOURCE / "skills")

    def test_scripts_are_grouped_by_use_case(self) -> None:
        for relative_path in sorted(SCRIPT_LAYOUT):
            self.assertTrue((ROOT / relative_path).exists(), relative_path)

    def test_makefile_exposes_obsidian_artifact_check(self) -> None:
        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")

        self.assertIn("check-obsidian-artifacts", makefile)
        self.assertIn("python3 scripts/operations/obsidian/check_obsidian_artifacts.py", makefile)

    def test_lint_target_runs_compileall_and_ruff(self) -> None:
        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")

        self.assertIn(
            "lint: .require-ruff\n"
            "\t$(VENV_PYTHON) -m compileall -q scripts end-2-end-tests/tools end-2-end-tests/tests\n"
            "\t$(VENV_PYTHON) -m ruff check scripts end-2-end-tests/tools end-2-end-tests/tests",
            makefile,
        )

    def test_makefile_exposes_pyright_typecheck(self) -> None:
        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")

        self.assertIn("typecheck", makefile)
        self.assertIn(".require-pyright:", makefile)
        self.assertIn("Pyright is not installed in $(VENV). Run: make install-dev", makefile)
        self.assertIn(
            "typecheck: .require-pyright\n"
            "\t$(VENV_PYTHON) -m pyright",
            makefile,
        )

    def test_makefile_exposes_python_dev_tool_install(self) -> None:
        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")

        self.assertIn("PYTHON ?= python3", makefile)
        self.assertIn("VENV ?= .venv", makefile)
        self.assertIn("VENV_PYTHON := $(VENV)/bin/python", makefile)
        self.assertIn("install-dev", makefile)
        self.assertIn("$(PYTHON) -m venv $(VENV)", makefile)
        self.assertIn('$(VENV_PYTHON) -m pip install ".[dev]"', makefile)
        self.assertIn(".require-ruff:", makefile)
        self.assertIn("Project virtual environment missing. Run: make install-dev", makefile)
        self.assertIn("Ruff is not installed in $(VENV). Run: make install-dev", makefile)

    def test_makefile_exposes_obsidian_research_plugin_commands(self) -> None:
        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")

        self.assertIn("check-obsidian-research-plugins", makefile)
        self.assertIn("python3 scripts/operations/obsidian/obsidian_research_plugins.py check", makefile)
        self.assertIn("install-obsidian-research-plugins", makefile)
        self.assertIn("bash scripts/operations/obsidian/install_obsidian_research_plugins.sh", makefile)

    def test_makefile_obsidian_targets_pin_project_root_vault(self) -> None:
        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")

        self.assertNotIn("check-obsidian-panel:", makefile)
        self.assertIn(
            "check-obsidian-codex:\n"
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
            "ci: lint typecheck test check-citations check-links check-external-skills check-obsidian-artifacts",
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
            "Install Python dev tools",
            "Lint Python scripts and QA tools",
            "Type-check Python scripts and QA tools",
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
        self.assertIn("run: make install-dev", workflow)
        self.assertIn("run: make typecheck", workflow)
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
        self.assertIn(".venv/", gitignore)
        self.assertIn("*.egg-info/", gitignore)

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
            "--force --skip-ars --skip-rbs --preserve-skill-plugin-checkouts"
        )

        self.assertIn(expected, docs)
        self.assertIn(expected, scripts_readme)


if __name__ == "__main__":
    unittest.main()
