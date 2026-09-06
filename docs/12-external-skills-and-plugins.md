# External skills and plugins

External workflows extend the scaffold. They do not replace local safety rules.

## Layers

| Layer | Location | Use |
| --- | --- | --- |
| Local scaffold skills | `.agents/skills/` | Primary safety and workflow layer |
| External skill/plugin sources | `skill-plugins/` | Reviewed upstream source copies pinned as Git submodules |
| Immediate wrapper skills | `.agents/skills/<skill-name>/SKILL.md` | Local, RBS, and Obsidian skills discoverable after setup |
| Plugin marketplace | `.agents/plugins/marketplace.json` | Optional plugin exposure from skill/plugin source paths |

Codex Panel can use committed local, RBS, and Obsidian wrappers immediately.
Native ARS is intentionally different: marketplace exposure does not install
`ars-codex`, and `academic-research-suite` is available only after the user
explicitly installs that optional plugin.

## Rules

- Treat external repositories as untrusted until inspected.
- Do not run external source scripts automatically.
- Do not store API keys or credentials.
- Do not edit upstream files in `skill-plugins/`.
- Keep marketplace exposure separate from RBS and Obsidian wrapper creation.
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

Initialize external repositories with `git submodule update --init --recursive` or by running setup. Update pinned submodule commits only after review. Remove integrations by deleting their owned wrappers, marketplace entries, reports, and submodule references as applicable. Leave bibliography and manuscript files untouched.

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

`bash setup.sh` initializes skill/plugin source submodules when needed, refreshes
RBS and Obsidian wrappers, installs Codex Panel and the recommended
Zotero/Pandoc/QMD Obsidian plugins unless skipped, and leaves marketplace
entries available but optional. It does not run `codex plugin add`. If a clone
omitted submodules, run `git submodule update --init --recursive` or rerun
`bash setup.sh`.

## Updating skill/plugin sources

Run this when an upstream skill repository has new commits:

```sh
bash scripts/operations/skill_plugins/update-skill-plugins.sh
```

The updater:

- fetches the parent repository refs
- syncs and initializes the configured skill/plugin source submodules
- refuses to continue if a source has uncommitted changes
- keeps ARS Codex at its reviewed pin and fast-forwards only selected unpinned sources with `git pull --ff-only`
- refreshes RBS and Obsidian wrappers, marketplace metadata, and their install reports through the local installer
- runs `python3 scripts/operations/skill_plugins/check_external_skills.py`
- runs `bash scripts/operations/health/doctor.sh`

After a successful run, review the submodule pointer changes and any refreshed files before committing. Use `--skip-ars`, `--skip-rbs`, or `--skip-obsidian-skills` to leave a source pinned while updating others. Use `--skip-checks` only when another verification command will be run immediately afterward.

## ARS Codex

`Imbad0202/academic-research-skills-codex` is checked out at
`skill-plugins/academic-research-skills-codex/` at the reviewed commit
`925975e933a20893b81681d925a3404e3b7f73b7`. The local marketplace exposes
`plugins/ars-codex` as plugin `ars-codex`, category `Research`, with
installation policy `AVAILABLE` and authentication policy `ON_INSTALL`.
Setup does not install it.

After a user explicitly installs the plugin, its native entrypoint is
`academic-research-suite`, invoked as `$ars-codex:academic-research-suite`.
There are no local ARS aliases or generated ARS installation report. Local
source, citation, evidence, manuscript, and audit rules still govern use.

### One-time migration for existing clones

The old and new repositories have unrelated histories, so setup never swaps the
legacy checkout's URL in place. Before removing an initialized legacy checkout
at `skill-plugins/academic-research-skills/`, the installer requires both:

- no tracked, untracked, or ignored changes; and
- `HEAD` exactly `81c7300b4066d233914563fc1c3f80512347b33c`.

It also requires the checkout's Git directory to exactly match the module path
Git selects for this checkout: `.git/modules/` in a primary checkout or the
corresponding `.git/worktrees/<name>/modules/` path in a linked worktree. When
every guard passes, only the legacy working-tree directory is removed. The
separate Git directory, commits, refs, and recovery history remain intact, and
the new repository is initialized at its distinct path.

If changed files are reported, inspect and copy them elsewhere or commit them
to a named legacy branch before rerunning. If the checkout is clean but at a
divergent commit, preserve that commit or ref, then explicitly return the
legacy checkout to the recorded gitlink before rerunning. If the path is a
nonempty non-submodule directory, a standalone clone, or uses Git storage
outside the current superproject module area, move or preserve it manually;
setup stops without deleting it. Never delete the legacy Git module directory
or local refs as migration cleanup.

Validate repository-owned boundaries with:

```sh
python3 scripts/operations/skill_plugins/check_external_skills.py
python3 scripts/operations/skill_plugins/check_external_skills.py --native-ars-smoke
```

The opt-in smoke uses a temporary `CODEX_HOME`, installs only into that
temporary directory, and performs no model turn. It verifies marketplace
discovery and native catalog loading; it does not enable the optional full
runtime, hooks, resolver clients, automatic subagents, external providers,
credentials, or network calls.

## Obsidian Skills

`kepano/obsidian-skills` is checked out at `skill-plugins/obsidian-skills/` for reviewed upstream guidance covering Obsidian Markdown, Bases, JSON Canvas, Obsidian CLI, and Defuddle workflows. The local installer validates the expected upstream `SKILL.md` files, creates or refreshes `.agents/skills/obsidian-research-*` wrappers, and records `.agents/skills/OBSIDIAN_SKILLS_INSTALLED.md`; it does not execute external source scripts or install the skills globally.

The wrappers are for Obsidian syntax and local vault mechanics only. They do not authorize sources, citations, page numbers, source metadata, quotations, source relationships, or final claims. Local scaffold rules win over upstream Obsidian guidance.

Use `docs/15-obsidian-skills.md` for wrapper list, optional agent-native install notes, folder conventions, usage recipes, local checks, and troubleshooting.

## Research Book Skills

`CoveMB/research-book-skills` is checked out at `skill-plugins/research-book-skills/`. Every skill listed in `RBS_SKILLS` in `scripts/lib/project_config.py` has a matching immediate-use wrapper under `.agents/skills/rbs-*/SKILL.md`.

Use the wrappers for accessibility support, research-intent routing, book planning, source discovery, annotation-to-source-note conversion, extraction tables, literature maps, claim ledgers, traceability, argument and chapter architecture, prose editing, citation audits, figure/table integrity audits, scholarly-integrity gates, AI/human workflow logs, rights/privacy release audits, continuity review, case-study integration, proposal work, and comps verification. The upstream skill is workflow guidance, not evidence. The wrappers require source notes, claim ledgers, audits, and bibliography checks before claims are promoted.

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

- `Imbad0202/academic-research-skills-codex`: CC-BY-NC-4.0.
- `CoveMB/research-book-skills`: MIT.
- `kepano/obsidian-skills`: MIT.
