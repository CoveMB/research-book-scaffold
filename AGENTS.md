# Agent instructions

## Purpose

This repository is a generic scholarly research and long-form writing scaffold. It supports source tracking, notes, manuscript drafting, citation checks, audits, and repo-scoped skills.

## Folder responsibilities

| Folder | Responsibility |
| --- | --- |
| `bibliography/` | BibTeX source of truth and citation style notes |
| `notes/` | Source notes, concepts, claims, briefs, audits, and synthesis |
| `research/` | Search logs, matrices, extraction tables, and protocols |
| `manuscript/` | Quarto book files and draft text |
| `templates/` | Reusable note and audit templates |
| `scripts/` | Setup, checks, rendering, and local helpers |
| `docs/` | Workflow and safety documentation |
| `.agents/skills/` | Repo-scoped agent skills |
| `vendor/` | External material kept for review and optional use |

## Allowed changes

- Add or update generic docs, notes, templates, scripts, and skills.
- Add source notes only from supplied or verifiable source material.
- Update manuscript files from existing notes, briefs, and claim records.
- Add audit notes that record uncertainty, missing evidence, or needed fixes.

## Forbidden changes

- Do not add domain-specific book content unless the user supplies it.
- Do not invent citations, page numbers, quotations, sources, or metadata.
- Do not store secrets, tokens, API keys, or personal credentials.
- Do not run installers, clone repos, or execute vendored scripts without explicit instruction.
- Do not rewrite large parts of the vault without a narrow task and review path.

## How to choose a skill

- Use search-planning skills before database or web discovery.
- Use source-note skills only when source metadata or reading notes are available.
- Use claim-ledger skills when a factual, interpretive, or causal claim needs evidence status.
- Use drafting skills only when source notes, claim notes, and a brief exist.
- Use audit skills after drafting or before export.

## Source-of-truth rules

- Zotero or `bibliography/references.bib` is the citation source of truth.
- Notes may summarize sources but must not replace bibliographic records.
- Manuscript citations must use citekeys found in the bibliography.
- AI output is provisional until checked against source notes and bibliography.

## Handling uncertainty

- Mark unsupported claims clearly.
- Record missing evidence as a research task.
- Prefer safer wording when evidence is incomplete.
- Ask for source material when a task depends on unavailable evidence.

## Templates and audits

- Start new notes from `templates/` when a matching template exists.
- Keep source notes, claim notes, briefs, drafts, and audits separate.
- Put audit findings in `notes/08-audits/`.
- Update audit trails when fixing a finding.

## Checks

Run available checks after relevant changes:

```sh
bash scripts/doctor.sh
python3 scripts/check_citations.py
python3 scripts/check_placeholders.py .
python3 scripts/check_broken_internal_links.py
```

## Obsidian Codex

Use Obsidian Codex only for bounded reads, note creation, drafting, or audit tasks. Keep command approval and file-write approval enabled. Start with read-only prompts and inspect diffs after edits.

## Vendored Academic Research Skills

Treat `vendor/academic-research-skills/` as external. Review instructions before use. Prefer local generic skills for this repo, and use vendored skills as optional references or extended workflows.

## Reporting changes

End work with:

- Files changed.
- Checks run.
- Skipped checks and why.
- Risks or unresolved follow-up.
