"""Shared paths and integration constants for scaffold scripts."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ARS_CODEX_REPO = "https://github.com/Imbad0202/academic-research-skills-codex.git"
ARS_CODEX_PIN = "925975e933a20893b81681d925a3404e3b7f73b7"
LEGACY_ARS_GITLINK = "81c7300b4066d233914563fc1c3f80512347b33c"
DEFAULT_RBS_REPO = "https://github.com/CoveMB/research-book-skills.git"
DEFAULT_OBSIDIAN_SKILLS_REPO = "https://github.com/kepano/obsidian-skills.git"

GITMODULES_PATH = Path(".gitmodules")
LEGACY_ARS_SOURCE = Path("skill-plugins/academic-research-skills")
ARS_CODEX_SOURCE = Path("skill-plugins/academic-research-skills-codex")
RBS_SOURCE = Path("skill-plugins/research-book-skills")
OBSIDIAN_SKILLS_SOURCE = Path("skill-plugins/obsidian-skills")
SKILLS_DIR = Path(".agents/skills")
PLUGIN_MARKETPLACE = Path(".agents/plugins/marketplace.json")
MARKETPLACE_PLUGIN_PATH = "./skill-plugins/research-book-skills"
RBS_MARKETPLACE_NAME = "research-book-skills"
RBS_PLUGIN_JSON_NAME = "research-skills-plugin"
MARKETPLACE_INSTALLATION_POLICY = "AVAILABLE"
MARKETPLACE_AUTHENTICATION_POLICY = "ON_INSTALL"


@dataclass(frozen=True)
class ExternalSourceSpec:
    key: str
    label: str
    path: Path
    default_repo: str
    branch: str = "main"
    pinned_ref: str | None = None


@dataclass(frozen=True)
class ExternalPluginSpec:
    source_key: str
    label: str
    marketplace_name: str
    plugin_path: str
    plugin_root: Path
    plugin_json_name: str
    skills_root: Path
    skill_names: tuple[str, ...]
    category: str


@dataclass(frozen=True)
class CommandSpec:
    command: tuple[str, ...]
    action: str

    def shell_text(self) -> str:
        return " ".join(self.command)


OBSIDIAN_SKILLS = ["obsidian-markdown", "obsidian-bases", "json-canvas", "obsidian-cli", "defuddle"]
OBSIDIAN_SKILL_WRAPPERS = {
    "obsidian-markdown": "obsidian-research-markdown",
    "obsidian-bases": "obsidian-research-bases",
    "json-canvas": "obsidian-research-canvas",
    "obsidian-cli": "obsidian-research-cli",
    "defuddle": "obsidian-research-defuddle",
}
RBS_SKILLS = [
    "research-intent-router",
    "dyslexia-research-companion",
    "dictation-to-research-notes",
    "reading-load-reducer",
    "dyslexia-friendly-prose-editor",
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
    "figure-table-integrity-auditor",
    "scholarly-integrity-gate",
    "ai-human-workflow-log",
    "rights-privacy-release-auditor",
    "manuscript-continuity-editor",
    "case-study-integration",
    "book-proposal-scholarship",
    "book-comps-verifier",
]
RBS_SKILL_WRAPPERS = {skill_name: f"rbs-{skill_name}" for skill_name in RBS_SKILLS}
LOCAL_PROJECT_SKILLS = (
    "quarto-export-readiness",
    "vault-hygiene-triage",
)
REPO_SCOPED_SKILL_NAMES = tuple(
    sorted(
        (
            *LOCAL_PROJECT_SKILLS,
            *RBS_SKILL_WRAPPERS.values(),
            *OBSIDIAN_SKILL_WRAPPERS.values(),
        )
    )
)

EXTERNAL_SOURCE_SPECS = (
    ExternalSourceSpec("ars", "ARS Codex", ARS_CODEX_SOURCE, ARS_CODEX_REPO, pinned_ref=ARS_CODEX_PIN),
    ExternalSourceSpec("rbs", "RBS", RBS_SOURCE, DEFAULT_RBS_REPO),
    ExternalSourceSpec(
        "obsidian-skills",
        "Obsidian Skills",
        OBSIDIAN_SKILLS_SOURCE,
        DEFAULT_OBSIDIAN_SKILLS_REPO,
    ),
)

RBS_PLUGIN_SPEC = ExternalPluginSpec(
    "rbs",
    "RBS",
    RBS_MARKETPLACE_NAME,
    MARKETPLACE_PLUGIN_PATH,
    RBS_SOURCE,
    RBS_PLUGIN_JSON_NAME,
    RBS_SOURCE / "skills",
    tuple(RBS_SKILLS),
    "Productivity",
)
ARS_CODEX_PLUGIN_ROOT = ARS_CODEX_SOURCE / "plugins" / "ars-codex"
ARS_CODEX_PLUGIN_SPEC = ExternalPluginSpec(
    "ars",
    "ARS Codex",
    "ars-codex",
    "./skill-plugins/academic-research-skills-codex/plugins/ars-codex",
    ARS_CODEX_PLUGIN_ROOT,
    "ars-codex",
    ARS_CODEX_PLUGIN_ROOT / "skills",
    ("academic-research-suite",),
    "Research",
)
EXTERNAL_PLUGIN_SPECS = (ARS_CODEX_PLUGIN_SPEC, RBS_PLUGIN_SPEC)

SETUP_RECOMMENDED_CHECKS = (
    CommandSpec(("bash", "scripts/operations/health/doctor.sh"), "run repository doctor"),
    CommandSpec(("python3", "scripts/operations/skill_plugins/check_external_skills.py"), "check external skill integrations"),
    CommandSpec(("python3", "scripts/operations/obsidian/check_obsidian_panel.py"), "check Codex Panel install"),
    CommandSpec(
        ("python3", "scripts/operations/obsidian/obsidian_research_plugins.py", "check"),
        "check Obsidian research plugins",
    ),
    CommandSpec(("python3", "scripts/operations/obsidian/check_obsidian_artifacts.py"), "check Obsidian artifacts"),
    CommandSpec(("python3", "scripts/research-writing/check_citations.py"), "check manuscript citations"),
    CommandSpec(("python3", "scripts/research-writing/check_placeholders.py", "."), "check unresolved placeholders"),
)

SKILL_PLUGIN_UPDATE_HEALTH_CHECKS = (
    CommandSpec(("python3", "scripts/operations/skill_plugins/check_external_skills.py"), "check external skill integrations"),
    CommandSpec(("bash", "scripts/operations/health/doctor.sh"), "run repository doctor"),
)

CODEX_PANEL_PLUGIN_ID = "codex-panel"
ZOTERO_INTEGRATION_PLUGIN_ID = "obsidian-zotero-desktop-connector"
PANDOC_REFERENCE_LIST_PLUGIN_ID = "obsidian-pandoc-reference-list"
QMD_AS_MD_PLUGIN_ID = "qmd-as-md-obsidian"
OBSIDIAN_RESEARCH_PLUGIN_IDS = (
    ZOTERO_INTEGRATION_PLUGIN_ID,
    PANDOC_REFERENCE_LIST_PLUGIN_ID,
    QMD_AS_MD_PLUGIN_ID,
)
OBSIDIAN_DIR = Path(".obsidian")
OBSIDIAN_PLUGINS_DIR = OBSIDIAN_DIR / "plugins"
OBSIDIAN_PLUGIN_DIR = OBSIDIAN_PLUGINS_DIR / CODEX_PANEL_PLUGIN_ID
REQUIRED_OBSIDIAN_PLUGIN_FILES = {"manifest.json", "main.js", "styles.css"}
OBSIDIAN_PLUGIN_SETTINGS_FILE = "data.json"


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
