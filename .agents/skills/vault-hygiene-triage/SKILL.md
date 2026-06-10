---
name: vault-hygiene-triage
description: Use for this repository when triaging the notes vault, organizing inbox files, checking note/research folder placement, finding stale placeholders, checking broken wiki links, or preparing bounded Obsidian-vault cleanup.
---

# Vault Hygiene Triage

## Purpose

Triage this project's notes and research vault without weakening the evidence trail or silently moving material into the wrong research layer.

## When to use

Use when the user asks to organize, clean, triage, sort, audit, or inspect the vault, `notes/00-inbox/`, notes folders, research records, wiki links, placeholders, or Obsidian-facing project structure.

## Inputs expected

- Scope: full vault by default, or named folders/files when supplied.
- Desired action: read-only triage, proposed moves, link repair, placeholder audit, or explicit file organization.
- Any protected files, active drafts, or notes that should not be moved.

If the user only asks for a hygiene review, stay read-only and propose changes. Move files or update links only after explicit instruction.

## Source and citation limits

- Do not treat notes in `notes/00-inbox/` as stable evidence.
- Do not invent source metadata, citekeys, page numbers, quotes, claims, or internal links.
- Keep summary, paraphrase, direct quotation, and interpretation boundaries intact.
- If a note has missing evidence, mark the gap instead of normalizing it into a stable claim.
- Do not classify AI output as evidence.

## Files/folders it may read

- `notes/README.md`
- `notes/*/README.md`
- `notes/*/*/README.md`
- `research/README.md`
- `research/*/README.md`
- `templates/README.md`
- `docs/05-security.md`
- `docs/11-obsidian-panel.md`
- `docs/03-agent-orchestration.md`
- `docs/07-citation-workflow.md`
- `notes/`
- `research/`
- `manuscript/` when checking links that cross into drafts.

## Files/folders it may write

None by default.

When explicitly asked, it may:

- Move notes into the correct local folder.
- Update wiki links affected by approved moves.
- Create a triage or hygiene audit note in `notes/90-audits/audits/`.

It must not edit bibliography files, vendor files, upstream skills, source PDFs, or manuscript prose unless the user separately asks for that specific work.

## Must not do

- Do not bulk rewrite the vault.
- Do not silently move files out of `notes/00-inbox/`.
- Do not convert uncertain material into claims.
- Do not delete notes or research records unless the user explicitly requests deletion.
- Do not expose secrets, private notes, or source text in reports beyond what is needed to identify the issue.
- Do not run setup or plugin-install commands as part of hygiene triage.

## Procedure

1. Inspect current repository status and preserve unrelated user edits.
2. Read the folder responsibility docs listed above.
3. Determine scope and whether the task is read-only or explicitly write-approved.
4. Inventory scoped Markdown and Quarto files.
5. Classify each issue by layer:
   - inbox
   - source note
   - literature map
   - concept note
   - claim ledger
   - case study
   - argument map
   - chapter brief
   - audit
   - synthesis memo
   - research search log
   - extraction table
   - source matrix
   - protocol
   - manuscript draft
6. Run structure checks when relevant:

```sh
python3 scripts/research-writing/check_placeholders.py .
python3 scripts/research-writing/check_broken_internal_links.py
```

7. Identify misplaced files, broken or ambiguous wiki links, stale placeholders, unresolved evidence gaps, and sensitive material risks.
8. For read-only triage, produce proposed moves and repairs only.
9. For approved edits, move/update the smallest set of files and rerun affected checks.
10. Report changed files, checks run, skipped checks with reasons, evidence gaps, unresolved risks, and recommended next step.

## Output format

```markdown
# Vault hygiene triage

## Scope

## Mode

## Checks run

## Findings
| File | Current layer | Recommended layer | Issue | Action |

## Proposed moves / repairs

## Skipped checks

## Evidence gaps / unresolved risks

## Decision

## Recommended next step
```

## Quality checks

- Folder recommendations must match local README responsibilities.
- Proposed moves must preserve evidence status and citation trail.
- Link repairs must be rerun through the broken-link checker after approved edits.
- Placeholder findings must not be hidden by deleting markers without resolving the underlying gap.
- Reports must separate organizational hygiene from scholarly evidence quality.

## Failure modes

- Bulk cleanup destroys the provenance of rough notes.
- Inbox material is promoted to stable source notes without source metadata.
- Broken links are repaired by inventing target names.
- Placeholder markers are removed without resolving support.
- Hygiene pass rewrites manuscript prose instead of reporting placement and structure issues.
