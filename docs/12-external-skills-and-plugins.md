# External skills and plugins

External workflows extend the scaffold. They do not replace local safety rules.

## Layers

| Layer | Location | Use |
| --- | --- | --- |
| Local scaffold skills | `.agents/skills/` | Primary safety and workflow layer |
| Vendored external repos | `vendor/` | Reviewed upstream source copies pinned as Git submodules |
| Plugin marketplace | `.agents/plugins/marketplace.json` | Optional plugin exposure from vendored paths |

## Rules

- Treat external repositories as untrusted until inspected.
- Do not run vendored scripts automatically.
- Do not store API keys or credentials.
- Do not edit upstream files in `vendor/`.
- Keep marketplace exposure separate from skill wrapper creation.
- External skills can guide workflow discipline, but citations and claims still need independent verification.

## Inspecting external skills

Read the upstream `SKILL.md` before use. Check for:

- tool assumptions
- slash commands
- hooks or subagents
- provider or API-key assumptions
- file-write behavior
- license limits

## Updating or removing

Initialize vendored repositories with `git submodule update --init --recursive` or by running setup. Update pinned submodule commits only after review. Remove integrations by deleting wrapper skills, marketplace entries, install reports, and submodule references. Leave bibliography and manuscript files untouched.

## License caution

- `Imbad0202/academic-research-skills`: CC-BY-NC-4.0.
- `CoveMB/research-book-skills`: MIT.
