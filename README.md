# Scholarly research and writing boilerplate

Clean scaffold for source management, notes, manuscript drafting, citation checks, research audits, and local agent workflows. It is domain-neutral by design.

## Four-layer architecture

| Layer | Folder | Source of truth |
| --- | --- | --- |
| Sources and bibliography | `bibliography/`, Zotero | Zotero or `bibliography/references.bib` |
| Notes and knowledge base | `notes/`, `research/` | Structured notes and audit files |
| Manuscript production | `manuscript/`, `exports/` | Quarto source files |
| Agent orchestration | `AGENTS.md`, `.agents/skills/`, `docs/` | Repo-scoped instructions |

## First setup after cloning

```sh
git clone --recurse-submodules <repo-url>
cd <repo-folder>
bash setup.sh
make check-obsidian-panel
make audit
```

If the repository was cloned without submodules, run:

```sh
git submodule update --init --recursive
```

`bash setup.sh` treats the project root as the Obsidian vault root, installs Codex Panel unless skipped, initializes vendored external skills, refreshes repo-scoped wrappers under `.agents/skills`, and keeps plugin marketplace entries optional. Use `bash setup.sh --dry-run` first when you want a preview, or `bash setup.sh --skip-external-skills` when you only want local tool and Codex Panel setup.

After setup, read `AGENTS.md`, add verified sources to Zotero or `bibliography/references.bib`, create notes from `templates/`, and draft in `manuscript/`. Obsidian is the recommended vault interface for local agent workflows; pass `--skip-obsidian-panel` for CLI or Markdown-editor-only work.

## Common commands

```sh
make doctor
make audit
make release-audit
make render
make render-html
make render-pdf
make render-docx
make check-citations-strict
make install-external-skills
```

## Templates

Use `templates/` for local source notes, concept notes, claim notes, audits, source matrices, project charters, and synthesis memos. Plugin-owned chapter brief, search log, literature map, and case-study templates are listed in `templates/README.md`.

## Repo-scoped skills and plugins

Immediate Codex skill availability comes from wrapper skills in `.agents/skills/<skill-name>/SKILL.md`. Codex Panel should launch Codex with this project root, or a path below it, as the working directory so Codex can discover those repo-scoped skills.

The external layers are separate:

- `vendor/` stores upstream source copies pinned as submodules.
- `.agents/skills/` stores safe local wrappers that are immediately usable after setup.
- `.agents/plugins/marketplace.json` keeps optional plugin exposure for users who choose to install repo marketplace plugins later.

Available wrappers include local scaffold skills, `ars-*` Academic Research Skills wrappers, `rbs-*` Research Book Skills wrappers, guarded `subagent-safe-*` wrappers, and `obsidian-research-*` Obsidian Skills wrappers. Use them for bounded tasks such as accessibility support, research-intent routing, search planning, candidate dedupe, source-note conversion, evidence extraction, claim traceability, claim audits, figure/table integrity checks, scholarly-integrity checks, workflow logging, release/privacy review, proposal comps, drafting from notes, final manuscript checks, Obsidian syntax/mechanics, and orchestration planning when subagents would materially help. Marketplace exposure is useful, but it is not the immediate availability path.

## Default local agent integration

- Codex Panel connects this project root to local agent workflows as an Obsidian vault. `bash setup.sh` creates `.obsidian/`, installs the plugin in the repository root, enables `codex-panel` in `.obsidian/community-plugins.json`, and writes an absolute Codex executable path in the plugin settings when one is available. For first-time GUI QA, pass `--register-obsidian-vault` to also register the project root in Obsidian's app-level vault registry so `obsidian://open?path=...` can find it. Pass `--skip-obsidian-panel` to leave Obsidian/Codex Panel setup for later, or pass `--obsidian-vault PATH` only for a different vault.

## Optional external integrations

- Academic Research Skills can be vendored from `Imbad0202/academic-research-skills` and exposed through safe wrapper skills.
- Research Book Skills can be vendored from `CoveMB/research-book-skills`, exposed through immediate `rbs-*` wrappers, and optionally exposed as a repo marketplace plugin from `vendor/research-book-skills/`.
- Subagent Orchestrator can be vendored from `CoveMB/subagent-orchestration-plugin` and exposed from `vendor/subagent-orchestration-plugin/plugin/subagent-orchestrator/`.
- Obsidian Skills can be vendored from `kepano/obsidian-skills` and exposed through local wrappers for Obsidian Markdown, Bases, JSON Canvas, Obsidian CLI, and Defuddle guidance.

External repositories stay optional. Review upstream files before use. Default external-skill setup refreshes guarded Subagent Orchestrator wrappers and marketplace exposure without executing the vendored installer or enabling hooks, project agents, global config, or global agents. Obsidian Skills are vendored and wrapped locally; they are not installed globally by this scaffold. The Obsidian setup does not create a nested vault folder or write workspace files. It installs Codex Panel from published release assets only, adds `codex-panel` to `.obsidian/community-plugins.json`, removes any older agent-plugin enablement entry when present, and writes `.obsidian/plugins/codex-panel/data.json`. Obsidian app-level vault registration is opt-in because it writes user app state outside the repository. `--force` only allows replacing an existing plugin folder.

The external repositories under `vendor/` are Git submodules. `bash setup.sh` and `make install-external-skills` initialize them. To do that manually, run:

```sh
git submodule update --init --recursive
```

Use `bash setup.sh --skip-obsidian-panel` when Obsidian/Codex Panel coverage is out of scope. Use `bash setup.sh --skip-external-skills` only when you do not want vendor initialization or wrapper refresh during setup.

In Codex Panel, verify repo-scoped skills with a read-only prompt:

```text
Read AGENTS.md and list the repo-scoped skills available from .agents/skills. Do not edit files.
```

See `docs/15-obsidian-skills.md` for Obsidian Skills usage, wrapper boundaries, optional agent-native installation notes, folder conventions, checks, and troubleshooting.

## Do not automate

- Secrets, API keys, or credentials.
- Citation creation from memory.
- Whole-vault rewrites.
- System installs without explicit permission.
- Execution of unreviewed vendored scripts.

## License

This scaffold is MIT licensed. Vendored integrations keep their upstream licenses; review `vendor/README.md` before redistribution or commercial use.
