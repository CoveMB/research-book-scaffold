# Citation workflow

## Source of truth

Zotero or `bibliography/references.bib` is the citation source of truth. Notes and drafts must match it.

## Zotero sync

Use Better BibTeX auto-export for normal Zotero sync. Zotero owns the source metadata. This repo stores the exported BibTeX file and checks whether drafts refer to known citekeys.

One-time setup:

1. Download the latest Better BibTeX `.xpi` from the official release.
2. In Zotero, open `Tools > Plugins`.
3. Select `Plugins`, then use the gear menu and choose `Install Plugin From File...`.
4. Choose the downloaded `.xpi`, click `Install`, and restart Zotero.
5. Confirm Better BibTeX is listed as installed and enabled in Zotero.
6. In Zotero settings, open Better BibTeX and leave automatic export on `On Change`. Use `When Idle` if exports slow Zotero down.
7. In the Zotero sidebar, right-click the collection for this book project and choose `Export Collection...`. Use `Export Library...` only when the whole library belongs in this project.
8. Set format to `Better BibTeX`.
9. Check `Keep updated`.
10. Save the export as `bibliography/references.bib`.
11. Run `make check-citations` or `python3 scripts/check_citations.py --include-notes`.

After this setup, Zotero updates `bibliography/references.bib` when exported items change. Avoid hand-editing `references.bib`; the next export can overwrite those edits. Fix metadata and citekeys in Zotero instead.

Do not enable Better BibTeX git push from this working copy. It can commit or push unrelated files. Commit bibliography changes through the normal project workflow.

If Zotero auto-export is not available, export manually from Zotero to `bibliography/references.bib`, then run the citation check.

Before refreshing `bibliography/references.bib` during QA, verify Zotero is open, the local Zotero API is reachable when API-based checks are in scope, Better BibTeX is installed and enabled, and `git status --short` is clean. After export, inspect `git diff -- bibliography/references.bib` and accept only verified Zotero or Better BibTeX metadata.

## Citekeys

- Use Better BibTeX citekeys when possible.
- Keep citekeys stable after notes or drafts reference them.
- To pin a citekey in Zotero, add `Citation Key: your_key_here` on its own line in the item `Extra` field.
- Check manuscript citekeys against `bibliography/references.bib`.
- Use `python3 scripts/check_citations.py --include-notes` when notes and research logs may contain citekeys.
- Use `python3 scripts/check_citations.py --require-citations` before treating a manuscript as citation-ready.
- Use `python3 scripts/check_citations.py --show-unused` only when you want bibliography cleanup noise.

## Syntax

Use Quarto or Pandoc citation forms:

```md
[@citekey]
[-@citekey]
[@first; @second]
```

## Missing support

Use visible markers for missing support:

```md
{{citation needed}}
{{verify}}
```

## Page numbers

Add page numbers when a claim depends on a specific passage. If page numbers are unknown, mark the gap.

## Web sources

Record title, author or organization, URL, access date when needed, and archive link when available.

## AI output

AI-generated citations are untrusted until verified against Zotero, BibTeX, or the source itself.
