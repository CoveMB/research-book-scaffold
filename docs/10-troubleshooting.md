# Troubleshooting

| Problem | Fix |
| --- | --- |
| Missing Codex CLI | Install and log in before setup or Obsidian agent checks. Do not store credentials in repo. |
| Missing Python | Install Python 3, then rerun setup or checks. |
| Missing Git | Install Git before relying on status, diff, or checkpoints. |
| Missing Quarto | Install Quarto before rendering the manuscript. |
| Missing Pandoc | Install Pandoc or use the Quarto bundle if available. |
| Missing `lualatex` after TinyTeX install | Run `quarto install tinytex --update-path`, open a new shell, then verify `lualatex --version`. On macOS, add `$HOME/Library/TinyTeX/bin/universal-darwin` to `PATH` if needed. |
| Missing `bibtex` after TinyTeX install | Verify `bibtex --version`. On macOS, add `$HOME/Library/TinyTeX/bin/universal-darwin` to `PATH` if needed. |
| Missing bibliography | Export from Zotero or create `bibliography/references.bib`. |
| Broken citekeys | Compare draft citations with BibTeX keys. |
| Broken wiki links | Run `python3 scripts/check_broken_internal_links.py`. |
| Placeholder markers remain | Run the placeholder checker and resolve each marker. |
| Obsidian Codex not visible | Confirm `.obsidian/plugins/obsidian-codex/` exists, `.obsidian/community-plugins.json` includes `obsidian-codex`, then restart Obsidian. |
| External skills not installed | Run `python3 scripts/install_external_skills.py --yes`, then review reports. |
| Research Book Skills plugin not visible | Check `vendor/research-book-skills/.codex-plugin/plugin.json` and `.agents/plugins/marketplace.json`. |
| Subagent Orchestrator plugin not visible | Check `vendor/subagent-orchestration-plugin/plugin/subagent-orchestrator/.codex-plugin/plugin.json` and `.agents/plugins/marketplace.json`. |
| Agent edited too much | Inspect diff, keep intended changes, revert only with user approval. |
| Export failed | Check Quarto, Pandoc, the TinyTeX `PATH`, bibliography path, and unresolved citation errors. |
