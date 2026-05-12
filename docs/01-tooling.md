# Tooling

| Tool | Use | Required |
| --- | --- | --- |
| Zotero | Source library, PDFs, metadata | Recommended |
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

Discovery tools such as Elicit, Semantic Scholar, OpenAlex, and Scite can help find candidate sources. Import and verify useful sources in Zotero or `bibliography/references.bib` before citing them.

Do not store API keys or credentials in this repository.

External repositories live under `vendor/`. The marketplace in `.agents/plugins/marketplace.json` points directly at the vendored Research Book Skills submodule.
