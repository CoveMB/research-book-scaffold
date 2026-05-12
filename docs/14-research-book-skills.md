# Research Book Skills

Repository:

```text
https://github.com/CoveMB/research-book-skills.git
```

Purpose: research nonfiction and research book workflows for planning, source discovery, source-note conversion, evidence extraction, argument structure, chapter design, claim traceability, citation audit, release-risk review, continuity review, and proposal work.

## Upstream orientation

This repository is structured as a local plugin with:

- `.codex-plugin/plugin.json`
- `skills/`
- `docs/`
- `examples/`
- `scripts/`
- `shared/contracts/book/`
- validation scripts

## Core skills

- `research-book-orchestrator`
- `scholarly-research-agenda`
- `systematic-source-discovery`
- `discovery-runner-deduper`
- `annotation-to-source-note`
- `extraction-table-builder`
- `literature-review-mapper`
- `annotated-bibliography-builder`
- `methodology-source-auditor`
- `claim-evidence-ledger`
- `claim-traceability-graph`
- `argument-architecture`
- `counterargument-peer-review`
- `chapter-architecture`
- `scholarly-prose-editor`
- `citation-integrity-auditor`
- `rights-privacy-release-auditor`
- `manuscript-continuity-editor`
- `case-study-integration`
- `book-proposal-scholarship`
- `book-comps-verifier`

## Local handling

- Vendor upstream under `vendor/research-book-skills/` as a Git submodule.
- Expose the vendored plugin directly through `.agents/plugins/marketplace.json`.
- Use plugin assets directly from `vendor/research-book-skills/` instead of local copies.
- Preserve upstream files unchanged.

## Use

- Research-book planning.
- Book-level workflow orchestration.
- Argument and chapter architecture.
- Source discovery for long-form work.
- Candidate-source dedupe and screening.
- Annotation-to-source-note conversion.
- Evidence extraction tables and source matrices.
- Claim-evidence ledgers.
- Claim-to-source traceability checks.
- Citation integrity audits.
- Rights, privacy, quotation, and release-risk audits.
- Manuscript continuity review.
- Book proposal drafting.
- Comparable-title verification for proposals.

## Avoid

- Replacing Zotero or `bibliography/references.bib`.
- Inventing citations.
- Bypassing claim audits.
- Bulk rewriting manuscript files without review.
