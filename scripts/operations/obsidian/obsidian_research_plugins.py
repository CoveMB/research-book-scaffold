#!/usr/bin/env python3
"""Install and verify the recommended Obsidian research plugins."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.error
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

_SCRIPTS_ROOT = next(parent for parent in Path(__file__).resolve().parents if parent.name == "scripts")
_LIB_DIR = _SCRIPTS_ROOT / "lib"
if str(_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(_LIB_DIR))

from import_paths import configure_script_paths

configure_script_paths(__file__)

from obsidian_agent import (
    community_plugins_path,
    download_release_assets,
    ensure_obsidian_plugin_parent,
    is_zip_url,
    read_enabled_community_plugins,
    read_json_object,
    read_release_payload,
    release_asset_name,
    replace_directory_atomically,
    vault_path_from_args,
    write_enabled_community_plugins,
)
from project_config import (
    OBSIDIAN_DIR,
    OBSIDIAN_PLUGINS_DIR,
    OBSIDIAN_RESEARCH_PLUGIN_IDS,
    PANDOC_REFERENCE_LIST_PLUGIN_ID,
    REQUIRED_OBSIDIAN_PLUGIN_FILES,
    ZOTERO_INTEGRATION_PLUGIN_ID,
    change_to_project_root,
    resolve_obsidian_vault_path,
)
from script_utils import StatusReport


@dataclass(frozen=True)
class ObsidianResearchPluginSpec:
    plugin_id: str
    label: str
    release_api_url: str
    release_arg_name: str


RESEARCH_PLUGIN_SPECS = (
    ObsidianResearchPluginSpec(
        ZOTERO_INTEGRATION_PLUGIN_ID,
        "Zotero Integration",
        "https://api.github.com/repos/obsidian-community/obsidian-zotero-integration/releases/latest",
        "zotero_integration_release_url",
    ),
    ObsidianResearchPluginSpec(
        PANDOC_REFERENCE_LIST_PLUGIN_ID,
        "Pandoc Reference List",
        "https://api.github.com/repos/obsidian-community/obsidian-pandoc-reference-list/releases/latest",
        "pandoc_reference_list_release_url",
    ),
)

PANDOC_CITE_FORMAT = {"name": "Pandoc citekey", "format": "pandoc"}
PANDOC_CITE_SUGGEST_TEMPLATE = "[@{{citekey}}]"
IEEE_CSL_STYLE_PATH = "bibliography/csl/ieee.csl"

RESEARCH_PLUGIN_DEFAULT_SETTINGS: dict[str, dict[str, object]] = {
    ZOTERO_INTEGRATION_PLUGIN_ID: {
        "database": "Zotero",
        "noteImportFolder": "",
        "pdfExportImageDPI": 120,
        "pdfExportImageFormat": "jpg",
        "pdfExportImageQuality": 90,
        "citeFormats": [PANDOC_CITE_FORMAT],
        "exportFormats": [],
        "citeSuggestTemplate": PANDOC_CITE_SUGGEST_TEMPLATE,
        "openNoteAfterImport": False,
        "whichNotesToOpenAfterImport": "first-imported-note",
        "exeOverridePath": "",
    },
    PANDOC_REFERENCE_LIST_PLUGIN_ID: {
        "pathToPandoc": "",
        "tooltipDelay": 400,
        "zoteroGroups": [],
        "renderCitations": True,
        "renderCitationsReadingMode": True,
        "renderLinkCitations": True,
        "pathToBibliography": "./bibliography/references.bib",
        "cslStylePath": IEEE_CSL_STYLE_PATH,
        "pullFromZotero": False,
    },
}


def add_install_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--obsidian-vault")
    parser.add_argument("--zotero-integration-release-url")
    parser.add_argument("--pandoc-reference-list-release-url")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command")

    install_parser = subparsers.add_parser("install", help="Install and enable recommended research plugins.")
    add_install_args(install_parser)

    check_parser = subparsers.add_parser("check", help="Check recommended research plugin installation.")
    check_parser.add_argument(
        "vault",
        nargs="?",
        help="Obsidian vault path. Defaults to OBSIDIAN_VAULT or the project root.",
    )

    if not argv:
        argv = ["install"]
    return parser.parse_args(argv)


def release_url_for_spec(spec: ObsidianResearchPluginSpec, args: argparse.Namespace) -> str:
    override = getattr(args, spec.release_arg_name, None)
    if isinstance(override, str) and override:
        return override
    return spec.release_api_url


def latest_plugin_release_asset_urls(spec: ObsidianResearchPluginSpec, release_url: str) -> dict[str, str]:
    if is_zip_url(release_url):
        raise RuntimeError(f"{spec.label} installs from individual release assets, not zip archives")
    payload = read_release_payload(release_url)
    assets = payload.get("assets", [])
    if not isinstance(assets, list):
        raise RuntimeError(f"{spec.label} release metadata assets must be a list")

    asset_urls: dict[str, str] = {}
    for asset in assets:
        if not isinstance(asset, dict):
            continue
        name = release_asset_name(asset)
        download_url = asset.get("browser_download_url")
        if name in REQUIRED_OBSIDIAN_PLUGIN_FILES and isinstance(download_url, str) and download_url:
            if is_zip_url(download_url):
                raise RuntimeError(f"{spec.label} release asset {name} points to a zip archive")
            asset_urls[name] = download_url

    missing_files = sorted(REQUIRED_OBSIDIAN_PLUGIN_FILES - set(asset_urls))
    if missing_files:
        raise RuntimeError(f"No {spec.label} release assets found for: {', '.join(missing_files)}")
    return asset_urls


def validate_research_plugin_manifest(plugin_dir: Path, plugin_id: str) -> None:
    manifest = read_json_object(plugin_dir / "manifest.json")
    manifest_id = manifest.get("id")
    if manifest_id != plugin_id:
        raise RuntimeError(f"manifest id is {manifest_id}; expected {plugin_id}")


def ensure_required_research_plugin_files(plugin_dir: Path, label: str, context: str = "Downloaded release") -> None:
    missing_files = sorted(file_name for file_name in REQUIRED_OBSIDIAN_PLUGIN_FILES if not (plugin_dir / file_name).is_file())
    if missing_files:
        raise RuntimeError(f"{context} for {label} is missing: {', '.join(missing_files)}")


def ensure_existing_research_plugin_is_usable(
    destination_dir: Path,
    spec: ObsidianResearchPluginSpec,
    report: StatusReport,
) -> bool:
    if not destination_dir.is_dir():
        report.add(
            "failed",
            f"{destination_dir} exists but is not a directory; remove it or rerun with --force to replace it",
        )
        return False
    try:
        ensure_required_research_plugin_files(destination_dir, spec.label, "Existing install")
        validate_research_plugin_manifest(destination_dir, spec.plugin_id)
    except RuntimeError as error:
        report.add(
            "failed",
            f"existing {spec.label} install at {destination_dir} is invalid: {error}; rerun with --force to replace it",
        )
        return False
    report.add("already_present", f"{spec.label} already installed at {destination_dir}")
    return True


def read_research_plugin_settings(settings_path: Path) -> dict[str, object]:
    if not settings_path.exists():
        return {}
    return read_json_object(settings_path)


def merged_research_plugin_settings(plugin_id: str, existing_settings: dict[str, object]) -> dict[str, object]:
    defaults = RESEARCH_PLUGIN_DEFAULT_SETTINGS.get(plugin_id, {})
    settings = dict(existing_settings)
    for key, value in defaults.items():
        if key not in settings:
            settings[key] = json.loads(json.dumps(value))

    if plugin_id == ZOTERO_INTEGRATION_PLUGIN_ID:
        cite_formats = settings.get("citeFormats")
        if not isinstance(cite_formats, list):
            cite_formats = []
        has_pandoc_format = any(
            isinstance(item, dict) and item.get("format") == "pandoc"
            for item in cite_formats
        )
        if not has_pandoc_format:
            cite_formats = [*cite_formats, dict(PANDOC_CITE_FORMAT)]
        settings["citeFormats"] = cite_formats

    if plugin_id == PANDOC_REFERENCE_LIST_PLUGIN_ID and not settings.get("pathToBibliography"):
        settings["pathToBibliography"] = RESEARCH_PLUGIN_DEFAULT_SETTINGS[PANDOC_REFERENCE_LIST_PLUGIN_ID][
            "pathToBibliography"
        ]

    return settings


def ensure_research_plugin_settings(
    destination_dir: Path,
    spec: ObsidianResearchPluginSpec,
    report: StatusReport,
    dry_run: bool,
) -> bool:
    settings_path = destination_dir / "data.json"
    try:
        existing_settings = read_research_plugin_settings(settings_path)
    except RuntimeError as error:
        report.add("failed", str(error))
        return False

    updated_settings = merged_research_plugin_settings(spec.plugin_id, existing_settings)
    if updated_settings == existing_settings:
        report.add("already_present", f"{spec.label} settings already configured at {settings_path}")
        return True

    if dry_run:
        report.add("skipped", f"dry-run would write {spec.label} settings to {settings_path}")
        return True

    try:
        settings_path.write_text(json.dumps(updated_settings, indent=2) + "\n", encoding="utf-8")
    except OSError as error:
        report.add("failed", f"could not write {spec.label} settings: {error}")
        return False
    report.add("installed", f"configured {spec.label} settings at {settings_path}")
    return True


def enabled_plugins_with_research_plugins(enabled_plugins: list[str]) -> list[str]:
    updated_plugins: list[str] = []
    seen_plugins: set[str] = set()

    for plugin_id in enabled_plugins:
        if plugin_id in seen_plugins:
            continue
        updated_plugins.append(plugin_id)
        seen_plugins.add(plugin_id)

    for plugin_id in OBSIDIAN_RESEARCH_PLUGIN_IDS:
        if plugin_id not in seen_plugins:
            updated_plugins.append(plugin_id)
            seen_plugins.add(plugin_id)
    return updated_plugins


def ensure_research_plugins_enabled(
    obsidian_dir: Path,
    enabled_plugins: list[str],
    report: StatusReport,
    dry_run: bool,
) -> bool:
    updated_plugins = enabled_plugins_with_research_plugins(enabled_plugins)
    if updated_plugins == enabled_plugins:
        report.add("already_present", f"Obsidian research plugins listed in {community_plugins_path(obsidian_dir)}")
        return True

    if dry_run:
        report.add("skipped", f"dry-run would enable Obsidian research plugins in {community_plugins_path(obsidian_dir)}")
        return True
    try:
        write_enabled_community_plugins(obsidian_dir, updated_plugins)
    except OSError as error:
        report.add("failed", f"could not enable Obsidian research plugins: {error}")
        return False
    report.add("installed", f"enabled Obsidian research plugins in {community_plugins_path(obsidian_dir)}")
    return True


def install_one_research_plugin(
    spec: ObsidianResearchPluginSpec,
    args: argparse.Namespace,
    plugins_dir: Path,
    report: StatusReport,
) -> bool:
    destination_dir = plugins_dir / spec.plugin_id
    if destination_dir.exists() and not args.force:
        return ensure_existing_research_plugin_is_usable(destination_dir, spec, report)

    if args.dry_run:
        report.add("skipped", f"dry-run would download latest release assets for {spec.label}")
        report.add("skipped", f"dry-run would install plugin to {destination_dir}")
        return True

    try:
        with tempfile.TemporaryDirectory(prefix="obsidian-research-plugin-") as temp_dir:
            plugin_root = Path(temp_dir) / spec.plugin_id
            asset_urls = latest_plugin_release_asset_urls(spec, release_url_for_spec(spec, args))
            download_release_assets(asset_urls, plugin_root)
            ensure_required_research_plugin_files(plugin_root, spec.label)
            validate_research_plugin_manifest(plugin_root, spec.plugin_id)
            replace_directory_atomically(plugin_root, destination_dir)
    except (
        OSError,
        RuntimeError,
        urllib.error.URLError,
        json.JSONDecodeError,
    ) as error:
        report.add("failed", f"{spec.label} install failed: {error}")
        return False
    report.add("installed", f"installed {spec.label} to {destination_dir}")
    return True


def install_research_plugins(args: argparse.Namespace, report: StatusReport) -> None:
    vault_path = vault_path_from_args(args)
    if not vault_path.exists():
        report.add("failed", f"Obsidian vault path missing: {vault_path}")
        return

    plugins_dir = ensure_obsidian_plugin_parent(vault_path, report, args.dry_run)
    if plugins_dir is None:
        return
    obsidian_dir = vault_path / OBSIDIAN_DIR
    try:
        enabled_plugins = read_enabled_community_plugins(obsidian_dir)
    except RuntimeError as error:
        report.add("failed", str(error))
        return

    for spec in RESEARCH_PLUGIN_SPECS:
        if not install_one_research_plugin(spec, args, plugins_dir, report):
            return
        if not ensure_research_plugin_settings(plugins_dir / spec.plugin_id, spec, report, args.dry_run):
            return

    ensure_research_plugins_enabled(obsidian_dir, enabled_plugins, report, args.dry_run)


def check_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="obsidian_research_plugins.py check",
        description="Check recommended Obsidian research plugin installation.",
    )
    parser.add_argument(
        "vault",
        nargs="?",
        help="Obsidian vault path. Defaults to OBSIDIAN_VAULT or the project root.",
    )
    return parser.parse_args(argv)


def check_vault_path(args: argparse.Namespace) -> Path:
    return resolve_obsidian_vault_path(getattr(args, "vault", None), os.environ.get("OBSIDIAN_VAULT"))


def print_fail(message: str, failures: list[str]) -> None:
    print(f"FAIL {message}")
    failures.append(message)


def print_pass(message: str) -> None:
    print(f"PASS {message}")


def print_warn(message: str) -> None:
    print(f"WARN {message}")


def check_required_files(plugin_dir: Path, plugin_id: str, failures: list[str]) -> None:
    for file_name in sorted(REQUIRED_OBSIDIAN_PLUGIN_FILES):
        file_path = plugin_dir / file_name
        if file_path.exists() and file_path.is_file():
            print_pass(f"{plugin_id} {file_name} exists")
        else:
            print_fail(f"{plugin_id} {file_name} missing", failures)


def check_manifest(plugin_dir: Path, plugin_id: str, failures: list[str]) -> None:
    try:
        validate_research_plugin_manifest(plugin_dir, plugin_id)
    except RuntimeError as error:
        print_fail(f"{plugin_id} {error}", failures)
        return
    print_pass(f"{plugin_id} manifest id matches")


def settings_has_pandoc_cite_format(settings: dict[str, object]) -> bool:
    cite_formats = settings.get("citeFormats")
    if not isinstance(cite_formats, list):
        return False
    return any(isinstance(item, dict) and item.get("format") == "pandoc" for item in cite_formats)


def check_zotero_integration_settings(settings: dict[str, object], failures: list[str]) -> None:
    if settings_has_pandoc_cite_format(settings):
        print_pass("Zotero Integration settings include a Pandoc citekey format")
    else:
        print_warn("Zotero Integration settings do not include a Pandoc citekey format")

    if settings.get("citeSuggestTemplate") == PANDOC_CITE_SUGGEST_TEMPLATE:
        print_pass("Zotero Integration autocomplete inserts Pandoc citation syntax")
    else:
        print_warn("Zotero Integration autocomplete is not Pandoc citation syntax")


def check_pandoc_reference_list_settings(settings: dict[str, object], failures: list[str]) -> None:
    bibliography_path = settings.get("pathToBibliography")
    if isinstance(bibliography_path, str) and bibliography_path.strip():
        print_pass("Pandoc Reference List bibliography path configured")
    else:
        print_warn("Pandoc Reference List bibliography path missing")

    if settings.get("cslStylePath") == IEEE_CSL_STYLE_PATH:
        print_pass("Pandoc Reference List IEEE CSL path configured")
    else:
        print_warn("Pandoc Reference List IEEE CSL path is not configured")


def check_research_plugin_settings(plugin_dir: Path, plugin_id: str, failures: list[str]) -> None:
    settings_path = plugin_dir / "data.json"
    try:
        settings = read_research_plugin_settings(settings_path)
    except RuntimeError as error:
        print_fail(str(error), failures)
        return
    if not settings_path.exists():
        print_warn(f"{plugin_id} settings missing: {settings_path}")
        return

    if plugin_id == ZOTERO_INTEGRATION_PLUGIN_ID:
        check_zotero_integration_settings(settings, failures)
    elif plugin_id == PANDOC_REFERENCE_LIST_PLUGIN_ID:
        check_pandoc_reference_list_settings(settings, failures)


def check_pandoc_available() -> None:
    pandoc_path = shutil.which("pandoc")
    if pandoc_path is None:
        print("WARN pandoc not found; Pandoc Reference List can be installed but cannot render references yet")
        return
    try:
        result = subprocess.run(
            [pandoc_path, "--version"],
            check=False,
            text=True,
            capture_output=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError) as error:
        print(f"WARN pandoc version check failed: {error}")
        return
    first_line = result.stdout.splitlines()[0] if result.stdout else pandoc_path
    if result.returncode == 0:
        print_pass(f"pandoc available: {first_line}")
    else:
        output = result.stderr.strip() or result.stdout.strip()
        print(f"WARN pandoc --version exited {result.returncode}: {output}")


def check_research_plugins(argv: list[str] | None = None) -> int:
    args = check_args(argv or [])
    vault_path = check_vault_path(args)
    failures: list[str] = []

    if vault_path.exists() and vault_path.is_dir():
        print_pass(f"vault exists: {vault_path}")
    else:
        print_fail(f"vault path missing: {vault_path}", failures)
        return 1

    obsidian_dir = vault_path / OBSIDIAN_DIR
    plugins_dir = vault_path / OBSIDIAN_PLUGINS_DIR
    if obsidian_dir.exists() and obsidian_dir.is_dir():
        print_pass(f"Obsidian config exists: {obsidian_dir}")
    else:
        print_fail(f"Obsidian config missing: {obsidian_dir}", failures)
        return 1

    try:
        enabled_plugins = read_enabled_community_plugins(obsidian_dir)
    except RuntimeError as error:
        print_fail(str(error), failures)
        return 1

    for plugin_id in OBSIDIAN_RESEARCH_PLUGIN_IDS:
        plugin_dir = plugins_dir / plugin_id
        if plugin_dir.exists() and plugin_dir.is_dir():
            print_pass(f"plugin directory exists: {plugin_dir}")
        else:
            print_fail(f"plugin directory missing: {plugin_dir}", failures)
            continue
        check_required_files(plugin_dir, plugin_id, failures)
        check_manifest(plugin_dir, plugin_id, failures)
        if plugin_id in enabled_plugins:
            print_pass(f"{plugin_id} enabled")
        else:
            print_fail(f"{plugin_id} not enabled in {community_plugins_path(obsidian_dir)}", failures)
        check_research_plugin_settings(plugin_dir, plugin_id, failures)

    check_pandoc_available()
    return 1 if failures else 0


def print_summary(report: StatusReport) -> None:
    report.print_summary("Obsidian research plugin install report")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if args.command == "check":
        change_to_project_root()
        return check_research_plugins([args.vault] if args.vault else [])

    change_to_project_root()
    report = StatusReport()
    if args.dry_run:
        print("Dry run: no Obsidian research plugin files will be changed.\n")
    install_research_plugins(args, report)
    print_summary(report)
    return 1 if report.failed else 0


if __name__ == "__main__":
    sys.exit(main())
