# Overview

This boilerplate keeps research, writing, and agent work separated so each claim can be traced back to notes and sources.

## Architecture

```text
sources + Zotero
      |
      v
bibliography/references.bib
      |
      v
notes + research logs -> claim ledger -> chapter briefs
      |                                      |
      v                                      v
audits -------------------------------> manuscript
                                             |
                                             v
                                          exports

AGENTS.md + .agents/skills guide agent work across the repo.
```

## Key rules

- Zotero or `bibliography/references.bib` is the citation source of truth.
- Draft from notes and claim records, not from memory.
- Mark missing evidence instead of smoothing over it.
- Keep source notes, claims, briefs, drafts, and audits in separate files.
- Treat AI-generated text as provisional until audited.
- Keep the scaffold generic and free of subject-matter assumptions.
