# Bibliography

Keep citation source files here.

Primary file:

```text
references.bib
```

Zotero or this BibTeX file is the citation source of truth. Do not add citations from memory.

## Zotero workflow

Use Better BibTeX in Zotero to keep this file current:

1. Add or verify sources in Zotero.
2. Right-click the project collection in Zotero and choose `Export Collection...`.
3. Use format `Better BibTeX`.
4. Check `Keep updated`.
5. Save the export as `bibliography/references.bib`.
6. Run `python3 scripts/research-writing/check_citations.py --include-notes`.

After auto-export is active, edit source metadata in Zotero. Avoid hand-editing `references.bib`; Zotero may overwrite it on the next export.

## Obsidian plugin use

The setup workflow installs Zotero Integration and Pandoc Reference List in the project-root Obsidian vault. Point both plugins at this exported bibliography path when a setting asks for a bibliography file:

```text
bibliography/references.bib
```

Use the plugins to insert and preview existing citekeys. Do not use plugin output to create unverified bibliography metadata.

## Manual fallback

If Better BibTeX auto-export is not set up, export BibTeX from Zotero into `references.bib`, then run citation checks before sharing drafts.
