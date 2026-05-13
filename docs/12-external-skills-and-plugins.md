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
- Do not run vendored scripts automatically, except the bounded project-scoped Subagent Orchestrator installer during explicit external-skill setup after boundary checks.
- Do not store API keys or credentials.
- Do not edit upstream files in `vendor/`.
- Keep marketplace exposure separate from skill wrapper creation.
- External skills can guide workflow discipline, but citations and claims still need independent verification.
- Subagents can organize work, but cannot authorize evidence.
- Scaffold source, citation, manuscript, audit, and vendor rules always win.
- Subagent output is not evidence.
- Do not invent sources, citekeys, page numbers, quotations, studies, metadata, or final claims from memory.

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

## Updating skill vendors

Run this when an upstream skill repository has new commits:

```sh
bash scripts/update-skills-vendors.sh
```

The updater:

- fetches the parent repository refs
- syncs and initializes the configured vendor submodules
- refuses to continue if a vendor has uncommitted changes
- fast-forwards each selected vendor with `git pull --ff-only`
- refreshes local skill wrappers, marketplace metadata, and install reports through the local installer
- runs `python3 scripts/check_external_skills.py`
- runs `bash scripts/doctor.sh`

After a successful run, review the submodule pointer changes and any refreshed files before committing. Use `--skip-ars`, `--skip-rbs`, or `--skip-subagent-orchestrator` to leave a vendor pinned while updating others. Use `--skip-checks` only when another verification command will be run immediately afterward.

## Optional subagent plugin

`CoveMB/subagent-orchestration-plugin` is vendored at `vendor/subagent-orchestration-plugin/` and exposed through `.agents/plugins/marketplace.json` from:

```text
./vendor/subagent-orchestration-plugin/plugin/subagent-orchestrator
```

The scaffold does not make subagents automatic for every research task. When Subagent Orchestrator is selected during external-skill setup, the installer runs only after boundary checks confirm the vendored submodule is configured, from the expected origin, clean, and available locally. `make install-subagent-orchestrator` runs only that integration path. The installer uses `--scope project`, keeps the plugin available-only, and must not install global hooks, global config, or global agents.

## License caution

- `Imbad0202/academic-research-skills`: CC-BY-NC-4.0.
- `CoveMB/research-book-skills`: MIT.
- `CoveMB/subagent-orchestration-plugin`: MIT.
