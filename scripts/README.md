# Scripts

Local research-writing tools, operational scripts, tests, and shared helpers live here.

## Layout

| Folder | Purpose |
| --- | --- |
| `research-writing/` | Day-to-day research, writing, manuscript audit, template, and render entry points |
| `operations/setup/` | Local setup and environment checks |
| `operations/health/` | Repository health checks |
| `operations/vendors/` | External skill, plugin, and vendor-submodule maintenance |
| `operations/obsidian/` | Codex Panel and Obsidian integration install/check scripts |
| `lib/` | Shared Python and shell helpers for scripts |
| `tests/` | Unit tests for script behavior and references |

Use `bash scripts/operations/health/doctor.sh` for a quick health check, `python3 -m unittest discover scripts/tests` for script tests, `make audit` for scaffold checks, and `make release-audit` before sharing a manuscript. `python3 scripts/operations/setup/setup_environment.py` treats the project root as the Obsidian vault root by default, installs Codex Panel unless skipped, and refreshes vendored external skill wrappers under `.agents/skills` unless `--skip-external-skills` is passed. Pass `--register-obsidian-vault` only when setup should also write Obsidian's app-level vault registry for direct GUI launches.

Use `bash scripts/operations/vendors/update-skills-vendors.sh` when the vendored skill or plugin repositories have new upstream commits. It fetches repository refs, fast-forwards the configured vendor submodules, refreshes local skill wrappers, marketplace metadata, install reports, and runs the external-skill and doctor checks.

Use `python3 scripts/operations/vendors/install_external_skills.py --yes --force --skip-ars --skip-rbs --skip-subagent-orchestrator --preserve-vendor-checkouts` when only the vendored Obsidian Skills wrappers and install report need to be refreshed from the current `vendor/obsidian-skills/` checkout. Verify with `python3 scripts/operations/vendors/check_external_skills.py`.

Use `make install-subagent-orchestrator` when only the optional subagent wrapper and marketplace exposure should be refreshed. External-skill setup keeps Subagent Orchestrator guarded through `.agents/skills/subagent-safe-*` wrappers, leaves marketplace exposure optional, and does not activate global hooks, global config, or global agents.

Use `python3 scripts/operations/obsidian/check_obsidian_artifacts.py` or `make check-obsidian-artifacts` to validate project-local `.base` and `.canvas` files.
