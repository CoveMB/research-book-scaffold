from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest import mock


from scripts.tests.helpers import add_scripts_to_path


add_scripts_to_path()

import check_external_skills
from project_config import (
    ExternalVendorSpec,
    OBSIDIAN_SKILL_WRAPPERS,
    RBS_PLUGIN_JSON_NAME,
    SUBAGENT_ORCHESTRATOR_PLUGIN_JSON_NAME,
)


class CheckExternalSkillsTests(unittest.TestCase):
    def obsidian_spec(self, root: Path) -> ExternalVendorSpec:
        return ExternalVendorSpec(
            "obsidian-skills",
            "Obsidian Skills",
            root / "vendor" / "obsidian-skills",
            "https://github.com/kepano/obsidian-skills.git",
        )

    def write_obsidian_upstream_skills(self, vendor: Path) -> None:
        for skill_name in OBSIDIAN_SKILL_WRAPPERS:
            skill_path = vendor / "skills" / skill_name / "SKILL.md"
            skill_path.parent.mkdir(parents=True, exist_ok=True)
            skill_path.write_text(
                f"---\nname: {skill_name}\ndescription: Upstream skill.\n---\n",
                encoding="utf-8",
            )

    def write_obsidian_wrappers(self, skills_dir: Path, vendor: Path) -> None:
        for skill_name, wrapper_name in OBSIDIAN_SKILL_WRAPPERS.items():
            wrapper_path = skills_dir / wrapper_name / "SKILL.md"
            wrapper_path.parent.mkdir(parents=True, exist_ok=True)
            upstream_path = vendor / "skills" / skill_name / "SKILL.md"
            wrapper_path.write_text(
                (
                    "---\n"
                    f"name: {wrapper_name}\n"
                    "description: Safe Obsidian wrapper.\n"
                    "---\n\n"
                    f"Read `{upstream_path}`.\n"
                    "AGENTS.md controls local use. Do not execute vendored scripts automatically.\n"
                ),
                encoding="utf-8",
            )

    def write_obsidian_install_report(self, root: Path) -> None:
        report_path = root / ".agents" / "skills" / "OBSIDIAN_SKILLS_INSTALLED.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text("# Installed Obsidian Skills\n", encoding="utf-8")

    def write_obsidian_fixture(self, root: Path) -> tuple[Path, Path]:
        vendor = self.obsidian_spec(root).path
        skills_dir = root / ".agents" / "skills"
        self.write_obsidian_upstream_skills(vendor)
        self.write_obsidian_wrappers(skills_dir, vendor)
        self.write_obsidian_install_report(root)
        return vendor, skills_dir

    def run_obsidian_check(
        self,
        root: Path,
        origin: str = "https://github.com/kepano/obsidian-skills.git",
    ) -> list[str]:
        spec = self.obsidian_spec(root)
        failures: list[str] = []
        warnings: list[str] = []

        with (
            mock.patch.object(check_external_skills, "VENDOR_SPECS_BY_KEY", {"obsidian-skills": spec}),
            mock.patch.object(check_external_skills, "SKILLS_DIR", root / ".agents" / "skills"),
            mock.patch.object(check_external_skills, "check_submodule"),
            mock.patch.object(check_external_skills, "git_origin", return_value=origin),
        ):
            with contextlib.redirect_stdout(io.StringIO()):
                check_external_skills.check_obsidian_skills(failures, warnings)

        self.assertEqual(warnings, [])
        return failures

    def test_dirty_submodule_status_is_actionable(self) -> None:
        status = " M .codex-plugin/plugin.json\n?? scratch.txt\n"

        self.assertEqual(
            check_external_skills.submodule_dirty_message("RBS", status),
            "RBS submodule has uncommitted changes: .codex-plugin/plugin.json, scratch.txt",
        )

    def test_submodule_pointer_drift_is_actionable(self) -> None:
        self.assertEqual(
            check_external_skills.submodule_status_message(
                "RBS",
                Path("vendor/research-book-skills"),
                "+6289f6f vendor/research-book-skills (remotes/origin/HEAD)\n",
                0,
            ),
            "RBS submodule pointer differs from parent index: vendor/research-book-skills",
        )

    def test_uninitialized_submodule_is_actionable(self) -> None:
        self.assertEqual(
            check_external_skills.submodule_status_message(
                "ARS",
                Path("vendor/academic-research-skills"),
                "-153203d vendor/academic-research-skills\n",
                0,
            ),
            "ARS submodule is not initialized: vendor/academic-research-skills",
        )

    def test_conflicted_submodule_is_actionable(self) -> None:
        self.assertEqual(
            check_external_skills.submodule_status_message(
                "Subagent Orchestrator",
                Path("vendor/subagent-orchestration-plugin"),
                "Uf2185e5 vendor/subagent-orchestration-plugin\n",
                0,
            ),
            "Subagent Orchestrator submodule has merge conflicts: vendor/subagent-orchestration-plugin",
        )

    def test_expected_rbs_plugin_name_matches_upstream(self) -> None:
        self.assertEqual(RBS_PLUGIN_JSON_NAME, "scholarly-research-book")

    def test_expected_subagent_orchestrator_plugin_name_matches_upstream(self) -> None:
        self.assertEqual(SUBAGENT_ORCHESTRATOR_PLUGIN_JSON_NAME, "subagent-orchestrator")

    def test_submodule_status_failure_is_actionable(self) -> None:
        failures: list[str] = []
        failed_status = mock.Mock(returncode=1, stdout="")
        gitmodules_path = mock.Mock()
        gitmodules_path.exists.return_value = True

        with (
            mock.patch.object(check_external_skills, "GITMODULES_PATH", gitmodules_path),
            mock.patch.object(check_external_skills, "is_submodule_path", return_value=True),
            mock.patch.object(check_external_skills, "read_text", return_value="url = https://example.invalid/repo.git"),
            mock.patch.object(check_external_skills, "has_git_checkout", return_value=True),
            mock.patch.object(check_external_skills.subprocess, "run", return_value=failed_status),
        ):
            with contextlib.redirect_stdout(io.StringIO()):
                check_external_skills.check_submodule(
                    Path("vendor/example"),
                    "https://example.invalid/repo.git",
                    "Example",
                    failures,
                )

        self.assertEqual(failures, ["Example submodule status failed"])

    def test_obsidian_missing_wrapper_fails_validation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            _, skills_dir = self.write_obsidian_fixture(root)
            missing_wrapper = skills_dir / "obsidian-research-defuddle" / "SKILL.md"
            missing_wrapper.unlink()

            failures = self.run_obsidian_check(root)

        self.assertIn(f"Obsidian Skills wrapper missing: {missing_wrapper}", failures)

    def test_obsidian_missing_upstream_skill_fails_validation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            vendor, _ = self.write_obsidian_fixture(root)
            missing_upstream = vendor / "skills" / "defuddle" / "SKILL.md"
            missing_upstream.unlink()

            failures = self.run_obsidian_check(root)

        self.assertIn(f"Obsidian Skills upstream skill missing: {missing_upstream}", failures)

    def test_obsidian_unexpected_origin_fails_validation(self) -> None:
        origin = "https://github.com/example/not-obsidian-skills.git"
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_obsidian_fixture(root)

            failures = self.run_obsidian_check(root, origin=origin)

        self.assertIn(f"unexpected Obsidian Skills origin: {origin}", failures)

    def test_obsidian_wrapper_frontmatter_requires_description(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            vendor, skills_dir = self.write_obsidian_fixture(root)
            wrapper = skills_dir / "obsidian-research-markdown" / "SKILL.md"
            wrapper.write_text(
                (
                    "---\n"
                    "name: obsidian-research-markdown\n"
                    "---\n\n"
                    f"Read `{vendor / 'skills' / 'obsidian-markdown' / 'SKILL.md'}`.\n"
                    "AGENTS.md controls local use. Do not execute vendored scripts automatically.\n"
                ),
                encoding="utf-8",
            )

            failures = self.run_obsidian_check(root)

        self.assertIn(f"Obsidian Skills wrapper description missing: {wrapper}", failures)


if __name__ == "__main__":
    unittest.main()
