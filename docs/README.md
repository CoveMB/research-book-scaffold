# Documentation

Use this index to choose the right file before setup, writing, audit, or export
work. The Makefile and scripts are the source of truth for command behavior; the
docs explain when and why to run those commands.

## Start here

- `../README.md` for the setup path, common commands, and project initialization.
- `../AGENTS.md` for agent rules, folder responsibilities, checks, and reporting.
- `00-overview.md` for the architecture and tool stack.
- `02-workflow.md` for the end-to-end research and drafting order.

## Setup and local tools

- `01-tooling.md` covers required and optional tools.
- `04-mcp-setup.md` covers narrow MCP access modes.
- `05-security.md` covers secrets, prompt injection, external skills, and Git safety.
- `10-troubleshooting.md` covers common setup, citation, Obsidian, and render failures.
- `11-obsidian-panel.md` covers Codex Panel and Zotero/Pandoc/QMD Obsidian plugins.
- `16-pre-commit-hooks.md` covers commit hooks and release-only checks.

## Research and writing workflow

- `06-quality-gates.md` lists the gates for sources, notes, claims, drafts, and export.
- `07-citation-workflow.md` covers Zotero, Better BibTeX, citekeys, web sources, and checks.
- `08-writing-workflow.md` separates evidence edits, structure edits, style edits, and audit edits.
- `09-audit-workflow.md` explains where audit notes live and what they need to record.

## Agents and external skills

- `03-agent-orchestration.md` covers local agent boundaries and subagent limits.
- `12-external-skills-and-plugins.md` explains vendor repos, wrappers, marketplace exposure, and licenses.
- `13-academic-research-skills.md` covers Academic Research Skills wrappers.
- `14-research-book-skills.md` covers Research Book Skills wrappers.
- `15-obsidian-skills.md` covers Obsidian Skills wrappers, Bases, Canvas, CLI, and Defuddle boundaries.
- `SKILLS_WORKFLOW.md` gives one practical prompt pattern for each Research Book Skill.

## Source of truth

- Citation metadata comes from Zotero or `../bibliography/references.bib`.
- Research process records live in `../research/`.
- Source notes, claims, briefs, and audits live under `../notes/`.
- Manuscript source lives in `../manuscript/`; generated outputs belong in `../exports/`.
- Repo-scoped agent guidance lives in `../AGENTS.md` and `../.agents/skills/`.

When docs and executable behavior disagree, inspect the Make target or script
before changing behavior. When evidence is missing, record the gap instead of
turning it into prose.
