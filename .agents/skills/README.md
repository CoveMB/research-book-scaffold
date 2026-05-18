# Skills

Repo-scoped wrapper skills live in subfolders.

Each skill should include a `SKILL.md` file with YAML front matter.

External integration reports are recorded in `ARS_INSTALLED.md`,
`RBS_INSTALLED.md`, and `SUBAGENT_ORCHESTRATOR_INSTALLED.md`.

## Local project skills

These skills are local to this repository because they depend on the exact folder
layout, checks, manuscript tooling, and vault conventions here. They are not
vendored plugin skills.

- `quarto-export-readiness`: release-audit and Quarto manuscript export readiness.
- `vault-hygiene-triage`: notes/research vault organization, inbox triage, placeholders, and wiki-link hygiene.

Use the vendored Research Book Skills `rights-privacy-release-auditor` for
external-sharing risk. Use `quarto-export-readiness` for this repository's
`make release-audit`, Quarto render, and export-check workflow. Use
`vault-hygiene-triage` for this repository's folder hygiene and inbox triage.
