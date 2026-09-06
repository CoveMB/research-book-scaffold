from __future__ import annotations

import argparse
import contextlib
import io
import unittest
from pathlib import Path
from unittest import mock


from scripts.tests.helpers import add_scripts_to_path


add_scripts_to_path()

import update_skill_plugins
from project_config import (
    ARS_CODEX_PIN,
    ARS_CODEX_SOURCE,
    ExternalSourceSpec,
    OBSIDIAN_SKILLS_SOURCE,
    RBS_SOURCE,
    SKILL_PLUGIN_UPDATE_HEALTH_CHECKS,
)


ROOT = Path(__file__).resolve().parents[2]


class UpdateSkillPluginsTests(unittest.TestCase):
    def fake_git_stdout(self, command: list[str], cwd: Path | None = None) -> str:
        del cwd
        if command[-2:] == ["branch", "--show-current"]:
            return "main"
        if ARS_CODEX_SOURCE.as_posix() in command and command[-2:] == ["rev-parse", "HEAD"]:
            return ARS_CODEX_PIN
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
        args: argparse.Namespace,
    ) -> tuple[list[update_skill_plugins.SkillPluginUpdate], list[tuple[str, ...]]]:
        calls: list[tuple[str, ...]] = []

        def fake_run(command: list[str], action: str, cwd: Path | None = None) -> None:
            del action, cwd
            calls.append(tuple(command))

        with (
            mock.patch.object(update_skill_plugins, "run_checked", side_effect=fake_run),
            mock.patch.object(update_skill_plugins, "git_stdout_required", side_effect=self.fake_git_stdout),
            mock.patch.object(update_skill_plugins, "submodule_status", return_value=""),
            mock.patch.object(update_skill_plugins, "has_git_checkout", return_value=True),
            mock.patch.object(update_skill_plugins, "migrate_legacy_ars_checkout", return_value=True),
        ):
            with contextlib.redirect_stdout(io.StringIO()):
                summaries = update_skill_plugins.update_skill_plugins(args)

        return summaries, calls

    def test_default_flow_updates_sources_refreshes_integrations_and_runs_checks(self) -> None:
        args = update_skill_plugins.parse_args([])

        summaries, calls = self.run_update_and_capture_commands(args)

        self.assertIn(("git", "fetch", "--all", "--prune"), calls)
        self.assertIn(("git", "submodule", "sync", "--", ARS_CODEX_SOURCE.as_posix()), calls)
        self.assertNotIn(("git", "-C", ARS_CODEX_SOURCE.as_posix(), "fetch", "--prune"), calls)
        self.assertNotIn(("git", "-C", ARS_CODEX_SOURCE.as_posix(), "pull", "--ff-only"), calls)
        self.assertIn(("git", "submodule", "sync", "--", RBS_SOURCE.as_posix()), calls)
        self.assertIn(("git", "-C", RBS_SOURCE.as_posix(), "pull", "--ff-only"), calls)
        self.assertIn(("git", "submodule", "sync", "--", OBSIDIAN_SKILLS_SOURCE.as_posix()), calls)
        self.assertIn(("git", "-C", OBSIDIAN_SKILLS_SOURCE.as_posix(), "pull", "--ff-only"), calls)
        self.assertIn(self.expected_install_external_command(), calls)
        for check in SKILL_PLUGIN_UPDATE_HEALTH_CHECKS:
            self.assertIn(tuple(check.command), calls)
        self.assertEqual([summary.label for summary in summaries], ["ARS Codex", "RBS", "Obsidian Skills"])
        self.assertEqual(summaries[0].old_ref, ARS_CODEX_PIN)
        self.assertEqual(summaries[0].new_ref, ARS_CODEX_PIN)

    def test_skip_flags_limit_source_refresh_scope(self) -> None:
        args = update_skill_plugins.parse_args(["--skip-ars", "--skip-checks"])

        summaries, calls = self.run_update_and_capture_commands(args)

        self.assertNotIn(("git", "submodule", "sync", "--", ARS_CODEX_SOURCE.as_posix()), calls)
        self.assertIn(("git", "submodule", "sync", "--", RBS_SOURCE.as_posix()), calls)
        self.assertIn(("git", "submodule", "sync", "--", OBSIDIAN_SKILLS_SOURCE.as_posix()), calls)
        self.assertIn(self.expected_install_external_command("--skip-ars"), calls)
        for check in SKILL_PLUGIN_UPDATE_HEALTH_CHECKS:
            self.assertNotIn(tuple(check.command), calls)
        self.assertEqual([summary.label for summary in summaries], ["RBS", "Obsidian Skills"])

    def test_obsidian_skills_skip_flag_limits_source_refresh_scope(self) -> None:
        args = update_skill_plugins.parse_args(["--skip-obsidian-skills", "--skip-checks"])

        summaries, calls = self.run_update_and_capture_commands(args)

        self.assertNotIn(("git", "submodule", "sync", "--", OBSIDIAN_SKILLS_SOURCE.as_posix()), calls)
        self.assertIn(self.expected_install_external_command("--skip-obsidian-skills"), calls)
        self.assertEqual([summary.label for summary in summaries], ["ARS Codex", "RBS"])

    def test_shell_entrypoint_forwards_source_flags_to_python(self) -> None:
        shell_script = (ROOT / "scripts" / "operations" / "skill_plugins" / "update-skill-plugins.sh").read_text(
            encoding="utf-8"
        )

        self.assertIn("exec python3", shell_script)
        self.assertIn('update_skill_plugins.py" "$@"', shell_script)

    def test_all_skip_flags_reject_empty_source_selection(self) -> None:
        args = update_skill_plugins.parse_args(["--skip-ars", "--skip-rbs", "--skip-obsidian-skills"])

        with self.assertRaisesRegex(update_skill_plugins.UpdateError, "No skill/plugin sources selected"):
            update_skill_plugins.source_specs(args)

    def test_legacy_migration_failure_stops_before_source_initialization(self) -> None:
        args = update_skill_plugins.parse_args([])

        with (
            mock.patch.object(update_skill_plugins, "run_checked"),
            mock.patch.object(update_skill_plugins, "git_stdout_required", return_value="main"),
            mock.patch.object(update_skill_plugins, "migrate_legacy_ars_checkout", return_value=False),
            mock.patch.object(update_skill_plugins, "update_skill_plugin") as update_mock,
            contextlib.redirect_stdout(io.StringIO()),
        ):
            with self.assertRaisesRegex(update_skill_plugins.UpdateError, "ARS migration preflight failed"):
                update_skill_plugins.update_skill_plugins(args)

        update_mock.assert_not_called()

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
                with self.assertRaisesRegex(update_skill_plugins.UpdateError, "ARS Codex skill/plugin source has uncommitted changes"):
                    update_skill_plugins.update_skill_plugins(args)


if __name__ == "__main__":
    unittest.main()
