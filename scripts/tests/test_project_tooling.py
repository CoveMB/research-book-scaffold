from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
from scripts.tests.helpers import add_scripts_to_path


add_scripts_to_path()

import project_config


class ProjectToolingTests(unittest.TestCase):
    def test_pyproject_declares_python_tooling_defaults(self) -> None:
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")

        self.assertIn("[tool.ruff]", pyproject)
        self.assertIn('target-version = "py311"', pyproject)
        self.assertIn("[tool.unittest]", pyproject)

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


if __name__ == "__main__":
    unittest.main()
