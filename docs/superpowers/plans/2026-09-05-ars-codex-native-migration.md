# ARS to ARS Codex Native Plugin Migration Implementation Plan

> **For implementers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the Claude-oriented Academic Research Skills submodule and four local wrappers with one immutable, optional, Codex-native `academic-research-suite` plugin integration.

**Architecture:** Keep the new upstream repository at a distinct submodule path because its history is unrelated to the legacy repository. A guarded, one-time migration removes only a verified legacy checkout while preserving its separate Git directory and refs; repository-owned validation then stops at the new gitlink, origin, plugin manifest, native entrypoint, marketplace contract, and one offline Codex CLI discovery/loading smoke test.

**Tech Stack:** Git submodules, Python 3.11 standard library, `unittest`, JSON, Codex CLI plugin commands, Markdown documentation.

**Spec:** `docs/superpowers/plans/2026-09-05-ars-codex-native-migration.md#global-constraints` captures the approved migration brief and is the implementation authority for this bounded change.

## Global Constraints

- Work in a separate worktree. Before any Git mutation, record `rtk git branch --show-current`, `rtk git rev-parse HEAD`, `rtk git status --short --branch`, and `rtk git submodule status`.
- The source checkout was verified on `main` at `1d07b763fea44c4e92af83a06cb567dc6d8890fc`; its only local change was the user-owned three-line `AGENTS.md` `## Sub-Agents` addition. The implementation worktree was then based on refreshed `origin/main` at `b8227e53b4ec6373acca11d96f51a774201de864`. Do not copy, delete, reformat, stage, or otherwise absorb the source-checkout change. Limit implementation-worktree `AGENTS.md` edits to the existing ARS paragraphs and installation-report sentence.
- Replace `https://github.com/Imbad0202/academic-research-skills.git` at `skill-plugins/academic-research-skills` with `https://github.com/Imbad0202/academic-research-skills-codex.git` at `skill-plugins/academic-research-skills-codex`, pinned to `925975e933a20893b81681d925a3404e3b7f73b7`.
- Treat `81c7300b4066d233914563fc1c3f80512347b33c` as the only safe legacy checkout `HEAD`. Never perform `git submodule set-url`, move the old checkout onto the new repository, merge the histories, delete the legacy module Git directory, or delete legacy refs.
- Expose only `skill-plugins/academic-research-skills-codex/plugins/ars-codex`, whose manifest name is `ars-codex`, whose manifest `skills` value is `./skills/`, and whose native entrypoint is `skills/academic-research-suite/SKILL.md` relative to that plugin root.
- The marketplace entry is exactly one object named `ars-codex`, with local path `./skill-plugins/academic-research-skills-codex/plugins/ars-codex`, category `Research`, installation policy `AVAILABLE`, and authentication policy `ON_INSTALL`.
- Marketplace exposure is availability, not installation. Setup and installer code must not run `codex plugin add`, change user-level Codex configuration, enable hooks, or auto-install the plugin.
- Delete the four repo-scoped ARS wrappers and all generator, checker, report, inventory, documentation, and smoke-test behavior that exists only for them. Do not add an `experiment-agent` wrapper or any replacement wrapper.
- Before deleting aliases, rerun a repository-owned consumer search. If it reveals a non-repository compatibility contract, stop and report the exact consumer instead of retaining an alias silently.
- Do not change Research Book Skills behavior, its submodule/gitlink, wrapper files, marketplace entry, install report, or documentation except shared prose that must distinguish it from the native ARS plugin.
- Do not change `notes/`, `research/`, `bibliography/`, `manuscript/`, templates, exports, or upstream contents under any `skill-plugins/` checkout.
- Do not enable runtime/plugin network calls, the optional full ARS runtime, hooks, resolver clients, automatic subagents, providers, or credentials. The only planned network access is Git object transfer needed to materialize the reviewed ARS Codex pin and the already-recorded RBS/Obsidian gitlinks in the isolated worktree. The native smoke test must use only local Codex CLI catalog/prompt assembly and a temporary Codex home; it must not start a model turn.
- Validate only this repository's integration boundary. Do not add canonical/plugin byte-parity checks, symlink inventories, nested source-SHA provenance, internal workflow inventories, or other upstream package-quality gates.
- The current execution request separately authorizes bounded implementation, commit, push, and MR creation after an independent zero-finding review. It does not authorize plugin installation, publication, merge, deployment, provider/credential changes, or any other external action.

## Verified Inputs and Remaining Uncertainty

- No existing ARS-to-ARS-Codex plan artifact was present under `docs/superpowers/plans/`, elsewhere in the source checkout, or in the existing linked worktrees; this file is the complete replacement plan.
- The upstream snapshot supplied for this plan was main `925975e933a20893b81681d925a3404e3b7f73b7`, plugin version `0.1.28`, with latest tag `v0.1.27`. Branch, tag, version, manifest, and skill-path facts were not refreshed because the exact approved pin and required contracts were already supplied.
- Official OpenAI documentation currently describes a skills-only plugin as `.codex-plugin/plugin.json` plus `skills/<name>/SKILL.md`, with a `skills: "./skills/"` manifest field. It documents the repository root containing `.agents/plugins/marketplace.json` as the local marketplace root, and says a plugin must be installed before its bundled skill is available in a new session: <https://developers.openai.com/plugins/build/plugins> and <https://developers.openai.com/codex/plugins>.
- Local help and an isolated empirical check with `codex-cli 0.146.0` confirm `codex plugin marketplace add`, `codex plugin list --available --json`, `codex plugin add`, and `codex debug prompt-input`. The prompt-input output registers the installed skill's namespaced catalog entry and cached `SKILL.md` path, but does not inject the full skill body before a model turn. The smoke test therefore proves native discovery and catalog loading without a model/network call. If the supported CLI command surface changes before implementation, update only the smoke adapter and its documentation; do not weaken the manifest or marketplace assertions.
- The only plausible compatibility uncertainty is an external consumer of the four old aliases that is not represented in this repository. The required pre-delete search is the stop gate for any such evidence.
- After independent review identified the actual license-documentation surface, the native repository's `LICENSE` was refreshed at the exact reviewed commit. It states Creative Commons Attribution-NonCommercial 4.0 International (CC-BY-NC-4.0): <https://github.com/Imbad0202/academic-research-skills-codex/blob/925975e933a20893b81681d925a3404e3b7f73b7/LICENSE>. `docs/12-external-skills-and-plugins.md`, not the generic `README.md` caution, owns the repository-specific license statement.

## File Map

### Planning artifact

- `docs/superpowers/plans/2026-09-05-ars-codex-native-migration.md` — this reviewed replacement plan, repaired before implementation to remove brittle source-text test expectations and encode the authorized review/MR closeout.

### Add

- `skill-plugins/academic-research-skills-codex` — new submodule gitlink at the reviewed commit; upstream contents remain untouched.
- `scripts/tests/test_ars_codex_migration.py` — real-Git fixture coverage for dirty, divergent, and unrelated-history legacy migrations.

### Modify

- `.gitmodules` — remove the complete legacy stanza and add a distinct native-repository stanza/path.
- `scripts/lib/project_config.py` — own the legacy guard constants, native source pin/path, plugin spec, one native skill name, and exact marketplace contract; remove ARS wrapper inventory.
- `scripts/operations/skill_plugins/install_external_skills.py` — guard and remove only safe legacy checkouts, initialize the pinned native submodule, expose its marketplace entry, and remove ARS wrapper/report generation.
- `scripts/operations/skill_plugins/update_skill_plugins.py` — run the same legacy guard before any native initialization, then keep ARS Codex pinned instead of fast-forwarding it while retaining existing RBS and Obsidian update behavior.
- `scripts/operations/skill_plugins/check_external_skills.py` — replace wrapper/internal checks with exact integration-boundary checks and the opt-in offline native Codex smoke.
- `scripts/operations/setup/setup_environment.py` — remove the arbitrary `--ars-ref` override and pass the remaining installer arguments unchanged.
- `scripts/tests/test_install_external_skills.py` — cover native installer dry-run/report behavior, exact marketplace merge behavior, and absence of ARS wrapper/report generation.
- `scripts/tests/test_update_skill_plugins.py` — assert ARS Codex is pinned and not fetched/pulled while RBS and Obsidian retain their current update flow.
- `scripts/tests/test_check_external_skills.py` — cover exact gitlink/origin, manifest, native entrypoint, marketplace equality/uniqueness, and native smoke command handling.
- `scripts/tests/test_project_tooling.py` — assert the new source/plugin constants and repo-scoped inventory without ARS wrapper directories.
- `scripts/tests/test_setup_environment.py` — assert `--ars-ref` is rejected and setup maps the remaining arguments correctly.
- `scripts/tests/test_docs_consistency.py` — bind general documentation to native ARS terminology and optional-install boundaries.
- `end-2-end-tests/tests/test_end_to_end_doc.py` — replace four wrapper assertions with one native plugin/skill and migration-recovery contract.
- `.agents/plugins/marketplace.json` — add the exact, unique `ars-codex` entry without changing the existing RBS object.
- `.agents/plugins/README.md` — distinguish marketplace availability from user installation and identify the native ARS plugin path.
- `.agents/skills/README.md` — remove the ARS wrapper/report inventory and direct users to the optional native plugin.
- `AGENTS.md` — update only existing ARS routing/source/handling/report language; preserve the user-owned `## Sub-Agents` addition outside the implementation diff.
- `README.md` — describe the native suite, optional installation, and one-time guarded migration.
- `docs/00-overview.md` — describe ARS as a native optional plugin rather than wrapper guidance.
- `docs/01-tooling.md` — record both local marketplace plugins and the native source path.
- `docs/02-workflow.md` — replace generic ARS-wrapper wording with `academic-research-suite` where academic workflow support is intended.
- `docs/03-agent-orchestration.md` — explain that RBS/Obsidian remain immediate wrappers while ARS is available only after optional plugin installation.
- `docs/05-security.md` — keep local safety rules authoritative without claiming an ARS wrapper safety layer.
- `docs/12-external-skills-and-plugins.md` — document the split wrapper/native architecture, pin policy, migration stop conditions, and optional install path.
- `docs/13-academic-research-skills.md` — replace the legacy integration guide with the native repository/plugin/suite contract and recovery steps.
- `docs/README.md` — rename the ARS guide description from wrappers to native plugin integration.
- `skill-plugins/README.md` — replace the legacy source listing and explain preserved legacy Git metadata during migration.
- `end-2-end-tests/docs/end-to-end.md` — replace four wrapper smokes with one native discovery/loading smoke and add guarded-migration QA.

### Remove

- `skill-plugins/academic-research-skills` — legacy gitlink and checkout path only; preserve its separate module Git directory and refs in existing clones.
- `.agents/skills/ars-deep-research/SKILL.md`
- `.agents/skills/ars-academic-paper/SKILL.md`
- `.agents/skills/ars-academic-paper-reviewer/SKILL.md`
- `.agents/skills/ars-academic-pipeline/SKILL.md`
- `.agents/skills/ARS_INSTALLED.md`

---

### Task 0: Materialize Unchanged Validation Dependencies in the Isolated Worktree

**Files:**
- Inspect only: `skill-plugins/research-book-skills`
- Inspect only: `skill-plugins/obsidian-skills`

**Interfaces:**
- Consumes: existing superproject gitlinks `6d000633f73f368f352e1bc937300322d40148d0` for RBS and `553ef99aa3306dd23f268e1ba9af752577684f69` for Obsidian Skills.
- Produces: clean, detached local checkouts at those exact existing pins so the unchanged all-integration checker and audit can run; no gitlink, configuration, wrapper, or upstream-file change.

- [ ] **Step 1: Confirm the isolated worktree still records the expected pins**

  ```sh
  rtk git ls-files --stage -- skill-plugins/research-book-skills skill-plugins/obsidian-skills
  rtk git submodule status -- skill-plugins/research-book-skills skill-plugins/obsidian-skills
  ```

  Expected: mode `160000` at the two hashes above. A leading `-` in submodule status means only that the checkout is not materialized. For each checkout without a leading `-`, also run:

  ```sh
  rtk git -C skill-plugins/research-book-skills status --short
  rtk git -C skill-plugins/research-book-skills rev-parse HEAD
  rtk git -C skill-plugins/obsidian-skills status --short
  rtk git -C skill-plugins/obsidian-skills rev-parse HEAD
  ```

  Require an empty status and the recorded gitlink for each initialized checkout. Skip only the two commands for a path whose status had a leading `-`. Any dirty checkout, divergent `HEAD`, or different gitlink is a preservation/scope-drift stop.

- [ ] **Step 2: Initialize only those unchanged gitlinks**

  ```sh
  rtk git submodule sync -- skill-plugins/research-book-skills skill-plugins/obsidian-skills
  rtk git submodule update --init --recursive --checkout -- skill-plugins/research-book-skills skill-plugins/obsidian-skills
  ```

  This may fetch missing Git objects. Do not use `--remote`, fetch a branch tip, run upstream scripts, or edit either checkout.

- [ ] **Step 3: Prove initialization did not change either integration**

  ```sh
  rtk git -C skill-plugins/research-book-skills rev-parse HEAD
  rtk git -C skill-plugins/research-book-skills status --short
  rtk git -C skill-plugins/obsidian-skills rev-parse HEAD
  rtk git -C skill-plugins/obsidian-skills status --short
  rtk git diff HEAD --submodule=short -- skill-plugins/research-book-skills skill-plugins/obsidian-skills
  ```

  Expected: exact recorded hashes, empty nested statuses, and no superproject diff. If materialization cannot reach the existing pins, stop; do not update or substitute either integration.

### Task 1: Lock the Native Integration Contract in Configuration

**Files:**
- Modify: `scripts/lib/project_config.py`
- Modify: `scripts/tests/test_project_tooling.py`
- Modify: `scripts/operations/setup/setup_environment.py`
- Modify: `scripts/tests/test_setup_environment.py`

**Interfaces:**
- Consumes: the approved old gitlink, new repository/pin, plugin root/name, native skill entrypoint, and marketplace values from Global Constraints.
- Produces: `LEGACY_ARS_SOURCE`, `LEGACY_ARS_GITLINK`, `ARS_CODEX_SOURCE`, `ARS_CODEX_REPO`, `ARS_CODEX_PIN`, `ARS_CODEX_PLUGIN_SPEC`, and one source spec keyed by the existing CLI selector `ars`.

- [ ] **Step 1: Write failing configuration tests**

  In `test_external_source_specs_are_canonical`, assert the `ars` spec has label `ARS Codex`, path `skill-plugins/academic-research-skills-codex`, exact HTTPS origin, and a pinned-ref field equal to `925975e933a20893b81681d925a3404e3b7f73b7`. In `test_external_plugin_specs_are_canonical`, assert:

  ```python
  self.assertEqual(ars.marketplace_name, "ars-codex")
  self.assertEqual(
      ars.plugin_path,
      "./skill-plugins/academic-research-skills-codex/plugins/ars-codex",
  )
  self.assertEqual(ars.plugin_root, project_config.ARS_CODEX_SOURCE / "plugins" / "ars-codex")
  self.assertEqual(ars.plugin_json_name, "ars-codex")
  self.assertEqual(ars.skills_root, ars.plugin_root / "skills")
  self.assertEqual(ars.skill_names, ("academic-research-suite",))
  self.assertEqual(ars.category, "Research")
  ```

  Assert `REPO_SCOPED_SKILL_NAMES` contains neither the four old aliases nor `academic-research-suite`, because the native skill belongs to an optionally installed plugin rather than `.agents/skills/`. Add setup tests that both setup and the external installer reject `--ars-ref`.

- [ ] **Step 2: Run the configuration tests and confirm the old contract fails**

  Run:

  ```sh
  rtk python3 -m unittest scripts.tests.test_project_tooling scripts.tests.test_setup_environment
  ```

  Expected: failures mention the legacy path/repository, missing ARS Codex plugin spec, wrapper names still present, and accepted `--ars-ref`.

- [ ] **Step 3: Replace only the ARS configuration model**

  Add `pinned_ref: str | None = None` to `ExternalSourceSpec` and `category: str` to `ExternalPluginSpec`. Define the constants named above, construct `ARS_CODEX_PLUGIN_SPEC`, add it beside the unchanged `RBS_PLUGIN_SPEC` in `EXTERNAL_PLUGIN_SPECS`, and remove `ARS_SKILLS` plus its expansion from `REPO_SCOPED_SKILL_NAMES`. Keep `--skip-ars`; remove `--ars-ref` from both parsers and from `external_args_from_setup_args`.

  Keep the shared marketplace policies as exact constants:

  ```python
  MARKETPLACE_INSTALLATION_POLICY = "AVAILABLE"
  MARKETPLACE_AUTHENTICATION_POLICY = "ON_INSTALL"
  ```

  Leave all RBS and Obsidian constants, lists, wrapper mappings, paths, and source specs semantically unchanged.

- [ ] **Step 4: Re-run the focused configuration tests**

  Run the command from Step 2. Expected: pass.

### Task 2: Add the Guarded One-Time Legacy Checkout Migration

**Files:**
- Create: `scripts/tests/test_ars_codex_migration.py`
- Modify: `scripts/operations/skill_plugins/install_external_skills.py`

**Interfaces:**
- Consumes: `LEGACY_ARS_SOURCE`, `LEGACY_ARS_GITLINK`, `ARS_CODEX_SOURCE`, the installer `Report`, and `args.dry_run`.
- Produces: `migrate_legacy_ars_checkout(args: argparse.Namespace, report: Report) -> bool`; `True` means absent or safely removed, `False` means no ARS Codex initialization may occur.

- [ ] **Step 1: Build a reusable real-Git fixture with unrelated repositories**

  In the new test module, create temporary old and new Git repositories with different root commits. The old repository's recorded commit must be patched into the migration function for the fixture; the new repository must contain:

  ```text
  plugins/ars-codex/.codex-plugin/plugin.json
  plugins/ars-codex/skills/academic-research-suite/SKILL.md
  ```

  Configure an initialized legacy submodule using `git -c protocol.file.allow=always submodule add ...`, then simulate the post-migration superproject metadata with a distinct new submodule path. Retain the legacy checkout's resolved `git rev-parse --absolute-git-dir` path for preservation assertions.

- [ ] **Step 2: Write the required failing migration tests**

  Add exactly these behavior tests:

  1. `test_dirty_legacy_checkout_stops_without_removal_or_new_initialization`: modify a tracked legacy file and add an untracked file; assert `False`, both paths remain, the report names changed files and recovery, and no new-submodule command runs.
  2. `test_clean_divergent_legacy_head_stops_without_removal_or_new_initialization`: commit a local legacy change; assert the report includes actual and expected hashes plus instructions to preserve the commit and return to the recorded gitlink; assert nothing is removed.
  3. `test_initialized_unrelated_legacy_checkout_migrates_without_deleting_legacy_gitdir`: create old and new histories from distinct parentless commits, assert the hashes differ and both parent lists are empty, then leave legacy clean at its recorded commit; assert the checkout path is removed and its resolved module Git directory can still resolve the old commit without rewriting either history or using `set-url`.
  4. `test_linked_worktree_migration_accepts_its_worktree_specific_module_gitdir`: initialize the legacy submodule in a linked worktree, advance that worktree to the migration metadata, and assert the guard accepts Git's worktree-specific module path, removes only the checkout, and preserves the module Git directory.
  5. `test_prepare_migrates_then_initializes_exact_native_pin_and_origin`: begin with the native checkout uninitialized, run the complete ARS preparation path, and assert successful legacy removal is followed by native initialization at the exact independent pin and origin while the legacy Git directory remains.

  Also cover an ignored file and an occupied non-Git legacy path as fail-closed data-loss guards. They are branches of the same migration contract, not wrapper-style smokes.

- [ ] **Step 3: Run the migration tests and confirm the helper is missing**

  ```sh
  rtk python3 -m unittest scripts.tests.test_ars_codex_migration
  ```

  Expected: fail because `migrate_legacy_ars_checkout` does not exist.

- [ ] **Step 4: Implement the fail-closed migration helper**

  The helper must follow this order:

  1. If the legacy path is absent, report no migration needed and return `True`.
  2. If the path exists without a Git checkout, remove it only when it is empty; otherwise report failure with manual recovery and return `False`.
  3. Resolve `git rev-parse --absolute-git-dir`, require that it is outside the checkout, and require exact equality with `git rev-parse --git-path modules/skill-plugins/academic-research-skills` from the current superproject. This uses `.git/modules/` in a primary checkout and the current worktree's `.git/worktrees/<name>/modules/` storage in a linked worktree. If `git rev-parse --show-superproject-working-tree` still reports a path, require it to identify this repository; allow an empty result because Git stops reporting the superproject after the legacy gitlink/stanza has been removed. Any other ownership result fails closed because deleting the path could remove history/refs or strand an unrelated worktree.
  4. Run `git status --porcelain=v1 --untracked-files=all --ignored=matching`. Any tracked, untracked, or ignored-path output is a hard stop. Include the changed paths and tell the user to inspect and preserve them by copy, branch, or commit as applicable before rerunning. Never reset, clean, stash, or discard them.
  5. Read `git rev-parse HEAD`. Any value other than `LEGACY_ARS_GITLINK` is a hard stop. Include both hashes and tell the user to preserve the local commit/ref, then explicitly check out the recorded legacy gitlink before rerunning.
  6. In dry-run mode, report the verified checkout and the exact path that would be removed; change nothing.
  7. Otherwise remove only `LEGACY_ARS_SOURCE`, verify the previously resolved separate Git directory still exists, report that preservation, and return `True`.

  All failure messages must end with the operational consequence: the legacy checkout was not removed and ARS Codex was not initialized.

- [ ] **Step 5: Re-run the migration tests**

  Run the command from Step 3. Expected: all cases pass with the old module Git directory preserved.

### Task 3: Replace the Gitlink Without Rewriting History

**Files:**
- Modify: `.gitmodules`
- Remove: `skill-plugins/academic-research-skills` gitlink
- Add: `skill-plugins/academic-research-skills-codex` gitlink

**Interfaces:**
- Consumes: the Task 2 migration guard and exact source contract from Task 1.
- Produces: a superproject index with one ARS Codex gitlink at `925975e933a20893b81681d925a3404e3b7f73b7` and no legacy ARS gitlink/stanza.

- [ ] **Step 1: Recheck the implementation worktree and any initialized legacy checkout**

  Run:

  ```sh
  rtk git status --short --branch
  rtk git submodule status -- skill-plugins/academic-research-skills
  rtk git -C skill-plugins/academic-research-skills status --short --untracked-files=all --ignored=matching
  rtk git -C skill-plugins/academic-research-skills rev-parse HEAD
  ```

  If the checkout is initialized and either of the last two results is not respectively empty and `81c7300b4066d233914563fc1c3f80512347b33c`, stop and use the recovery behavior in Task 2. If it is uninitialized, do not initialize it merely to delete the old index entry.

- [ ] **Step 2: Remove the old index entry and complete `.gitmodules` stanza**

  Remove only the old gitlink from the index, then delete the full old stanza from `.gitmodules`:

  ```sh
  rtk git rm --cached -- skill-plugins/academic-research-skills
  ```

  Do not use `git submodule set-url`, `git mv`, or a URL edit that retains the old submodule identity. If the safety preflight did not authorize removal of an initialized checkout, stop before this step.

- [ ] **Step 3: Add the new repository at the distinct path and detach it at the reviewed pin**

  ```sh
  rtk git submodule add https://github.com/Imbad0202/academic-research-skills-codex.git skill-plugins/academic-research-skills-codex
  rtk git -C skill-plugins/academic-research-skills-codex checkout --detach 925975e933a20893b81681d925a3404e3b7f73b7
  rtk git add .gitmodules skill-plugins/academic-research-skills-codex
  ```

  This is the only implementation step that needs the public repository. If the commit is unavailable at that origin, stop rather than substituting the latest tag or another commit.

- [ ] **Step 4: Verify exact submodule identity before continuing**

  ```sh
  rtk git config -f .gitmodules --get submodule.skill-plugins/academic-research-skills-codex.url
  rtk git ls-files --stage -- skill-plugins/academic-research-skills-codex
  rtk git -C skill-plugins/academic-research-skills-codex remote get-url origin
  rtk git -C skill-plugins/academic-research-skills-codex rev-parse HEAD
  ```

  Expected: exact HTTPS origin, mode `160000`, exact reviewed pin in both index and checkout, and no legacy stanza/gitlink. Do not run upstream scripts or edit any file inside the submodule.

### Task 4: Replace Wrapper Installation With Native Plugin Exposure

**Files:**
- Modify: `scripts/operations/skill_plugins/install_external_skills.py`
- Modify: `scripts/operations/skill_plugins/update_skill_plugins.py`
- Modify: `.agents/plugins/marketplace.json`
- Modify: `scripts/tests/test_install_external_skills.py`
- Modify: `scripts/tests/test_update_skill_plugins.py`
- Remove: `.agents/skills/ARS_INSTALLED.md`
- Remove: `.agents/skills/ars-deep-research/SKILL.md`
- Remove: `.agents/skills/ars-academic-paper/SKILL.md`
- Remove: `.agents/skills/ars-academic-paper-reviewer/SKILL.md`
- Remove: `.agents/skills/ars-academic-pipeline/SKILL.md`

**Interfaces:**
- Consumes: `migrate_legacy_ars_checkout`, `ARS_CODEX_PLUGIN_SPEC`, and the unchanged RBS/Obsidian installer interfaces.
- Produces: an installer that initializes/validates the native source and reports marketplace availability, with no ARS wrapper or generated ARS install-report output.

- [ ] **Step 1: Repeat the compatibility search before alias deletion**

  ```sh
  rtk git grep -n -E 'ars-(deep-research|academic-paper|academic-paper-reviewer|academic-pipeline)' -- ':!docs/superpowers/plans/2026-09-05-ars-codex-native-migration.md'
  ```

  Classify every result. Continue only if all consumers are the repo-owned wrappers, configuration, tests, generated inventory, and documentation already listed in this plan. A real external/public compatibility declaration is a stop condition and must be reported without retaining aliases automatically.

- [ ] **Step 2: Write failing installer and updater tests**

  Installer tests must assert:

  - ARS selection calls the legacy guard before any native `git submodule` command and aborts native initialization when the guard returns `False`.
  - A valid native plugin is considered ready from only its manifest plus `academic-research-suite/SKILL.md`.
  - `--dry-run --yes --skip-rbs --skip-obsidian-skills` reports the guarded migration/native initialization and marketplace availability but creates no checkout, wrapper, report, or marketplace change.
  - Normal native preparation writes/merges exactly one `ars-codex` marketplace object and never calls `codex plugin add`.
  - Existing non-ARS entries, especially the current `research-book-skills` object, are preserved.
  - Installer behavior creates no ARS wrapper or `ARS_INSTALLED.md` artifact and reports only native marketplace availability; avoid source-text assertions about removed private helper names.

  Updater tests must assert the legacy guard runs before any ARS source initialization and stops all source updates on failure. After a successful guard, the pinned ARS source is synced/initialized and verified at its configured pin without `fetch`, `pull`, `submodule update --remote`, or branch checkout, while the unchanged RBS and Obsidian sources still fast-forward as before.

- [ ] **Step 3: Run focused installer/updater tests and confirm failures**

  ```sh
  rtk python3 -m unittest scripts.tests.test_install_external_skills scripts.tests.test_update_skill_plugins
  ```

  Expected: fail on legacy wrapper/report generation, legacy source path, incomplete marketplace contract, and ARS fast-forward behavior.

- [ ] **Step 4: Make plugin specs drive exact marketplace entries**

  Change `marketplace_entry` to consume an `ExternalPluginSpec` and emit exactly:

  ```json
  {
    "name": "ars-codex",
    "source": {
      "source": "local",
      "path": "./skill-plugins/academic-research-skills-codex/plugins/ars-codex"
    },
    "policy": {
      "installation": "AVAILABLE",
      "authentication": "ON_INSTALL"
    },
    "category": "Research"
  }
  ```

  Preserve the existing RBS object and its `Productivity` category. Merge by plugin name so reruns replace stale `ars-codex` entries with one canonical object while leaving unrelated marketplace objects untouched.

- [ ] **Step 5: Replace the ARS installer branch**

  Remove `ARS_SKILLS`, `ars_skill_path`, `validate_ars`'s four-skill loop, both wrapper functions, wrapper accumulation, `write_ars_install_report`, and all `ARS_INSTALLED.md` output. The new branch must:

  1. honor `--skip-ars` without deleting or installing anything;
  2. call `migrate_legacy_ars_checkout` and stop the ARS branch on `False`;
  3. initialize only the configured native submodule/gitlink;
  4. validate only the plugin manifest and native suite entrypoint needed to decide marketplace readiness;
  5. add/refresh the marketplace entry and report `ars-codex available for optional installation`, never `installed` unless Codex itself reports a user-initiated install outside this script.

  The ARS branch must ignore the generic remote-update path even when `--update` is present: initialize the superproject gitlink, detach at `ARS_CODEX_PIN` if needed, and fail if either the gitlink or checkout cannot equal that pin. The existing `--preserve-skill-plugin-checkouts` behavior remains for update refreshes; the explicit migration preflight may remove only a verified stale legacy checkout and must never alter the new checkout when preservation is requested.

- [ ] **Step 6: Make the updater pin-aware**

  Before updating any selected source, run the same legacy ARS migration guard whenever ARS is selected; a failure stops before native initialization or any other source update. For an `ExternalSourceSpec` with `pinned_ref`, then sync/initialize its gitlink, require `HEAD == pinned_ref`, and report it as pinned. Do not fetch/pull it. Keep the existing fast-forward flow byte-for-byte in behavior for unpinned RBS and Obsidian sources. A future ARS Codex upgrade therefore requires a separately reviewed change to the gitlink and `ARS_CODEX_PIN`; the routine updater cannot silently move it.

- [ ] **Step 7: Delete wrapper/report artifacts and update the tracked marketplace**

  Remove the five files listed above. Write the exact ARS entry beside, not instead of, the existing RBS entry. Do not create `academic-research-suite` or `experiment-agent` under `.agents/skills/`.

- [ ] **Step 8: Re-run focused tests**

  Run the command from Step 3. Expected: pass.

### Task 5: Validate Only the Owned Integration Boundary

**Files:**
- Modify: `scripts/operations/skill_plugins/check_external_skills.py`
- Modify: `scripts/tests/test_check_external_skills.py`

**Interfaces:**
- Consumes: exact source/plugin/marketplace configuration from Task 1 and the prepared new submodule from Tasks 3-4.
- Produces: `check_ars_codex(failures, warnings)` and an opt-in `--native-ars-smoke` that performs one local Codex CLI discovery/load check without a model turn.

- [ ] **Step 1: Write failing static-boundary tests**

  Add tests that reject each of these independently:

  - `.gitmodules` URL differs by any byte from the approved HTTPS URL;
  - index mode is not `160000` or gitlink is not the reviewed pin;
  - initialized checkout origin or `HEAD` differs from the approved values;
  - plugin manifest is absent, invalid JSON, has another `name`, or has `skills` other than `./skills/`;
  - native `skills/academic-research-suite/SKILL.md` is absent;
  - the marketplace has zero, two, or a non-exact `ars-codex` object.

  Do not add fixtures for byte parity, symlinks, nested provenance, or workflow inventories.

- [ ] **Step 2: Write the one failing native Codex smoke test**

  Mock subprocess at the unit layer and require this exact offline sequence under one temporary directory passed as `CODEX_HOME` only to child processes:

  ```text
  codex plugin marketplace add <absolute-project> --json
  codex plugin list --marketplace local-research-workflow-plugins --available --json
  codex plugin add ars-codex@local-research-workflow-plugins --json
  codex -C <absolute-project> debug prompt-input "Use $ars-codex:academic-research-suite. State only the loaded skill name. Do not use tools."
  ```

  Assert the available listing contains `ars-codex` and the add result reports success. For catalog loadability, parse prompt-input JSON, exclude the appended user-prompt item, and require non-user developer context to contain both the exact namespaced skill `ars-codex:academic-research-suite` and an installed path ending in `/plugins/cache/local-research-workflow-plugins/ars-codex/0.1.28/skills/academic-research-suite/SKILL.md`. A bare match on `academic-research-suite` is a failing test because that text is already present in the user prompt. Do not assert full skill-body injection: `prompt-input` registers the catalog entry and defers body loading to the model-driven skill invocation that this offline smoke intentionally does not run. Reject any attempted `codex exec`, network flag, hook bypass, provider, credential, or wrapper invocation. Temporary state is automatically removed; the user's real Codex configuration is untouched.

- [ ] **Step 3: Run checker tests and confirm legacy expectations fail**

  ```sh
  rtk python3 -m unittest scripts.tests.test_check_external_skills
  ```

  Expected: fail because the checker still expects four wrappers/install report and validates only partial marketplace/plugin fields.

- [ ] **Step 4: Implement exact ARS Codex checks**

  Replace `check_ars` with `check_ars_codex`. Use exact string equality for the new `.gitmodules` URL and initialized origin, parse `git ls-files --stage -- <path>` to require a single `160000 <pin> 0\t<path>` entry, reuse general submodule cleanliness/pointer checks, parse the manifest once, and check only its `name`, `skills`, and native suite path. Remove ARS calls to `check_all_source_skills_configured`, `check_skill_wrappers`, and install-report existence.

  Extend marketplace validation for ARS to count matching entries and compare the sole entry to the exact object from Task 4. Keep existing RBS validation behavior intact.

- [ ] **Step 5: Implement the opt-in smoke adapter**

  Add `argparse` support for `--native-ars-smoke`. Run it only after static ARS checks pass. Require `codex` to be present; create an isolated temporary Codex home; run the four commands above with captured output and `check=False`; parse each JSON result; fail with the command and stderr on any nonzero status, missing expected plugin, or absent non-user namespaced catalog entry and installed skill path. `debug prompt-input` is the catalog-load assertion and must not contact a model.

- [ ] **Step 6: Re-run checker tests and the real local smoke**

  ```sh
  rtk python3 -m unittest scripts.tests.test_check_external_skills
  rtk python3 scripts/operations/skill_plugins/check_external_skills.py --native-ars-smoke
  ```

  Expected: both pass; the second command reports one discovered `ars-codex` plugin and one loaded `academic-research-suite` skill, leaves `git status --short` unchanged, and creates no user-level plugin installation.

### Task 6: Update Documentation, Inventories, and Reporting Boundaries

**Files:**
- Modify: `.agents/plugins/README.md`
- Modify: `.agents/skills/README.md`
- Modify: `AGENTS.md`
- Modify: `README.md`
- Modify: `docs/00-overview.md`
- Modify: `docs/01-tooling.md`
- Modify: `docs/02-workflow.md`
- Modify: `docs/03-agent-orchestration.md`
- Modify: `docs/05-security.md`
- Modify: `docs/12-external-skills-and-plugins.md`
- Modify: `docs/13-academic-research-skills.md`
- Modify: `docs/README.md`
- Modify: `skill-plugins/README.md`
- Modify: `end-2-end-tests/docs/end-to-end.md`
- Modify: `scripts/tests/test_docs_consistency.py`
- Modify: `end-2-end-tests/tests/test_end_to_end_doc.py`

**Interfaces:**
- Consumes: implemented native source/plugin/marketplace behavior and Task 2 stop/recovery semantics.
- Produces: one consistent user story: source available at a reviewed pin, marketplace entry tracked, user installation optional, native suite invoked as `$ars-codex:academic-research-suite`, and legacy checkout removal guarded.

- [ ] **Step 1: Write focused documentation/runbook contract tests**

  Preserve existing executable documentation checks and add only contracts whose breakage would make a documented command, path, link, inventory, or license attribution incorrect: the native repository/path, `ars-codex`, `academic-research-suite`, marketplace policies, and the one native smoke command. Assert `docs/12-external-skills-and-plugins.md` binds the native repository to `CC-BY-NC-4.0` and no longer attributes that line to the legacy URL. Review narrative migration/recovery prose manually instead of adding exact-sentence change detectors. The end-to-end test should validate the executable native smoke path without retaining a four-wrapper loop.

- [ ] **Step 2: Run documentation tests and confirm legacy text fails**

  ```sh
  rtk python3 -m unittest scripts.tests.test_docs_consistency
  rtk python3 -m unittest discover -s end-2-end-tests/tests -p 'test_end_to_end_doc.py'
  ```

  Expected: fail on legacy repository/path/wrapper/report assertions.

- [ ] **Step 3: Update routing and inventory prose without weakening local rules**

  In `AGENTS.md`, replace only the ARS-specific routing, repository, location, handling, and report sentence. State that the installed native suite remains subordinate to scaffold source/citation/privacy rules and that plugin installation is optional. Do not touch the EOF `## Sub-Agents` area in any checkout where it exists.

  In `.agents/skills/README.md`, remove ARS from repo-scoped wrappers and reports; explain that `$ars-codex:academic-research-suite` appears only after the user installs `ars-codex`. Keep all RBS and Obsidian wrapper inventory. In `.agents/plugins/README.md`, explain that setup prepares marketplace metadata but does not install either marketplace plugin.

- [ ] **Step 4: Document the one-time migration and recovery precisely**

  In `README.md`, `docs/12-external-skills-and-plugins.md`, `docs/13-academic-research-skills.md`, and `skill-plugins/README.md`, document:

  - old and new repositories are unrelated and use distinct submodule paths;
  - setup/installer first requires an empty `git status --short` in the initialized legacy checkout and exact legacy `HEAD` `81c7300b4066d233914563fc1c3f80512347b33c`;
  - dirty recovery is user-controlled preservation by copy, branch, or commit followed by a rerun;
  - divergent recovery is user-controlled preservation of the local ref followed by an explicit checkout of the recorded legacy commit and rerun;
  - the installer never resets, cleans, stashes, deletes the legacy module Git directory/refs, or rewrites the old repository remote;
  - after successful guarded checkout removal, the new distinct submodule initializes at the reviewed pin;
  - setup adds/refreshes availability metadata only; installation is a later user choice through Codex Plugins.

  Replace the legacy ARS license row in `docs/12-external-skills-and-plugins.md` with the exact native repository and the verified pinned license, `CC-BY-NC-4.0`. Keep `README.md`'s generic external-license caution unchanged unless its adjacent ARS source/wrapper prose must change.

  Do not instruct users to remove `.git/modules/skill-plugins/academic-research-skills`.

- [ ] **Step 5: Update overview, workflow, security, and end-to-end language**

  Make `docs/00-overview.md`, `docs/01-tooling.md`, `docs/02-workflow.md`, `docs/03-agent-orchestration.md`, `docs/05-security.md`, and `docs/README.md` distinguish the optional native ARS plugin from immediate RBS/Obsidian wrappers. In the runbook, replace the four ARS wrapper smokes with the single `--native-ars-smoke` command and its offline expectations. Keep the current RBS wrapper QA unchanged.

- [ ] **Step 6: Re-run documentation tests**

  Run the commands from Step 2. Expected: pass.

### Task 7: Complete Focused and Full Verification

**Files:**
- Inspect only; fix only files already listed when a check exposes a defect.

**Interfaces:**
- Consumes: the complete migration change.
- Produces: evidence that the plan's owned boundary and negative constraints hold on one unchanged tested tree.

- [ ] **Step 1: Run focused regression coverage once**

  ```sh
  rtk python3 -m unittest scripts.tests.test_ars_codex_migration scripts.tests.test_install_external_skills scripts.tests.test_update_skill_plugins scripts.tests.test_check_external_skills scripts.tests.test_project_tooling scripts.tests.test_setup_environment scripts.tests.test_docs_consistency
  rtk python3 -m unittest discover -s end-2-end-tests/tests -p 'test_end_to_end_doc.py'
  ```

  Acceptance: dirty and divergent legacy cases stop without deletion; unrelated histories migrate at distinct paths; marketplace exactness/uniqueness, native discovery/loading, and post-wrapper installer dry-run/report behavior all pass.

- [ ] **Step 2: Prove installer dry-run is non-mutating**

  Record `rtk git status --porcelain=v2` before and after:

  ```sh
  rtk python3 scripts/operations/skill_plugins/install_external_skills.py --dry-run --yes --skip-rbs --skip-obsidian-skills
  ```

  Acceptance: the two status snapshots are identical; output says the native plugin is available for optional installation; it does not claim installed wrappers or an ARS install report.

- [ ] **Step 3: Run the repository-owned boundary checker and native smoke**

  ```sh
  rtk python3 scripts/operations/skill_plugins/check_external_skills.py
  rtk python3 scripts/operations/skill_plugins/check_external_skills.py --native-ars-smoke
  ```

  Acceptance: exact origin/gitlink/manifest/entrypoint/marketplace checks pass; the isolated Codex prompt assembly loads `academic-research-suite`; no model, provider, credential, hook, or network path is exercised.

- [ ] **Step 4: Run the full relevant suite once on the unchanged tree**

  ```sh
  rtk make lint
  rtk make typecheck
  rtk make test
  rtk make audit
  rtk git diff HEAD --check
  ```

  Acceptance: every command exits zero. Do not repeat a successful expensive check unless a relevant input changes.

- [ ] **Step 5: Run negative scope and residue checks**

  ```sh
  rtk git grep -n -E 'ars-(deep-research|academic-paper|academic-paper-reviewer|academic-pipeline)' -- ':!docs/superpowers/plans/2026-09-05-ars-codex-native-migration.md'
  rtk git grep -n 'experiment-agent' -- ':!docs/superpowers/plans/2026-09-05-ars-codex-native-migration.md'
  rtk git diff HEAD --name-only -- notes research bibliography manuscript templates exports skill-plugins/research-book-skills
  rtk git diff HEAD --submodule=short -- skill-plugins/research-book-skills
  ```

  Acceptance: all four commands print nothing. Inspect the changed integration code and confirm it contains no ARS byte-parity, symlink, nested-SHA, or workflow-inventory validator and no `codex plugin add` call outside the isolated smoke adapter.

- [ ] **Step 6: Verify the final Git and submodule state**

  ```sh
  rtk git status --short --branch
  rtk git submodule status
  rtk git ls-files --stage -- skill-plugins/academic-research-skills skill-plugins/academic-research-skills-codex
  rtk git diff HEAD --stat
  ```

  Acceptance: only planned files are changed/removed; the old gitlink is absent; the new gitlink is mode `160000` at `925975e933a20893b81681d925a3404e3b7f73b7`; RBS and Obsidian gitlinks are unchanged; the source checkout's user-owned `AGENTS.md` change is untouched.

- [ ] **Step 7: Iterate one fresh independent read-only reviewer to zero findings**

  Give one reviewer the approved brief, this plan, `rtk git diff HEAD`, and focused test output. Require findings only for material correctness, data-loss, compatibility, scope, or regression gaps. Resolve every verified material finding in the listed files, rerun checks affected by the fix, and return the repaired changed scope to the same reviewer. Repeat until that reviewer returns: `No material improvements recommended.` Do not fan out repeated reviews of an unchanged diff.

- [ ] **Step 8: Deliver the authorized MR**

  After the zero-finding verdict and fresh verification, confirm the final diff contains only planned files, commit with a concise repository-style message, refresh `origin/main`, and ensure the branch still cleanly targets current `main`. Push `feat/ars-codex-native-migration`, open one MR against `main`, and preserve the worktree for review feedback. Report changed files, checks, skipped checks, migration risks, upstream facts not refreshed, the independent review verdict, commit, and MR URL. Do not install the plugin into the user's Codex profile, merge the MR, publish, deploy, or change providers/credentials.

## Migration Stop Conditions and Recovery

| Condition | Required behavior | User-controlled recovery |
| --- | --- | --- |
| Legacy checkout has tracked, untracked, or ignored paths | Stop before removal and before new initialization; print changed paths | Inspect every reported path; copy it elsewhere or preserve it on a legacy branch/commit as applicable, then rerun only when the guarded status command is empty |
| Legacy checkout is clean but `HEAD` is not `81c7300b4066d233914563fc1c3f80512347b33c` | Stop; print actual and expected hashes; leave both paths and Git metadata untouched | Preserve the divergent ref/commit, explicitly return the legacy checkout to the recorded gitlink, then rerun |
| Legacy path is nonempty but not a submodule checkout | Stop rather than deleting ambiguous data | Inspect and relocate the directory manually; rerun when the path is absent or safely empty |
| Legacy `.git` resolves inside the checkout | Stop because recursive removal would delete Git history/refs | Convert or relocate the standalone clone manually; do not let the installer remove it |
| New reviewed commit is unavailable from the exact approved origin | Stop; do not substitute another ref | Resolve upstream availability or approve a different reviewed pin in a separate change |
| Exact manifest/entrypoint/marketplace contract fails | Do not claim plugin availability or run the native smoke | Correct only repository-owned configuration, or select another reviewed upstream pin through a new review |
| A real external consumer of an old alias is found | Stop alias deletion and report the consumer | Obtain an explicit compatibility/migration decision; do not silently retain wrappers |
| Codex CLI lacks the verified plugin/debug command surface | Static checks may pass, but native smoke and loadability claims stop | Update the bounded smoke adapter against current official/local CLI documentation, without adding a model/network fallback |

## Acceptance Criteria

- The superproject contains no legacy ARS gitlink/stanza and contains one distinct ARS Codex gitlink at the exact reviewed commit and origin.
- Existing initialized clones migrate only after both legacy safety predicates pass; legacy module Git storage and refs survive.
- The repository exposes exactly one optional `ars-codex` marketplace entry with the required path, category, and policies; setup never installs it.
- The checker validates only repository-owned origin/gitlink/manifest/entrypoint/marketplace boundaries plus one offline native Codex discovery/load smoke.
- The four ARS aliases, their generator/check/report/inventory behavior, and four wrapper-specific smokes are gone; no `experiment-agent` wrapper exists.
- Installer dry-run/reporting describes guarded migration and native plugin availability without wrappers or `ARS_INSTALLED.md`.
- RBS and Obsidian integration behavior and gitlinks are unchanged; manuscript/research data is untouched.
- Documentation consistently uses `academic-research-suite`, explains the one-time migration and recovery, and preserves the no-hooks/no-providers/no-credentials/no-network/no-automatic-subagents boundaries.
- Focused tests, native smoke, full unit suite, lint, typecheck, audit, `git diff --check`, residue checks, and independent review complete successfully.
- Commit, push, and MR/PR creation occur only under the current explicit delivery authorization; no plugin installation in the user's profile, merge, deployment, publication, provider, or credential action occurs.

## Necessity and Duplication Audit

- Distinct submodule path: necessary because old/new histories are unrelated; an in-place remote swap is explicitly unsafe.
- Legacy checkout guard: necessary to prevent loss of dirty work or divergent local commits in initialized clones.
- Immutable pin and exact origin/gitlink checks: necessary to bind the reviewed upstream snapshot.
- Manifest, entrypoint, and exact marketplace checks: necessary because those are the local integration surfaces this repository owns.
- One native Codex smoke: necessary to prove the marketplace/plugin/skill path is actually discoverable and loadable; prompt assembly avoids a model or network dependency.
- Installer/updater changes: necessary to stop regenerating wrappers/reports and to prevent routine updates from silently moving the reviewed pin.
- Documentation/inventory changes: necessary to remove obsolete invocation names and give existing clones actionable migration recovery.
- New migration test module: necessary because dirty, divergent, and unrelated-history cases require real Git behavior not represented by existing mock-only tests.
- No wrapper, alias, compatibility shim, `experiment-agent`, wrapper smoke, upstream byte-parity/symlink/provenance/workflow validator, full runtime, hook, resolver, provider, credential, or automatic subagent remains in scope. Each would duplicate upstream ownership, reintroduce the removed layer, or exceed the approved integration boundary.
