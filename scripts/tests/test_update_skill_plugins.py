from __future__ import annotations

import contextlib
import io
import unittest
from pathlib import Path
from unittest import mock


from scripts.tests.helpers import add_scripts_to_path


add_scripts_to_path()

import update_skill_plugins
from project_config import (
    ARS_SOURCE,
    ExternalSourceSpec,
    OBSIDIAN_SKILLS_SOURCE,
    RBS_SOURCE,
    SUBAGENT_ORCHESTRATOR_SOURCE,
    SKILL_PLUGIN_UPDATE_HEALTH_CHECKS,
)


ROOT = Path(__file__).resolve().parents[2]


class UpdateSkillPluginsTests(unittest.TestCase):
    def fake_git_stdout(self, command: list[str], cwd: Path | None = None) -> str:
        del cwd
        if command[-2:] == ["branch", "--show-current"]:
            return "main"
        return "abc123"

    def expected_install_external_command(self, *extra_flags: str) -> tuple[str, ...]:
        return (
            "python3",
            "scripts/operations/skill_plugins/install_external_skills.py",
            "--yes",
            "--force",
            "--no-update",
            "--preserve-skill-plugin-checkouts",
            *extra_flags,
        )

    def run_update_and_capture_commands(
        self,
        args: object,
    ) -> tuple[list[update_skill_plugins.SkillPluginUpdate], list[tuple[str, ...]]]:
        calls: list[tuple[str, ...]] = []

        def fake_run(command: list[str], action: str, cwd: Path | None = None) -> None:
            del action, cwd
            calls.append(tuple(command))

        with (
            mock.patch.object(update_skill_plugins, "run_checked", side_effect=fake_run),
            mock.patch.object(update_skill_plugins, "git_stdout_required", side_effect=self.fake_git_stdout),
            mock.patch.object(update_skill_plugins, "submodule_status", return_value=""),
        ):
            with contextlib.redirect_stdout(io.StringIO()):
                summaries = update_skill_plugins.update_skill_plugins(args)

        return summaries, calls

    def test_default_flow_updates_sources_refreshes_integrations_and_runs_checks(self) -> None:
        args = update_skill_plugins.parse_args([])

        summaries, calls = self.run_update_and_capture_commands(args)

        self.assertIn(("git", "fetch", "--all", "--prune"), calls)
        self.assertIn(("git", "submodule", "sync", "--", ARS_SOURCE.as_posix()), calls)
        self.assertIn(("git", "-C", ARS_SOURCE.as_posix(), "pull", "--ff-only"), calls)
        self.assertIn(("git", "submodule", "sync", "--", RBS_SOURCE.as_posix()), calls)
        self.assertIn(("git", "-C", RBS_SOURCE.as_posix(), "pull", "--ff-only"), calls)
        self.assertIn(("git", "submodule", "sync", "--", SUBAGENT_ORCHESTRATOR_SOURCE.as_posix()), calls)
        self.assertIn(("git", "-C", SUBAGENT_ORCHESTRATOR_SOURCE.as_posix(), "pull", "--ff-only"), calls)
        self.assertIn(("git", "submodule", "sync", "--", OBSIDIAN_SKILLS_SOURCE.as_posix()), calls)
        self.assertIn(("git", "-C", OBSIDIAN_SKILLS_SOURCE.as_posix(), "pull", "--ff-only"), calls)
        self.assertIn(self.expected_install_external_command(), calls)
        for check in SKILL_PLUGIN_UPDATE_HEALTH_CHECKS:
            self.assertIn(tuple(check.command), calls)
        self.assertEqual([summary.label for summary in summaries], ["ARS", "RBS", "Subagent Orchestrator", "Obsidian Skills"])

    def test_skip_flags_limit_source_refresh_scope(self) -> None:
        args = update_skill_plugins.parse_args(["--skip-ars", "--skip-checks"])

        summaries, calls = self.run_update_and_capture_commands(args)

        self.assertNotIn(("git", "submodule", "sync", "--", ARS_SOURCE.as_posix()), calls)
        self.assertIn(("git", "submodule", "sync", "--", RBS_SOURCE.as_posix()), calls)
        self.assertIn(("git", "submodule", "sync", "--", SUBAGENT_ORCHESTRATOR_SOURCE.as_posix()), calls)
        self.assertIn(("git", "submodule", "sync", "--", OBSIDIAN_SKILLS_SOURCE.as_posix()), calls)
        self.assertIn(self.expected_install_external_command("--skip-ars"), calls)
        for check in SKILL_PLUGIN_UPDATE_HEALTH_CHECKS:
            self.assertNotIn(tuple(check.command), calls)
        self.assertEqual([summary.label for summary in summaries], ["RBS", "Subagent Orchestrator", "Obsidian Skills"])

    def test_obsidian_skills_skip_flag_limits_source_refresh_scope(self) -> None:
        args = update_skill_plugins.parse_args(["--skip-obsidian-skills", "--skip-checks"])

        summaries, calls = self.run_update_and_capture_commands(args)

        self.assertNotIn(("git", "submodule", "sync", "--", OBSIDIAN_SKILLS_SOURCE.as_posix()), calls)
        self.assertIn(self.expected_install_external_command("--skip-obsidian-skills"), calls)
        self.assertEqual([summary.label for summary in summaries], ["ARS", "RBS", "Subagent Orchestrator"])

    def test_shell_entrypoint_forwards_source_flags_to_python(self) -> None:
        shell_script = (ROOT / "scripts" / "operations" / "skill_plugins" / "update-skill-plugins.sh").read_text(
            encoding="utf-8"
        )

        self.assertIn("exec python3", shell_script)
        self.assertIn('update_skill_plugins.py" "$@"', shell_script)

    def test_subagent_skip_flag_limits_source_refresh_scope(self) -> None:
        args = update_skill_plugins.parse_args(
            ["--skip-ars", "--skip-rbs", "--skip-subagent-orchestrator", "--skip-obsidian-skills"]
        )

        with self.assertRaisesRegex(update_skill_plugins.UpdateError, "No skill/plugin sources selected"):
            update_skill_plugins.source_specs(args)

    def test_detached_source_tracks_origin_when_local_branch_missing(self) -> None:
        source = ExternalSourceSpec("example", "Example", Path("skill-plugins/example"), "https://example.invalid/repo.git")
        calls: list[tuple[str, ...]] = []

        def fake_git_stdout(command: list[str], cwd: Path | None = None) -> str:
            del cwd
            if command[-2:] == ["branch", "--show-current"]:
                return ""
            return "abc123"

        def fake_run(command: list[str], action: str, cwd: Path | None = None) -> None:
            del action, cwd
            calls.append(tuple(command))
            if command == ["git", "-C", "skill-plugins/example", "checkout", "main"]:
                raise update_skill_plugins.CommandError("missing local branch")

        with (
            mock.patch.object(update_skill_plugins, "git_stdout_required", side_effect=fake_git_stdout),
            mock.patch.object(update_skill_plugins, "run_checked", side_effect=fake_run),
        ):
            update_skill_plugins.ensure_source_branch(source)

        self.assertEqual(
            calls,
            [
                ("git", "-C", "skill-plugins/example", "checkout", "main"),
                ("git", "-C", "skill-plugins/example", "checkout", "--track", "origin/main"),
            ],
        )

    def test_dirty_source_fails_before_pull(self) -> None:
        args = update_skill_plugins.parse_args([])

        with (
            mock.patch.object(update_skill_plugins, "run_checked"),
            mock.patch.object(update_skill_plugins, "git_stdout_required", side_effect=self.fake_git_stdout),
            mock.patch.object(update_skill_plugins, "submodule_status", return_value=" M SKILL.md\n"),
        ):
            with contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaisesRegex(update_skill_plugins.UpdateError, "ARS skill/plugin source has uncommitted changes"):
                    update_skill_plugins.update_skill_plugins(args)


if __name__ == "__main__":
    unittest.main()
