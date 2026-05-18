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
    "scripts/research-writing/check_placeholders.py",
    "scripts/research-writing/check_broken_internal_links.py",
    "scripts/research-writing/check_manuscript_readiness.py",
    "scripts/research-writing/render_manuscript.py",
    "scripts/research-writing/render.sh",
    "scripts/operations/setup/setup_environment.py",
    "scripts/operations/setup/environment_checks.py",
    "scripts/operations/health/doctor.py",
    "scripts/operations/health/doctor.sh",
    "scripts/operations/vendors/install_external_skills.py",
    "scripts/operations/vendors/check_external_skills.py",
    "scripts/operations/vendors/update_skills_vendors.py",
    "scripts/operations/vendors/update-skills-vendors.sh",
    "scripts/operations/obsidian/obsidian_agent.py",
    "scripts/operations/obsidian/check_obsidian_panel.py",
    "scripts/operations/obsidian/install_obsidian_panel.sh",
    "scripts/lib/project_config.py",
    "scripts/lib/script_utils.py",
    "scripts/lib/git_utils.py",
    "scripts/lib/import_paths.py",
    "scripts/lib/script_env.sh",
}

LEGACY_SCRIPT_PATHS = {
    "scripts/check_broken_internal_links.py",
    "scripts/check_citations.py",
    "scripts/check_external_skills.py",
    "scripts/check_manuscript_readiness.py",
    "scripts/check_obsidian_panel.py",
    "scripts/check_placeholders.py",
    "scripts/doctor.py",
    "scripts/doctor.sh",
    "scripts/environment_checks.py",
    "scripts/git_utils.py",
    "scripts/install_external_skills.py",
    "scripts/install_obsidian_panel.sh",
    "scripts/new_from_template.py",
    "scripts/obsidian_agent.py",
    "scripts/project_config.py",
    "scripts/render.sh",
    "scripts/render_manuscript.py",
    "scripts/script_env.sh",
    "scripts/script_utils.py",
    "scripts/setup_environment.py",
    "scripts/update-skills-vendors.sh",
    "scripts/update_skills_vendors.py",
}


def text_reference_files() -> list[Path]:
    roots = [
        ROOT / "README.md",
        ROOT / "AGENTS.md",
        ROOT / "Makefile",
        ROOT / "setup.sh",
        ROOT / "bibliography" / "README.md",
        ROOT / "docs",
        ROOT / "end-2-end-tests" / "docs",
        ROOT / ".agents" / "skills",
        ROOT / "scripts" / "README.md",
    ]
    files: list[Path] = []
    for root in roots:
        if root.is_file():
            files.append(root)
            continue
        if root.is_dir():
            files.extend(path for path in root.rglob("*") if path.is_file())
    return sorted(files)


class ProjectToolingTests(unittest.TestCase):
    def test_pyproject_declares_python_tooling_defaults(self) -> None:
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")

        self.assertIn("[tool.ruff]", pyproject)
        self.assertIn('target-version = "py311"', pyproject)
        self.assertNotIn("[tool.unittest]", pyproject)

    def test_external_vendor_specs_are_canonical(self) -> None:
        specs_by_key = {spec.key: spec for spec in project_config.EXTERNAL_VENDOR_SPECS}

        self.assertEqual(specs_by_key["ars"].label, "ARS")
        self.assertEqual(specs_by_key["ars"].path, project_config.ARS_VENDOR)
        self.assertEqual(specs_by_key["ars"].default_repo, project_config.DEFAULT_ARS_REPO)
        self.assertEqual(specs_by_key["rbs"].label, "RBS")
        self.assertEqual(specs_by_key["rbs"].path, project_config.RBS_VENDOR)
        self.assertEqual(specs_by_key["rbs"].default_repo, project_config.DEFAULT_RBS_REPO)
        self.assertEqual(specs_by_key["subagent-orchestrator"].label, "Subagent Orchestrator")
        self.assertEqual(
            specs_by_key["subagent-orchestrator"].path,
            project_config.SUBAGENT_ORCHESTRATOR_VENDOR,
        )
        self.assertEqual(
            specs_by_key["subagent-orchestrator"].default_repo,
            project_config.DEFAULT_SUBAGENT_ORCHESTRATOR_REPO,
        )

    def test_external_plugin_specs_are_canonical(self) -> None:
        specs_by_key = {spec.vendor_key: spec for spec in project_config.EXTERNAL_PLUGIN_SPECS}

        self.assertEqual(specs_by_key["rbs"].marketplace_name, project_config.RBS_MARKETPLACE_NAME)
        self.assertEqual(specs_by_key["rbs"].plugin_path, project_config.MARKETPLACE_PLUGIN_PATH)
        self.assertEqual(specs_by_key["rbs"].skills_root, project_config.RBS_VENDOR / "skills")
        self.assertEqual(specs_by_key["subagent-orchestrator"].marketplace_name, "subagent-orchestrator")
        self.assertEqual(
            specs_by_key["subagent-orchestrator"].plugin_root,
            project_config.SUBAGENT_ORCHESTRATOR_PLUGIN_ROOT,
        )

    def test_scripts_are_grouped_by_use_case(self) -> None:
        for relative_path in sorted(SCRIPT_LAYOUT):
            self.assertTrue((ROOT / relative_path).exists(), relative_path)

        for relative_path in sorted(LEGACY_SCRIPT_PATHS):
            self.assertFalse((ROOT / relative_path).exists(), relative_path)

    def test_docs_and_commands_reference_grouped_script_paths(self) -> None:
        references_by_file = {
            path.relative_to(ROOT).as_posix(): sorted(
                legacy_path
                for legacy_path in LEGACY_SCRIPT_PATHS
                if legacy_path in path.read_text(encoding="utf-8")
            )
            for path in text_reference_files()
        }
        stale_references = {
            path: references for path, references in references_by_file.items() if references
        }

        self.assertEqual(stale_references, {})


if __name__ == "__main__":
    unittest.main()
