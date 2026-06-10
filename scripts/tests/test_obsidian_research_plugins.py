from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts.tests.helpers import SilentReport, working_directory, write_plugin_release

import obsidian_research_plugins
import setup_environment
from project_config import OBSIDIAN_RESEARCH_PLUGIN_IDS, REQUIRED_OBSIDIAN_PLUGIN_FILES


def write_research_plugin_releases(temp_path: Path) -> dict[str, str]:
    release_urls: dict[str, str] = {}
    for plugin_id in OBSIDIAN_RESEARCH_PLUGIN_IDS:
        release_path = temp_path / f"{plugin_id}-release.json"
        write_plugin_release(release_path, manifest_id=plugin_id)
        release_urls[plugin_id] = release_path.as_uri()
    return release_urls


def setup_args_with_releases(release_urls: dict[str, str], *extra_args: str) -> object:
    return setup_environment.parse_args(
        [
            "--zotero-integration-release-url",
            release_urls["obsidian-zotero-desktop-connector"],
            "--pandoc-reference-list-release-url",
            release_urls["obsidian-pandoc-reference-list"],
            *extra_args,
        ]
    )


class ObsidianResearchPluginInstallerTests(unittest.TestCase):
    def test_install_research_plugins_installs_and_enables_expected_plugins(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            release_urls = write_research_plugin_releases(temp_path)
            obsidian_dir = temp_path / ".obsidian"
            obsidian_dir.mkdir()
            community_plugins_path = obsidian_dir / "community-plugins.json"
            community_plugins_path.write_text('["existing-plugin"]\n', encoding="utf-8")

            report = SilentReport()
            with working_directory(temp_path):
                obsidian_research_plugins.install_research_plugins(setup_args_with_releases(release_urls), report)

            enabled_plugins = json.loads(community_plugins_path.read_text(encoding="utf-8"))
            self.assertEqual(
                enabled_plugins,
                [
                    "existing-plugin",
                    "obsidian-zotero-desktop-connector",
                    "obsidian-pandoc-reference-list",
                ],
            )
            for plugin_id in OBSIDIAN_RESEARCH_PLUGIN_IDS:
                plugin_dir = temp_path / ".obsidian" / "plugins" / plugin_id
                with self.subTest(plugin_id=plugin_id):
                    self.assertTrue(plugin_dir.is_dir())
                    for file_name in REQUIRED_OBSIDIAN_PLUGIN_FILES:
                        self.assertTrue((plugin_dir / file_name).is_file())
                    manifest = json.loads((plugin_dir / "manifest.json").read_text(encoding="utf-8"))
                    self.assertEqual(manifest["id"], plugin_id)

            zotero_settings = json.loads(
                (
                    temp_path
                    / ".obsidian"
                    / "plugins"
                    / "obsidian-zotero-desktop-connector"
                    / "data.json"
                ).read_text(encoding="utf-8")
            )
            self.assertIn({"name": "Pandoc citekey", "format": "pandoc"}, zotero_settings["citeFormats"])
            self.assertEqual(zotero_settings["citeSuggestTemplate"], "[@{{citekey}}]")

            reference_list_settings = json.loads(
                (
                    temp_path
                    / ".obsidian"
                    / "plugins"
                    / "obsidian-pandoc-reference-list"
                    / "data.json"
                ).read_text(encoding="utf-8")
            )
            self.assertEqual(reference_list_settings["pathToBibliography"], "./bibliography/references.bib")
            self.assertEqual(reference_list_settings["cslStylePath"], "bibliography/csl/ieee.csl")
            self.assertEqual(reference_list_settings["pathToPandoc"], "")
            self.assertFalse(reference_list_settings["pullFromZotero"])
            self.assertEqual(reference_list_settings["zoteroGroups"], [])

    def test_existing_research_plugin_settings_are_preserved_and_missing_defaults_are_added(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            obsidian_dir = temp_path / ".obsidian"
            plugins_dir = obsidian_dir / "plugins"
            plugins_dir.mkdir(parents=True)
            (obsidian_dir / "community-plugins.json").write_text("[]\n", encoding="utf-8")
            for plugin_id in OBSIDIAN_RESEARCH_PLUGIN_IDS:
                plugin_dir = plugins_dir / plugin_id
                plugin_dir.mkdir()
                (plugin_dir / "manifest.json").write_text(json.dumps({"id": plugin_id}), encoding="utf-8")
                (plugin_dir / "main.js").write_text("module.exports = {};\n", encoding="utf-8")
                (plugin_dir / "styles.css").write_text("", encoding="utf-8")
            custom_reference_settings = {
                "pathToBibliography": "./bibliography/custom.bib",
                "pathToPandoc": "/usr/local/bin/pandoc",
            }
            (
                plugins_dir
                / "obsidian-pandoc-reference-list"
                / "data.json"
            ).write_text(json.dumps(custom_reference_settings), encoding="utf-8")

            report = SilentReport()
            with working_directory(temp_path):
                obsidian_research_plugins.install_research_plugins(setup_environment.parse_args([]), report)

            reference_list_settings = json.loads(
                (
                    plugins_dir
                    / "obsidian-pandoc-reference-list"
                    / "data.json"
                ).read_text(encoding="utf-8")
            )
            self.assertEqual(reference_list_settings["pathToBibliography"], "./bibliography/custom.bib")
            self.assertEqual(reference_list_settings["cslStylePath"], "bibliography/csl/ieee.csl")
            self.assertEqual(reference_list_settings["pathToPandoc"], "/usr/local/bin/pandoc")
            self.assertFalse(reference_list_settings["pullFromZotero"])

    def test_existing_cite_suggest_template_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            obsidian_dir = temp_path / ".obsidian"
            plugins_dir = obsidian_dir / "plugins"
            plugins_dir.mkdir(parents=True)
            (obsidian_dir / "community-plugins.json").write_text("[]\n", encoding="utf-8")
            for plugin_id in OBSIDIAN_RESEARCH_PLUGIN_IDS:
                plugin_dir = plugins_dir / plugin_id
                plugin_dir.mkdir()
                (plugin_dir / "manifest.json").write_text(json.dumps({"id": plugin_id}), encoding="utf-8")
                (plugin_dir / "main.js").write_text("module.exports = {};\n", encoding="utf-8")
                (plugin_dir / "styles.css").write_text("", encoding="utf-8")
            (
                plugins_dir
                / "obsidian-zotero-desktop-connector"
                / "data.json"
            ).write_text(json.dumps({"citeSuggestTemplate": "[[{{citekey}}]]"}), encoding="utf-8")

            report = SilentReport()
            with working_directory(temp_path):
                obsidian_research_plugins.install_research_plugins(setup_environment.parse_args([]), report)

            zotero_settings = json.loads(
                (
                    plugins_dir
                    / "obsidian-zotero-desktop-connector"
                    / "data.json"
                ).read_text(encoding="utf-8")
            )
            self.assertEqual(zotero_settings["citeSuggestTemplate"], "[[{{citekey}}]]")

    def test_custom_cite_suggest_template_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            obsidian_dir = temp_path / ".obsidian"
            plugins_dir = obsidian_dir / "plugins"
            plugins_dir.mkdir(parents=True)
            (obsidian_dir / "community-plugins.json").write_text("[]\n", encoding="utf-8")
            for plugin_id in OBSIDIAN_RESEARCH_PLUGIN_IDS:
                plugin_dir = plugins_dir / plugin_id
                plugin_dir.mkdir()
                (plugin_dir / "manifest.json").write_text(json.dumps({"id": plugin_id}), encoding="utf-8")
                (plugin_dir / "main.js").write_text("module.exports = {};\n", encoding="utf-8")
                (plugin_dir / "styles.css").write_text("", encoding="utf-8")
            (
                plugins_dir
                / "obsidian-zotero-desktop-connector"
                / "data.json"
            ).write_text(json.dumps({"citeSuggestTemplate": "{{citekey}}"}), encoding="utf-8")

            report = SilentReport()
            with working_directory(temp_path):
                obsidian_research_plugins.install_research_plugins(setup_environment.parse_args([]), report)

            zotero_settings = json.loads(
                (
                    plugins_dir
                    / "obsidian-zotero-desktop-connector"
                    / "data.json"
                ).read_text(encoding="utf-8")
            )
            self.assertEqual(zotero_settings["citeSuggestTemplate"], "{{citekey}}")

    def test_existing_invalid_plugin_folder_blocks_enablement_until_forced(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            release_urls = write_research_plugin_releases(temp_path)
            obsidian_dir = temp_path / ".obsidian"
            plugins_dir = obsidian_dir / "plugins"
            plugins_dir.mkdir(parents=True)
            community_plugins_path = obsidian_dir / "community-plugins.json"
            community_plugins_path.write_text("[]\n", encoding="utf-8")
            invalid_plugin_dir = plugins_dir / "obsidian-zotero-desktop-connector"
            invalid_plugin_dir.mkdir()
            (invalid_plugin_dir / "manifest.json").write_text(json.dumps({"id": "wrong-plugin"}), encoding="utf-8")

            report = SilentReport()
            with working_directory(temp_path):
                obsidian_research_plugins.install_research_plugins(setup_args_with_releases(release_urls), report)

            self.assertTrue(any("--force" in message for message in report.failed), report.failed)
            self.assertEqual(json.loads(community_plugins_path.read_text(encoding="utf-8")), [])
            self.assertFalse((plugins_dir / "obsidian-pandoc-reference-list").exists())

    def test_existing_plugin_path_file_blocks_enablement_until_removed_or_forced(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            release_urls = write_research_plugin_releases(temp_path)
            obsidian_dir = temp_path / ".obsidian"
            plugins_dir = obsidian_dir / "plugins"
            plugins_dir.mkdir(parents=True)
            community_plugins_path = obsidian_dir / "community-plugins.json"
            community_plugins_path.write_text("[]\n", encoding="utf-8")
            (plugins_dir / "obsidian-zotero-desktop-connector").write_text("not a directory", encoding="utf-8")

            report = SilentReport()
            with working_directory(temp_path):
                obsidian_research_plugins.install_research_plugins(setup_args_with_releases(release_urls), report)

            self.assertTrue(any("exists but is not a directory" in message for message in report.failed), report.failed)
            self.assertEqual(json.loads(community_plugins_path.read_text(encoding="utf-8")), [])

    def test_existing_valid_plugin_folders_are_enabled_without_release_download(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            obsidian_dir = temp_path / ".obsidian"
            plugins_dir = obsidian_dir / "plugins"
            plugins_dir.mkdir(parents=True)
            community_plugins_path = obsidian_dir / "community-plugins.json"
            community_plugins_path.write_text('["existing-plugin"]\n', encoding="utf-8")
            for plugin_id in OBSIDIAN_RESEARCH_PLUGIN_IDS:
                plugin_dir = plugins_dir / plugin_id
                plugin_dir.mkdir()
                (plugin_dir / "manifest.json").write_text(json.dumps({"id": plugin_id}), encoding="utf-8")
                (plugin_dir / "main.js").write_text("module.exports = {};\n", encoding="utf-8")
                (plugin_dir / "styles.css").write_text("", encoding="utf-8")

            report = SilentReport()
            with working_directory(temp_path):
                obsidian_research_plugins.install_research_plugins(setup_environment.parse_args([]), report)

            self.assertFalse(report.failed)
            self.assertEqual(
                json.loads(community_plugins_path.read_text(encoding="utf-8")),
                ["existing-plugin", *OBSIDIAN_RESEARCH_PLUGIN_IDS],
            )

    def test_force_replaces_existing_invalid_plugin_folder(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            release_urls = write_research_plugin_releases(temp_path)
            obsidian_dir = temp_path / ".obsidian"
            plugins_dir = obsidian_dir / "plugins"
            plugins_dir.mkdir(parents=True)
            community_plugins_path = obsidian_dir / "community-plugins.json"
            community_plugins_path.write_text("[]\n", encoding="utf-8")
            invalid_plugin_dir = plugins_dir / "obsidian-zotero-desktop-connector"
            invalid_plugin_dir.mkdir()
            (invalid_plugin_dir / "manifest.json").write_text(json.dumps({"id": "wrong-plugin"}), encoding="utf-8")

            report = SilentReport()
            with working_directory(temp_path):
                obsidian_research_plugins.install_research_plugins(
                    setup_args_with_releases(release_urls, "--force"),
                    report,
                )

            self.assertFalse(report.failed)
            enabled_plugins = json.loads(community_plugins_path.read_text(encoding="utf-8"))
            self.assertEqual(enabled_plugins, list(OBSIDIAN_RESEARCH_PLUGIN_IDS))
            manifest = json.loads((invalid_plugin_dir / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["id"], "obsidian-zotero-desktop-connector")

    def test_setup_installs_research_plugins_by_default(self) -> None:
        args = setup_environment.parse_args(["--dry-run"])
        report = SilentReport()

        with mock.patch.object(setup_environment, "install_research_plugins") as install_mock:
            setup_environment.install_obsidian_research_plugin_layer(args, report)

        install_mock.assert_called_once_with(args, report)

    def test_setup_can_skip_research_plugins(self) -> None:
        args = setup_environment.parse_args(["--skip-obsidian-research-plugins"])
        report = SilentReport()

        with mock.patch.object(setup_environment, "install_research_plugins") as install_mock:
            setup_environment.install_obsidian_research_plugin_layer(args, report)

        install_mock.assert_not_called()
        self.assertIn("Obsidian research plugin setup skipped by --skip-obsidian-research-plugins", report.skipped)


class ObsidianResearchPluginCheckerTests(unittest.TestCase):
    def test_check_research_plugins_passes_when_plugins_are_installed_and_enabled(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            obsidian_dir = temp_path / ".obsidian"
            plugins_dir = obsidian_dir / "plugins"
            plugins_dir.mkdir(parents=True)
            (obsidian_dir / "community-plugins.json").write_text(
                json.dumps(list(OBSIDIAN_RESEARCH_PLUGIN_IDS)),
                encoding="utf-8",
            )
            for plugin_id in OBSIDIAN_RESEARCH_PLUGIN_IDS:
                plugin_dir = plugins_dir / plugin_id
                plugin_dir.mkdir()
                (plugin_dir / "manifest.json").write_text(json.dumps({"id": plugin_id}), encoding="utf-8")
                (plugin_dir / "main.js").write_text("module.exports = {};\n", encoding="utf-8")
                (plugin_dir / "styles.css").write_text("", encoding="utf-8")
            (
                plugins_dir
                / "obsidian-zotero-desktop-connector"
                / "data.json"
            ).write_text(
                json.dumps(
                    {
                        "citeFormats": [{"name": "Pandoc citekey", "format": "pandoc"}],
                        "citeSuggestTemplate": "[@{{citekey}}]",
                    }
                ),
                encoding="utf-8",
            )
            (
                plugins_dir
                / "obsidian-pandoc-reference-list"
                / "data.json"
            ).write_text(
                json.dumps(
                    {
                        "pathToBibliography": "./bibliography/references.bib",
                        "cslStylePath": "bibliography/csl/ieee.csl",
                    }
                ),
                encoding="utf-8",
            )

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = obsidian_research_plugins.check_research_plugins([str(temp_path)])

            self.assertEqual(exit_code, 0, stdout.getvalue())
            self.assertIn("PASS obsidian-zotero-desktop-connector enabled", stdout.getvalue())
            self.assertIn("PASS obsidian-pandoc-reference-list enabled", stdout.getvalue())
            self.assertIn("PASS Zotero Integration settings include a Pandoc citekey format", stdout.getvalue())
            self.assertIn("PASS Zotero Integration autocomplete inserts Pandoc citation syntax", stdout.getvalue())
            self.assertIn("PASS Pandoc Reference List bibliography path configured", stdout.getvalue())
            self.assertIn("PASS Pandoc Reference List IEEE CSL path configured", stdout.getvalue())

    def test_check_research_plugins_warns_when_user_changes_recommended_settings(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            obsidian_dir = temp_path / ".obsidian"
            plugins_dir = obsidian_dir / "plugins"
            plugins_dir.mkdir(parents=True)
            (obsidian_dir / "community-plugins.json").write_text(
                json.dumps(list(OBSIDIAN_RESEARCH_PLUGIN_IDS)),
                encoding="utf-8",
            )
            for plugin_id in OBSIDIAN_RESEARCH_PLUGIN_IDS:
                plugin_dir = plugins_dir / plugin_id
                plugin_dir.mkdir()
                (plugin_dir / "manifest.json").write_text(json.dumps({"id": plugin_id}), encoding="utf-8")
                (plugin_dir / "main.js").write_text("module.exports = {};\n", encoding="utf-8")
                (plugin_dir / "styles.css").write_text("", encoding="utf-8")
            (
                plugins_dir
                / "obsidian-zotero-desktop-connector"
                / "data.json"
            ).write_text(
                json.dumps(
                    {
                        "citeFormats": [{"name": "Pandoc citekey", "format": "pandoc"}],
                        "citeSuggestTemplate": "[[{{citekey}}]]",
                    }
                ),
                encoding="utf-8",
            )
            (
                plugins_dir
                / "obsidian-pandoc-reference-list"
                / "data.json"
            ).write_text(
                json.dumps({"pathToBibliography": "./bibliography/custom.bib"}),
                encoding="utf-8",
            )

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = obsidian_research_plugins.check_research_plugins([str(temp_path)])

            self.assertEqual(exit_code, 0, stdout.getvalue())
            self.assertIn("WARN Zotero Integration autocomplete is not Pandoc citation syntax", stdout.getvalue())
            self.assertIn("WARN Pandoc Reference List IEEE CSL path is not configured", stdout.getvalue())

    def test_check_research_plugins_fails_when_settings_json_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            obsidian_dir = temp_path / ".obsidian"
            plugins_dir = obsidian_dir / "plugins"
            plugins_dir.mkdir(parents=True)
            (obsidian_dir / "community-plugins.json").write_text(
                json.dumps(list(OBSIDIAN_RESEARCH_PLUGIN_IDS)),
                encoding="utf-8",
            )
            for plugin_id in OBSIDIAN_RESEARCH_PLUGIN_IDS:
                plugin_dir = plugins_dir / plugin_id
                plugin_dir.mkdir()
                (plugin_dir / "manifest.json").write_text(json.dumps({"id": plugin_id}), encoding="utf-8")
                (plugin_dir / "main.js").write_text("module.exports = {};\n", encoding="utf-8")
                (plugin_dir / "styles.css").write_text("", encoding="utf-8")
                (plugin_dir / "data.json").write_text("{not valid json", encoding="utf-8")

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = obsidian_research_plugins.check_research_plugins([str(temp_path)])

            self.assertEqual(exit_code, 1)
            self.assertIn("FAIL invalid", stdout.getvalue())

    def test_check_research_plugins_fails_when_expected_plugin_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            obsidian_dir = temp_path / ".obsidian"
            plugins_dir = obsidian_dir / "plugins"
            plugins_dir.mkdir(parents=True)
            (obsidian_dir / "community-plugins.json").write_text(
                json.dumps(["obsidian-zotero-desktop-connector"]),
                encoding="utf-8",
            )
            plugin_dir = plugins_dir / "obsidian-zotero-desktop-connector"
            plugin_dir.mkdir()
            for file_name in REQUIRED_OBSIDIAN_PLUGIN_FILES:
                content = json.dumps({"id": "obsidian-zotero-desktop-connector"}) if file_name == "manifest.json" else ""
                (plugin_dir / file_name).write_text(content, encoding="utf-8")

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = obsidian_research_plugins.check_research_plugins([str(temp_path)])

            self.assertEqual(exit_code, 1)
            self.assertIn("FAIL plugin directory missing", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
