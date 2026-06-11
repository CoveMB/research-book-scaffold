# Academic Research Skills

Repository:

```text
https://github.com/Imbad0202/academic-research-skills.git
```

Purpose: academic research and paper workflow support, including deep research, paper writing, peer review, and pipeline planning.

## Upstream orientation

This repository is Claude Code and Claude plugin oriented. Do not assume its plugin install commands, slash commands, hooks, subagents, or provider assumptions work in this environment.

## Core upstream skills

- `deep-research`
- `academic-paper`
- `academic-paper-reviewer`
- `academic-pipeline`

## Local handling

- Source upstream under `skill-plugins/academic-research-skills/` as a Git submodule.
- Preserve upstream files unchanged.
- Create wrappers under `.agents/skills/ars-*/`.
- Each wrapper points to the upstream `SKILL.md`.
- Each wrapper warns when an upstream step depends on Claude-specific behavior.

## Use

- Literature review planning.
- Systematic research workflows.
- Academic paper integrity checks.
- Peer-review style critique.
- Research pipeline planning.
- Citation and claim discipline.

## Avoid

- Creating final citations from memory.
- Creating unverified sources.
- Running Claude-specific plugin commands here.
- Running external source scripts before inspection.
- Commercial workflows unless license compatibility is confirmed.
