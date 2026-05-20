# QA Environment Requirements

Use this file with `end-2-end-tests/docs/end-to-end.md` when a QA run claims app, citation-library, render, or local integration coverage. These requirements are for test execution and release evidence. They are not required for ordinary research or writing work unless that work explicitly uses the same local integration.

## Zotero Local API

Routine writing does not require the Zotero local API. The normal citation workflow is Zotero plus Better BibTeX exporting verified records to `bibliography/references.bib`.

Enable the local API only when QA or a local tool needs to inspect the Zotero library through Zotero Desktop. Examples include API-based citation-library verification, Zotero helper `status` or `probe` checks, and release evidence that claims local Zotero integration.

To enable it:

1. Open Zotero.
2. Open Zotero settings.
3. In `Advanced`, enable `Allow other applications on this computer to communicate with Zotero`.
4. Keep Zotero open while running API-based checks.

The expected local API base is `http://localhost:23119/api/`.

The local API does not use a zotero.org web API key. A plain browser visit to the API root may show `Request not allowed`; use a Zotero-aware helper or a targeted API route that sends Zotero's expected headers. `http://127.0.0.1:23119/connector/ping` confirms the connector server is running, but it does not prove API-based library routes are reachable.

Normal citation-library export QA needs at least one verified Zotero record selected before the run starts. If no verified record is available, reduce the claim to Zotero and Better BibTeX availability only; do not call it end-to-end export coverage.

Before any QA refresh of `bibliography/references.bib`:

1. Confirm Zotero is open.
2. Confirm Better BibTeX is installed and enabled.
3. Confirm the disposable QA clone is clean with `git status --short`.
4. Refresh or export only verified Zotero or Better BibTeX records.
5. Inspect `git diff -- bibliography/references.bib`.
6. Reject generated or unverified bibliography metadata.

If the local library has no verified records for the QA fixture, record Zotero and Better BibTeX availability as checked, skip bibliography refresh, and state that end-to-end export coverage was not claimed. Do not create placeholder Zotero records solely to make QA pass.
