# Troubleshooting

| Problem | Fix |
| --- | --- |
| Missing Codex CLI | Install and log in before setup or Obsidian agent checks. Do not store credentials in repo. |
| Missing or old Python | Install Python 3.11 or newer, then rerun setup or checks. |
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
| Zotero/Pandoc/QMD Obsidian plugins not visible | Run `make install-obsidian-research-plugins`, confirm `.obsidian/community-plugins.json` includes `obsidian-zotero-desktop-connector`, `obsidian-pandoc-reference-list`, and `qmd-as-md-obsidian`, then reload Community plugins in Obsidian. If an existing plugin folder has missing files or a manifest mismatch, run `python3 scripts/operations/obsidian/obsidian_research_plugins.py install --force` before checking again. |
| Pandoc Reference List cannot render references | Confirm Pandoc is installed, configure the plugin bibliography path as `./bibliography/references.bib`, and use an absolute `cslStylePath` for `bibliography/csl/ieee.csl`. Run `make check-obsidian-research-plugins` and `make check-citations`. |
| Pandoc Reference List does not suggest citekeys | In the Pandoc Reference List status-bar menu or plugin settings, enable `Show citekey suggestions`. Type `@` plus at least two characters in a Markdown note, then use `Cmd+Enter` on macOS or `Ctrl+Enter` on Windows or Linux to insert `[@citekey]`. |
| `.qmd` files do not open as Markdown in Obsidian | Confirm qmd as md is installed and enabled, then run `make check-obsidian-research-plugins`. The check should report `.qmd` linking enabled and `manuscript/` visible. |
| qmd as md does not load in Obsidian | Use Obsidian Desktop 1.8.0 or newer. The plugin is desktop-only and will not load on Obsidian mobile. |
| qmd as md cannot preview or render | Install Quarto, then set qmd as md's Quarto path to `quarto` or an absolute executable path. GUI Obsidian may not inherit the shell `PATH`, so an absolute path can be more reliable. |
| `_quarto.yml` is not visible in Obsidian | Confirm qmd as md has YAML files enabled and that `.obsidian/app.json` or the File Explorer CSS snippet is not hiding `manuscript/`. Run `make check-obsidian-research-plugins`. |
| External skills not installed | Run `python3 scripts/operations/skill_plugins/install_external_skills.py --yes`, then review reports. |
| Research Book Skills plugin not visible | Check `skill-plugins/research-book-skills/.codex-plugin/plugin.json` and `.agents/plugins/marketplace.json`. |
| Subagent Orchestrator plugin not visible | Check `skill-plugins/subagent-orchestration-plugin/plugin/subagent-orchestrator/.codex-plugin/plugin.json` and `.agents/plugins/marketplace.json`. |
| Obsidian Skills wrapper missing | Run `python3 scripts/operations/skill_plugins/check_external_skills.py`, then confirm `skill-plugins/obsidian-skills/skills/` is initialized and refresh wrappers with the local installer if needed. |
| Agent edited too much | Inspect diff, keep intended changes, revert only with user approval. |
| Export failed | Check Quarto, Pandoc, the TinyTeX `PATH`, bibliography path, and unresolved citation errors. |
| Quarto render reports `unable to open database file` in sandboxed automation | Rerun render QA with normal user permissions or a writable Quarto cache location, then record the sandbox failure as an environment constraint rather than a manuscript failure if the normal render passes. |
| Quarto warns about `site_libs` outside the project | Confirm `manuscript/_quarto.yml` uses `output-dir: _book`, then rerun the render through `make render-html` or `scripts/research-writing/render.sh`. Direct Quarto output belongs in `manuscript/_book`; the wrapper mirrors generated files into `exports/`. |
