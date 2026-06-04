# Source notes

Structured notes tied to specific sources and citekeys.

Use `templates/source-note-template.md` when creating a new source note. The
front matter is for traceability, reading status, and claim discipline; it is
not a replacement for Zotero, Better BibTeX, or `bibliography/references.bib`.
Zotero or the exported BibTeX file remains the bibliographic source of truth.

Leave metadata blank when it is not known at note-creation time. Use
`unknown` or `not_checked` for status fields when that is the honest state.
Do not guess DOI, URL, archive URL, access date, citekey, authors, title,
year, page numbers, quotations, or source relationships.

Use these compact fields consistently:

- `citekey`: Better BibTeX key after it exists in Zotero or
  `bibliography/references.bib`.
- `zotero_uri`: Zotero item URI, when available.
- `DOI`, `URL`, `archive_url`, `access_date`: copy from Zotero or a verified
  source record. Leave blank if not checked.
- `source_type`: brief type such as book, journal_article, report, interview,
  archival_record, web_page, or `unknown`.
- `evidence_type`: leave blank until classified, then use `empirical_study`,
  `review`, `theory`, `method`, `historical_source`, `primary_text`,
  `policy_or_report`, `commentary`, or `other`.
- `peer_review_status`: use `not_checked` until verified.
- `source_status`: `unread`, `skimmed`, `deep_read`, `extracted`, `coded`,
  `verified`, or `rejected`.
- `locator_quality`: `precise_page_or_section`, `approximate`,
  `missing_locator`, or `not_applicable`.
- `relevance_to_project`, `main_use`, `limitations`, `last_checked`: short
  working fields for project fit, intended use, known limits, and the last
  date the note metadata or source access was checked.

Record summaries, paraphrases, direct quotations, and interpretations as
different note types in the key-passages table. Passage-specific claims and
direct quotations need page numbers, stable section names, timestamps, archive
locators, or another checkable locator. If the locator is missing, make that
gap visible instead of smoothing it over.
