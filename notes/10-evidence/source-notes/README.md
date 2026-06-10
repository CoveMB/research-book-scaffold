# Source notes

Use `source-notes/` for notes tied to one source, citekey, document, interview,
archive item, web record, or other checkable source.

Create a source note after a source has been selected for the project or after
an annotation import needs review. Use `templates/source-note-template.md`.

The front matter helps trace reading status, source access, and locator quality.
It does not replace Zotero, Better BibTeX, or `bibliography/references.bib`.
Zotero or the exported BibTeX file remains the bibliographic source of truth.

Leave metadata blank when it has not been checked. Use `unknown` or
`not_checked` only when that is the honest state. Do not guess DOI, URL, archive
URL, access date, citekey, authors, title, year, page numbers, quotations, or
source relationships.

Use these fields consistently:

- `citekey`: Better BibTeX key after it exists in Zotero or
  `bibliography/references.bib`.
- `zotero_uri`: Zotero item URI, when available.
- `DOI`, `URL`, `archive_url`, `access_date`: copy from Zotero, the source
  itself, or another verified record. Leave blank if not checked.
- `source_type`: brief type such as `book`, `journal_article`, `report`,
  `interview`, `archival_record`, `web_page`, or `unknown`.
- `evidence_type`: leave blank until classified. Use `empirical_study`,
  `review`, `theory`, `method`, `historical_source`, `primary_text`,
  `policy_or_report`, `commentary`, or `other`.
- `peer_review_status`: use `not_checked` until verified.
- `source_status`: use `unread`, `skimmed`, `deep_read`, `extracted`, `coded`,
  `verified`, or `rejected`.
- `locator_quality`: use `precise_page_or_section`, `approximate`,
  `missing_locator`, or `not_applicable`.
- `relevance_to_project`, `main_use`, `limitations`, `last_checked`: short
  working fields for fit, intended use, known limits, and the last source check.

Keep summaries, paraphrases, direct quotations, and interpretation separate in
the key-passages table. Passage-specific claims and direct quotations need page
numbers, stable section names, timestamps, archive locators, or another locator
that a reader can check.
