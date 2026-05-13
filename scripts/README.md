# Scripts

Local setup, checks, rendering, and helper scripts live here.

Use `bash scripts/doctor.sh` for a quick health check, `python3 -m unittest discover scripts/tests` for script tests, `make audit` for scaffold checks, and `make release-audit` before sharing a manuscript. `python3 scripts/setup_environment.py` treats the project root as the Obsidian vault root by default.

Use `bash scripts/update-skills-vendors.sh` when the vendored skill or plugin repositories have new upstream commits. It fetches repository refs, fast-forwards the configured vendor submodules, refreshes local skill wrappers, marketplace metadata, install reports, and runs the external-skill and doctor checks.

Use `make install-subagent-orchestrator` when only the optional subagent plugin should be refreshed. External-skill setup runs that installer after boundary checks, passes `--scope project`, keeps the plugin available-only, and does not activate the prompt gate or install project agents.
