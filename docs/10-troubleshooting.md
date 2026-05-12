# Troubleshooting

| Problem | Fix |
| --- | --- |
| Missing Codex CLI | Install and log in before setup or Obsidian agent checks. Do not store credentials in repo. |
| Missing Python | Install Python 3, then rerun setup or checks. |
| Missing Git | Install Git before relying on status, diff, or checkpoints. |
| Missing Quarto | Install Quarto before rendering the manuscript. |
| Missing Pandoc | Install Pandoc or use the Quarto bundle if available. |
| Missing bibliography | Export from Zotero or create `bibliography/references.bib`. |
| Broken citekeys | Compare draft citations with BibTeX keys. |
| Broken wiki links | Run `python3 scripts/check_broken_internal_links.py`. |
| Placeholder markers remain | Run the placeholder checker and resolve each marker. |
| Obsidian Codex not visible | Restart Obsidian, enable Community Plugins, then enable the plugin. |
| External skills not installed | Run `python3 scripts/install_external_skills.py --yes`, then review reports. |
| Research Book Skills plugin not visible | Check `vendor/research-book-skills/.codex-plugin/plugin.json` and `.agents/plugins/marketplace.json`. |
| Agent edited too much | Inspect diff, keep intended changes, revert only with user approval. |
| Export failed | Check Quarto, Pandoc, bibliography path, and unresolved citation errors. |
