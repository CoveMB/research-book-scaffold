# Scholarly research and writing boilerplate

Generic scaffold for source management, notes, manuscript drafting, citation checks, research audits, and agent workflows.

## Architecture

1. Sources and bibliography: Zotero or `bibliography/references.bib` is the citation source of truth.
2. Notes and knowledge base: notes keep source notes, concepts, claims, audits, and synthesis separate.
3. Manuscript production: manuscript files hold draftable Quarto material.
4. Agent orchestration: `.agents/` holds repo-scoped workflow instructions and skills.

## Current state

Phase 1 scaffold only. Installers, checks, templates, repo skills, and vendor integrations come in later phases.

## Basic rules

- Keep this project domain-neutral.
- Do not store secrets, API keys, or credentials.
- Do not invent citations.
- Treat AI draft text as provisional until audited.
- Keep changes small and documented.

