# Plugin marketplace

Repo-scoped plugin marketplace files live here.

`marketplace.json` exposes local plugins from reviewed vendored paths. Keep the
registry tracked; external-skill setup refreshes the vendored submodules and
rewrites the marketplace entry when needed.

The optional Subagent Orchestrator entry exposes only the nested plugin path.
Default setup refreshes the guarded wrappers and optional marketplace metadata
without running the vendored installer. Subagents do not authorize evidence or
override scaffold source, citation, manuscript, audit, or vendor rules.
