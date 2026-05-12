# Scholarly research and writing boilerplate

Clean scaffold for source management, notes, manuscript drafting, citation checks, research audits, and local agent workflows. It is domain-neutral by design.

## Four-layer architecture

| Layer | Folder | Source of truth |
| --- | --- | --- |
| Sources and bibliography | `bibliography/`, Zotero | Zotero or `bibliography/references.bib` |
| Notes and knowledge base | `notes/`, `research/` | Structured notes and audit files |
| Manuscript production | `manuscript/`, `exports/` | Quarto source files |
| Agent orchestration | `AGENTS.md`, `.agents/skills/`, `docs/` | Repo-scoped instructions |

## Common commands

These commands will be available after later phases add scripts:

```sh
bash setup.sh
bash scripts/doctor.sh
bash scripts/render.sh
python3 scripts/check_citations.py
python3 scripts/check_placeholders.py .
python3 scripts/check_broken_internal_links.py
```

## Templates

Use `templates/` for source notes, concept notes, claim notes, chapter briefs, search logs, audits, and synthesis memos. Create new notes from templates instead of starting from a blank file.

## Repo-scoped skills

Future skills live in `.agents/skills/`. Use them for bounded tasks such as search planning, source notes, claim audits, drafting from notes, and final manuscript checks.

## Optional integrations

- Obsidian Codex can connect an Obsidian vault to local agent workflows. Install it only with an explicit vault path.
- Academic Research Skills can be vendored under `vendor/academic-research-skills/` and copied into `.agents/skills/` after review.

## Do not automate

- Secrets, API keys, or credentials.
- Citation creation from memory.
- Whole-vault rewrites.
- System installs without explicit permission.
- Execution of unreviewed vendored scripts.
