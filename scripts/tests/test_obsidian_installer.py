from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock


from scripts.tests.helpers import SilentReport, install_in_directory, write_plugin_release

import setup_environment
import obsidian_agent
from project_config import OBSIDIAN_PLUGIN_DIR


class ObsidianInstallerTests(unittest.TestCase):
    def test_default_install_uses_root_vault_and_preserves_settings(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            archive_path = temp_path / "release.zip"
            write_plugin_release(archive_path)

            obsidian_dir = temp_path / ".obsidian"
            obsidian_dir.mkdir()
            community_plugins_path = obsidian_dir / "community-plugins.json"
            workspace_path = obsidian_dir / "workspace.json"
            community_plugins_path.write_text('["existing-plugin"]\n', encoding="utf-8")
            workspace_path.write_text('{"existing": true}\n', encoding="utf-8")

            args = setup_environment.parse_args(["--obsidian-release-url", archive_path.as_uri()])
            report = SilentReport()
            install_in_directory(temp_path, args, report)

            plugin_dir = temp_path / OBSIDIAN_PLUGIN_DIR
            self.assertTrue((plugin_dir / "manifest.json").is_file())
            self.assertEqual(community_plugins_path.read_text(encoding="utf-8"), '["existing-plugin"]\n')
            self.assertEqual(workspace_path.read_text(encoding="utf-8"), '{"existing": true}\n')

    def test_install_reports_obsidian_path_conflict(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            archive_path = temp_path / "release.zip"
            write_plugin_release(archive_path)

            (temp_path / ".obsidian").write_text("not a directory", encoding="utf-8")
            args = setup_environment.parse_args(["--obsidian-release-url", archive_path.as_uri()])
            report = SilentReport()
            install_in_directory(temp_path, args, report)

            self.assertTrue(any(".obsidian exists but is not a directory" in message for message in report.failed))

    def test_install_reports_missing_release_archive(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            missing_archive = temp_path / "missing.zip"
            args = setup_environment.parse_args(["--obsidian-release-url", missing_archive.as_uri()])
            report = SilentReport()

            install_in_directory(temp_path, args, report)

            self.assertTrue(any("Obsidian plugin install failed" in message for message in report.failed))

    def test_install_reports_invalid_release_archive(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            archive_path = temp_path / "release.zip"
            archive_path.write_text("not a zip", encoding="utf-8")
            args = setup_environment.parse_args(["--obsidian-release-url", archive_path.as_uri()])
            report = SilentReport()

            install_in_directory(temp_path, args, report)

            self.assertTrue(any("Obsidian plugin install failed" in message for message in report.failed))

    def test_install_reports_checksum_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            archive_path = temp_path / "release.zip"
            write_plugin_release(archive_path)
            args = setup_environment.parse_args(
                [
                    "--obsidian-release-url",
                    archive_path.as_uri(),
                    "--obsidian-release-sha256",
                    "0" * 64,
                ]
            )
            report = SilentReport()

            install_in_directory(temp_path, args, report)

            self.assertTrue(any("archive checksum mismatch" in message for message in report.failed))

    def test_force_install_preserves_existing_plugin_when_replacement_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            archive_path = temp_path / "release.zip"
            write_plugin_release(archive_path)

            plugin_dir = temp_path / OBSIDIAN_PLUGIN_DIR
            plugin_dir.mkdir(parents=True)
            existing_manifest = plugin_dir / "manifest.json"
            existing_manifest.write_text(json.dumps({"id": "existing"}), encoding="utf-8")

            args = setup_environment.parse_args(["--force", "--obsidian-release-url", archive_path.as_uri()])
            report = SilentReport()

            with mock.patch.object(obsidian_agent.shutil, "copytree", side_effect=OSError("copy failed")):
                install_in_directory(temp_path, args, report)

            self.assertTrue(any("copy failed" in message for message in report.failed))
            self.assertEqual(existing_manifest.read_text(encoding="utf-8"), json.dumps({"id": "existing"}))

    def test_sha256_file_returns_expected_digest(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "archive.zip"
            path.write_bytes(b"release")

            self.assertEqual(setup_environment.sha256_file(path), hashlib.sha256(b"release").hexdigest())

    def test_safe_extract_rejects_path_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            archive_path = Path(temp_dir) / "bad.zip"
            destination = Path(temp_dir) / "extract"
            destination.mkdir()
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("../evil.txt", "bad")

            with zipfile.ZipFile(archive_path) as archive:
                with self.assertRaises(ValueError):
                    setup_environment.safe_extract_zip(archive, destination)


if __name__ == "__main__":
    unittest.main()
