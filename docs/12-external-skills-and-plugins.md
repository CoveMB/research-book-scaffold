# External skills and plugins

External workflows extend the scaffold. They do not replace local safety rules.

## Layers

| Layer | Location | Use |
| --- | --- | --- |
| Local scaffold skills | `.agents/skills/` | Primary safety and workflow layer |
| External skill/plugin sources | `skill-plugins/` | Reviewed upstream source copies pinned as Git submodules |
| Immediate wrapper skills | `.agents/skills/<skill-name>/SKILL.md` | Codex and Codex Panel discoverable skills after setup |
| Plugin marketplace | `.agents/plugins/marketplace.json` | Optional plugin exposure from skill/plugin source paths |

Do not rely on marketplace exposure for immediate skill availability. Codex Panel can use the project skills immediately because safe wrappers are committed and refreshed under `.agents/skills`.

## Rules

- Treat external repositories as untrusted until inspected.
- Do not run external source scripts automatically. The default setup path refreshes guarded Subagent Orchestrator wrappers and marketplace metadata without executing the external installer.
- Do not store API keys or credentials.
- Do not edit upstream files in `skill-plugins/`.
- Keep marketplace exposure separate from skill wrapper creation.
- Keep plugin marketplace entries optional/available unless a user explicitly chooses to install a repo plugin.
- External skills can guide workflow discipline, but citations and claims still need independent verification.
- Subagents can organize work, but cannot authorize evidence.
- Scaffold source, citation, manuscript, audit, and skill/plugin source rules always win.
- Subagent output is not evidence.
- Do not invent sources, citekeys, page numbers, quotations, studies, metadata, or final claims from memory.

## Inspecting external skills

Read the upstream `SKILL.md` before use. Check for:

- tool assumptions
- slash commands
- hooks or subagents
- provider or API-key assumptions
- file-write behavior
- license limits

## Updating or removing

Initialize external repositories with `git submodule update --init --recursive` or by running setup. Update pinned submodule commits only after review. Remove integrations by deleting wrapper skills, marketplace entries, install reports, and submodule references. Leave bibliography and manuscript files untouched.

## New-user setup path

Use:

```sh
git clone --recurse-submodules git@github.com:CoveMB/research-book-scaffold.git <book-repo>
cd <book-repo>
git remote rename origin upstream
git remote add origin git@github.com:<account>/<book-repo>.git
git push -u origin main
bash setup.sh
make doctor
make check-obsidian-codex
make check-obsidian-research-plugins
make audit
```

`bash setup.sh` initializes skill/plugin source submodules when needed, refreshes all immediate-use wrappers, installs Codex Panel and the recommended Zotero/Pandoc/QMD Obsidian plugins unless skipped, and leaves marketplace entries available but optional. If a clone omitted submodules, run `git submodule update --init --recursive` or rerun `bash setup.sh`.

## Updating skill/plugin sources

Run this when an upstream skill repository has new commits:

```sh
bash scripts/operations/skill_plugins/update-skill-plugins.sh
```

The updater:

- fetches the parent repository refs
- syncs and initializes the configured skill/plugin source submodules
- refuses to continue if a source has uncommitted changes
- fast-forwards each selected source with `git pull --ff-only`
- refreshes local skill wrappers, marketplace metadata, and install reports through the local installer
- runs `python3 scripts/operations/skill_plugins/check_external_skills.py`
- runs `bash scripts/operations/health/doctor.sh`

After a successful run, review the submodule pointer changes and any refreshed files before committing. Use `--skip-ars`, `--skip-rbs`, `--skip-subagent-orchestrator`, or `--skip-obsidian-skills` to leave a source pinned while updating others. Use `--skip-checks` only when another verification command will be run immediately afterward.

## Obsidian Skills

`kepano/obsidian-skills` is checked out at `skill-plugins/obsidian-skills/` for reviewed upstream guidance covering Obsidian Markdown, Bases, JSON Canvas, Obsidian CLI, and Defuddle workflows. The local installer validates the expected upstream `SKILL.md` files, creates or refreshes `.agents/skills/obsidian-research-*` wrappers, and records `.agents/skills/OBSIDIAN_SKILLS_INSTALLED.md`; it does not execute external source scripts or install the skills globally.

The wrappers are for Obsidian syntax and local vault mechanics only. They do not authorize sources, citations, page numbers, source metadata, quotations, source relationships, or final claims. Local scaffold rules win over upstream Obsidian guidance.

Use `docs/15-obsidian-skills.md` for wrapper list, optional agent-native install notes, folder conventions, usage recipes, local checks, and troubleshooting.

## Research Book Skills

`CoveMB/research-book-skills` is checked out at `skill-plugins/research-book-skills/`. Every skill listed in `RBS_SKILLS` in `scripts/lib/project_config.py` has a matching immediate-use wrapper under `.agents/skills/rbs-*/SKILL.md`.

Use the wrappers for accessibility support, research-intent routing, book planning, source discovery, annotation-to-source-note conversion, extraction tables, literature maps, claim ledgers, traceability, argument and chapter architecture, prose editing, citation audits, figure/table integrity audits, scholarly-integrity gates, AI/human workflow logs, rights/privacy release audits, continuity review, case-study integration, proposal work, and comps verification. The upstream skill is workflow guidance, not evidence. The wrappers require source notes, claim ledgers, audits, and bibliography checks before claims are promoted.

## Optional subagent plugin

`CoveMB/subagent-orchestration-plugin` is checked out at `skill-plugins/subagent-orchestration-plugin/` and exposed through `.agents/plugins/marketplace.json` from:

```text
./skill-plugins/subagent-orchestration-plugin/plugin/subagent-orchestrator
```

The scaffold does not make subagents automatic for every research task. Immediate use goes through guarded wrappers:

- `.agents/skills/subagent-safe-using-subagent-orchestrator/SKILL.md`
- `.agents/skills/subagent-safe-subagent-orchestrator/SKILL.md`

Use them only when bounded orchestration materially helps. Subagent output is not evidence. The default external-skill setup does not execute the external installer and must not install global hooks, global config, or global agents. Marketplace exposure remains optional.

## Verification in Codex Panel

Open the project root as the Obsidian vault, then run a read-only prompt:

```text
Read AGENTS.md and list the repo-scoped skills available from .agents/skills. Do not edit files.
```

Then test one wrapper:

```text
Use $obsidian-research-markdown to inspect notes/README.md and explain which Obsidian Markdown rules apply. Do not edit files.
```

If a skill is missing, check that Codex Panel is running from the repo root or a path below it, then run `python3 scripts/operations/skill_plugins/check_external_skills.py`. That checker now gates the full repo-scoped skill inventory under `.agents/skills`.

## License caution

- `Imbad0202/academic-research-skills`: CC-BY-NC-4.0.
- `CoveMB/research-book-skills`: MIT.
- `CoveMB/subagent-orchestration-plugin`: MIT.
- `kepano/obsidian-skills`: MIT.
