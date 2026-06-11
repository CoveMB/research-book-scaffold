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
    missing_required_plugin_files,
    read_enabled_community_plugins,
    read_json_object,
    replace_directory_atomically,
    required_release_asset_urls,
    validate_plugin_manifest,
    vault_path_from_args,
    write_enabled_community_plugins,
    ReleaseAsset,
)
from project_config import (
    OBSIDIAN_DIR,
    OBSIDIAN_PLUGINS_DIR,
    OBSIDIAN_RESEARCH_PLUGIN_IDS,
    PANDOC_REFERENCE_LIST_PLUGIN_ID,
    QMD_AS_MD_PLUGIN_ID,
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
    ObsidianResearchPluginSpec(
        QMD_AS_MD_PLUGIN_ID,
        "qmd as md",
        "https://api.github.com/repos/danieltomasz/qmd-as-md-obsidian/releases/latest",
        "qmd_as_md_release_url",
    ),
)

# Older GitHub release assets can return digest: null. These exact URL pins keep
# install verification strict without accepting unverified downloads.
PINNED_RESEARCH_PLUGIN_ASSET_SHA256 = {
    "https://github.com/obsidian-community/obsidian-zotero-integration/releases/download/3.2.1/main.js": (
        "41582448d790d7b9a4691c00ff46dda09b0f3bbea02c89d093cc4018dfc14032"
    ),
    "https://github.com/obsidian-community/obsidian-zotero-integration/releases/download/3.2.1/manifest.json": (
        "c18f252a1f921085467ba823d7d272a369e65e3f30011f6f9558ae420191395c"
    ),
    "https://github.com/obsidian-community/obsidian-zotero-integration/releases/download/3.2.1/styles.css": (
        "3ea6988aab6c45183dc69c85d5873787dcbbd0d76264f211c07b8400f9dbc06a"
    ),
    "https://github.com/obsidian-community/obsidian-pandoc-reference-list/releases/download/2.0.25/main.js": (
        "6ca0d01e3927011c01277c0776de52ecdd2af2a6cb029b503950a8d536252edb"
    ),
    "https://github.com/obsidian-community/obsidian-pandoc-reference-list/releases/download/2.0.25/manifest.json": (
        "ec3f3a129b80cac0d8e49c0fd713b58c27833fa63805653fd444ef96830ab434"
    ),
    "https://github.com/obsidian-community/obsidian-pandoc-reference-list/releases/download/2.0.25/styles.css": (
        "587b002748cd8798deb9c0236285e707bd54cfb7cc4f077f1b5d099aae15086a"
    ),
}

PANDOC_CITE_FORMAT = {"name": "Pandoc citekey", "format": "pandoc"}
PANDOC_CITE_SUGGEST_TEMPLATE = "[@{{citekey}}]"
IEEE_CSL_STYLE_PATH = "./bibliography/csl/ieee.csl"

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
        "enableCiteKeyCompletion": True,
        "pathToBibliography": "./bibliography/references.bib",
        "pullFromZotero": False,
    },
}

QMD_AS_MD_STATIC_DEFAULT_SETTINGS: dict[str, object] = {
    "enableQmdLinking": True,
    "quartoTypst": "",
    "openPdfInObsidian": False,
    "previewInObsidian": True,
    "previewMarkdownFiles": False,
    "outlineMarkdownFiles": False,
    "showYamlFiles": True,
    "showLuaFiles": False,
    "showOutline": True,
    "templatesFolder": "",
}


# Pandoc Reference List resolves bibliography paths from the vault root, but it
# checks cslStylePath directly through Node's filesystem APIs.
def default_ieee_csl_style_path(vault_path: Path) -> str:
    return str((vault_path / IEEE_CSL_STYLE_PATH).resolve())


def default_quarto_path() -> str:
    return shutil.which("quarto") or "quarto"


def default_research_plugin_settings(plugin_id: str, vault_path: Path) -> dict[str, object]:
    if plugin_id == QMD_AS_MD_PLUGIN_ID:
        return {
            "quartoPath": default_quarto_path(),
            **QMD_AS_MD_STATIC_DEFAULT_SETTINGS,
        }
    return RESEARCH_PLUGIN_DEFAULT_SETTINGS.get(plugin_id, {})


def is_default_ieee_csl_style_path(style_path: object, vault_path: Path) -> bool:
    if not isinstance(style_path, str) or not style_path.strip():
        return False
    resolved_style_path = Path(style_path).expanduser()
    return resolved_style_path.is_absolute() and resolved_style_path.resolve() == Path(
        default_ieee_csl_style_path(vault_path)
    )


def add_install_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--obsidian-vault")
    parser.add_argument("--zotero-integration-release-url")
    parser.add_argument("--pandoc-reference-list-release-url")
    parser.add_argument("--qmd-as-md-release-url")


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


def latest_plugin_release_asset_urls(spec: ObsidianResearchPluginSpec, release_url: str) -> dict[str, ReleaseAsset]:
    return required_release_asset_urls(
        release_url,
        spec.label,
        sha256_fallbacks=PINNED_RESEARCH_PLUGIN_ASSET_SHA256,
    )


def ensure_required_research_plugin_files(plugin_dir: Path, label: str, context: str = "Downloaded release") -> None:
    missing_files = missing_required_plugin_files(plugin_dir)
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
        validate_plugin_manifest(destination_dir, spec.plugin_id)
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


def merged_research_plugin_settings(
    plugin_id: str,
    existing_settings: dict[str, object],
    vault_path: Path,
) -> dict[str, object]:
    defaults = default_research_plugin_settings(plugin_id, vault_path)
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
    if plugin_id == PANDOC_REFERENCE_LIST_PLUGIN_ID:
        has_csl_style_path = isinstance(settings.get("cslStylePath"), str) and bool(
            str(settings["cslStylePath"]).strip()
        )
        if not has_csl_style_path:
            settings["cslStylePath"] = default_ieee_csl_style_path(vault_path)

    return settings


def ensure_research_plugin_settings(
    destination_dir: Path,
    spec: ObsidianResearchPluginSpec,
    report: StatusReport,
    dry_run: bool,
    vault_path: Path,
) -> bool:
    settings_path = destination_dir / "data.json"
    try:
        existing_settings = read_research_plugin_settings(settings_path)
    except RuntimeError as error:
        report.add("failed", str(error))
        return False

    updated_settings = merged_research_plugin_settings(spec.plugin_id, existing_settings, vault_path)
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
            validate_plugin_manifest(plugin_root, spec.plugin_id)
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


def report_skipped_research_plugin_batch(
    specs: tuple[ObsidianResearchPluginSpec, ...],
    start_index: int,
    report: StatusReport,
    reason: str,
) -> None:
    for skipped_spec in specs[start_index:]:
        report.add("skipped", f"{skipped_spec.label} install skipped because {reason}")
    report.add("skipped", f"Obsidian research plugin enablement skipped because {reason}")


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

    for index, spec in enumerate(RESEARCH_PLUGIN_SPECS):
        if not install_one_research_plugin(spec, args, plugins_dir, report):
            report_skipped_research_plugin_batch(
                RESEARCH_PLUGIN_SPECS,
                index + 1,
                report,
                f"{spec.label} install failed",
            )
            return
        if not ensure_research_plugin_settings(plugins_dir / spec.plugin_id, spec, report, args.dry_run, vault_path):
            report_skipped_research_plugin_batch(
                RESEARCH_PLUGIN_SPECS,
                index + 1,
                report,
                f"{spec.label} settings configuration failed",
            )
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
        validate_plugin_manifest(plugin_dir, plugin_id)
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


def check_pandoc_reference_list_settings(settings: dict[str, object], failures: list[str], vault_path: Path) -> None:
    bibliography_path = settings.get("pathToBibliography")
    if isinstance(bibliography_path, str) and bibliography_path.strip():
        print_pass("Pandoc Reference List bibliography path configured")
    else:
        print_warn("Pandoc Reference List bibliography path missing")

    if is_default_ieee_csl_style_path(settings.get("cslStylePath"), vault_path):
        print_pass("Pandoc Reference List IEEE CSL path configured")
    else:
        print_warn("Pandoc Reference List IEEE CSL path is not configured")

    if settings.get("enableCiteKeyCompletion") is True:
        print_pass("Pandoc Reference List citekey completion enabled")
    else:
        print_warn("Pandoc Reference List citekey completion is not enabled")


def executable_quarto_path(path_text: str) -> str | None:
    if not path_text.strip():
        return None
    candidate_path = Path(path_text).expanduser()
    if candidate_path.is_absolute():
        if candidate_path.is_file() and os.access(candidate_path, os.X_OK):
            return str(candidate_path)
        return None
    return shutil.which(path_text)


def check_qmd_as_md_settings(settings: dict[str, object], failures: list[str]) -> None:
    if settings.get("enableQmdLinking") is True:
        print_pass("qmd as md editing enabled for .qmd files")
    else:
        print_warn("qmd as md editing is not enabled for .qmd files")

    if settings.get("showYamlFiles") is True:
        print_pass("qmd as md YAML files visible for _quarto.yml editing")
    else:
        print_warn("qmd as md YAML files are hidden; _quarto.yml editing may be harder")

    if settings.get("showOutline") is True:
        print_pass("qmd as md Quarto outline enabled")
    else:
        print_warn("qmd as md Quarto outline is not enabled")

    if settings.get("openPdfInObsidian") is False:
        print_pass("qmd as md PDF auto-open disabled for repository render workflow")
    else:
        print_warn("qmd as md PDF auto-open is enabled; repository render targets remain authoritative")

    quarto_path = settings.get("quartoPath")
    if isinstance(quarto_path, str) and quarto_path.strip():
        available_path = executable_quarto_path(quarto_path)
        if available_path:
            print_pass(f"qmd as md Quarto path available: {available_path}")
        else:
            print_warn(f"qmd as md Quarto path is not executable: {quarto_path}")
    else:
        print_warn("qmd as md Quarto path is not configured")


def check_research_plugin_settings(plugin_dir: Path, plugin_id: str, failures: list[str], vault_path: Path) -> None:
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
        check_pandoc_reference_list_settings(settings, failures, vault_path)
    elif plugin_id == QMD_AS_MD_PLUGIN_ID:
        check_qmd_as_md_settings(settings, failures)


def check_qmd_vault_visibility(vault_path: Path) -> None:
    app_config_path = vault_path / OBSIDIAN_DIR / "app.json"
    if app_config_path.exists():
        try:
            app_config = read_json_object(app_config_path)
        except RuntimeError as error:
            print_warn(f"could not read Obsidian app config for QMD visibility: {error}")
        else:
            ignore_filters = app_config.get("userIgnoreFilters")
            hidden_paths = ignore_filters if isinstance(ignore_filters, list) else []
            if "manuscript/" in hidden_paths or "manuscript" in hidden_paths:
                print_warn("manuscript/ is hidden by Obsidian userIgnoreFilters; .qmd files may be hard to reach")
            else:
                print_pass("manuscript/ is visible to Obsidian search and link suggestions")

    snippet_path = vault_path / OBSIDIAN_DIR / "snippets" / "hide-repo-infrastructure.css"
    if snippet_path.exists():
        try:
            snippet_text = snippet_path.read_text(encoding="utf-8")
        except OSError as error:
            print_warn(f"could not read Obsidian visibility CSS snippet: {error}")
            return
        if 'data-path="manuscript"' in snippet_text or "data-path='manuscript'" in snippet_text:
            print_warn("manuscript/ is hidden by the Obsidian File Explorer CSS snippet")
        else:
            print_pass("manuscript/ is visible in the Obsidian File Explorer CSS snippet")


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
        check_research_plugin_settings(plugin_dir, plugin_id, failures, vault_path)

    check_qmd_vault_visibility(vault_path)
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
