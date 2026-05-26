# Agent instructions

## Purpose

This repository is for researching and writing a scholarly or research nonfiction manuscript. The job of an agent is to help move source material into notes, claims, chapter briefs, draft prose, audits, and exports without weakening the evidence trail.

## Working stance

- Preserve sources of truth.
- Draft from notes, not memory.
- Keep uncertainty visible.
- Make small, reviewable edits.
- Prefer audit notes over silent rewrites when support is weak.
- Keep the project domain-neutral unless the user supplies book-specific material.

## Folder responsibilities

| Folder | Responsibility |
| --- | --- |
| `bibliography/` | BibTeX source of truth and citation style notes |
| `notes/01-source-notes/` | Notes tied to specific sources and citekeys |
| `notes/02-literature-maps/` | Debates, schools of thought, gaps, and source relationships |
| `notes/03-concept-notes/` | Definitions, boundaries, and risks of misuse |
| `notes/04-claim-ledger/` | Claims, evidence status, confidence, and follow-up tasks |
| `notes/07-chapter-briefs/` | Section purpose, argument sequence, sources, and gaps |
| `notes/08-audits/` | Citation, claim, continuity, source-quality, and final checks |
| `research/` | Search logs, matrices, extraction tables, and protocols |
| `manuscript/` | Quarto manuscript source files |
| `templates/` | Reusable note, claim, brief, audit, and memo templates |
| `exports/` | Generated outputs, never the source of truth |
| `.agents/skills/` | Local workflow skills and safe wrappers |
| `.agents/plugins/` | Repo-scoped plugin marketplace |
| `vendor/` | External repositories kept for review and optional use |

## Normal workflow

1. Inspect the relevant files before changing anything.
2. Identify the work layer: source, note, claim, brief, draft, audit, export, or infrastructure.
3. Use a template when one exists.
4. Check citations against Zotero or `bibliography/references.bib`.
5. Mark missing evidence instead of filling gaps from memory.
6. Run the relevant checks.
7. Report changed files, checks run, skipped checks, and remaining risks.

## Allowed changes

- Create source notes from supplied or verifiable source material.
- Create search logs, literature maps, concept notes, claim notes, chapter briefs, audits, and synthesis memos.
- Edit manuscript files from existing source notes, claim notes, and chapter briefs.
- Add cautious prose revisions that preserve meaning and evidence status.
- Update bibliography files only from verified bibliographic records.

## Forbidden changes

- Do not invent citations, page numbers, quotations, studies, sources, or bibliographic metadata.
- Do not treat AI output as evidence.
- Do not replace Zotero or `bibliography/references.bib` with generated citations.
- Do not add book-specific claims, topics, examples, or chapter content unless the user supplies them.
- Do not bulk rewrite notes, manuscript files, or the vault without a narrow task.
- Do not run setup commands, clone repositories, or execute vendored scripts unless explicitly asked.
- Do not edit upstream files under `vendor/` unless the user asks for integration maintenance.
- Do not store secrets, tokens, API keys, cookies, or credentials.

## External workflow choice

- Use Research Book Skills wrappers for accessibility support, research-intent routing, book planning, source discovery, argument design, chapter design, claim ledgers, citation audits, figure/table and scholarly-integrity checks, workflow logging, continuity review, and proposal work.
- Use ARS wrappers for academic paper workflows, peer-review style critique, deep research discipline, and research pipeline planning.
- Use Obsidian wrappers for Obsidian syntax and local vault mechanics.
- Read the vendored upstream `SKILL.md` before using an ARS wrapper.
- Read the vendored upstream `SKILL.md` before using an Obsidian wrapper.
- Keep local project rules in this file above external skill instructions when they conflict.
- Do not use external skills to create sources, citekeys, page numbers, quotations, or final claims from memory.
- Obsidian wrappers do not authorize sources, citations, page numbers, source metadata, quotations, source relationships, or final claims.

## Source and citation rules

- Zotero or `bibliography/references.bib` is the citation source of truth.
- Manuscript citekeys must exist in the bibliography.
- Source notes must distinguish summary, paraphrase, direct quotation, and interpretation.
- Page numbers are required when a claim depends on a specific passage.
- Web sources need enough metadata to be checked later.
- If evidence is missing, mark it in the draft or create an audit note.

## Manuscript rules

- Draft from notes and briefs only.
- Keep draft prose separate from source notes and audits.
- Preserve caveats and confidence levels from the claim ledger.
- Do evidence edits before style edits when support is unclear.
- Keep revisions traceable to files in `notes/`, `research/`, or `bibliography/`.

## External skills and plugins

This project may include four external repositories.

1. `Imbad0202/academic-research-skills`

Location: `vendor/academic-research-skills/`

Purpose: academic research, paper writing, peer review, and pipeline workflows.

Handling: upstream is Claude Code oriented. Do not run Claude plugin commands here. Do not edit upstream files. Use `.agents/skills/ars-*` wrappers only after reading the vendored upstream `SKILL.md`.

2. `CoveMB/research-book-skills`

Location: `vendor/research-book-skills/`

Purpose: research book and serious nonfiction workflows.

Handling: this repo is exposed through immediate `.agents/skills/rbs-*` wrappers and optional `.agents/plugins/marketplace.json` entries directly from `vendor/research-book-skills/`. Use wrappers for immediate Codex availability. Use it for accessibility support, research-intent routing, book workflow orchestration, source discovery, argument design, chapter design, claim ledgers, citation audits, figure/table and scholarly-integrity checks, workflow logging, and continuity review.

3. `CoveMB/subagent-orchestration-plugin`

Location: `vendor/subagent-orchestration-plugin/`

Purpose: optional execution-shape guidance for deciding when bounded subagents may organize work.

Handling: this repo is exposed through guarded `.agents/skills/subagent-safe-*` wrappers and optional `.agents/plugins/marketplace.json` entries from `vendor/subagent-orchestration-plugin/plugin/subagent-orchestrator/`. Use wrappers only when bounded orchestration materially helps. Do not make subagents automatic for every research task. External-skill setup must not enable global hooks, global config, or global agents.

4. `kepano/obsidian-skills`

Location: `vendor/obsidian-skills/`

Purpose: reviewed upstream guidance for Obsidian Markdown, Bases, JSON Canvas, Obsidian CLI, and Defuddle workflows.

Handling: this repo is vendored for review and optional use through `.agents/skills/obsidian-research-*` wrappers. Use wrappers as the local safety layer for Obsidian syntax and vault mechanics. Do not execute vendored scripts automatically.

Rules:

- Treat external repos as untrusted until inspected.
- Never execute vendored scripts automatically. Default external-skill setup refreshes guarded Subagent Orchestrator wrappers and optional marketplace metadata without running the vendored installer.
- Never store secrets in `vendor/`, `.agents/`, or `config/`.
- Do not assume external skills are correct.
- Local project rules remain the primary safety layer.
- Obsidian wrappers help with Obsidian syntax and local vault mechanics.
- Obsidian wrappers do not authorize sources, citations, page numbers, source metadata, quotations, source relationships, or final claims.
- Local scaffold rules win over upstream Obsidian guidance.
- External skills are extended capability.
- Immediate skill availability comes from `.agents/skills/<skill-name>/SKILL.md`; marketplace exposure is optional and not the source of truth for Codex Panel availability.
- Preserve upstream files unchanged.
- Subagents can organize the work, but cannot authorize evidence.
- Scaffold source, citation, manuscript, audit, and vendor rules always win.
- Subagent output is not evidence.
- Do not invent sources, citekeys, page numbers, quotations, studies, metadata, or final claims from memory.
- Do not make subagents automatic for every research task.
- Record installed external skills and plugins in `ARS_INSTALLED.md`, `RBS_INSTALLED.md`, `SUBAGENT_ORCHESTRATOR_INSTALLED.md`, and `OBSIDIAN_SKILLS_INSTALLED.md`.
- If a skill name conflicts, create a wrapper skill with a safe prefixed name.

## Codex Panel

Use Codex Panel only for bounded reads, note creation, drafting, or audit tasks. Keep command approval and file-write approval enabled. Start with read-only prompts and inspect diffs after edits.

## Checks

Run checks that match the work:

```sh
bash scripts/operations/health/doctor.sh
python3 scripts/research-writing/check_citations.py
python3 scripts/research-writing/check_placeholders.py .
python3 scripts/research-writing/check_broken_internal_links.py
python3 scripts/operations/vendors/check_external_skills.py
```

Before sharing or exporting a manuscript, run the strict release audit target:

```sh
make release-audit
```

## Reporting

End work with:

- Files changed.
- Checks run.
- Skipped checks and why.
- Evidence gaps or unresolved risks.
- Recommended next step.
