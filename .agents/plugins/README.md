# Plugin marketplace

Repo-scoped plugin marketplace files live here.

`marketplace.json` exposes local plugins from reviewed skill/plugin source paths. Keep the
registry tracked; external-skill setup refreshes the source submodules and
rewrites the marketplace entry when needed.

The optional Subagent Orchestrator entry exposes only the nested plugin path.
Default setup refreshes the guarded wrappers and optional marketplace metadata
without running the external installer. Subagents do not authorize evidence or
override scaffold source, citation, manuscript, audit, or skill/plugin source rules.
