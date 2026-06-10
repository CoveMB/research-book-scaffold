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

import check_obsidian_panel
from project_config import CODEX_PANEL_PLUGIN_ID


def make_completed_process(returncode: int, stdout: str = "", stderr: str = "") -> object:
    return type("CompletedProcess", (), {"returncode": returncode, "stdout": stdout, "stderr": stderr})()


def write_fake_codex(path: Path) -> Path:
    path.parent.mkdir(parents=True)
    path.write_text("#!/bin/sh\n", encoding="utf-8")
    path.chmod(0o755)
    return path


def write_plugin(vault_path: Path, *, enabled: bool = True, manifest_id: str = CODEX_PANEL_PLUGIN_ID) -> Path:
    plugin_dir = vault_path / ".obsidian" / "plugins" / CODEX_PANEL_PLUGIN_ID
    plugin_dir.mkdir(parents=True)
    (plugin_dir / "main.js").write_text("", encoding="utf-8")
    (plugin_dir / "manifest.json").write_text(json.dumps({"id": manifest_id}), encoding="utf-8")
    (plugin_dir / "styles.css").write_text("", encoding="utf-8")
    codex_path = write_fake_codex(vault_path / "bin" / "codex")
    (plugin_dir / "data.json").write_text(json.dumps({"codexPath": str(codex_path)}), encoding="utf-8")
    enabled_plugins = [CODEX_PANEL_PLUGIN_ID] if enabled else []
    (vault_path / ".obsidian" / "community-plugins.json").write_text(json.dumps(enabled_plugins), encoding="utf-8")
    return plugin_dir


class CheckObsidianCodexTests(unittest.TestCase):
    def test_help_uses_argparse_usage(self) -> None:
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            with self.assertRaises(SystemExit) as error:
                check_obsidian_panel.main(["--help"])

        self.assertEqual(error.exception.code, 0)
        self.assertIn("usage: check_obsidian_panel.py", output.getvalue())

    def test_missing_vault_reports_single_failure(self) -> None:
        with mock.patch.object(check_obsidian_panel, "check_cli", return_value=True):
            with tempfile.TemporaryDirectory() as temp_dir:
                missing_vault = Path(temp_dir) / "missing"
                output = io.StringIO()

                with contextlib.redirect_stdout(output):
                    exit_code = check_obsidian_panel.main([str(missing_vault)])

            text = output.getvalue()

        self.assertEqual(exit_code, 1)
        self.assertEqual(text.count("FAIL"), 1)
        self.assertNotIn("manifest.json missing", text)

    def test_community_plugins_must_be_a_list(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            obsidian_dir = Path(temp_dir) / ".obsidian"
            obsidian_dir.mkdir()
            (obsidian_dir / "community-plugins.json").write_text(
                json.dumps({CODEX_PANEL_PLUGIN_ID: True}),
                encoding="utf-8",
            )
            output = io.StringIO()

            with contextlib.redirect_stdout(output):
                check_obsidian_panel.check_community_plugins(obsidian_dir)

        text = output.getvalue()
        self.assertIn("FAIL invalid", text)
        self.assertIn("community-plugins.json", text)
        self.assertNotIn("PASS Obsidian plugin listed as enabled", text)

    def test_disabled_community_plugin_is_a_failure(self) -> None:
        with mock.patch.object(check_obsidian_panel, "check_cli", return_value=True):
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                write_plugin(temp_path, enabled=False)
                output = io.StringIO()

                with contextlib.redirect_stdout(output):
                    exit_code = check_obsidian_panel.main([str(temp_path)])

        self.assertEqual(exit_code, 1)
        self.assertIn("FAIL Obsidian plugin is installed but not listed as enabled", output.getvalue())

    def test_manifest_id_mismatch_is_a_failure(self) -> None:
        with mock.patch.object(check_obsidian_panel, "check_cli", return_value=True):
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                write_plugin(temp_path, manifest_id="wrong-plugin")
                output = io.StringIO()

                with contextlib.redirect_stdout(output):
                    exit_code = check_obsidian_panel.main([str(temp_path)])

        self.assertEqual(exit_code, 1)
        self.assertIn("FAIL manifest id is wrong-plugin; expected codex-panel", output.getvalue())

    def test_enabled_community_plugin_passes_when_files_manifest_settings_and_cli_are_present(self) -> None:
        with mock.patch.object(check_obsidian_panel, "check_cli", return_value=True):
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                write_plugin(temp_path)
                output = io.StringIO()

                with contextlib.redirect_stdout(output):
                    exit_code = check_obsidian_panel.main([str(temp_path)])

        self.assertEqual(exit_code, 0)
        self.assertIn("PASS Obsidian plugin listed as enabled", output.getvalue())

    def test_configured_codex_path_must_exist(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            plugin_dir = write_plugin(temp_path)
            (plugin_dir / "data.json").write_text(json.dumps({"codexPath": str(temp_path / "missing")}), encoding="utf-8")
            output = io.StringIO()

            with contextlib.redirect_stdout(output):
                result = check_obsidian_panel.check_cli(plugin_dir)

        self.assertFalse(result)
        self.assertIn("FAIL configured codexPath missing", output.getvalue())

    def test_app_server_help_unavailable_is_a_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            plugin_dir = write_plugin(temp_path)
            calls: list[tuple[str, ...]] = []

            def fake_run(command: list[str], **_kwargs: object) -> object:
                calls.append(tuple(command))
                if command[1:] == ["--version"]:
                    return make_completed_process(0, stdout="codex-cli 0.130.0\n")
                return make_completed_process(2, stderr="unknown command\n")

            output = io.StringIO()
            with mock.patch.object(check_obsidian_panel.subprocess, "run", side_effect=fake_run):
                with contextlib.redirect_stdout(output):
                    result = check_obsidian_panel.check_cli(plugin_dir)

        self.assertFalse(result)
        self.assertIn(("app-server", "--help"), [call[1:] for call in calls])
        self.assertIn("FAIL codex app-server --help exited 2", output.getvalue())

    def test_configured_codex_path_and_app_server_help_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            plugin_dir = write_plugin(Path(temp_dir))

            def fake_run(command: list[str], **_kwargs: object) -> object:
                if command[1:] == ["--version"]:
                    return make_completed_process(0, stdout="codex-cli 0.130.0\n")
                return make_completed_process(0, stdout="app-server help\n")

            output = io.StringIO()
            with mock.patch.object(check_obsidian_panel.subprocess, "run", side_effect=fake_run):
                with contextlib.redirect_stdout(output):
                    result = check_obsidian_panel.check_cli(plugin_dir)

        self.assertTrue(result)
        self.assertIn("PASS codex --version: codex-cli 0.130.0", output.getvalue())
        self.assertIn("PASS codex app-server --help", output.getvalue())

    def test_successful_multiline_command_output_is_summarized(self) -> None:
        result = make_completed_process(0, stdout="first line\nsecond line\n")
        output = io.StringIO()

        with mock.patch.object(check_obsidian_panel.subprocess, "run", return_value=result):
            with contextlib.redirect_stdout(output):
                success = check_obsidian_panel.run_codex_command(["codex", "example"], "codex example")

        self.assertTrue(success)
        self.assertIn("PASS codex example: first line", output.getvalue())
        self.assertNotIn("second line", output.getvalue())


if __name__ == "__main__":
    unittest.main()
