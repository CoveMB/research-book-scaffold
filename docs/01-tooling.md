# Tooling

| Tool | Use | Required |
| --- | --- | --- |
| Zotero | Source library, PDFs, metadata | Recommended |
| Better BibTeX | Stable citekeys and BibTeX export | Recommended |
| Obsidian project-root vault | Project-root notes and local navigation | Recommended; setup default unless skipped |
| Markdown editor | Direct file editing outside Obsidian | Optional |
| Quarto | Book rendering | Optional until export |
| Pandoc | Format conversion | Optional until export |
| Git | Version history, submodules, and checkpoints | Required for setup and vendor checks |
| Python 3 | Local scripts, checks, setup, and tests | Required |
| pre-commit | Lightweight local commit hooks for hygiene and scaffold checks | Optional |
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
