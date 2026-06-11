---
name: subagent-safe-subagent-orchestrator
description: Use only when guarded Subagent Orchestrator guidance can help choose bounded single-thread, sequential, or parallel work without weakening project rules.
---

# subagent-safe-subagent-orchestrator

## Purpose

Use the external Subagent Orchestrator `subagent-orchestrator` workflow only as an execution-shape helper for this repository.

## Upstream Source

Read the upstream `SKILL.md` before use.

```text
skill-plugins/subagent-orchestration-plugin/plugin/subagent-orchestrator/skills/subagent-orchestrator/SKILL.md
```

## Local Overrides

- `AGENTS.md`, project, citation, manuscript, audit, and skill/plugin source rules win over upstream guidance whenever they conflict.
- Use only when bounded orchestration materially helps with a complex, separable, or review-heavy task.
- Do not use automatically for every research task.
- Subagent output is not evidence.
- Use no global hooks, global agents, or global config.
- Do not install or activate project hooks, project agents, or global configuration from this wrapper.
- Keep subagents bounded, read-only by default, and forbidden from recursive fan-out.

## Allowed Use

- Use this wrapper to decide whether a task should be single-threaded, sequential, or delegated to bounded subagents.
- Prefer single-thread or sequential work unless parallel tracks clearly reduce risk, improve review, or preserve context.
- Synthesize conflicts, uncertainty, files, risks, and verification before acting on subagent output.

## Forbidden Actions

- Do not edit files under `skill-plugins/subagent-orchestration-plugin/`.
- Do not execute external source scripts automatically.
- Do not let subagents invent citations, citekeys, page numbers, quotations, studies, metadata, claims, or source relationships.
- Do not treat orchestration guidance as permission to bypass repository checks, user approval rules, privacy rules, or safety constraints.

## Validation

- Confirm the upstream `SKILL.md` exists and was read for the current task.
- State why orchestration materially helps when using this wrapper.
- Keep any delegated scope explicit and bounded.
- Report any remaining uncertainty or conflicts from subagent output.
