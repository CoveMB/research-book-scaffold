# Skills

Repo-scoped wrapper skills live in subfolders.

Each skill should include a `SKILL.md` file with YAML front matter.

External integration reports are recorded in `ARS_INSTALLED.md`,
`RBS_INSTALLED.md`, `SUBAGENT_ORCHESTRATOR_INSTALLED.md`, and
`OBSIDIAN_SKILLS_INSTALLED.md`.

## Local project skills

These skills are local to this repository because they depend on the exact folder
layout, checks, manuscript tooling, and vault conventions here. They are not
external plugin skills.

- `quarto-export-readiness`: release-audit and Quarto manuscript export readiness.
- `vault-hygiene-triage`: notes/research vault organization, inbox triage, placeholders, and wiki-link hygiene.

## External wrapper skills

These wrappers adapt upstream skill/plugin guidance to this repository's citation,
evidence, and vault rules.

- `ars-deep-research`: Academic Research Skills deep-research guidance through the local safety wrapper.
- `ars-academic-paper`: Academic Research Skills academic-paper guidance through the local safety wrapper.
- `ars-academic-paper-reviewer`: Academic Research Skills reviewer guidance through the local safety wrapper.
- `ars-academic-pipeline`: Academic Research Skills pipeline guidance through the local safety wrapper.
- `rbs-*`: Research Book Skills guidance through local wrappers for accessibility support, research-intent routing, source discovery, source notes, extraction tables, literature maps, claim ledgers, argument and chapter design, citation audits, figure/table integrity, scholarly integrity, workflow logging, release audits, continuity work, proposal support, and comps verification.
- `subagent-safe-using-subagent-orchestrator`: guarded Subagent Orchestrator compatibility gate.
- `subagent-safe-subagent-orchestrator`: guarded Subagent Orchestrator execution-shape helper.
- `obsidian-research-markdown`: Obsidian Markdown guidance through the local safety wrapper.
- `obsidian-research-bases`: Obsidian Bases guidance through the local safety wrapper.
- `obsidian-research-canvas`: JSON Canvas guidance through the local safety wrapper.
- `obsidian-research-cli`: Obsidian CLI guidance through the local safety wrapper.
- `obsidian-research-defuddle`: Defuddle web-ingest guidance through the local safety wrapper.

Use `rbs-rights-privacy-release-auditor` for external-sharing risk. Use
`quarto-export-readiness` for this repository's
`make release-audit`, Quarto render, and export-check workflow. Use
`vault-hygiene-triage` for this repository's folder hygiene and inbox triage.
Use the Obsidian wrappers only for Obsidian syntax and local vault mechanics.
They do not authorize sources, citations, page numbers, source metadata,
quotations, source relationships, or final claims.

Marketplace entries under `.agents/plugins/marketplace.json` are optional plugin
exposure. Immediate Codex and Codex Panel availability comes from the wrappers
in this directory.
