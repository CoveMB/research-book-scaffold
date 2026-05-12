# Research Book Skills

Repository:

```text
https://github.com/CoveMB/research-book-skills.git
```

Purpose: research nonfiction and research book workflows for planning, source discovery, argument structure, chapter design, citation audit, continuity review, and proposal work.

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
- `literature-review-mapper`
- `annotated-bibliography-builder`
- `methodology-source-auditor`
- `claim-evidence-ledger`
- `argument-architecture`
- `counterargument-peer-review`
- `chapter-architecture`
- `scholarly-prose-editor`
- `citation-integrity-auditor`
- `manuscript-continuity-editor`
- `case-study-integration`
- `book-proposal-scholarship`

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
- Claim-evidence ledgers.
- Citation integrity audits.
- Manuscript continuity review.
- Book proposal drafting.

## Avoid

- Replacing Zotero or `bibliography/references.bib`.
- Inventing citations.
- Bypassing claim audits.
- Bulk rewriting manuscript files without review.
