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
11. Run `make check-citations` or `python3 scripts/research-writing/check_citations.py --include-notes`.

After this setup, Zotero updates `bibliography/references.bib` when exported items change. Avoid hand-editing `references.bib`; the next export can overwrite those edits. Fix metadata and citekeys in Zotero instead.

Do not enable Better BibTeX git push from this working copy. It can commit or push unrelated files. Commit bibliography changes through the normal project workflow.

If Zotero auto-export is not available, export manually from Zotero to `bibliography/references.bib`, then run the citation check.

## Obsidian citation plugins

Setup installs two Obsidian research plugins by default:

- Zotero Integration (`obsidian-zotero-desktop-connector`)
- Pandoc Reference List (`obsidian-pandoc-reference-list`)

These plugins are convenience tools. Zotero or `bibliography/references.bib` remains the source of truth for metadata and citekeys.

Use this workflow after Better BibTeX auto-export is configured:

1. Open the repository root as the Obsidian vault.
2. Confirm Zotero is open and Better BibTeX has exported the project collection to `bibliography/references.bib`.
3. In Obsidian, confirm Zotero Integration and Pandoc Reference List are enabled in Community plugins.
4. Configure Zotero Integration so inserted citations use Pandoc citekey syntax such as `[@citekey]`.
5. Confirm Pandoc Reference List uses `./bibliography/references.bib` and `./bibliography/csl/ieee.csl`, with citekey completion enabled. If the project later changes citation style, update the Obsidian CSL path and `manuscript/_quarto.yml` together.
6. Insert citations from Zotero Integration while drafting notes or manuscript files.
7. Open the Pandoc Reference List sidebar to check that each visible citekey resolves to a formatted reference.
8. Run `make check-citations` before relying on the citation in a manuscript draft.

If Zotero Integration inserts a formatted prose citation instead of a Pandoc citekey, do not use that text in `manuscript/`. Reconfigure the plugin or replace the citation with the checked citekey form.

To insert a citekey from `bibliography/references.bib` instead of searching Zotero, use Pandoc Reference List citekey completion. Open a Markdown note, type `@` followed by at least two characters from the citekey or title, then choose from the suggestion list. Use `Cmd+Enter` on macOS or `Ctrl+Enter` on Windows or Linux to insert the bracketed Pandoc form `[@citekey]`. Pressing `Enter` inserts the bare form `@citekey`.

Imported Zotero notes, PDF annotations, and highlights are source material, not final evidence by themselves. Move useful material into `notes/01-source-notes/` with the source-note template, keep quotations distinct from paraphrase, and add page numbers or locators when a claim depends on a specific passage.

Pandoc Reference List is a preview aid. It can catch unresolved citekeys while writing, but `python3 scripts/research-writing/check_citations.py` is the repository check.

## Citekeys

- Use Better BibTeX citekeys when possible.
- Keep citekeys stable after notes or drafts reference them.
- To pin a citekey in Zotero, add `Citation Key: your_key_here` on its own line in the item `Extra` field.
- Check manuscript citekeys against `bibliography/references.bib`.
- Use `python3 scripts/research-writing/check_citations.py --include-notes` when notes and research logs may contain citekeys.
- Use `python3 scripts/research-writing/check_citations.py --require-citations` before treating a manuscript as citation-ready.
- Use `python3 scripts/research-writing/check_citations.py --show-unused` only when you want bibliography cleanup noise.

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

## Source-note metadata

Source-note front matter is an audit aid for reading status, locator quality,
and claim discipline. It does not authorize bibliographic metadata. Zotero or
`bibliography/references.bib` remains the source of truth for citekeys and
source metadata.

When using `templates/source-note-template.md`, copy `citekey`, `zotero_uri`,
`DOI`, `URL`, `archive_url`, and `access_date` from Zotero, Better BibTeX, the
source itself, or another verified record. Leave DOI, URL, archive URL, and
access date blank when they have not been checked; do not fill them with guessed
values. The external-reference checker reads `DOI:`, `URL:`, `archive_url:`,
and `access_date:` fields when they contain values, so inaccurate placeholders
can become false reference failures.

Use status fields to keep uncertainty visible. The controlled vocabulary for
source-note fields lives in `notes/01-source-notes/README.md`.

## Web sources

Record title, author or organization, URL, access date when needed, and archive link when available.

Use `make check-external-references` for an explicit network check of external URLs and DOI resolution in `bibliography/references.bib`, `notes/`, `research/`, and `manuscript/`. The checker validates URL and DOI syntax, prefers `HEAD` with `GET` fallback, uses a clear user agent, and separates likely failures from uncertain network results.

The checker treats malformed URLs, malformed DOIs, HTTP 404, HTTP 410, and repeated DNS failure as likely failures. It treats HTTP 403, HTTP 429, timeouts, TLS errors, server errors, and access-controlled or paywalled responses as warnings because they are common false-positive sources.

Archive coverage is opt-in. Pass `--check-archives` to query the Internet Archive availability endpoint. This submits checked public URLs to a third-party service but does not create snapshots. Pass `--create-archives` only when you intentionally want to request public archive snapshots; this can disclose URLs. Do not use archive creation for private, sensitive, embargoed, localhost, or internal sources. Local and private-looking URLs are skipped for archive submission unless `--allow-private-archive-submission` is also passed.

Use `make external-reference-report` to write `reports/external-reference-check.json`. Reports and checker findings are audit aids; they do not repair, invent, or authorize bibliographic metadata. Fix source metadata in Zotero or verified BibTeX records.

## AI output

AI-generated citations are untrusted until verified against Zotero, BibTeX, or the source itself.
