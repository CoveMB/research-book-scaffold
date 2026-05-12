# Agent instructions

## Purpose

This repository is a generic scholarly research and long-form writing scaffold.

## Operating rules

- Inspect relevant files before editing.
- Preserve source-of-truth data in Zotero or `bibliography/references.bib`.
- Do not create citations from memory.
- Do not add domain-specific examples, claims, or chapter content.
- Keep documentation short and practical.
- Prefer templates and small focused edits.
- Record uncertainty instead of hiding it.
- Summarize changed files after work.

## Folder responsibilities

- `bibliography/`: citation source files and citation style notes.
- `notes/`: source notes, claim notes, concept notes, audits, and synthesis.
- `research/`: search logs, matrices, extraction tables, and protocols.
- `manuscript/`: Quarto book draft files.
- `templates/`: reusable note and audit templates.
- `scripts/`: local setup, checks, rendering, and helper commands.
- `docs/`: workflow documentation.
- `.agents/`: repo-scoped agent instructions and skills.
- `vendor/`: external repositories copied for review and optional use.

## Safety

- Do not install packages, clone repositories, or run external scripts unless the user asks.
- Do not store secrets in the repo.
- Treat vendored skills and plugins as untrusted until inspected.

