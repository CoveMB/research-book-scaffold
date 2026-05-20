"""Install and verify the required Codex Panel Obsidian plugin."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

_SCRIPTS_ROOT = next(parent for parent in Path(__file__).resolve().parents if parent.name == "scripts")
_LIB_DIR = _SCRIPTS_ROOT / "lib"
if str(_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(_LIB_DIR))

from import_paths import configure_script_paths

configure_script_paths(__file__)

from project_config import (
    CODEX_PANEL_PLUGIN_ID,
    OBSIDIAN_DIR,
    OBSIDIAN_PLUGIN_SETTINGS_FILE,
    OBSIDIAN_PLUGINS_DIR,
    REQUIRED_OBSIDIAN_PLUGIN_FILES,
    LEGACY_OBSIDIAN_PLUGIN_IDS,
    resolve_obsidian_vault_path,
)
from script_utils import StatusReport


DEFAULT_OBSIDIAN_REPO = "https://github.com/murashit/codex-panel"
DEFAULT_OBSIDIAN_RELEASE_API_URL = "https://api.github.com/repos/murashit/codex-panel/releases/latest"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--obsidian-vault")
    parser.add_argument("--obsidian-release-url")
    parser.add_argument("--obsidian-release-sha256")
    parser.add_argument(
        "--register-obsidian-vault",
        action="store_true",
        help="Register the vault path in Obsidian's app-level vault registry.",
    )
    parser.add_argument("--obsidian-registry-path", help=argparse.SUPPRESS)
    return parser.parse_args(argv)


def vault_path_from_args(args: argparse.Namespace) -> Path:
    return resolve_obsidian_vault_path(args.obsidian_vault, os.environ.get("OBSIDIAN_VAULT"))


def is_zip_url(url: str) -> bool:
    return urlparse(url).path.lower().endswith(".zip")


def read_release_payload(release_url: str) -> dict[str, object]:
    if is_zip_url(release_url):
        raise RuntimeError("codex-panel installs from individual release assets, not zip archives")
    request = urllib.request.Request(release_url, headers={"Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("release metadata must be a JSON object")
    return payload


def release_asset_name(asset: object) -> str | None:
    if not isinstance(asset, dict):
        return None
    name = asset.get("name")
    if isinstance(name, str) and name:
        return name
    download_url = asset.get("browser_download_url")
    if isinstance(download_url, str) and download_url:
        return Path(urlparse(download_url).path).name
    return None


def latest_obsidian_release_asset_urls(release_url: str | None = None) -> dict[str, str]:
    payload = read_release_payload(release_url or DEFAULT_OBSIDIAN_RELEASE_API_URL)
    assets = payload.get("assets", [])
    if not isinstance(assets, list):
        raise RuntimeError("release metadata assets must be a list")

    asset_urls: dict[str, str] = {}
    for asset in assets:
        if not isinstance(asset, dict):
            continue
        name = release_asset_name(asset)
        download_url = asset.get("browser_download_url")
        if name in REQUIRED_OBSIDIAN_PLUGIN_FILES and isinstance(download_url, str) and download_url:
            if is_zip_url(download_url):
                raise RuntimeError(f"codex-panel release asset {name} points to a zip archive")
            asset_urls[name] = download_url

    missing_files = sorted(REQUIRED_OBSIDIAN_PLUGIN_FILES - set(asset_urls))
    if missing_files:
        missing_text = ", ".join(missing_files)
        raise RuntimeError(f"No codex-panel release assets found for: {missing_text}")
    return asset_urls


def download_url_to_file(download_url: str, destination_path: Path) -> None:
    request = urllib.request.Request(download_url, headers={"Accept": "application/octet-stream"})
    with urllib.request.urlopen(request, timeout=30) as response:
        with destination_path.open("wb") as file_handle:
            shutil.copyfileobj(response, file_handle)


def download_release_assets(asset_urls: dict[str, str], destination_dir: Path) -> None:
    destination_dir.mkdir(parents=True, exist_ok=True)
    for file_name in sorted(REQUIRED_OBSIDIAN_PLUGIN_FILES):
        download_url = asset_urls[file_name]
        if is_zip_url(download_url):
            raise RuntimeError(f"codex-panel release asset {file_name} points to a zip archive")
        download_url_to_file(download_url, destination_dir / file_name)


def read_json_object(path: Path) -> dict[str, object]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise RuntimeError(f"invalid {path}: {error}") from error
    if not isinstance(payload, dict):
        raise RuntimeError(f"invalid {path}: expected a JSON object")
    return payload


def validate_plugin_manifest(plugin_dir: Path) -> None:
    manifest_path = plugin_dir / "manifest.json"
    manifest = read_json_object(manifest_path)
    manifest_id = manifest.get("id")
    if manifest_id != CODEX_PANEL_PLUGIN_ID:
        raise RuntimeError(f"manifest id is {manifest_id}; expected {CODEX_PANEL_PLUGIN_ID}")


def ensure_required_plugin_files(plugin_dir: Path) -> None:
    missing_files = sorted(file_name for file_name in REQUIRED_OBSIDIAN_PLUGIN_FILES if not (plugin_dir / file_name).is_file())
    if missing_files:
        raise RuntimeError(f"Downloaded Codex Panel release is missing: {', '.join(missing_files)}")


def ensure_obsidian_plugin_parent(vault_path: Path, report: StatusReport, dry_run: bool) -> Path | None:
    obsidian_dir = vault_path / OBSIDIAN_DIR
    plugins_dir = vault_path / OBSIDIAN_PLUGINS_DIR
    for directory in [obsidian_dir, plugins_dir]:
        if directory.exists():
            if not directory.is_dir():
                report.add("failed", f"{directory} exists but is not a directory")
                return None
            report.add("already_present", f"{directory} exists")
            continue
        if dry_run:
            report.add("skipped", f"dry-run would create {directory}")
            continue
        try:
            directory.mkdir(parents=True, exist_ok=True)
        except OSError as error:
            report.add("failed", f"could not create {directory}: {error}")
            return None
        report.add("installed", f"created {directory}")
    return plugins_dir


def community_plugins_path(obsidian_dir: Path) -> Path:
    return obsidian_dir / "community-plugins.json"


def read_enabled_community_plugins(obsidian_dir: Path) -> list[str]:
    path = community_plugins_path(obsidian_dir)
    if not path.exists():
        return []
    try:
        enabled_plugins = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise RuntimeError(f"invalid {path}: {error}") from error
    if not isinstance(enabled_plugins, list):
        raise RuntimeError(f"invalid {path}: expected a list")
    if not all(isinstance(plugin_id, str) for plugin_id in enabled_plugins):
        raise RuntimeError(f"invalid {path}: expected a list of plugin id strings")
    return enabled_plugins


def write_enabled_community_plugins(obsidian_dir: Path, enabled_plugins: list[str]) -> None:
    community_plugins_path(obsidian_dir).write_text(
        json.dumps(enabled_plugins, indent=2) + "\n",
        encoding="utf-8",
    )


def default_obsidian_registry_path() -> Path:
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "obsidian" / "obsidian.json"
    if os.name == "nt":
        appdata = os.environ.get("APPDATA")
        base_path = Path(appdata) if appdata else Path.home() / "AppData" / "Roaming"
        return base_path / "obsidian" / "obsidian.json"
    config_home = os.environ.get("XDG_CONFIG_HOME")
    base_path = Path(config_home) if config_home else Path.home() / ".config"
    return base_path / "obsidian" / "obsidian.json"


def obsidian_registry_path_from_args(args: argparse.Namespace) -> Path:
    requested_path = getattr(args, "obsidian_registry_path", None)
    if requested_path:
        return Path(requested_path).expanduser().resolve(strict=False)
    return default_obsidian_registry_path()


def read_obsidian_registry(registry_path: Path) -> dict[str, object]:
    if not registry_path.exists():
        return {}
    return read_json_object(registry_path)


def normalized_vault_path_text(vault_path: Path) -> str:
    return str(vault_path.expanduser().resolve(strict=False))


def obsidian_vault_id(path_text: str, salt: str = "") -> str:
    return hashlib.sha256(f"{path_text}{salt}".encode("utf-8")).hexdigest()[:16]


def unique_obsidian_vault_id(vaults: dict[str, object], path_text: str) -> str:
    candidate = obsidian_vault_id(path_text)
    if candidate not in vaults:
        return candidate
    suffix = 2
    while True:
        candidate = obsidian_vault_id(path_text, f":{suffix}")
        if candidate not in vaults:
            return candidate
        suffix += 1


def vault_entry_matches_path(vault_entry: object, path_text: str) -> bool:
    if not isinstance(vault_entry, dict):
        return False
    entry_path = vault_entry.get("path")
    if not isinstance(entry_path, str):
        return False
    try:
        return normalized_vault_path_text(Path(entry_path)) == path_text
    except (OSError, RuntimeError, ValueError):
        return False


def registry_with_registered_vault(
    registry: dict[str, object],
    vault_path: Path,
    timestamp_ms: int | None = None,
) -> tuple[dict[str, object], bool]:
    vaults = registry.get("vaults", {})
    if not isinstance(vaults, dict):
        raise RuntimeError("invalid Obsidian registry: expected vaults to be a JSON object")

    path_text = normalized_vault_path_text(vault_path)
    if any(vault_entry_matches_path(vault_entry, path_text) for vault_entry in vaults.values()):
        return dict(registry), False

    updated_vaults = dict(vaults)
    updated_vaults[unique_obsidian_vault_id(updated_vaults, path_text)] = {
        "path": path_text,
        "ts": timestamp_ms if timestamp_ms is not None else int(time.time() * 1000),
    }
    updated_registry = dict(registry)
    updated_registry["vaults"] = updated_vaults
    return updated_registry, True


def write_obsidian_registry(registry_path: Path, registry: dict[str, object]) -> None:
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = registry_path.with_name(f".{registry_path.name}.tmp")
    temporary_path.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    temporary_path.replace(registry_path)


def ensure_obsidian_vault_registered(
    vault_path: Path,
    registry_path: Path,
    report: StatusReport,
    dry_run: bool,
) -> bool:
    path_text = normalized_vault_path_text(vault_path)
    try:
        registry = read_obsidian_registry(registry_path)
        updated_registry, changed = registry_with_registered_vault(registry, vault_path)
    except (OSError, RuntimeError) as error:
        report.add("failed", f"Obsidian vault registration failed: {error}")
        return False

    if not changed:
        report.add("already_present", f"Obsidian vault already registered in {registry_path}")
        return True

    if dry_run:
        report.add("skipped", f"dry-run would register Obsidian vault {path_text} in {registry_path}")
        return True

    try:
        write_obsidian_registry(registry_path, updated_registry)
    except OSError as error:
        report.add("failed", f"Obsidian vault registration failed: {error}")
        return False
    report.add("installed", f"registered Obsidian vault {path_text} in {registry_path}")
    return True


def ensure_requested_obsidian_vault_registration(
    args: argparse.Namespace,
    vault_path: Path,
    report: StatusReport,
) -> bool:
    if not getattr(args, "register_obsidian_vault", False):
        return True
    return ensure_obsidian_vault_registered(
        vault_path,
        obsidian_registry_path_from_args(args),
        report,
        args.dry_run,
    )


def enabled_plugins_with_codex_panel(enabled_plugins: list[str]) -> list[str]:
    updated_plugins: list[str] = []
    panel_added = False
    legacy_plugin_ids = set(LEGACY_OBSIDIAN_PLUGIN_IDS)

    for plugin_id in enabled_plugins:
        if plugin_id == CODEX_PANEL_PLUGIN_ID:
            if not panel_added:
                updated_plugins.append(plugin_id)
                panel_added = True
            continue
        if plugin_id in legacy_plugin_ids:
            if not panel_added:
                updated_plugins.append(CODEX_PANEL_PLUGIN_ID)
                panel_added = True
            continue
        updated_plugins.append(plugin_id)

    if not panel_added:
        updated_plugins.append(CODEX_PANEL_PLUGIN_ID)
    return updated_plugins


def ensure_codex_panel_enabled(
    obsidian_dir: Path,
    enabled_plugins: list[str],
    report: StatusReport,
    dry_run: bool,
) -> bool:
    updated_plugins = enabled_plugins_with_codex_panel(enabled_plugins)
    if updated_plugins == enabled_plugins:
        report.add("already_present", f"{CODEX_PANEL_PLUGIN_ID} listed in {community_plugins_path(obsidian_dir)}")
        return True

    if dry_run:
        report.add("skipped", f"dry-run would enable {CODEX_PANEL_PLUGIN_ID} in {community_plugins_path(obsidian_dir)}")
        return True
    try:
        write_enabled_community_plugins(obsidian_dir, updated_plugins)
    except OSError as error:
        report.add("failed", f"could not enable {CODEX_PANEL_PLUGIN_ID}: {error}")
        return False
    report.add("installed", f"enabled {CODEX_PANEL_PLUGIN_ID} in {community_plugins_path(obsidian_dir)}")
    return True


def replace_directory_atomically(source_dir: Path, destination_dir: Path) -> None:
    with tempfile.TemporaryDirectory(prefix=f".{destination_dir.name}-", dir=destination_dir.parent) as temp_dir:
        temp_path = Path(temp_dir)
        staged_dir = temp_path / destination_dir.name
        backup_dir = temp_path / f"{destination_dir.name}.backup"
        shutil.copytree(source_dir, staged_dir)
        if destination_dir.exists():
            shutil.move(str(destination_dir), backup_dir)
        try:
            shutil.move(str(staged_dir), destination_dir)
        except OSError:
            if backup_dir.exists() and not destination_dir.exists():
                shutil.move(str(backup_dir), destination_dir)
            raise


def obsidian_next_steps(include_read_only_test: bool) -> list[str]:
    steps = [
        "Open Obsidian.",
        "Confirm Community Plugins are enabled in Obsidian.",
        "If Codex Panel does not appear, open Settings -> Community plugins and click Reload plugins.",
        "Confirm Codex Panel is enabled.",
        "Run the command palette action Codex Panel: Open panel.",
    ]
    if include_read_only_test:
        steps.append("Run a harmless read-only prompt first.")
    return steps


def codex_panel_settings_path(plugin_dir: Path) -> Path:
    return plugin_dir / OBSIDIAN_PLUGIN_SETTINGS_FILE


def read_codex_panel_settings(plugin_dir: Path) -> dict[str, object]:
    settings_path = codex_panel_settings_path(plugin_dir)
    if not settings_path.exists():
        return {}
    return read_json_object(settings_path)


def is_valid_codex_path(path_text: object) -> bool:
    if not isinstance(path_text, str) or not path_text:
        return False
    path = Path(path_text).expanduser()
    return path.is_absolute() and path.exists() and path.is_file() and os.access(path, os.X_OK)


def codex_path_candidates(existing_settings: dict[str, object]) -> list[Path]:
    candidates: list[Path] = []
    existing_path = existing_settings.get("codexPath")
    if isinstance(existing_path, str):
        candidates.append(Path(existing_path).expanduser())
    path_codex = shutil.which("codex")
    if path_codex:
        candidates.append(Path(path_codex).expanduser())
    candidates.extend(
        [
            Path.home() / ".volta" / "bin" / "codex",
            Path("/Applications/Codex.app/Contents/Resources/codex"),
        ]
    )
    return candidates


def resolve_codex_path(existing_settings: dict[str, object]) -> str | None:
    seen_paths: set[Path] = set()
    for candidate in codex_path_candidates(existing_settings):
        resolved_candidate = candidate.resolve(strict=False)
        if resolved_candidate in seen_paths:
            continue
        seen_paths.add(resolved_candidate)
        candidate_text = str(candidate)
        if is_valid_codex_path(candidate_text):
            return candidate_text
    return None


def write_codex_panel_settings(plugin_dir: Path, settings: dict[str, object]) -> None:
    codex_panel_settings_path(plugin_dir).write_text(
        json.dumps(settings, indent=2) + "\n",
        encoding="utf-8",
    )


def ensure_codex_panel_settings(
    plugin_dir: Path,
    existing_settings: dict[str, object],
    report: StatusReport,
    dry_run: bool,
) -> bool:
    codex_path = resolve_codex_path(existing_settings)
    if codex_path is None:
        report.add("warnings", "could not find an absolute executable codex path for Codex Panel settings")
        return True

    settings = dict(existing_settings)
    settings["codexPath"] = codex_path
    if dry_run:
        report.add("skipped", f"dry-run would write {codex_panel_settings_path(plugin_dir)}")
        return True
    try:
        write_codex_panel_settings(plugin_dir, settings)
    except OSError as error:
        report.add("failed", f"could not write Codex Panel settings: {error}")
        return False
    report.add("installed", f"configured Codex Panel codexPath at {codex_panel_settings_path(plugin_dir)}")
    return True


def load_existing_plugin_settings(destination_dir: Path, report: StatusReport) -> dict[str, object] | None:
    try:
        return read_codex_panel_settings(destination_dir)
    except RuntimeError as error:
        report.add("failed", str(error))
        return None


def install_codex_panel(args: argparse.Namespace, report: StatusReport) -> None:
    vault_path = vault_path_from_args(args)
    if not vault_path.exists():
        report.add("failed", f"Obsidian vault path missing: {vault_path}")
        return

    if args.obsidian_release_sha256:
        report.add("failed", "--obsidian-release-sha256 is not supported because codex-panel installs individual release assets")
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
    destination_dir = plugins_dir / CODEX_PANEL_PLUGIN_ID
    existing_settings = load_existing_plugin_settings(destination_dir, report)
    if existing_settings is None:
        return

    if destination_dir.exists() and not args.force:
        report.add("skipped", f"{destination_dir} exists; use --force to replace")
        if not ensure_codex_panel_settings(destination_dir, existing_settings, report, args.dry_run):
            return
        if not ensure_codex_panel_enabled(obsidian_dir, enabled_plugins, report, args.dry_run):
            return
        if not ensure_requested_obsidian_vault_registration(args, vault_path, report):
            return
        return
    if args.dry_run:
        report.add("skipped", f"dry-run would download latest release assets from {DEFAULT_OBSIDIAN_REPO}/releases/latest")
        report.add("skipped", f"dry-run would install plugin to {destination_dir}")
        ensure_codex_panel_settings(destination_dir, existing_settings, report, args.dry_run)
        ensure_codex_panel_enabled(obsidian_dir, enabled_plugins, report, args.dry_run)
        if not ensure_requested_obsidian_vault_registration(args, vault_path, report):
            return
        report.next_steps.extend(obsidian_next_steps(include_read_only_test=False))
        return

    try:
        with tempfile.TemporaryDirectory(prefix="obsidian-plugin-") as temp_dir:
            temp_path = Path(temp_dir)
            plugin_root = temp_path / CODEX_PANEL_PLUGIN_ID
            asset_urls = latest_obsidian_release_asset_urls(args.obsidian_release_url)
            download_release_assets(asset_urls, plugin_root)
            ensure_required_plugin_files(plugin_root)
            validate_plugin_manifest(plugin_root)
            replace_directory_atomically(plugin_root, destination_dir)
    except (
        OSError,
        RuntimeError,
        urllib.error.URLError,
        json.JSONDecodeError,
    ) as error:
        report.add("failed", f"Obsidian plugin install failed: {error}")
        return
    report.add("installed", f"installed Obsidian plugin to {destination_dir}")
    if not ensure_codex_panel_settings(destination_dir, existing_settings, report, args.dry_run):
        return
    if not ensure_codex_panel_enabled(obsidian_dir, enabled_plugins, report, args.dry_run):
        return
    if not ensure_requested_obsidian_vault_registration(args, vault_path, report):
        return
    report.next_steps.extend(obsidian_next_steps(include_read_only_test=True))


def print_summary(report: StatusReport) -> None:
    report.print_summary("Obsidian plugin install report")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    report = StatusReport()
    if args.dry_run:
        print("Dry run: no Obsidian plugin files will be changed.\n")
    install_codex_panel(args, report)
    print_summary(report)
    return 1 if report.failed else 0


if __name__ == "__main__":
    sys.exit(main())
