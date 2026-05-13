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
bash setup.sh --dry-run
bash setup.sh
make install-external-skills
make audit
```

If the repository was cloned without submodules, run:

```sh
git submodule update --init --recursive
```

After setup, read `AGENTS.md`, add verified sources to Zotero or `bibliography/references.bib`, create notes from `templates/`, and draft in `manuscript/`. Obsidian is the required vault interface for local agent workflows; Markdown editors remain useful for direct file edits.

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

ARS wrappers live in `.agents/skills/`. Research Book Skills and the optional Subagent Orchestrator plugin are exposed through `.agents/plugins/marketplace.json`, which points directly at reviewed vendored paths. Use them for bounded tasks such as search planning, candidate dedupe, source-note conversion, evidence extraction, claim traceability, claim audits, release/privacy review, proposal comps, drafting from notes, final manuscript checks, and orchestration planning when subagents would materially help.

## Required local agent integration

- Obsidian Codex connects this project root to local agent workflows as an Obsidian vault. `bash setup.sh` creates `.obsidian/` and installs the plugin in the repository root by default; pass `--obsidian-vault PATH` only for a different vault.

## Optional external integrations

- Academic Research Skills can be vendored from `Imbad0202/academic-research-skills` and exposed through safe wrapper skills.
- Research Book Skills can be vendored from `CoveMB/research-book-skills` and exposed directly from `vendor/research-book-skills/`.
- Subagent Orchestrator can be vendored from `CoveMB/subagent-orchestration-plugin` and exposed from `vendor/subagent-orchestration-plugin/plugin/subagent-orchestrator/`.

External repositories stay optional. Review upstream files before use and do not run vendored scripts automatically. The subagent plugin installer is not run by default; when explicitly requested, use `make install-subagent-orchestrator` so the installer receives `--scope project` and stays available-only. The Obsidian setup does not create a nested vault folder, write workspace files, or modify existing Obsidian settings. It installs the required Obsidian plugin by default when missing. `--force` only allows replacing an existing plugin folder. For reproducible plugin installation, pass a reviewed release URL and SHA-256 checksum.

The external repositories under `vendor/` are Git submodules. After cloning, initialize them with:

```sh
git submodule update --init --recursive
```

`make install-external-skills` also initializes them. `bash setup.sh` checks local tools, scaffold files, and the required Obsidian integration without changing external repositories unless `--with-external-skills` is passed.

## Do not automate

- Secrets, API keys, or credentials.
- Citation creation from memory.
- Whole-vault rewrites.
- System installs without explicit permission.
- Execution of unreviewed vendored scripts.

## License

This scaffold is MIT licensed. Vendored integrations keep their upstream licenses; review `vendor/README.md` before redistribution or commercial use.
