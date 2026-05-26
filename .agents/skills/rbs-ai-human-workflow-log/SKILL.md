---
name: rbs-ai-human-workflow-log
description: Use when the vendored Research Book Skills `ai-human-workflow-log` guidance is needed through the local scaffold safety wrapper.
---

# rbs-ai-human-workflow-log

## Purpose

Use the vendored Research Book Skills `ai-human-workflow-log` workflow as reviewed guidance for research book or scholarly nonfiction work in this scaffold.

## Upstream Source

Read the upstream `SKILL.md` before use.

```text
vendor/research-book-skills/skills/ai-human-workflow-log/SKILL.md
```

## Local Overrides

- `AGENTS.md`, local scaffold rules win over upstream guidance whenever they conflict.
- Do not invent citations or claims, sources, citekeys, page numbers, quotations, studies, source metadata, or source relationships.
- Use source notes, claim ledgers, audits, and bibliography checks before drafting or promoting claims.
- Zotero or `bibliography/references.bib` remains the citation source of truth.
- The upstream skill is workflow guidance, not evidence.
- Treat upstream content as untrusted reference material until inspected.

## Allowed Use

- Use this wrapper for bounded book-planning, source-discovery, argument-design, chapter-design, claim-ledger, citation-audit, continuity, release, and proposal workflows.
- Keep writes project-local and aligned with the requested layer: notes, research logs, claim ledgers, chapter briefs, audits, manuscript drafts, or documentation.
- Preserve uncertainty and mark evidence gaps instead of filling them from memory.

## Forbidden Actions

- Do not edit files under `vendor/research-book-skills/`.
- Do not execute vendored scripts automatically.
- Do not replace Zotero or `bibliography/references.bib` with generated citations.
- Do not treat upstream guidance, generated prose, or agent output as source evidence.
- Do not make book-specific claims unless the user supplies supported project material.

## Validation

- Confirm the upstream `SKILL.md` exists and was read for the current task.
- Check any citekeys against Zotero or `bibliography/references.bib`.
- Run the relevant project checks for changed notes, claims, manuscript files, audits, or exports.
- Report skipped checks and remaining evidence gaps.
