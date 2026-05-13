"""Shared paths and integration constants for scaffold scripts."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARS_REPO = "https://github.com/Imbad0202/academic-research-skills.git"
DEFAULT_RBS_REPO = "https://github.com/CoveMB/research-book-skills.git"
DEFAULT_SUBAGENT_ORCHESTRATOR_REPO = "https://github.com/CoveMB/subagent-orchestration-plugin.git"

GITMODULES_PATH = Path(".gitmodules")
ARS_VENDOR = Path("vendor/academic-research-skills")
RBS_VENDOR = Path("vendor/research-book-skills")
SUBAGENT_ORCHESTRATOR_VENDOR = Path("vendor/subagent-orchestration-plugin")
SKILLS_DIR = Path(".agents/skills")
PLUGIN_MARKETPLACE = Path(".agents/plugins/marketplace.json")
MARKETPLACE_PLUGIN_PATH = "./vendor/research-book-skills"
SUBAGENT_ORCHESTRATOR_PLUGIN_PATH = "./vendor/subagent-orchestration-plugin/plugin/subagent-orchestrator"
SUBAGENT_ORCHESTRATOR_PLUGIN_ROOT = SUBAGENT_ORCHESTRATOR_VENDOR / "plugin" / "subagent-orchestrator"
LEGACY_RBS_PLUGIN = Path("plugins/research-book-skills")
RBS_MARKETPLACE_NAME = "research-book-skills"
RBS_PLUGIN_JSON_NAME = "scholarly-research-book"
SUBAGENT_ORCHESTRATOR_MARKETPLACE_NAME = "subagent-orchestrator"
SUBAGENT_ORCHESTRATOR_PLUGIN_JSON_NAME = "subagent-orchestrator"


@dataclass(frozen=True)
class ExternalVendorSpec:
    key: str
    label: str
    path: Path
    default_repo: str
    branch: str = "main"


@dataclass(frozen=True)
class ExternalPluginSpec:
    vendor_key: str
    label: str
    marketplace_name: str
    plugin_path: str
    plugin_root: Path
    plugin_json_name: str
    skills_root: Path
    skill_names: tuple[str, ...]


@dataclass(frozen=True)
class CommandSpec:
    command: tuple[str, ...]
    action: str

    def shell_text(self) -> str:
        return " ".join(self.command)


ARS_SKILLS = ["deep-research", "academic-paper", "academic-paper-reviewer", "academic-pipeline"]
SUBAGENT_ORCHESTRATOR_SKILLS = ["using-subagent-orchestrator", "subagent-orchestrator"]
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

EXTERNAL_VENDOR_SPECS = (
    ExternalVendorSpec("ars", "ARS", ARS_VENDOR, DEFAULT_ARS_REPO),
    ExternalVendorSpec("rbs", "RBS", RBS_VENDOR, DEFAULT_RBS_REPO),
    ExternalVendorSpec(
        "subagent-orchestrator",
        "Subagent Orchestrator",
        SUBAGENT_ORCHESTRATOR_VENDOR,
        DEFAULT_SUBAGENT_ORCHESTRATOR_REPO,
    ),
)

RBS_PLUGIN_SPEC = ExternalPluginSpec(
    "rbs",
    "RBS",
    RBS_MARKETPLACE_NAME,
    MARKETPLACE_PLUGIN_PATH,
    RBS_VENDOR,
    RBS_PLUGIN_JSON_NAME,
    RBS_VENDOR / "skills",
    tuple(RBS_SKILLS),
)
SUBAGENT_ORCHESTRATOR_PLUGIN_SPEC = ExternalPluginSpec(
    "subagent-orchestrator",
    "Subagent Orchestrator",
    SUBAGENT_ORCHESTRATOR_MARKETPLACE_NAME,
    SUBAGENT_ORCHESTRATOR_PLUGIN_PATH,
    SUBAGENT_ORCHESTRATOR_PLUGIN_ROOT,
    SUBAGENT_ORCHESTRATOR_PLUGIN_JSON_NAME,
    SUBAGENT_ORCHESTRATOR_PLUGIN_ROOT / "skills",
    tuple(SUBAGENT_ORCHESTRATOR_SKILLS),
)
EXTERNAL_PLUGIN_SPECS = (
    RBS_PLUGIN_SPEC,
    SUBAGENT_ORCHESTRATOR_PLUGIN_SPEC,
)

SETUP_RECOMMENDED_CHECKS = (
    CommandSpec(("bash", "scripts/doctor.sh"), "run repository doctor"),
    CommandSpec(("python3", "scripts/check_external_skills.py"), "check external skill integrations"),
    CommandSpec(("python3", "scripts/check_obsidian_codex.py"), "check Obsidian plugin install"),
    CommandSpec(("python3", "scripts/check_citations.py"), "check manuscript citations"),
    CommandSpec(("python3", "scripts/check_placeholders.py", "."), "check unresolved placeholders"),
)

VENDOR_UPDATE_HEALTH_CHECKS = (
    CommandSpec(("python3", "scripts/check_external_skills.py"), "check external skill integrations"),
    CommandSpec(("bash", "scripts/doctor.sh"), "run repository doctor"),
)

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
