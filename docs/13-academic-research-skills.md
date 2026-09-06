# ARS Codex native plugin

Repository:

```text
https://github.com/Imbad0202/academic-research-skills-codex.git
```

Reviewed pin:

```text
925975e933a20893b81681d925a3404e3b7f73b7
```

Purpose: native Codex support for deep research, literature and systematic
reviews, academic writing, peer-review critique, and research-to-paper planning.

## Repository integration

- The upstream repository lives at
  `skill-plugins/academic-research-skills-codex/` as a pinned Git submodule.
- The bundled plugin root is `plugins/ars-codex` within that submodule.
- Its manifest name is `ars-codex`, with `skills: "./skills/"`.
- Its native skill entrypoint is
  `skills/academic-research-suite/SKILL.md` within the plugin root.
- `.agents/plugins/marketplace.json` exposes exactly one local `ars-codex`
  entry in category `Research`, with `AVAILABLE` installation and `ON_INSTALL`
  authentication policies.

Marketplace exposure is not installation. Setup and
`make install-external-skills` prepare the local source and marketplace entry
but never run `codex plugin add`. After a user separately chooses to install
the plugin, invoke the native skill as `$ars-codex:academic-research-suite`.

## Local boundaries

Use the native suite under `AGENTS.md` and the repository evidence rules. Do
not use it to invent sources, citations, citekeys, page numbers, quotations,
studies, metadata, or final claims. Do not enable the optional full runtime,
hooks, resolver clients, automatic subagents, external providers, credentials,
or network calls through repository setup.

The repository validates only what it owns: exact submodule URL, gitlink and
initialized origin; the plugin manifest's name and skills path; the native
entrypoint; the exact unique marketplace contract; and one isolated Codex CLI
discovery/catalog-loading smoke. The immutable pin and upstream gates own
package-internal parity, symlinks, nested provenance, and workflow inventory.

## One-time migration

The legacy repository and ARS Codex have unrelated histories. The installer
therefore uses a distinct path and never performs an in-place URL swap.

Before it removes an initialized legacy checkout at
`skill-plugins/academic-research-skills/`, both conditions must pass:

1. The checkout has no tracked, untracked, or ignored changes.
2. Its `HEAD` is exactly `81c7300b4066d233914563fc1c3f80512347b33c`,
   the legacy superproject gitlink.

The checkout must also use the exact separate module storage Git selects for
this checkout: `.git/modules/` in a primary checkout or the corresponding
`.git/worktrees/<name>/modules/` path in a linked worktree. When the guards pass,
migration removes only the old working-tree directory and preserves its Git
directory, commits, and local refs. It then initializes ARS Codex at the
distinct native path and exact pin.

Migration stops without deletion when the old checkout contains uncommitted
changes, is clean but at a divergent commit, resolves Git storage inside the
checkout or outside the current superproject, or is a nonempty non-submodule
directory. For changed files, inspect and copy them elsewhere or commit them to
a named legacy branch. For a divergent commit, preserve the commit or ref and
explicitly return the checkout to the recorded legacy gitlink. For ambiguous
directories or standalone clones, relocate them manually. Never delete the
legacy module Git directory or local refs as cleanup.

## Validation

Run the static repository boundary check:

```sh
python3 scripts/operations/skill_plugins/check_external_skills.py
```

Add the offline native smoke when Codex CLI loadability is in scope:

```sh
python3 scripts/operations/skill_plugins/check_external_skills.py --native-ars-smoke
```

The smoke creates a temporary `CODEX_HOME`, registers this repository as a
local marketplace, installs `ars-codex` only there, and verifies the namespaced
skill catalog entry and installed `SKILL.md` path through `codex debug
prompt-input`. It does not start a model turn or modify the user's Codex
profile.

## License

The reviewed upstream pin is licensed under Creative Commons
Attribution-NonCommercial 4.0 International (CC-BY-NC-4.0). Confirm
redistribution and commercial-use compatibility before relying on upstream
content outside the repository's permitted workflow.
