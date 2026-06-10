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
| Broken wiki links | Run `python3 scripts/research-writing/check_broken_internal_links.py`. |
| Placeholder markers remain | Run the placeholder checker and resolve each marker. |
| Obsidian direct URL says vault not found | Open the project root once with Obsidian's `Open folder as vault` flow, or rerun setup with `--register-obsidian-vault` when writing Obsidian app-level vault registry state is acceptable. |
| Codex Panel not visible | Confirm `.obsidian/plugins/codex-panel/` exists, `.obsidian/community-plugins.json` includes `codex-panel`, then open Settings -> Community plugins and click Reload plugins. |
| Codex Panel cannot start Codex | Confirm `.obsidian/plugins/codex-panel/data.json` contains an absolute executable `codexPath`, then run `python3 scripts/operations/obsidian/check_obsidian_panel.py`. |
| Codex Panel reports `[features].codex_hooks` deprecation | This comes from local Codex CLI configuration, not the scaffold vault files. Update the user config key to `[features].hooks` before claiming warning-free GUI QA. |
| Zotero/Pandoc Obsidian plugins not visible | Run `make install-obsidian-research-plugins`, confirm `.obsidian/community-plugins.json` includes `obsidian-zotero-desktop-connector` and `obsidian-pandoc-reference-list`, then reload Community plugins in Obsidian. If a stale existing plugin folder has missing files or a manifest mismatch, run `python3 scripts/operations/obsidian/obsidian_research_plugins.py install --force` before checking again. |
| Pandoc Reference List cannot render references | Confirm Pandoc is installed, then configure the plugin bibliography path as `bibliography/references.bib`. Run `make check-obsidian-research-plugins` and `make check-citations`. |
| External skills not installed | Run `python3 scripts/operations/vendors/install_external_skills.py --yes`, then review reports. |
| Research Book Skills plugin not visible | Check `vendor/research-book-skills/.codex-plugin/plugin.json` and `.agents/plugins/marketplace.json`. |
| Subagent Orchestrator plugin not visible | Check `vendor/subagent-orchestration-plugin/plugin/subagent-orchestrator/.codex-plugin/plugin.json` and `.agents/plugins/marketplace.json`. |
| Obsidian Skills wrapper missing | Run `python3 scripts/operations/vendors/check_external_skills.py`, then confirm `vendor/obsidian-skills/skills/` is initialized and refresh wrappers with the local installer if needed. |
| Agent edited too much | Inspect diff, keep intended changes, revert only with user approval. |
| Export failed | Check Quarto, Pandoc, the TinyTeX `PATH`, bibliography path, and unresolved citation errors. |
| Quarto render reports `unable to open database file` in sandboxed automation | Rerun render QA with normal user permissions or a writable Quarto cache location, then record the sandbox failure as an environment constraint rather than a manuscript failure if the normal render passes. |
| Quarto warns about `site_libs` outside the project | The scaffold renders the Quarto book from `manuscript/` into `exports/html`, which is outside the Quarto project root. If the output files inspect correctly, record this as a non-blocking warning. To remove the warning in a future release, render to an internal build directory such as `manuscript/_book` and copy final artifacts into `exports/`. |
