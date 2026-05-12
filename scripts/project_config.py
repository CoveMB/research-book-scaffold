"""Shared paths and integration constants for scaffold scripts."""

from __future__ import annotations

import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARS_REPO = "https://github.com/Imbad0202/academic-research-skills.git"
DEFAULT_RBS_REPO = "https://github.com/CoveMB/research-book-skills.git"

GITMODULES_PATH = Path(".gitmodules")
ARS_VENDOR = Path("vendor/academic-research-skills")
RBS_VENDOR = Path("vendor/research-book-skills")
SKILLS_DIR = Path(".agents/skills")
PLUGIN_MARKETPLACE = Path(".agents/plugins/marketplace.json")
MARKETPLACE_PLUGIN_PATH = "./vendor/research-book-skills"
LEGACY_RBS_PLUGIN = Path("plugins/research-book-skills")
RBS_MARKETPLACE_NAME = "research-book-skills"
RBS_PLUGIN_JSON_NAME = "scholarly-research-book"

ARS_SKILLS = ["deep-research", "academic-paper", "academic-paper-reviewer", "academic-pipeline"]
RBS_SKILLS = [
    "research-book-orchestrator",
    "scholarly-research-agenda",
    "systematic-source-discovery",
    "discovery-runner-deduper",
    "annotation-to-source-note",
    "extraction-table-builder",
    "literature-review-mapper",
    "annotated-bibliography-builder",
    "methodology-source-auditor",
    "claim-evidence-ledger",
    "claim-traceability-graph",
    "argument-architecture",
    "counterargument-peer-review",
    "chapter-architecture",
    "scholarly-prose-editor",
    "citation-integrity-auditor",
    "rights-privacy-release-auditor",
    "manuscript-continuity-editor",
    "case-study-integration",
    "book-proposal-scholarship",
    "book-comps-verifier",
]

OBSIDIAN_CODEX_PLUGIN_ID = "obsidian-codex"
OBSIDIAN_DIR = Path(".obsidian")
OBSIDIAN_PLUGINS_DIR = OBSIDIAN_DIR / "plugins"
OBSIDIAN_PLUGIN_DIR = OBSIDIAN_PLUGINS_DIR / OBSIDIAN_CODEX_PLUGIN_ID
REQUIRED_OBSIDIAN_PLUGIN_FILES = {"manifest.json", "main.js", "styles.css"}


def resolve_obsidian_vault_path(
    requested_path: str | None,
    env_value: str | None,
    cwd: Path | None = None,
) -> Path:
    if requested_path:
        return Path(requested_path).expanduser().resolve()
    if env_value:
        return Path(env_value).expanduser().resolve()
    return (cwd or Path.cwd()).resolve()


def change_to_project_root() -> None:
    os.chdir(PROJECT_ROOT)
