"""Install and verify the required Obsidian agent plugin."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

from project_config import (
    OBSIDIAN_CODEX_PLUGIN_ID,
    OBSIDIAN_DIR,
    OBSIDIAN_PLUGINS_DIR,
    REQUIRED_OBSIDIAN_PLUGIN_FILES,
    resolve_obsidian_vault_path,
)
from script_utils import StatusReport


DEFAULT_OBSIDIAN_REPO = "https://github.com/AKin-lvyifang/obsidian-codex"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--obsidian-vault")
    parser.add_argument("--obsidian-release-url")
    parser.add_argument("--obsidian-release-sha256")
    return parser.parse_args(argv)


def vault_path_from_args(args: argparse.Namespace) -> Path:
    return resolve_obsidian_vault_path(args.obsidian_vault, os.environ.get("OBSIDIAN_VAULT"))


def latest_obsidian_release_zip_url() -> str:
    api_url = "https://api.github.com/repos/AKin-lvyifang/obsidian-codex/releases/latest"
    request = urllib.request.Request(api_url, headers={"Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    for asset in payload.get("assets", []):
        download_url = asset.get("browser_download_url", "")
        file_name = download_url.rsplit("/", 1)[-1].lower()
        if file_name.startswith("obsidian-codex-") and file_name.endswith(".zip"):
            return download_url
    raise RuntimeError("No obsidian-codex release zip asset found for latest Obsidian plugin release")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_archive_checksum(path: Path, expected_sha256: str | None) -> None:
    if not expected_sha256:
        return
    actual_sha256 = sha256_file(path)
    if actual_sha256.lower() != expected_sha256.lower():
        raise RuntimeError(f"archive checksum mismatch: expected {expected_sha256}, got {actual_sha256}")


def safe_extract_zip(archive: zipfile.ZipFile, destination: Path) -> None:
    destination_root = destination.resolve()
    for member in archive.infolist():
        target = (destination / member.filename).resolve()
        if destination_root != target and destination_root not in target.parents:
            raise ValueError(f"unsafe archive path: {member.filename}")
    archive.extractall(destination)


def find_obsidian_plugin_root(extracted_dir: Path) -> Path | None:
    for path in extracted_dir.rglob("*"):
        if not path.is_dir():
            continue
        if REQUIRED_OBSIDIAN_PLUGIN_FILES.issubset({child.name for child in path.iterdir() if child.is_file()}):
            return path
    return None


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


def ensure_obsidian_codex_enabled(
    obsidian_dir: Path,
    enabled_plugins: list[str],
    report: StatusReport,
    dry_run: bool,
) -> bool:
    if OBSIDIAN_CODEX_PLUGIN_ID in enabled_plugins:
        report.add("already_present", f"{OBSIDIAN_CODEX_PLUGIN_ID} listed in {community_plugins_path(obsidian_dir)}")
        return True

    updated_plugins = [*enabled_plugins, OBSIDIAN_CODEX_PLUGIN_ID]
    if dry_run:
        report.add("skipped", f"dry-run would enable {OBSIDIAN_CODEX_PLUGIN_ID} in {community_plugins_path(obsidian_dir)}")
        return True
    try:
        write_enabled_community_plugins(obsidian_dir, updated_plugins)
    except OSError as error:
        report.add("failed", f"could not enable {OBSIDIAN_CODEX_PLUGIN_ID}: {error}")
        return False
    report.add("installed", f"enabled {OBSIDIAN_CODEX_PLUGIN_ID} in {community_plugins_path(obsidian_dir)}")
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
        "Restart Obsidian.",
        "Confirm Community Plugins are enabled in Obsidian.",
        "Confirm Codex for Obsidian is enabled.",
    ]
    if include_read_only_test:
        steps.append("Open the plugin sidebar and run a harmless read-only test first.")
    return steps


def install_obsidian_codex(args: argparse.Namespace, report: StatusReport) -> None:
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
    destination_dir = plugins_dir / OBSIDIAN_CODEX_PLUGIN_ID
    if destination_dir.exists() and not args.force:
        report.add("skipped", f"{destination_dir} exists; use --force to replace")
        ensure_obsidian_codex_enabled(obsidian_dir, enabled_plugins, report, args.dry_run)
        return
    if args.dry_run:
        report.add("skipped", f"dry-run would download latest release from {DEFAULT_OBSIDIAN_REPO}/releases/latest")
        report.add("skipped", f"dry-run would install plugin to {destination_dir}")
        ensure_obsidian_codex_enabled(obsidian_dir, enabled_plugins, report, args.dry_run)
        report.next_steps.extend(obsidian_next_steps(include_read_only_test=False))
        return

    try:
        with tempfile.TemporaryDirectory(prefix="obsidian-plugin-") as temp_dir:
            temp_path = Path(temp_dir)
            zip_url = args.obsidian_release_url or latest_obsidian_release_zip_url()
            archive_path = temp_path / "release.zip"
            urllib.request.urlretrieve(zip_url, archive_path)
            verify_archive_checksum(archive_path, args.obsidian_release_sha256)
            extract_dir = temp_path / "extract"
            extract_dir.mkdir()
            with zipfile.ZipFile(archive_path) as archive:
                safe_extract_zip(archive, extract_dir)
            plugin_root = find_obsidian_plugin_root(extract_dir)
            if plugin_root is None:
                report.add("failed", "Downloaded Obsidian plugin release does not contain expected files")
                return
            replace_directory_atomically(plugin_root, destination_dir)
    except (
        OSError,
        RuntimeError,
        ValueError,
        zipfile.BadZipFile,
        urllib.error.URLError,
        json.JSONDecodeError,
    ) as error:
        report.add("failed", f"Obsidian plugin install failed: {error}")
        return
    report.add("installed", f"installed Obsidian plugin to {destination_dir}")
    if not ensure_obsidian_codex_enabled(obsidian_dir, enabled_plugins, report, args.dry_run):
        return
    report.next_steps.extend(obsidian_next_steps(include_read_only_test=True))


def print_summary(report: StatusReport) -> None:
    print("\nObsidian plugin install report")
    sections = [
        ("Installed", report.installed),
        ("Already present", report.already_present),
        ("Skipped", report.skipped),
        ("Failed", report.failed),
        ("Warnings", report.warnings),
        ("Next manual steps", report.next_steps),
    ]
    for title, values in sections:
        print(f"\n{title}:")
        if not values:
            print("- none")
        else:
            for value in values:
                print(f"- {value}")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    report = StatusReport()
    if args.dry_run:
        print("Dry run: no Obsidian plugin files will be changed.\n")
    install_obsidian_codex(args, report)
    print_summary(report)
    return 1 if report.failed else 0


if __name__ == "__main__":
    sys.exit(main())
