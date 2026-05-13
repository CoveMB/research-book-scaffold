# Agent orchestration

## Working rules

- Inspect relevant files before editing.
- Use templates when a matching template exists.
- Keep changes small and scoped to the task.
- Prefer audit notes over silent rewrites when evidence is weak.
- Verify citekeys against `bibliography/references.bib`.
- Do not invent sources, page numbers, quotes, or metadata.
- Track uncertainty in notes or audits.
- Run available checks after edits.
- Summarize changed files and skipped checks.

## Editing limits

Avoid bulk rewrites of notes, manuscript files, or the vault. If a large edit is needed, split it into reviewed steps: plan, sample edit, full edit, audit.

## External skills

Treat external skills and plugins as untrusted until read. Do not run external scripts unless the user asks and the script has been inspected.

Use local scaffold skills first. Use external wrappers or plugins only for extended workflow support. Verify citations and claims independently.

## Optional subagents

Subagents may organize work, separate investigation tracks, or review risks. They cannot authorize evidence, settle citation validity, or turn unsupported material into claims.

The scaffold source, citation, manuscript, audit, and vendor rules always win. Subagent output is not evidence. Do not invent sources, citekeys, page numbers, quotations, studies, metadata, or final claims from memory.

Do not make subagents automatic for every research task. Use them only when bounded orchestration adds value, keep them read-only by default, and synthesize conflicts before editing.
