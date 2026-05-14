# Tooling

| Tool | Use | Required |
| --- | --- | --- |
| Zotero | Source library, PDFs, metadata | Recommended |
| Zotero local API | Local citation-library inspection from tools | Recommended for citation-library QA |
| Better BibTeX | Stable citekeys and BibTeX export | Recommended |
| Obsidian project-root vault | Project-root notes and local navigation | Required |
| Markdown editor | Direct file editing outside Obsidian | Optional |
| Quarto | Book rendering | Optional until export |
| Pandoc | Format conversion | Optional until export |
| Git | Version history and checkpoints | Recommended |
| Codex CLI | Local agent workflows | Required |
| Repo-scoped skills | Task-specific agent procedures | Optional |
| MCP | Controlled access to tools and data | Optional |
| Obsidian Codex plugin | Agent work inside Obsidian | Required |
| Academic Research Skills vendor repo | External academic paper and pipeline workflows | Optional |
| Research Book Skills plugin | External research book workflows | Optional |
| Subagent Orchestrator plugin | Optional execution-shape guidance for bounded subagents | Optional |

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

## Zotero local API verification

For local citation-library QA, Zotero should be open and its local API should be enabled.

In Zotero, open `Zotero > Settings > Advanced` on macOS, then enable:

```text
Allow other applications on this computer to communicate with Zotero
```

The expected local endpoint is:

```text
http://localhost:23119/api/
```

Use the Zotero helper status check when available. A plain browser visit to the API root may show `Request not allowed`; that does not by itself prove the Zotero app is unusable. `http://127.0.0.1:23119/connector/ping` verifies the Zotero connector server is running, while API-based library checks should use API routes through a tool that sends Zotero's expected headers.

Use the built-in Zotero local API for this scaffold.
