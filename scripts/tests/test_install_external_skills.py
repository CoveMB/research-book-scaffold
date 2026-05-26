from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock


from scripts.tests.helpers import REMOVED_EXTERNAL_REPO_FLAGS, add_scripts_to_path, assert_parse_args_rejects


add_scripts_to_path()

import install_external_skills


class SilentReport(install_external_skills.Report):
    def add(self, bucket: str, message: str) -> None:
        getattr(self, bucket).append(message)


class InstallExternalSkillsTests(unittest.TestCase):
    def test_removed_subagent_install_flag_is_rejected(self) -> None:
        assert_parse_args_rejects(self, install_external_skills.parse_args, ["--install-subagent-orchestrator"])

    def test_update_conflict_is_rejected_during_argparse(self) -> None:
        assert_parse_args_rejects(self, install_external_skills.parse_args, ["--update", "--no-update"])

    def test_removed_update_mode_flag_is_rejected(self) -> None:
        assert_parse_args_rejects(self, install_external_skills.parse_args, ["--update-mode", "remote"])

    def test_removed_repo_override_flags_are_rejected(self) -> None:
        for flag in REMOVED_EXTERNAL_REPO_FLAGS:
            with self.subTest(flag=flag):
                assert_parse_args_rejects(
                    self,
                    install_external_skills.parse_args,
                    [flag, "https://example.invalid/repo.git"],
                )

    def test_preserve_vendor_checkouts_does_not_reset_configured_submodule(self) -> None:
        args = install_external_skills.parse_args(["--preserve-vendor-checkouts"])
        report = SilentReport()

        with (
            mock.patch.object(install_external_skills, "git_available", return_value=True),
            mock.patch.object(install_external_skills, "is_configured_submodule", return_value=True),
            mock.patch.object(install_external_skills, "run") as run_mock,
        ):
            install_external_skills.clone_or_update(
                Path("vendor/example"),
                None,
                args,
                report,
                "Example",
            )

        run_mock.assert_not_called()
        self.assertEqual(report.already_present, ["Example configured as Git submodule: vendor/example"])
        self.assertEqual(report.skipped, ["Example submodule checkout preserved"])

    def test_vendor_path_must_be_configured_submodule(self) -> None:
        args = install_external_skills.parse_args([])
        report = SilentReport()

        with (
            mock.patch.object(install_external_skills, "git_available", return_value=True),
            mock.patch.object(install_external_skills, "is_configured_submodule", return_value=False),
            mock.patch.object(install_external_skills, "run") as run_mock,
        ):
            install_external_skills.clone_or_update(
                Path("vendor/example"),
                None,
                args,
                report,
                "Example",
            )

        run_mock.assert_not_called()
        self.assertEqual(
            report.failed,
            ["Example vendor path is not configured as a Git submodule: vendor/example"],
        )

    def test_subagent_orchestrator_installer_is_project_scoped_and_available_only(self) -> None:
        command = install_external_skills.subagent_orchestrator_install_command()

        self.assertIn("--scope", command)
        self.assertEqual(command[command.index("--scope") + 1], "project")
        self.assertIn("--available-only", command)
        self.assertIn("--link-skills", command)
        self.assertIn("--with-repo-marketplace", command)
        self.assertNotIn("--activate-gate", command)
        self.assertNotIn("--with-project-agents", command)
        self.assertNotIn("--append-project-agents-md", command)
        self.assertNotIn("--with-hook", command)

    def test_subagent_orchestrator_installer_runs_after_validation_by_default(self) -> None:
        args = install_external_skills.parse_args(["--skip-ars", "--skip-rbs", "--skip-obsidian-skills"])
        report = SilentReport()

        with (
            mock.patch.object(install_external_skills, "clone_or_update"),
            mock.patch.object(install_external_skills, "validate_subagent_orchestrator", return_value=True),
            mock.patch.object(install_external_skills, "write_marketplace", return_value=True),
            mock.patch.object(install_external_skills, "write_subagent_orchestrator_install_report"),
            mock.patch.object(install_external_skills, "run") as run_mock,
        ):
            install_external_skills.install_external(args, report)

        run_mock.assert_called_once_with(
            install_external_skills.subagent_orchestrator_install_command(),
            report,
            args.dry_run,
            "installed Subagent Orchestrator project-scoped integration",
        )

    def test_subagent_orchestrator_installer_boundary_blocks_dirty_vendor(self) -> None:
        report = SilentReport()

        with (
            mock.patch.object(install_external_skills, "has_git_checkout", return_value=True),
            mock.patch.object(
                install_external_skills,
                "git_stdout",
                side_effect=["https://github.com/CoveMB/subagent-orchestration-plugin.git", " M install.sh"],
            ),
        ):
            self.assertFalse(install_external_skills.subagent_orchestrator_installer_boundary(report))

        self.assertIn("Subagent Orchestrator vendor has uncommitted changes: M install.sh", report.failed)

    def test_subagent_orchestrator_boundary_failure_does_not_expose_plugin(self) -> None:
        args = install_external_skills.parse_args(["--skip-ars", "--skip-rbs", "--skip-obsidian-skills"])
        report = SilentReport()

        with (
            mock.patch.object(install_external_skills, "clone_or_update"),
            mock.patch.object(install_external_skills, "validate_subagent_orchestrator", return_value=True),
            mock.patch.object(install_external_skills, "subagent_orchestrator_installer_boundary", return_value=False),
            mock.patch.object(install_external_skills, "write_marketplace") as write_marketplace_mock,
            mock.patch.object(install_external_skills, "write_subagent_orchestrator_install_report") as write_report_mock,
            mock.patch.object(install_external_skills, "run") as run_mock,
        ):
            install_external_skills.install_external(args, report)

        run_mock.assert_not_called()
        write_marketplace_mock.assert_not_called()
        write_report_mock.assert_not_called()

    def test_write_marketplace_preserves_skipped_existing_plugins(self) -> None:
        args = install_external_skills.parse_args(["--force"])
        report = SilentReport()
        existing_payload = {
            "name": "local-research-workflow-plugins",
            "interface": {"displayName": "Local Research Workflow Plugins"},
            "plugins": [
                install_external_skills.marketplace_entry("research-book-skills", "./vendor/research-book-skills"),
                {
                    "name": "custom-plugin",
                    "source": {"source": "local", "path": "./custom"},
                    "category": "Productivity",
                },
            ],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            marketplace = Path(temp_dir) / "marketplace.json"
            marketplace.write_text(json.dumps(existing_payload), encoding="utf-8")
            with mock.patch.object(install_external_skills, "PLUGIN_MARKETPLACE", marketplace):
                install_external_skills.write_marketplace(
                    args,
                    report,
                    include_rbs=False,
                    include_subagent_orchestrator=True,
                )
            plugin_names = [
                plugin.get("name")
                for plugin in json.loads(marketplace.read_text(encoding="utf-8"))["plugins"]
            ]

        self.assertEqual(plugin_names, ["research-book-skills", "custom-plugin", "subagent-orchestrator"])

    def test_validate_rbs_requires_expected_skill_files(self) -> None:
        report = SilentReport()

        with tempfile.TemporaryDirectory() as temp_dir:
            vendor = Path(temp_dir) / "research-book-skills"
            (vendor / ".codex-plugin").mkdir(parents=True)
            (vendor / ".codex-plugin" / "plugin.json").write_text("{}", encoding="utf-8")
            (vendor / "skills").mkdir()
            plugin_spec = install_external_skills.ExternalPluginSpec(
                "rbs",
                "RBS",
                "research-book-skills",
                "./vendor/research-book-skills",
                vendor,
                "scholarly-research-book",
                vendor / "skills",
                ("missing-skill",),
            )
            with mock.patch.object(install_external_skills, "RBS_PLUGIN_SPEC", plugin_spec):
                self.assertFalse(install_external_skills.validate_rbs(report))

        self.assertTrue(any("RBS skill missing" in message for message in report.failed))

    def test_obsidian_skills_vendor_is_validated_with_wrappers_without_vendored_scripts(self) -> None:
        args = install_external_skills.parse_args(
            ["--skip-ars", "--skip-rbs", "--skip-subagent-orchestrator", "--obsidian-skills-ref", "main"]
        )
        report = SilentReport()
        wrapper_paths = [Path(wrapper_name) for wrapper_name in install_external_skills.OBSIDIAN_SKILL_WRAPPERS.values()]

        with tempfile.TemporaryDirectory() as temp_dir:
            vendor = Path(temp_dir) / "obsidian-skills"
            vendor.mkdir()
            with (
                mock.patch.object(install_external_skills, "OBSIDIAN_SKILLS_VENDOR", vendor),
                mock.patch.object(install_external_skills, "clone_or_update") as clone_or_update_mock,
                mock.patch.object(install_external_skills, "validate_obsidian_skills", return_value=True) as validate_mock,
                mock.patch.object(install_external_skills, "create_obsidian_wrappers", return_value=wrapper_paths) as create_wrappers_mock,
                mock.patch.object(install_external_skills, "run") as run_mock,
                mock.patch.object(install_external_skills, "write_obsidian_skills_install_report") as write_report_mock,
            ):
                install_external_skills.install_external(args, report)

        clone_or_update_mock.assert_called_once_with(
            vendor,
            "main",
            args,
            report,
            "Obsidian Skills",
        )
        validate_mock.assert_called_once_with(report)
        create_wrappers_mock.assert_called_once_with(args, report)
        run_mock.assert_not_called()
        write_report_mock.assert_called_once_with(args, report, wrapper_paths)

    def test_obsidian_wrapper_text_includes_project_safety_contract(self) -> None:
        text = install_external_skills.obsidian_wrapper_text("obsidian-markdown", "obsidian-research-markdown")

        self.assertIn("name: obsidian-research-markdown", text)
        self.assertIn("obsidian-markdown", text)
        self.assertIn("vendor/obsidian-skills/skills/obsidian-markdown/SKILL.md", text)
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

    def test_validate_obsidian_skills_requires_expected_skill_files(self) -> None:
        report = SilentReport()

        with tempfile.TemporaryDirectory() as temp_dir:
            vendor = Path(temp_dir) / "obsidian-skills"
            (vendor / "skills" / "obsidian-markdown").mkdir(parents=True)
            (vendor / "skills" / "obsidian-markdown" / "SKILL.md").write_text(
                "---\nname: obsidian-markdown\n---\n",
                encoding="utf-8",
            )

            with mock.patch.object(install_external_skills, "OBSIDIAN_SKILLS_VENDOR", vendor):
                self.assertFalse(install_external_skills.validate_obsidian_skills(report))

        self.assertTrue(any("Obsidian Skills skill missing" in message for message in report.failed))


if __name__ == "__main__":
    unittest.main()
