from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import setup_environment


class SilentReport(setup_environment.Report):
    def add(self, bucket: str, message: str) -> None:
        getattr(self, bucket).append(message)


def write_plugin_release(archive_path: Path) -> None:
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("plugin/manifest.json", json.dumps({"id": "obsidian-codex"}))
        archive.writestr("plugin/main.js", "module.exports = {};")
        archive.writestr("plugin/styles.css", "")


def install_in_directory(work_dir: Path, args: object, report: setup_environment.Report) -> None:
    original_cwd = Path.cwd()
    try:
        os.chdir(work_dir)
        setup_environment.install_obsidian_codex(args, report)
    finally:
        os.chdir(original_cwd)


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

            plugin_dir = temp_path / ".obsidian" / "plugins" / "obsidian-codex"
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
