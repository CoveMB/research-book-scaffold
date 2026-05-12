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
6. Run `python3 scripts/check_citations.py --include-notes`.

After auto-export is active, edit source metadata in Zotero. Avoid hand-editing `references.bib`; Zotero may overwrite it on the next export.

## Manual fallback

If Better BibTeX auto-export is not set up, export BibTeX from Zotero into `references.bib`, then run citation checks before sharing drafts.
