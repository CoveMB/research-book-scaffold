"""Shared paths and integration constants for scaffold scripts."""

from __future__ import annotations

from pathlib import Path


DEFAULT_ARS_REPO = "https://github.com/Imbad0202/academic-research-skills.git"
DEFAULT_RBS_REPO = "https://github.com/CoveMB/research-book-skills.git"

GITMODULES_PATH = Path(".gitmodules")
ARS_VENDOR = Path("vendor/academic-research-skills")
RBS_VENDOR = Path("vendor/research-book-skills")
SKILLS_DIR = Path(".agents/skills")
PLUGIN_MARKETPLACE = Path(".agents/plugins/marketplace.json")
MARKETPLACE_PLUGIN_PATH = "./vendor/research-book-skills"
LEGACY_RBS_PLUGIN = Path("plugins/research-book-skills")

ARS_SKILLS = ["deep-research", "academic-paper", "academic-paper-reviewer", "academic-pipeline"]
RBS_SKILLS = [
    "research-book-orchestrator",
    "scholarly-research-agenda",
    "systematic-source-discovery",
    "literature-review-mapper",
    "annotated-bibliography-builder",
    "methodology-source-auditor",
    "claim-evidence-ledger",
    "argument-architecture",
    "counterargument-peer-review",
    "chapter-architecture",
    "scholarly-prose-editor",
    "citation-integrity-auditor",
    "manuscript-continuity-editor",
    "case-study-integration",
    "book-proposal-scholarship",
]

OBSIDIAN_PLUGIN_DIR = Path(".obsidian/plugins/obsidian-codex")
REQUIRED_OBSIDIAN_PLUGIN_FILES = {"manifest.json", "main.js", "styles.css"}
