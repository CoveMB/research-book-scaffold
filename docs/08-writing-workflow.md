# Writing workflow

## Drafting rules

- Draft from source notes, claim notes, and chapter briefs.
- Keep notes, briefs, drafts, and final prose separate.
- Mark unsupported claims.
- Keep uncertainty visible.
- Do not add sources or citations from memory.

## Writing manuscript files in Obsidian

Open the repository root as the Obsidian vault so `notes/`, `research/`, and `manuscript/` share one project context. Manuscript source lives in `manuscript/`, which should stay visible in Obsidian for drafting. `bibliography/` can stay hidden because Zotero and Better BibTeX manage `bibliography/references.bib`, and Pandoc Reference List reads it from the configured path. Use `notes/40-writing-bridge/` for chapter briefs and section prep before moving prose into Quarto files.

Use Zotero Integration to insert Pandoc-style citekeys such as `[@citekey]`, `[-@citekey]`, or `[@first; @second]`. Use Pandoc Reference List to preview the references for citekeys in the active file while drafting. The preview is a convenience check only. Zotero or `bibliography/references.bib` remains the citation source of truth, and Quarto remains the manuscript renderer.

When editing `.qmd` files directly in Obsidian, confirm Obsidian opens them as Markdown text in your local setup. If Pandoc Reference List does not render for a `.qmd` chapter, preview citations in a Markdown section brief under `notes/40-writing-bridge/`, then move the reviewed prose into the manuscript file.

After an Obsidian drafting session, run the citation check before relying on the draft:

```sh
python3 scripts/research-writing/check_citations.py --include-notes
```

## Edit types

| Edit type | Use |
| --- | --- |
| Evidence edit | Add, remove, or qualify claims based on sources |
| Structure edit | Reorder sections or argument flow |
| Style edit | Improve wording without changing support |
| Audit edit | Record risks, gaps, or required fixes |

Do evidence edits before style edits when support is unclear.

## Codex Panel

Use Codex Panel only for bounded edits: one note, one section, one audit, or one draft pass. Keep approval on for commands and file writes.
