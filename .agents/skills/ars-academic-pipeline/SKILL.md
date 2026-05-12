---
name: ars-academic-pipeline
description: Use this wrapper to consult the vendored Academic Research Skills `academic-pipeline` workflow after reading and validating the upstream instructions.
---

# ars-academic-pipeline

## Purpose

Use the vendored `academic-pipeline` workflow as external guidance for academic research discipline.

## Upstream source

Read this file before using the wrapper:

```text
vendor/academic-research-skills/academic-pipeline/SKILL.md
```

## Rules

- The upstream repository is Claude Code oriented.
- Do not assume Claude-specific slash commands, hooks, subagents, plugin commands, or API-key assumptions work here.
- Do not execute vendored scripts automatically.
- Do not edit upstream files under `vendor/academic-research-skills/`.
- Verify citations, claims, page numbers, and source metadata independently.
- Keep local scaffold skills as the primary safety layer.

## Output

Summarize which upstream guidance was used, what evidence was checked, and what uncertainty remains.
