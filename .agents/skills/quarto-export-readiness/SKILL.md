---
name: quarto-export-readiness
description: Use for this repository before manuscript sharing, release audit, Quarto rendering, export readiness, citation checks, placeholder checks, broken-link checks, or HTML/PDF/DOCX manuscript output review.
---

# Quarto Export Readiness

## Purpose

Check whether this project's Quarto manuscript is ready to share or export, while keeping citation, claim, placeholder, and evidence gaps visible.

## When to use

Use when the user asks to prepare, audit, render, share, export, or release the manuscript, or when they mention Quarto output, `make release-audit`, `make render`, HTML, PDF, DOCX, citation readiness, placeholders, or broken internal links.

## Inputs expected

- Intended output target: readiness only, HTML, PDF, DOCX, or all formats.
- Scope: full manuscript by default, or a named chapter/appendix when supplied.
- Any known unresolved citation, evidence, placeholder, or rendering concern.

If the user does not specify an output target, default to readiness only and run render commands only when they ask for exported files or visual/output verification.

## Source and citation limits

- Zotero or `bibliography/references.bib` remains citation source of truth.
- Do not invent citekeys, bibliography entries, page numbers, source support, or claims.
- A passing citation-key check does not prove source-claim fit.
- If source text, notes, or locators are unavailable, mark claim and quotation verification as unavailable.
- Do not advance export readiness by hiding failed gates; record failures and next fixes.

## Files/folders it may read

- `AGENTS.md`
- `docs/06-quality-gates.md`
- `docs/07-citation-workflow.md`
- `docs/08-writing-workflow.md`
- `docs/09-audit-workflow.md`
- `Makefile`
- `scripts/research-writing/render_manuscript.py`
- `manuscript/_quarto.yml`
- `manuscript/`
- `bibliography/references.bib`
- `notes/90-audits/audits/`

Read other notes, research files, or source materials only when the user asks for evidence or claim verification.

## Files/folders it may write

None by default.

When explicitly asked, it may create or update a release-readiness audit in `notes/90-audits/audits/`. It must not edit manuscript chapters, bibliography files, source notes, exports, or vendor files unless the user separately asks for those edits.

## Must not do

- Do not create or repair citations from memory.
- Do not treat render success as scholarly readiness.
- Do not treat citation-key existence as source-claim verification.
- Do not modify `bibliography/references.bib`; fix metadata in Zotero or ask the user to update the export.
- Do not run broad cleanup, format conversion, or manuscript rewrites as part of readiness unless asked.
- Do not ignore missing Quarto, Pandoc, TeX, bibliography, placeholder, or link failures.

## Procedure

1. Inspect current repository status and preserve unrelated user edits.
2. Read the listed workflow files when not already loaded.
3. Identify requested export target and manuscript scope.
4. Check manuscript configuration in `manuscript/_quarto.yml`, including bibliography path and enabled formats.
5. Run the readiness command:

```sh
make release-audit
```

6. If the user requested rendering, run one of:

```sh
make render
make render-html
make render-pdf
make render-docx
```

7. Classify each failure by gate: placeholder, citation, internal link, external skill setup, render tooling, render output, or unresolved scholarly risk.
8. If explicitly asked to document readiness, write an audit note in `notes/90-audits/audits/` using the local audit template structure.
9. Report changed files, checks run, skipped checks with reasons, evidence gaps, unresolved risks, and recommended next step.

## Output format

```markdown
# Export readiness

## Scope

## Checks run

## Render targets

## Findings
| Gate | Status | Evidence | Required fix |

## Skipped checks

## Evidence gaps / unresolved risks

## Decision

## Recommended next step
```

## Quality checks

- `make release-audit` must be run before saying the manuscript is release-ready.
- Render checks must name exact targets attempted.
- Missing tools must be reported as blockers or skipped checks, not success.
- Citation findings must distinguish citekey validity from source-claim fit.
- Any created audit note must include scope, findings, required fixes, decision, and follow-up.

## Failure modes

- Export readiness claimed after only `make render`.
- Citation audit reduced to formatting while unsupported claims remain.
- Placeholder or broken-link findings dismissed as cosmetic.
- Missing TeX engine, Quarto, or Pandoc treated as a manuscript problem rather than a tooling blocker.
- Audit note rewrites manuscript content instead of recording findings.
