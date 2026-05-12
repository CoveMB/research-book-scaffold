# Overview

This scaffold ties the research book workflow together without mixing its layers. Sources live in Zotero and BibTeX. Evidence becomes notes, claims, briefs, and audits. Drafts live in Quarto. Local agent tools work around those files under the rules in this repository.

## Architecture

```text
Search tools + source files
      |
      v
Zotero + Better BibTeX -> bibliography/references.bib
      |
      v
Obsidian or Markdown editor -> notes/ + research/
      |                              |
      v                              v
claim ledger -----------------> chapter briefs
      |                              |
      v                              v
audits -----------------------> manuscript/ Quarto source
                                      |
                                      v
                              Quarto + Pandoc -> exports/

Codex CLI, Obsidian Codex, MCP, and repo-scoped skills operate around this flow.
They help with small reads, focused edits, audits, and checks. Zotero, notes, BibTeX, audits, and user review remain the controlling record.
```

## Tool stack

| Tool | Role | How it fits |
| --- | --- | --- |
| Zotero | Source library | Store PDFs, annotations, and source metadata. Verify sources here before notes, claims, or citations depend on them. |
| Better BibTeX | Citekey and BibTeX export | Export stable citekeys from Zotero to `bibliography/references.bib`. |
| `bibliography/references.bib` | Local citation file | Give Quarto, Pandoc, and citation checks the citekeys used in drafts. |
| Obsidian or Markdown editor | Writing and navigation workspace | Work directly with `notes/`, `research/`, `manuscript/`, and audit files in the project root. |
| Obsidian Codex plugin | Agent work inside Obsidian | Create notes, revise single sections, and run audits with command approval and file write approval enabled. |
| Codex CLI | Local agent runtime | Inspect repository files, follow `AGENTS.md`, make small edits, and run approved checks. |
| Repo-scoped skills | Agent workflow rules | Give agents repeatable procedures for source discovery, chapter design, claim ledgers, citation audits, continuity checks, and safe wrappers. |
| Research Book Skills | Research book workflows | Add optional support for book planning, source discovery, argument design, chapter design, drafting from notes, and manuscript checks. |
| Academic Research Skills | Academic workflow wrappers | Add optional support for paper planning, peer review style critique, deep research, and pipeline design after the upstream instructions have been reviewed. |
| MCP | Permissioned tool bridge | Connect agents to narrow local integrations such as Zotero without opening broad filesystem or credential access. |
| Discovery tools | Source finding | Use tools such as Elicit, Semantic Scholar, OpenAlex, and Scite to find candidate sources. Verify anything kept in Zotero or BibTeX before citing it. |
| Quarto | Manuscript source and renderer | Keep draft chapters in `manuscript/` and render outputs only from checked source files. |
| Pandoc | Format conversion | Convert rendered manuscript output to formats such as HTML, PDF, and DOCX. |
| Git | Version history | Track small edits to notes, docs, scripts, manuscript files, and integration metadata. |
| Audit scripts and Make targets | Checks | Check citations, placeholders, broken links, external skill setup, and release readiness before sharing or export. |

## Key rules

- Zotero or `bibliography/references.bib` is the citation source of truth.
- Draft from notes and claim records, not from memory.
- Mark missing evidence instead of smoothing over it.
- Keep source notes, claims, briefs, drafts, and audits in separate files.
- Treat AI-generated text as provisional until audited.
- Keep the scaffold generic and free of subject-matter assumptions.
