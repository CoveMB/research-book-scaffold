from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock


from scripts.tests.helpers import add_scripts_to_path


add_scripts_to_path()

import check_external_skills
from project_config import (
    ExternalPluginSpec,
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

    def write_wrapper(
        self,
        skills_dir: Path,
        wrapper_name: str,
        upstream_path: Path,
        body: str,
    ) -> Path:
        wrapper_path = skills_dir / wrapper_name / "SKILL.md"
        wrapper_path.parent.mkdir(parents=True, exist_ok=True)
        wrapper_path.write_text(
            (
                "---\n"
                f"name: {wrapper_name}\n"
                "description: Safe wrapper.\n"
                "---\n\n"
                f"Read `{upstream_path}`.\n"
                f"{body}\n"
            ),
            encoding="utf-8",
        )
        return wrapper_path

    def write_repo_skill(self, skills_dir: Path, skill_name: str, front_matter_name: str | None = None) -> Path:
        skill_path = skills_dir / skill_name / "SKILL.md"
        skill_path.parent.mkdir(parents=True, exist_ok=True)
        skill_path.write_text(
            (
                "---\n"
                f"name: {front_matter_name or skill_name}\n"
                "description: Repo-scoped skill.\n"
                "---\n\n"
                "Body.\n"
            ),
            encoding="utf-8",
        )
        return skill_path

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

    def rbs_plugin_spec(self, vendor: Path, skill_names: tuple[str, ...]) -> ExternalPluginSpec:
        return ExternalPluginSpec(
            "rbs",
            "RBS",
            "research-book-skills",
            "./vendor/research-book-skills",
            vendor,
            "scholarly-research-book",
            vendor / "skills",
            skill_names,
        )

    def subagent_plugin_spec(self, vendor: Path, skill_names: tuple[str, ...]) -> ExternalPluginSpec:
        plugin_root = vendor / "plugin" / "subagent-orchestrator"
        return ExternalPluginSpec(
            "subagent-orchestrator",
            "Subagent Orchestrator",
            "subagent-orchestrator",
            "./vendor/subagent-orchestration-plugin/plugin/subagent-orchestrator",
            plugin_root,
            "subagent-orchestrator",
            plugin_root / "skills",
            skill_names,
        )

    def write_plugin_fixture(self, plugin_spec: ExternalPluginSpec) -> None:
        plugin_json = plugin_spec.plugin_root / ".codex-plugin" / "plugin.json"
        plugin_json.parent.mkdir(parents=True, exist_ok=True)
        plugin_json.write_text(json.dumps({"name": plugin_spec.plugin_json_name}), encoding="utf-8")
        for skill_name in plugin_spec.skill_names:
            skill_path = plugin_spec.skills_root / skill_name / "SKILL.md"
            skill_path.parent.mkdir(parents=True, exist_ok=True)
            skill_path.write_text(
                f"---\nname: {skill_name}\ndescription: Upstream skill.\n---\n",
                encoding="utf-8",
            )

    def run_rbs_check(self, root: Path, plugin_spec: ExternalPluginSpec) -> list[str]:
        failures: list[str] = []
        warnings: list[str] = []
        vendor_spec = ExternalVendorSpec(
            "rbs",
            "RBS",
            plugin_spec.plugin_root,
            "https://github.com/CoveMB/research-book-skills.git",
        )

        with (
            mock.patch.object(check_external_skills, "VENDOR_SPECS_BY_KEY", {"rbs": vendor_spec}),
            mock.patch.object(check_external_skills, "RBS_PLUGIN_SPEC", plugin_spec),
            mock.patch.object(check_external_skills, "SKILLS_DIR", root / ".agents" / "skills"),
            mock.patch.object(check_external_skills, "LEGACY_RBS_PLUGIN", root / "missing-legacy"),
            mock.patch.object(check_external_skills, "check_submodule"),
            mock.patch.object(check_external_skills, "git_origin", return_value="https://github.com/CoveMB/research-book-skills.git"),
        ):
            with contextlib.redirect_stdout(io.StringIO()):
                check_external_skills.check_rbs(failures, warnings)

        self.assertEqual(warnings, [])
        return failures

    def run_subagent_check(self, root: Path, vendor: Path, plugin_spec: ExternalPluginSpec) -> list[str]:
        failures: list[str] = []
        warnings: list[str] = []
        vendor_spec = ExternalVendorSpec(
            "subagent-orchestrator",
            "Subagent Orchestrator",
            vendor,
            "https://github.com/CoveMB/subagent-orchestration-plugin.git",
        )

        with (
            mock.patch.object(
                check_external_skills,
                "VENDOR_SPECS_BY_KEY",
                {"subagent-orchestrator": vendor_spec},
            ),
            mock.patch.object(check_external_skills, "SUBAGENT_ORCHESTRATOR_PLUGIN_SPEC", plugin_spec),
            mock.patch.object(check_external_skills, "SKILLS_DIR", root / ".agents" / "skills"),
            mock.patch.object(check_external_skills, "check_submodule"),
            mock.patch.object(
                check_external_skills,
                "git_origin",
                return_value="https://github.com/CoveMB/subagent-orchestration-plugin.git",
            ),
        ):
            with contextlib.redirect_stdout(io.StringIO()):
                check_external_skills.check_subagent_orchestrator(failures, warnings)

        self.assertEqual(warnings, [])
        return failures

    def test_dirty_submodule_status_is_actionable(self) -> None:
        status = " M .codex-plugin/plugin.json\n?? scratch.txt\n"

        self.assertEqual(
            check_external_skills.submodule_dirty_message("RBS", status),
            "RBS submodule has uncommitted changes: .codex-plugin/plugin.json, scratch.txt",
        )

    def test_repo_scoped_skill_inventory_requires_every_expected_skill(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skills_dir = root / ".agents" / "skills"
            self.write_repo_skill(skills_dir, "present-skill")
            failures: list[str] = []

            with (
                mock.patch.object(check_external_skills, "SKILLS_DIR", skills_dir),
                mock.patch.object(
                    check_external_skills,
                    "REPO_SCOPED_SKILL_NAMES",
                    ("present-skill", "missing-skill"),
                ),
            ):
                with contextlib.redirect_stdout(io.StringIO()):
                    check_external_skills.check_repo_scoped_skill_inventory(failures)

        self.assertIn("repo-scoped skill missing: missing-skill", failures)

    def test_repo_scoped_skill_inventory_rejects_unconfigured_skill_directories(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skills_dir = root / ".agents" / "skills"
            self.write_repo_skill(skills_dir, "expected-skill")
            self.write_repo_skill(skills_dir, "stale-skill")
            failures: list[str] = []

            with (
                mock.patch.object(check_external_skills, "SKILLS_DIR", skills_dir),
                mock.patch.object(check_external_skills, "REPO_SCOPED_SKILL_NAMES", ("expected-skill",)),
            ):
                with contextlib.redirect_stdout(io.StringIO()):
                    check_external_skills.check_repo_scoped_skill_inventory(failures)

        self.assertIn("repo-scoped skill directory not configured: stale-skill", failures)

    def test_repo_scoped_skill_inventory_rejects_skill_directory_without_skill_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skills_dir = root / ".agents" / "skills"
            (skills_dir / "expected-skill").mkdir(parents=True)
            failures: list[str] = []

            with (
                mock.patch.object(check_external_skills, "SKILLS_DIR", skills_dir),
                mock.patch.object(check_external_skills, "REPO_SCOPED_SKILL_NAMES", ("expected-skill",)),
            ):
                with contextlib.redirect_stdout(io.StringIO()):
                    check_external_skills.check_repo_scoped_skill_inventory(failures)

        self.assertIn("repo-scoped skill file missing: expected-skill", failures)

    def test_repo_scoped_skill_inventory_requires_frontmatter_name_to_match_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skills_dir = root / ".agents" / "skills"
            self.write_repo_skill(skills_dir, "expected-skill", front_matter_name="wrong-name")
            failures: list[str] = []

            with (
                mock.patch.object(check_external_skills, "SKILLS_DIR", skills_dir),
                mock.patch.object(check_external_skills, "REPO_SCOPED_SKILL_NAMES", ("expected-skill",)),
            ):
                with contextlib.redirect_stdout(io.StringIO()):
                    check_external_skills.check_repo_scoped_skill_inventory(failures)

        self.assertIn("repo-scoped skill front matter name mismatch: expected-skill", failures)

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
            mock.patch.object(check_external_skills, "gitmodule_has_expected_github_repo", return_value=True),
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

    def test_obsidian_origin_must_match_exact_github_repository(self) -> None:
        origin = "https://github.com/attacker/kepano/obsidian-skills.git"
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.write_obsidian_fixture(root)

            failures = self.run_obsidian_check(root, origin=origin)

        self.assertIn(f"unexpected Obsidian Skills origin: {origin}", failures)

    def test_gitmodule_url_must_match_exact_github_repository(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            gitmodules = root / ".gitmodules"
            gitmodules.write_text(
                (
                    '[submodule "vendor/obsidian-skills"]\n'
                    "\tpath = vendor/obsidian-skills\n"
                    "\turl = https://github.com/attacker/kepano/obsidian-skills.git\n"
                ),
                encoding="utf-8",
            )

            with mock.patch.object(check_external_skills, "GITMODULES_PATH", gitmodules):
                self.assertFalse(
                    check_external_skills.gitmodule_has_expected_github_repo(
                        Path("vendor/obsidian-skills"),
                        "https://github.com/kepano/obsidian-skills.git",
                    )
                )

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

    def test_rbs_missing_wrapper_fails_validation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            vendor = root / "vendor" / "research-book-skills"
            plugin_spec = self.rbs_plugin_spec(vendor, ("claim-evidence-ledger",))
            self.write_plugin_fixture(plugin_spec)
            report = root / ".agents" / "skills" / "RBS_INSTALLED.md"
            report.parent.mkdir(parents=True, exist_ok=True)
            report.write_text("# Installed Research Book Skills\n", encoding="utf-8")

            failures = self.run_rbs_check(root, plugin_spec)

        expected = root / ".agents" / "skills" / "rbs-claim-evidence-ledger" / "SKILL.md"
        self.assertIn(f"RBS wrapper missing: {expected}", failures)

    def test_rbs_unconfigured_vendor_skill_fails_validation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            vendor = root / "vendor" / "research-book-skills"
            plugin_spec = self.rbs_plugin_spec(vendor, ("claim-evidence-ledger",))
            self.write_plugin_fixture(plugin_spec)
            extra_skill = vendor / "skills" / "research-intent-router" / "SKILL.md"
            extra_skill.parent.mkdir(parents=True, exist_ok=True)
            extra_skill.write_text(
                "---\nname: research-intent-router\ndescription: Upstream skill.\n---\n",
                encoding="utf-8",
            )
            upstream = plugin_spec.skills_root / "claim-evidence-ledger" / "SKILL.md"
            self.write_wrapper(
                root / ".agents" / "skills",
                "rbs-claim-evidence-ledger",
                upstream,
                (
                    "local scaffold rules win. Do not invent citations or claims. "
                    "This is workflow guidance, not evidence."
                ),
            )
            report = root / ".agents" / "skills" / "RBS_INSTALLED.md"
            report.write_text("# Installed Research Book Skills\n", encoding="utf-8")

            failures = self.run_rbs_check(root, plugin_spec)

        self.assertIn(
            "RBS vendor skills missing from wrapper config: research-intent-router",
            failures,
        )

    def test_subagent_wrapper_guard_text_is_required(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            vendor = root / "vendor" / "subagent-orchestration-plugin"
            plugin_spec = self.subagent_plugin_spec(vendor, ("subagent-orchestrator",))
            self.write_plugin_fixture(plugin_spec)
            upstream = plugin_spec.skills_root / "subagent-orchestrator" / "SKILL.md"
            self.write_wrapper(
                root / ".agents" / "skills",
                "subagent-safe-subagent-orchestrator",
                upstream,
                "AGENTS.md controls local use.",
            )
            report = root / ".agents" / "skills" / "SUBAGENT_ORCHESTRATOR_INSTALLED.md"
            report.write_text("# Installed Subagent Orchestrator\n", encoding="utf-8")

            failures = self.run_subagent_check(root, vendor, plugin_spec)

        wrapper = root / ".agents" / "skills" / "subagent-safe-subagent-orchestrator" / "SKILL.md"
        self.assertIn(f"Subagent Orchestrator wrapper safety wording missing: {wrapper}", failures)


if __name__ == "__main__":
    unittest.main()
