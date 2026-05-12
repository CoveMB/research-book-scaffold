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

After setup, read `AGENTS.md`, add verified sources to Zotero or `bibliography/references.bib`, create notes from `templates/`, and draft in `manuscript/`.

## Common commands

```sh
make doctor
make audit
make render
make check-citations-strict
make install-external-skills
```

## Templates

Use `templates/` for source notes, concept notes, claim notes, chapter briefs, search logs, audits, and synthesis memos. Create new notes from templates instead of starting from a blank file.

## Repo-scoped skills and plugins

ARS wrappers live in `.agents/skills/`. Research Book Skills is exposed through `.agents/plugins/marketplace.json`, which points directly at the vendored submodule. Use them for bounded tasks such as search planning, source notes, claim audits, drafting from notes, and final manuscript checks.

## Optional integrations

- Obsidian Codex can connect this project root to local agent workflows as an Obsidian vault. `bash setup.sh` creates `.obsidian/` and installs the plugin in the repository root by default; pass `--skip-obsidian-codex` to skip it or `--obsidian-vault PATH` for a different vault.
- Academic Research Skills can be vendored from `Imbad0202/academic-research-skills` and exposed through safe wrapper skills.
- Research Book Skills can be vendored from `CoveMB/research-book-skills` and exposed directly from `vendor/research-book-skills/`.

External integrations stay optional. Review upstream files before use and do not run vendored scripts automatically. The Obsidian setup does not create a nested vault folder, does not write workspace files, and does not modify existing Obsidian settings unless `--force` is passed.

The two external repositories under `vendor/` are Git submodules. After cloning, initialize them with:

```sh
git submodule update --init --recursive
```

`make install-external-skills` also initializes them. `bash setup.sh` checks local tools and scaffold files without changing external integrations unless `--with-external-skills` is passed.

## Do not automate

- Secrets, API keys, or credentials.
- Citation creation from memory.
- Whole-vault rewrites.
- System installs without explicit permission.
- Execution of unreviewed vendored scripts.

## License

This scaffold is MIT licensed. Vendored integrations keep their upstream licenses; review `vendor/README.md` before redistribution or commercial use.
