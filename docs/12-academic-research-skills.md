# Academic Research Skills

Academic Research Skills is an external research workflow suite from:

```text
https://github.com/CoveMB/academic-research-skills
```

It is Claude-oriented upstream, so local Codex use may need adaptation.

## Planned layout

```text
vendor/academic-research-skills/
.agents/skills/ars-<skill-name>/
```

The installer will discover all folders containing `SKILL.md`. It must not assume only one repo layout.

## Default targets

If present, install these preferred skills first:

- `deep-research`
- `academic-book`
- `academic-paper`
- `academic-paper-reviewer`
- `academic-pipeline`

Other discovered skills may be listed for review.

## Installation rules

- Preserve upstream files under `vendor/academic-research-skills/`.
- Copy usable skills into `.agents/skills/` with an `ars-` prefix when needed.
- If a front matter name collides, create a local wrapper or document the collision.
- Record installed mappings in `.agents/skills/ARS_INSTALLED.md`.
- Do not run vendored scripts automatically.
- Do not install Claude plugins.
- Do not require Anthropic credentials.
- Do not store API keys.

## Use

Use vendored skills for research process, reviews, citation checking, integrity gates, academic-book workflows, and pipeline discipline.

Keep local generic skills as the primary workflow for this repository.
