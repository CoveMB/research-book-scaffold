from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock


from scripts.tests.helpers import SilentReport, install_in_directory, write_plugin_release

import obsidian_agent
import setup_environment
from project_config import CODEX_PANEL_PLUGIN_ID, OBSIDIAN_PLUGIN_DIR

ROOT = Path(__file__).resolve().parents[2]


def previous_agent_plugin_id() -> str:
    return "obsidian-" + "codex"


def install_with_plugin_release(
    temp_path: Path,
    *extra_args: str,
    manifest_id: str = CODEX_PANEL_PLUGIN_ID,
) -> SilentReport:
    release_path = temp_path / "release.json"
    write_plugin_release(release_path, manifest_id=manifest_id)
    args = setup_environment.parse_args([*extra_args, "--obsidian-release-url", release_path.as_uri()])
    report = SilentReport()
    install_in_directory(temp_path, args, report)
    return report


class ObsidianInstallerTests(unittest.TestCase):
    def test_obsidian_wrapper_runs_obsidian_only_dry_run(self) -> None:
        result = subprocess.run(
            ["/bin/sh", "scripts/operations/obsidian/install_obsidian_panel.sh", "--dry-run"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("Obsidian plugin install report", result.stdout)
        self.assertNotIn("package checks", result.stdout)
        self.assertNotIn("external skills skipped", result.stdout)

    def test_default_install_uses_root_vault_and_preserves_workspace_settings(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            obsidian_dir = temp_path / ".obsidian"
            obsidian_dir.mkdir()
            community_plugins_path = obsidian_dir / "community-plugins.json"
            workspace_path = obsidian_dir / "workspace.json"
            community_plugins_path.write_text('["existing-plugin"]\n', encoding="utf-8")
            workspace_path.write_text('{"existing": true}\n', encoding="utf-8")

            install_with_plugin_release(temp_path)

            plugin_dir = temp_path / OBSIDIAN_PLUGIN_DIR
            self.assertTrue((plugin_dir / "manifest.json").is_file())
            self.assertEqual(
                json.loads(community_plugins_path.read_text(encoding="utf-8")),
                ["existing-plugin", CODEX_PANEL_PLUGIN_ID],
            )
            self.assertEqual(workspace_path.read_text(encoding="utf-8"), '{"existing": true}\n')

    def test_install_auto_enables_plugin_and_preserves_existing_enabled_plugins(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            obsidian_dir = temp_path / ".obsidian"
            obsidian_dir.mkdir()
            community_plugins_path = obsidian_dir / "community-plugins.json"
            community_plugins_path.write_text('["existing-plugin"]\n', encoding="utf-8")

            install_with_plugin_release(temp_path)

            enabled_plugins = json.loads(community_plugins_path.read_text(encoding="utf-8"))
            self.assertEqual(enabled_plugins, ["existing-plugin", CODEX_PANEL_PLUGIN_ID])

    def test_install_replaces_previous_agent_plugin_enablement(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            obsidian_dir = temp_path / ".obsidian"
            obsidian_dir.mkdir()
            community_plugins_path = obsidian_dir / "community-plugins.json"
            community_plugins_path.write_text(json.dumps(["existing-plugin", previous_agent_plugin_id()]), encoding="utf-8")

            install_with_plugin_release(temp_path)

            enabled_plugins = json.loads(community_plugins_path.read_text(encoding="utf-8"))
            self.assertEqual(enabled_plugins, ["existing-plugin", CODEX_PANEL_PLUGIN_ID])
            self.assertFalse((temp_path / ".obsidian" / "plugins" / previous_agent_plugin_id()).exists())

    def test_install_writes_codex_panel_settings_with_absolute_codex_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            fake_codex = temp_path / "bin" / "codex"
            fake_codex.parent.mkdir()
            fake_codex.write_text("#!/bin/sh\n", encoding="utf-8")
            fake_codex.chmod(0o755)

            with mock.patch.object(obsidian_agent.shutil, "which", return_value=str(fake_codex)):
                install_with_plugin_release(temp_path)

            settings_path = temp_path / OBSIDIAN_PLUGIN_DIR / "data.json"
            self.assertEqual(json.loads(settings_path.read_text(encoding="utf-8")), {"codexPath": str(fake_codex)})

    def test_install_prefers_existing_valid_codex_path_setting(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            existing_codex = temp_path / "existing" / "codex"
            existing_codex.parent.mkdir()
            existing_codex.write_text("#!/bin/sh\n", encoding="utf-8")
            existing_codex.chmod(0o755)
            path_codex = temp_path / "path" / "codex"
            path_codex.parent.mkdir()
            path_codex.write_text("#!/bin/sh\n", encoding="utf-8")
            path_codex.chmod(0o755)

            plugin_dir = temp_path / OBSIDIAN_PLUGIN_DIR
            plugin_dir.mkdir(parents=True)
            (plugin_dir / "data.json").write_text(json.dumps({"codexPath": str(existing_codex)}), encoding="utf-8")

            with mock.patch.object(obsidian_agent.shutil, "which", return_value=str(path_codex)):
                install_with_plugin_release(temp_path, "--force")

            settings_path = temp_path / OBSIDIAN_PLUGIN_DIR / "data.json"
            self.assertEqual(json.loads(settings_path.read_text(encoding="utf-8")), {"codexPath": str(existing_codex)})

    def test_install_creates_enabled_plugin_list_when_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            install_with_plugin_release(temp_path)

            community_plugins_path = temp_path / ".obsidian" / "community-plugins.json"
            enabled_plugins = json.loads(community_plugins_path.read_text(encoding="utf-8"))
            self.assertEqual(enabled_plugins, [CODEX_PANEL_PLUGIN_ID])

    def test_register_obsidian_vault_is_opt_in_and_writes_app_registry(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            registry_path = temp_path / "app-support" / "obsidian.json"

            report = install_with_plugin_release(
                temp_path,
                "--register-obsidian-vault",
                "--obsidian-registry-path",
                str(registry_path),
            )

            registry = json.loads(registry_path.read_text(encoding="utf-8"))
            registered_paths = [entry["path"] for entry in registry["vaults"].values()]
            self.assertEqual(registered_paths, [str(temp_path.resolve())])
            self.assertTrue(any("registered Obsidian vault" in message for message in report.installed))

    def test_register_obsidian_vault_preserves_existing_registry_entries(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            registry_path = temp_path / "app-support" / "obsidian.json"
            registry_path.parent.mkdir(parents=True)
            registry_path.write_text(
                json.dumps(
                    {
                        "vaults": {
                            "existing": {
                                "path": str((temp_path / "other-vault").resolve()),
                                "ts": 1,
                            }
                        },
                        "user-setting": True,
                    }
                ),
                encoding="utf-8",
            )

            install_with_plugin_release(
                temp_path,
                "--register-obsidian-vault",
                "--obsidian-registry-path",
                str(registry_path),
            )

            registry = json.loads(registry_path.read_text(encoding="utf-8"))
            registered_paths = sorted(entry["path"] for entry in registry["vaults"].values())
            self.assertEqual(
                registered_paths,
                sorted([str((temp_path / "other-vault").resolve()), str(temp_path.resolve())]),
            )
            self.assertTrue(registry["user-setting"])

    def test_register_obsidian_vault_does_not_duplicate_existing_vault_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            registry_path = temp_path / "app-support" / "obsidian.json"
            registry_path.parent.mkdir(parents=True)
            registry_path.write_text(
                json.dumps({"vaults": {"existing": {"path": str(temp_path.resolve()), "ts": 1}}}),
                encoding="utf-8",
            )

            report = install_with_plugin_release(
                temp_path,
                "--register-obsidian-vault",
                "--obsidian-registry-path",
                str(registry_path),
            )

            registry = json.loads(registry_path.read_text(encoding="utf-8"))
            self.assertEqual(list(registry["vaults"]), ["existing"])
            self.assertTrue(any("Obsidian vault already registered" in message for message in report.already_present))

    def test_register_obsidian_vault_dry_run_does_not_write_app_registry(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            registry_path = temp_path / "app-support" / "obsidian.json"
            args = setup_environment.parse_args(
                [
                    "--dry-run",
                    "--register-obsidian-vault",
                    "--obsidian-registry-path",
                    str(registry_path),
                ]
            )
            report = SilentReport()

            install_in_directory(temp_path, args, report)

            self.assertFalse(registry_path.exists())
            self.assertTrue(any("dry-run would register Obsidian vault" in message for message in report.skipped))

    def test_register_obsidian_vault_rejects_invalid_registry_shape(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            registry_path = temp_path / "app-support" / "obsidian.json"
            registry_path.parent.mkdir(parents=True)
            registry_path.write_text(json.dumps({"vaults": []}), encoding="utf-8")

            report = install_with_plugin_release(
                temp_path,
                "--register-obsidian-vault",
                "--obsidian-registry-path",
                str(registry_path),
            )

            self.assertTrue(any("expected vaults to be a JSON object" in message for message in report.failed))
            self.assertEqual(json.loads(registry_path.read_text(encoding="utf-8")), {"vaults": []})

    def test_install_rejects_invalid_enabled_plugin_list(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            obsidian_dir = temp_path / ".obsidian"
            obsidian_dir.mkdir()
            community_plugins_path = obsidian_dir / "community-plugins.json"
            community_plugins_path.write_text(json.dumps({CODEX_PANEL_PLUGIN_ID: True}), encoding="utf-8")

            report = install_with_plugin_release(temp_path)

            self.assertTrue(any("community-plugins.json" in message for message in report.failed))
            self.assertFalse((temp_path / OBSIDIAN_PLUGIN_DIR / "manifest.json").exists())
            self.assertEqual(
                json.loads(community_plugins_path.read_text(encoding="utf-8")),
                {CODEX_PANEL_PLUGIN_ID: True},
            )

    def test_latest_release_requires_codex_panel_file_assets(self) -> None:
        payload = {
            "assets": [{"name": "source.zip", "browser_download_url": "https://example.invalid/source.zip"}],
            "zipball_url": "https://example.invalid/source-code.zip",
        }

        response = mock.MagicMock()
        response.__enter__.return_value.read.return_value = json.dumps(payload).encode("utf-8")

        with mock.patch.object(obsidian_agent.urllib.request, "urlopen", return_value=response):
            with self.assertRaisesRegex(RuntimeError, "codex-panel.*main.js.*manifest.json.*styles.css"):
                obsidian_agent.latest_obsidian_release_asset_urls()

    def test_install_rejects_manifest_id_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            report = install_with_plugin_release(temp_path, manifest_id="wrong-plugin")

            self.assertTrue(any("manifest id" in message and "codex-panel" in message for message in report.failed))
            self.assertFalse((temp_path / OBSIDIAN_PLUGIN_DIR / "manifest.json").exists())

    def test_install_rejects_zip_release_url(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            zip_path = temp_path / "source.zip"
            zip_path.write_text("not used", encoding="utf-8")
            args = setup_environment.parse_args(["--obsidian-release-url", zip_path.as_uri()])
            report = SilentReport()

            install_in_directory(temp_path, args, report)

            self.assertTrue(any("release assets" in message and "zip" in message for message in report.failed))

    def test_install_reports_obsidian_path_conflict(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            (temp_path / ".obsidian").write_text("not a directory", encoding="utf-8")
            report = install_with_plugin_release(temp_path)

            self.assertTrue(any(".obsidian exists but is not a directory" in message for message in report.failed))

    def test_install_reports_missing_release_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            missing_release = temp_path / "missing.json"
            args = setup_environment.parse_args(["--obsidian-release-url", missing_release.as_uri()])
            report = SilentReport()

            install_in_directory(temp_path, args, report)

            self.assertTrue(any("Obsidian plugin install failed" in message for message in report.failed))

    def test_install_reports_invalid_release_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            release_path = temp_path / "release.json"
            release_path.write_text("not json", encoding="utf-8")
            args = setup_environment.parse_args(["--obsidian-release-url", release_path.as_uri()])
            report = SilentReport()

            install_in_directory(temp_path, args, report)

            self.assertTrue(any("Obsidian plugin install failed" in message for message in report.failed))

    def test_force_install_preserves_existing_plugin_when_replacement_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            plugin_dir = temp_path / OBSIDIAN_PLUGIN_DIR
            plugin_dir.mkdir(parents=True)
            existing_manifest = plugin_dir / "manifest.json"
            existing_manifest.write_text(json.dumps({"id": "existing"}), encoding="utf-8")

            with mock.patch.object(obsidian_agent.shutil, "copytree", side_effect=OSError("copy failed")):
                report = install_with_plugin_release(temp_path, "--force")

            self.assertTrue(any("copy failed" in message for message in report.failed))
            self.assertEqual(existing_manifest.read_text(encoding="utf-8"), json.dumps({"id": "existing"}))


if __name__ == "__main__":
    unittest.main()
