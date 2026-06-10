# Tooling

| Tool | Use | Required |
| --- | --- | --- |
| Zotero | Source library, PDFs, metadata | Recommended |
| Better BibTeX | Stable citekeys and BibTeX export | Recommended |
| Obsidian project-root vault | Project-root notes and local navigation | Recommended; setup default unless skipped |
| Zotero Integration Obsidian plugin | Insert Pandoc-style citations and import Zotero notes or annotations | Recommended; setup default unless skipped |
| Pandoc Reference List Obsidian plugin | Preview references for citekeys in the current note | Recommended; setup default unless skipped |
| qmd as md Obsidian plugin | Open, edit, preview, and outline Quarto `.qmd` files in Obsidian | Recommended; setup default unless skipped; requires Obsidian Desktop 1.8.0+ |
| Markdown editor | Direct file editing outside Obsidian | Optional |
| Quarto | Book rendering | Optional until export |
| Pandoc | Format conversion and Pandoc Reference List rendering | Optional until export; needed for live reference preview |
| Git | Version history, submodules, and checkpoints | Required for setup and vendor checks |
| Python 3.11+ | Local scripts, checks, setup, and tests | Required |
| pre-commit | Lightweight local commit hooks for file hygiene, Python syntax, citations, and internal links | Optional |
| curl | Core command checked by setup and health checks for download workflows | Required by setup and doctor checks |
| unzip | Core command checked by setup and health checks for archive workflows | Required by setup and doctor checks |
| Codex CLI | Local agent workflows | Required |
| Repo-scoped skills | Task-specific agent procedures | Optional |
| MCP | Controlled access to tools and data | Optional |
| Codex Panel Obsidian plugin | Agent work inside Obsidian | Recommended; setup default unless skipped |
| Academic Research Skills vendor repo | External academic paper and pipeline workflows | Optional |
| Research Book Skills plugin | External research book workflows | Optional |
| Subagent Orchestrator plugin | Optional execution-shape guidance for bounded subagents | Optional |
| Obsidian Skills vendor repo | Obsidian Markdown, Bases, Canvas, CLI, and Defuddle wrapper guidance | Optional |

Discovery tools such as Elicit, Semantic Scholar, OpenAlex, and Scite can help find candidate sources. Import and verify useful sources in Zotero or `bibliography/references.bib` before citing them.

Do not store API keys or credentials in this repository.

External repositories live under `vendor/`. The marketplace in `.agents/plugins/marketplace.json` points directly at the vendored Research Book Skills submodule and the nested optional Subagent Orchestrator plugin path.

`bash setup.sh` uses network access when it initializes vendor submodules or
downloads Obsidian plugin release assets. For offline or CLI-only setup, use
`bash setup.sh --skip-external-skills --skip-obsidian-panel --skip-obsidian-research-plugins`.

`bash setup.sh` installs Codex Panel, Zotero Integration, Pandoc Reference List, and qmd as md under `.obsidian/plugins/`. It also writes safe default settings for the research plugins:

- Zotero Integration gets a Pandoc citekey format and autocomplete that inserts `[@citekey]`.
- Pandoc Reference List points at `./bibliography/references.bib`, enables citekey completion, and uses an absolute path to `bibliography/csl/ieee.csl`. The plugin resolves bibliography paths from the vault root, but it checks local CSL paths as filesystem paths.
- qmd as md enables `.qmd` linking, shows YAML files for `_quarto.yml`, enables the Quarto outline, and uses `quarto` or the resolved Quarto executable when setup can find it. It leaves automatic PDF opening disabled so repository render targets stay authoritative.

qmd as md is desktop-only. Use Obsidian Desktop 1.8.0 or newer for `.qmd` authoring; Obsidian mobile will not load that plugin.

The plugin folders are not ignored by default, so a fork can choose to persist reviewed Obsidian plugin configuration. Review those diffs before committing because local settings may contain absolute executable paths, Zotero library cache state, or other machine-specific values. `.obsidian/community-plugins.json` is trackable so this scaffold can declare the recommended vault-level plugin set. `.pandoc/` is ignored because Pandoc Reference List can cache bibliography data, CSL files, and locale files there. Track reviewed CSL files under `bibliography/csl/` when a project changes citation style.

## Render tool verification

Install TinyTeX for PDF rendering with Quarto:

```sh
quarto install tinytex --update-path
```

Then open a new shell and verify the commands used by render QA:

```sh
lualatex --version
bibtex --version
```

On macOS, if TinyTeX is installed but those commands are not found, add the TinyTeX binary directory to `PATH`:

```sh
export PATH="$HOME/Library/TinyTeX/bin/universal-darwin:$PATH"
```

Put that line in the shell startup file used by your terminal, then open a new shell before rerunning render checks.

Non-interactive automation may not source interactive shell startup files. When in doubt, prefix render commands explicitly:

```sh
PATH="$HOME/Library/TinyTeX/bin/universal-darwin:$PATH" make render-pdf
```
