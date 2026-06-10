# Production Release QA Runbook

Use this runbook to test a release candidate from a fresh clone through setup, script verification, seeded content checks, skill usage, manuscript gates, rendering, and release decision. Run destructive, mutating, networked, and intentionally failing checks only in a disposable QA clone.

The synthetic files under `end-2-end-tests/fixtures/release_seed/` and the tool `end-2-end-tests/tools/seed_release_qa.py` exist only to exercise repository QA paths. They are not scholarly evidence, not source support, and not releasable manuscript content.

## Release Standard

A production release is ready only when:

- the repository can be cloned with submodules from the intended remote, branch, tag, or commit
- setup completes or reports only explicitly accepted skipped optional tools
- required local integrations are installed and checked
- every Make target and direct script has positive coverage
- every release gate passes without hiding evidence, citation, placeholder, link, vendor, or skill-usage problems
- required render targets are generated and manually inspected
- all skipped checks, warnings, and residual scholarly risks are recorded

Warnings are not automatic failures, but each warning needs an explicit release decision. Failures from `make release-audit` are release blockers.

## Prerequisites

Required for core scaffold QA:

- Git
- Python 3.11 or newer
- `curl`
- `unzip`
- `pre-commit` for local hook QA
- Codex CLI installed and logged in for local agent workflows

Optional until the matching workflow is tested:

- Obsidian for the recommended project-root vault workflow
- Codex Panel, installed by default setup unless `--skip-obsidian-panel` is used
- Zotero Integration and Pandoc Reference List, installed by default setup unless `--skip-obsidian-research-plugins` is used
- Node and npm, used by setup only if Codex CLI needs installation through npm
- Quarto, Pandoc, and a TeX engine such as `lualatex` for manuscript rendering
- Zotero and Better BibTeX for citation-library verification
- `end-2-end-tests/docs/qa-environment-requirements.md` followed when API-based Zotero checks are in scope

Install TinyTeX for PDF rendering when TeX is not already available by running `quarto install tinytex --update-path`:

```sh
quarto install tinytex --update-path
```

Open a new shell after installation. On macOS, if TinyTeX is installed but TeX commands such as `lualatex --version` and `bibtex --version` are still unavailable, add `$HOME/Library/TinyTeX/bin/universal-darwin` to `PATH`.

For a persistent macOS setup, add the TinyTeX path to the shell startup file used by the terminal, then open a new shell before rerunning render checks.

Non-interactive automation may not source interactive shell startup files. If render QA still cannot find TeX after the profile update, prefix render commands explicitly:

```sh
PATH="$HOME/Library/TinyTeX/bin/universal-darwin:$PATH" make render-pdf
```

Record versions before setup:

```sh
git --version
python3 --version
curl --version
unzip -v
pre-commit --version
codex --version
quarto --version
pandoc --version
lualatex --version
bibtex --version
```

Expected result:

- Required tools print versions.
- Optional render tools may be missing before render QA, but missing Quarto, Pandoc, or TeX blocks export QA.

## Fresh Clone QA

Start from a parent directory outside any existing checkout:

```sh
git clone --recurse-submodules <repo-url> release-qa
cd release-qa
git fetch --all --prune
git checkout <intended-branch-or-tag>
git submodule update --init --recursive
```

Record the tested state:

```sh
git status --short --branch
git submodule status --recursive
git log -1 --oneline
```

Expected result:

- The checkout is on the intended branch, tag, or commit.
- The working tree is clean before setup.
- Submodules are initialized and do not show `+`, `-`, or `U` status markers.
- The commit hash is recorded in the QA evidence log.

## Setup QA

Run setup dry first:

```sh
bash setup.sh --dry-run
python3 scripts/operations/setup/setup_environment.py --dry-run
python3 scripts/operations/setup/setup_environment.py --dry-run --skip-external-skills
python3 scripts/operations/setup/setup_environment.py --dry-run --skip-obsidian-panel
python3 scripts/operations/setup/setup_environment.py --dry-run --register-obsidian-vault
```

Expected result:

- Dry runs exit 0.
- No files, packages, repositories, plugins, or vendor pointers are changed.
- Recommended checks include `bash scripts/operations/health/doctor.sh`, external skill check, Obsidian check, Obsidian artifact check, citation check, and placeholder check.
- When `--skip-obsidian-panel` is used, setup reports Codex Panel setup as skipped and does not require the Codex Panel check until that coverage is in scope.
- When `--skip-obsidian-research-plugins` is used, setup reports Zotero/Pandoc Obsidian plugin setup as skipped and does not require the research plugin check until that coverage is in scope.
- When `--register-obsidian-vault` is used with `--dry-run`, setup reports that it would update Obsidian's app-level vault registry without writing user app state.
- External skills are initialized and local wrappers are refreshed unless `--skip-external-skills` is passed.

Run setup in the disposable clone:

```sh
bash setup.sh
python3 scripts/operations/obsidian/check_obsidian_panel.py
python3 scripts/operations/obsidian/obsidian_research_plugins.py check
python3 scripts/operations/obsidian/check_obsidian_artifacts.py
```

When GUI app checks include direct `obsidian://open?path=...` launches, opt in to vault registration during setup:

```sh
bash setup.sh --register-obsidian-vault
```

Expected result:

- Required tools are found or reported with clear manual steps.
- `.agents/skills/` exists and local skill front matter validates.
- ARS, RBS, guarded Subagent Orchestrator, and Obsidian Skills wrappers are present under `.agents/skills/`.
- The project root is treated as the Obsidian vault root.
- `.obsidian/plugins/codex-panel/` is installed or an existing plugin folder is reported as skipped unless `--force` was intentionally used.
- Setup writes `.obsidian/community-plugins.json` so `codex-panel` is listed as enabled.
- Setup writes `.obsidian/community-plugins.json` so `obsidian-zotero-desktop-connector` and `obsidian-pandoc-reference-list` are listed as enabled.
- Setup writes `.obsidian/plugins/codex-panel/data.json` with an absolute executable `codexPath` when one is available.
- With `--register-obsidian-vault`, setup preserves existing Obsidian vault entries and adds the project root to Obsidian's app-level vault registry if it is not already present.
- Without `--register-obsidian-vault`, a first-time Obsidian GUI check may need the manual `Open folder as vault` flow before direct Obsidian URLs work.
- Existing Obsidian workspace files are not overwritten.
- Invalid `community-plugins.json` content fails setup instead of being overwritten.

If system package installation is managed outside setup, use:

```sh
bash setup.sh --skip-packages
```

Expected result:

- Package checks are explicitly skipped.
- Later `make doctor` still verifies required commands.

## Project Start Script QA

Run the guided initializer and fill every prompt in a disposable QA clone before claiming the scaffold can move from uninitialized manuscript defaults to an initialized project state. Use synthetic QA answers only. Do not use real private subject matter, source metadata, page numbers, quotations, or claims in this smoke test.

First inspect the prompt flow:

```sh
python3 scripts/start_project.py --help
make start-project
```

Expected interactive behavior:

- `make start-project` runs `python3 scripts/start_project.py`.
- The initializer prompts for working title, author/display name, project type, research question, scope, output formats, chapter names, citation setup, Obsidian use, agent use, audit, and render choices.
- Fill every prompt with synthetic QA values, using `unknown`, `undecided`, or `decide later` only where unresolved decisions are intentionally being tested.
- Stop before continuing with other mutating QA if the prompt flow skips required questions, records private data, or silently invents bibliography metadata.

For reproducible QA, record equivalent synthetic answers in `.qa-start-project.yml` and run the answers-file path:

```yaml
working_title: QA Start Script Manuscript
subtitle: Synthetic Workflow Check
author_name: QA Operator
project_slug: qa-start-script-manuscript
project_type: book
central_research_question: How does the scaffold initialize a project without inventing evidence?
working_thesis: unknown yet
primary_audience: Scaffold maintainers
secondary_audience: Future project authors
fields_disciplines:
  - workflow QA
theories_to_engage:
  - unknown yet
contested_theories:
  - unknown yet
scope_included:
  - start script behavior
scope_excluded:
  - real scholarship
main_uncertainties:
  - citation library state
initial_research_tasks:
  - verify generated project files
output_formats:
  - html
chapter_names:
  - Introduction
  - Evidence Plan
citation_style: undecided
target_venue: undecided
bibliography_path: bibliography/references.bib
better_bibtex_auto_export: not sure
use_obsidian: yes
use_codex_agents: yes
strict_placeholder_detection: yes
run_audit_after_initialization: no
render_after_initialization: no
```

Run `python3 scripts/start_project.py --dry-run --answers .qa-start-project.yml --non-interactive --skip-render` first, then run `python3 scripts/start_project.py --answers .qa-start-project.yml --non-interactive --skip-render`. After initialization, verify the release manuscript with `python3 scripts/research-writing/check_manuscript_readiness.py`.

```sh
python3 scripts/start_project.py --dry-run --answers .qa-start-project.yml --non-interactive --skip-render
python3 scripts/start_project.py --answers .qa-start-project.yml --non-interactive --skip-render
python3 scripts/research-writing/check_manuscript_readiness.py
python3 scripts/research-writing/check_placeholders.py .
git status --short
git diff -- manuscript/_quarto.yml manuscript/index.qmd manuscript/chapters notes/00-inbox/project-charter.md project-start.yml
```

Expected result:

- Dry run shows planned changes without writing files.
- The real run writes `project-start.yml`, `manuscript/_quarto.yml`, `manuscript/index.qmd`, front/back matter files, project chapter stubs, and `notes/00-inbox/project-charter.md`.
- Scaffold manuscript identity is removed from release manuscript files.
- Manuscript readiness exits 0 after initialization.
- The placeholder command may exit nonzero while synthetic unresolved decisions remain; limit findings to those intentional unresolved decisions when strict placeholder detection is enabled.
- The diff contains only synthetic QA initialization content and no invented citations, page numbers, quotations, source metadata, or final claims.
- If later QA needs a clean uninitialized scaffold, create a fresh disposable clone or intentionally restore the checkout before continuing.

## Scaffold App Usability QA

Confirm that every required or recommended app can open and be used against the scaffolded project. Command-line checks alone are not enough for GUI QA.

Codex Panel is installed by default setup unless `--skip-obsidian-panel` is used. Zotero Integration and Pandoc Reference List are installed by default setup unless `--skip-obsidian-research-plugins` is used. If a skip flag was used, skip only the matching checks below and record that the skipped coverage is not claimed for the run.

Obsidian opens the scaffold project root as a vault:

1. If setup used `--register-obsidian-vault`, open the project with `obsidian://open?path=<release-qa-clone-root>` or from Obsidian's vault list.
2. If setup did not use `--register-obsidian-vault`, open Obsidian and choose the release QA clone root with `Open folder as vault`.
3. Confirm `AGENTS.md`, `notes/`, `research/`, `manuscript/`, and `end-2-end-tests/docs/end-to-end.md` are visible.
4. Open a note from `notes/` and a manuscript file from `manuscript/`.

Expected result:

- The scaffold project root opens directly as the vault.
- The direct URL path does not report "vault not found" when the registry flag was used.
- Obsidian does not require a nested vault folder.
- Existing project files are readable without moving or copying them.

Codex Panel can run a bounded read-only prompt:

1. Open Settings -> Community plugins.
2. Click Reload plugins if Obsidian initially shows zero plugins or Codex Panel is not visible.
3. Confirm Codex Panel is installed and enabled.
4. Run the command palette action `Codex Panel: Open panel`.

Safe smoke prompt:

```text
Read AGENTS.md and summarize the project rules. Do not edit anything.
```

Skill discovery smoke prompt:

```text
Read AGENTS.md and list the repo-scoped skills available from .agents/skills. Then use $obsidian-research-markdown to inspect notes/README.md and explain which Obsidian Markdown rules apply. Do not edit files.
```

Expected result:

- The Codex Panel plugin is enabled for the project-root vault.
- `.obsidian/community-plugins.json` lists `codex-panel` as enabled.
- `.obsidian/plugins/codex-panel/data.json` points to an absolute Codex executable path.
- Codex approval prompts remain governed by Codex CLI and `codex app-server`.
- The read-only prompt can inspect scaffold files.
- Codex Panel can discover repo-scoped skills from `.agents/skills` without manual repo marketplace plugin installation.
- The `$obsidian-research-markdown` wrapper can be invoked from Codex Panel.
- File writes and command execution remain approval-gated.
- `git status --short` shows no unexpected source changes after the smoke prompt.

Obsidian research plugins are installed and enabled:

1. Open Settings -> Community plugins.
2. Confirm Zotero Integration and Pandoc Reference List are installed and enabled.
3. Run `make check-obsidian-research-plugins` from the disposable QA clone.
4. Open a manuscript or source note with a known citekey when the seed fixture or verified bibliography is available.
5. Configure Pandoc Reference List with `bibliography/references.bib`.
6. Run the command palette action `Pandoc Reference List: Show reference list`.

Expected result:

- `.obsidian/community-plugins.json` lists `obsidian-zotero-desktop-connector` and `obsidian-pandoc-reference-list`.
- The plugin folders contain `manifest.json`, `main.js`, and `styles.css`.
- The manifests use the expected plugin IDs.
- Pandoc Reference List can read `bibliography/references.bib` when Pandoc is available.
- Missing Pandoc is recorded as a live-preview limitation, not as a failed install.
- No plugin settings containing local Zotero database paths, API keys, or PDF paths are committed.

Codex CLI runs from the scaffold project root:

```sh
codex --version
pwd
git status --short --branch
```

Expected result:

- `codex --version` exits 0.
- The current directory is the release QA clone root.
- Codex can use the scaffolded project rules and local `.agents/skills/` files.

Zotero and Better BibTeX can be used with `bibliography/references.bib`:

1. Open Zotero.
2. Download the latest Better BibTeX `.xpi` when the add-on is not installed.
3. In Zotero, use `Tools > Plugins`, select `Plugins`, open the gear menu, and choose `Install Plugin From File...`.
4. Restart Zotero and confirm Better BibTeX is installed and enabled when citation-library QA is in scope.
5. Identify at least one verified Zotero record or collection before claiming export QA.
6. When API-based citation-library checks are in scope, follow `end-2-end-tests/docs/qa-environment-requirements.md`.
7. Before refreshing `bibliography/references.bib`, confirm the disposable QA clone is clean with `git status --short`.
8. Export or refresh BibTeX into `bibliography/references.bib` only from verified library records.
9. If no verified library records are available in the QA environment, record Better BibTeX availability and skip bibliography refresh with release impact instead of creating or exporting unverified records.
10. Inspect `git diff -- bibliography/references.bib`.
11. In Obsidian, use Zotero Integration to insert a Pandoc-style citation for the verified record into a disposable note or seeded manuscript fixture.
12. Confirm the inserted form is `[@citekey]`, `[-@citekey]`, or `[@first; @second]`.
13. Use Pandoc Reference List to preview the inserted citekey.
14. Run `python3 scripts/research-writing/check_citations.py --include-notes --require-citations`.

Expected result:

- Zotero opens the relevant library.
- Better BibTeX can provide stable citekeys.
- `bibliography/references.bib` remains the repository citation source of truth.
- Export QA is not skipped in normal citation-library QA; it is skipped only when no verified Zotero record is available and export coverage is explicitly not claimed.
- API-based Zotero checks are claimed only after `end-2-end-tests/docs/qa-environment-requirements.md` passes.
- `git diff -- bibliography/references.bib` shows only expected verified Zotero or Better BibTeX changes.
- Zotero Integration inserts a Pandoc-style citekey that exists in `bibliography/references.bib`.
- Pandoc Reference List displays the reference for the inserted citekey when Pandoc is available.
- A skipped bibliography refresh means only Zotero/Better BibTeX availability was checked, not end-to-end library export.
- No generated or unverified bibliographic metadata is accepted as evidence.

Quarto, Pandoc, and the configured TeX engine can render from the scaffold when export or render QA is in scope:

```sh
quarto --version
pandoc --version
lualatex --version
bibtex --version
make render-html
make render-docx
make render-pdf
```

Expected result:

- Quarto and Pandoc are available to the scaffold.
- The configured TeX engine is available before PDF QA.
- Rendered outputs are generated from `manuscript/` into `exports/`.
- Missing render tools are recorded as skipped or blocking according to the release target.
- If `lualatex` or `bibtex` is missing after TinyTeX install, verify `$HOME/Library/TinyTeX/bin/universal-darwin` is on `PATH` on macOS.

## Make Target QA Matrix

| Target | Purpose | Pass condition |
| --- | --- | --- |
| `make help` | Lists available targets | Includes setup, check, render, audit, and release-audit targets |
| `make start-project` | Runs the guided project initializer | Prints preflight status, resumes from `project-start.yml` when present, and preserves existing non-scaffold content unless force is intentionally used |
| `make doctor` | Checks local tools, files, folders, and git tracking | Exits 0 and has no `FAIL` lines |
| `make render` | Renders all enabled Quarto formats | Exits 0 and all required outputs are present |
| `make render-html` | Renders HTML only | Exits 0 and generated HTML is present under `exports/` |
| `make render-pdf` | Renders PDF only | Exits 0 and generated PDF is present under `exports/` |
| `make render-docx` | Renders DOCX only | Exits 0 and generated DOCX is present under `exports/` |
| `make test` | Runs script tests and root QA tests | Exits 0 with all tests passing |
| `make lint` | Compile-checks Python scripts and QA tools | Exits 0 |
| `make check-placeholders` | Scans Markdown and QMD files for unresolved markers | Exits 0 and reports no unresolved markers |
| `make check-citations` | Checks manuscript citekeys against `bibliography/references.bib` | Exits 0 and missing citekey count is zero |
| `make check-citations-strict` | Checks manuscript, notes, and research citekeys and requires at least one citation | Exits 0 for production release |
| `make check-links` | Checks wiki-style internal links | Exits 0 and reports no broken or ambiguous links |
| `make check-external-references` | Checks external URLs and DOI resolution without archive lookup | Run only when network QA is in scope; warnings are reviewed without blocking ordinary writing |
| `make external-reference-report` | Writes `reports/external-reference-check.json` for external-reference audit review | Run only when a generated report is useful; archive lookup still requires an explicit script flag |
| `make check-manuscript-readiness` | Detects remaining scaffold manuscript entries | Exits 0 for production release |
| `make check-external-skills` | Validates vendor submodules, wrappers, plugins, marketplace, and old repo references | Exits 0 with zero failures |
| `make install-external-skills` | Vendors external skills and updates marketplace | Use only in disposable QA or intentional integration updates; verify resulting diff |
| `make install-subagent-orchestrator` | Refreshes only the optional guarded subagent wrappers and marketplace path | Keeps plugin exposure optional and does not activate global hooks, global config, or global agents |
| `make update-skills-vendors` | Fast-forwards vendored skill repositories and refreshes integrations | Use only when the release includes vendor updates |
| `make check-obsidian-panel` | Verifies Codex Panel install, configured Codex CLI path, and app-server support | Exits 0 after plugin files, settings, and Codex CLI are present |
| `make check-obsidian-research-plugins` | Verifies Zotero Integration and Pandoc Reference List plugin installs | Exits 0 after plugin files, manifests, and enablement are present |
| `make check-obsidian-artifacts` | Validates project-local `.base` and `.canvas` artifacts | Exits 0 |
| `make install-obsidian-panel` | Installs Codex Panel plugin | Use only in disposable QA or intentional local setup |
| `make install-obsidian-research-plugins` | Installs Zotero Integration and Pandoc Reference List plugins | Use only in disposable QA or intentional local setup |
| `make install-hooks` | Installs the configured local pre-commit hook | Use after `pre-commit` is installed; hook installation does not run release-only checks |
| `make precommit-run` | Runs default pre-commit hooks across all files | Exits 0 after file hygiene, citation, placeholder, link, and Python compile checks pass |
| `make audit` | Runs normal scaffold health checks | Exits 0 |
| `make release-audit` | Runs strict pre-release manuscript checks | Exits 0 and all blockers are resolved |
| `make ci` | Runs hosted CI-safe lint and normal scaffold audit checks | Exits 0 on every supported Python version for a fresh scaffold |

Standard command sequence:

```sh
make doctor
make lint
make test
make precommit-run
make audit
make release-audit
```

Expected result:

- `make doctor`, `make lint`, `make test`, and `make audit` exit 0 for a fresh scaffold.
- A fresh uninitialized scaffold fails manuscript readiness and `make release-audit` until generic manuscript identity is replaced by `make start-project` or project-specific manuscript files.
- `make release-audit` exits 0 for an initialized production manuscript after all blockers are resolved.
- `make ci` is the hosted-CI aggregate and can be used as the local one-command equivalent of lint plus the normal scaffold audit. It intentionally does not replace `make release-audit`.
- A production manuscript still needs real project material, verified source notes, and manual scholarly QA even when scaffold release gates pass.

## Seeded Content Fixture QA

The reusable release seed covers:

- `bibliography/references.bib`
- `manuscript/_quarto.yml`
- `manuscript/index.qmd`
- `manuscript/chapters/qa-seed-chapter.qmd`
- `notes/01-source-notes/qa-seed-source.md`
- `notes/02-literature-maps/qa-seed-literature-map.md`
- `notes/03-concept-notes/qa-seed-concept.md`
- `notes/04-claim-ledger/qa-seed-claim.md`
- `notes/07-chapter-briefs/qa-seed-brief.md`
- `notes/08-audits/qa-seed-release-audit.md`
- `research/extraction-tables/qa-seed-extraction-table.md`
- `research/search-logs/qa-seed-search-log.md`
- `research/source-matrices/qa-seed-source-matrix.md`

Check seed status before applying:

```sh
python3 end-2-end-tests/tools/seed_release_qa.py status
python3 end-2-end-tests/tools/seed_release_qa.py apply --dry-run
```

The disposable QA clone must be clean before applying the seed:

```sh
git status --short
```

Expected result:

- `git status --short` prints no tracked or untracked project changes.
- Do not run `python3 end-2-end-tests/tools/seed_release_qa.py apply` from an authoring checkout.
- If the clone is not clean, stop and create a fresh disposable QA clone before continuing.

Apply the seed in a disposable QA clone:

```sh
python3 end-2-end-tests/tools/seed_release_qa.py apply
```

Run content gates against the seed:

```sh
python3 scripts/research-writing/check_placeholders.py .
python3 scripts/research-writing/check_citations.py
python3 scripts/research-writing/check_citations.py --include-notes --require-citations
python3 scripts/research-writing/check_broken_internal_links.py
python3 scripts/research-writing/check_manuscript_readiness.py
make audit
make release-audit
```

Expected result:

- Placeholder check exits 0.
- Citation checks exit 0 and find `qaSeed2026`.
- Strict citation mode exits 0 because manuscript, notes, and research fixture files contain a valid citation.
- Internal-link check exits 0 because all seeded wiki links resolve.
- Manuscript-readiness check exits 0 because the seeded Quarto config has a real title and no sample scaffold chapter or appendix entries.

Clean the seed before returning to normal release QA:

```sh
python3 end-2-end-tests/tools/seed_release_qa.py clean --dry-run
python3 end-2-end-tests/tools/seed_release_qa.py clean
git status --short
```

Expected result:

- Seed-only files are removed.
- Tracked scaffold files are restored only when their content still matches the seed.
- Changed seed files are left for manual review instead of being removed silently.

## Script-by-Script QA

Entry points and support modules:

- `scripts/start_project.py`
- `scripts/research-writing/check_broken_internal_links.py`
- `scripts/research-writing/check_citations.py`
- `scripts/research-writing/check_external_references.py`
- `scripts/operations/vendors/check_external_skills.py`
- `scripts/research-writing/check_manuscript_readiness.py`
- `scripts/operations/obsidian/check_obsidian_artifacts.py`
- `scripts/operations/obsidian/check_obsidian_panel.py`
- `scripts/operations/obsidian/obsidian_research_plugins.py`
- `scripts/research-writing/check_placeholders.py`
- `scripts/operations/health/doctor.py`
- `scripts/operations/health/doctor.sh`
- `scripts/operations/setup/environment_checks.py`
- `scripts/lib/git_utils.py`
- `scripts/lib/import_paths.py`
- `scripts/operations/vendors/install_external_skills.py`
- `scripts/operations/obsidian/install_obsidian_panel.sh`
- `scripts/operations/obsidian/install_obsidian_research_plugins.sh`
- `scripts/research-writing/new_from_template.py`
- `scripts/operations/obsidian/obsidian_agent.py`
- `scripts/lib/project_config.py`
- `scripts/research-writing/render.sh`
- `scripts/research-writing/render_manuscript.py`
- `scripts/lib/script_env.sh`
- `scripts/lib/script_utils.py`
- `scripts/operations/setup/setup_environment.py`
- `scripts/operations/vendors/update-skills-vendors.sh`
- `scripts/operations/vendors/update_skills_vendors.py`

Run support coverage:

```sh
python3 -m unittest discover scripts/tests
python3 -m unittest discover end-2-end-tests/tests
python3 -m compileall -q scripts end-2-end-tests/tools end-2-end-tests/tests
```

Expected result:

- Unit tests cover package detection, Obsidian install safety, git helpers, script utilities, render preflights, external skill checks, setup behavior, template creation, seeded QA, docs consistency, and direct QA runbook coverage.
- Compile check exits 0.

Targeted script checks:

```sh
python3 scripts/start_project.py --help
bash scripts/operations/health/doctor.sh
python3 scripts/operations/health/doctor.py
python3 scripts/operations/obsidian/check_obsidian_artifacts.py
python3 scripts/operations/obsidian/check_obsidian_panel.py
python3 scripts/operations/obsidian/obsidian_research_plugins.py check
python3 scripts/operations/obsidian/obsidian_research_plugins.py install --dry-run
python3 scripts/operations/vendors/install_external_skills.py --dry-run --yes
python3 scripts/operations/vendors/check_external_skills.py
python3 scripts/research-writing/check_placeholders.py .
python3 scripts/research-writing/check_citations.py
python3 scripts/research-writing/check_citations.py --include-notes --require-citations
python3 scripts/research-writing/check_citations.py --show-unused
python3 scripts/research-writing/check_broken_internal_links.py
python3 scripts/research-writing/check_external_references.py --help
python3 scripts/research-writing/check_manuscript_readiness.py
python3 scripts/research-writing/new_from_template.py --help
python3 scripts/research-writing/render_manuscript.py --to html
bash scripts/research-writing/render.sh --to html
```

Expected result:

- Non-mutating checks exit 0 where prerequisites and initialized manuscript state exist; manuscript readiness exits nonzero on a fresh uninitialized scaffold.
- Missing optional render tooling is reported as a tooling blocker, not a manuscript failure.
- Vendor checks fail if submodule pointers differ from the parent index, are uninitialized, conflicted, dirty, or from an unexpected origin.

Template placeholder diagnostic:

```sh
python3 scripts/research-writing/check_placeholders.py --include-templates templates
```

Expected result:

- `python3 scripts/research-writing/check_placeholders.py --include-templates templates` is expected to exit nonzero while templates contain intentional template placeholders.
- Record the count as template fixture coverage, not a release blocker, unless placeholders appear outside `templates/` or inside generated project content.

## Vendor Update QA

Only run this section when the release intentionally updates vendored skill repositories.

```sh
bash scripts/operations/vendors/update-skills-vendors.sh --skip-checks
python3 scripts/operations/vendors/check_external_skills.py
bash scripts/operations/health/doctor.sh
git status --short --branch
git submodule status --recursive
```

Expected result:

- The updater fast-forwards only selected vendor submodules.
- Local skill wrappers, marketplace metadata, and install reports are refreshed.
- Post-update checks pass.
- Submodule pointer changes are visible for review.
- No unexpected files are modified.

## Negative fixture checks

Run these only in a disposable QA clone and clean up immediately afterward.

Placeholder failure:

```sh
mkdir -p .qa-fixtures
printf 'Unresolved marker: {{MISSING_VALUE}}\n' > .qa-fixtures/placeholder.md
python3 scripts/research-writing/check_placeholders.py .qa-fixtures
rm -f .qa-fixtures/placeholder.md
rmdir .qa-fixtures 2>/dev/null || true
```

Citation failure:

```sh
printf '\nMissing citation test [-@qaMissingCitationKey].\n' >> manuscript/index.qmd
python3 scripts/research-writing/check_citations.py
git restore manuscript/index.qmd
```

Internal-link failure:

```sh
mkdir -p notes/00-inbox
printf 'Broken link [[qa-missing-target]]\n' > notes/00-inbox/qa-link-fixture.md
python3 scripts/research-writing/check_broken_internal_links.py
rm -f notes/00-inbox/qa-link-fixture.md
```

Template overwrite and invalid replacement failures:

```sh
mkdir -p .qa-fixtures
printf 'existing\n' > .qa-fixtures/existing.md
python3 scripts/research-writing/new_from_template.py templates/source-note-template.md .qa-fixtures/existing.md
python3 scripts/research-writing/new_from_template.py templates/source-note-template.md .qa-fixtures/bad.md --set invalid
rm -f .qa-fixtures/existing.md
rmdir .qa-fixtures 2>/dev/null || true
```

Expected result:

- Each checker exits nonzero while the bad fixture exists.
- Output identifies the failing file, marker, link, citekey, or argument.
- Cleanup returns the disposable clone to an intentional state.

## Codex Panel QA

Run dry and direct checks:

```sh
bash scripts/operations/obsidian/install_obsidian_panel.sh --dry-run
python3 scripts/operations/obsidian/obsidian_agent.py --dry-run
python3 scripts/operations/obsidian/obsidian_agent.py --dry-run --register-obsidian-vault
python3 scripts/operations/obsidian/check_obsidian_panel.py
```

When testing a real plugin install, use the published Codex Panel release assets:

```sh
python3 scripts/operations/setup/setup_environment.py --force
python3 scripts/operations/obsidian/check_obsidian_panel.py
```

Expected result:

- Dry run does not modify files.
- `--register-obsidian-vault` is opt-in and dry-run safe because it reports the app registry write without making it.
- The plugin folder `.obsidian/plugins/codex-panel/` contains `manifest.json`, `main.js`, and `styles.css`.
- The manifest ID is `codex-panel`.
- `.obsidian/community-plugins.json` is created or updated so `codex-panel` is enabled.
- Zotero Integration and Pandoc Reference List may also be listed because they are installed by default setup for the citation workflow.
- `.obsidian/plugins/codex-panel/data.json` contains an absolute executable `codexPath`.
- `codex app-server --help` exits 0 through that configured path.
- Invalid `community-plugins.json` content fails the install and is not overwritten.
- Missing release assets fail the install.
- GitHub source zipballs are not accepted as plugin release packages.
- Existing Obsidian workspace files are not overwritten.
- Obsidian's app-level vault registry is modified only when `--register-obsidian-vault` is explicitly passed.

Safe usage prompt:

```text
Read AGENTS.md and summarize the project rules. Do not edit anything.
```

Expected result:

- The plugin performs bounded read-only work.
- Any file-write or command action still requires approval.
- `git status --short` shows no unexpected source changes.

## Obsidian Research Plugin QA

Run dry and direct checks:

```sh
bash scripts/operations/obsidian/install_obsidian_research_plugins.sh --dry-run
python3 scripts/operations/obsidian/obsidian_research_plugins.py install --dry-run
python3 scripts/operations/obsidian/obsidian_research_plugins.py check
```

When testing a real plugin install, use the published release assets:

```sh
python3 scripts/operations/setup/setup_environment.py --force
python3 scripts/operations/obsidian/obsidian_research_plugins.py check
```

Expected result:

- Dry run does not modify files.
- `.obsidian/plugins/obsidian-zotero-desktop-connector/` contains `manifest.json`, `main.js`, and `styles.css`.
- `.obsidian/plugins/obsidian-pandoc-reference-list/` contains `manifest.json`, `main.js`, and `styles.css`.
- The manifests use `obsidian-zotero-desktop-connector` and `obsidian-pandoc-reference-list`.
- `.obsidian/community-plugins.json` enables both plugin IDs.
- Missing release assets fail the install.
- Existing malformed research plugin folders fail without `--force` and are not enabled as successful installs.
- `--force` replaces an existing malformed research plugin folder with validated release assets.
- Existing Obsidian workspace files are not overwritten.
- Pandoc absence is reported as a warning because it blocks live reference rendering, not plugin installation.

## External skills and plugin QA

Run integration checks:

```sh
python3 scripts/operations/vendors/install_external_skills.py --dry-run --yes
python3 scripts/operations/vendors/install_external_skills.py --dry-run --yes --skip-ars
python3 scripts/operations/vendors/install_external_skills.py --dry-run --yes --skip-rbs
python3 scripts/operations/vendors/install_external_skills.py --dry-run --yes --skip-subagent-orchestrator
python3 scripts/operations/vendors/install_external_skills.py --dry-run --yes --no-rbs-plugin
python3 scripts/operations/vendors/install_external_skills.py --dry-run --yes --no-subagent-orchestrator-plugin
python3 scripts/operations/vendors/check_external_skills.py
```

Expected result:

- Dry runs report vendor operations without changing submodules, wrappers, marketplace files, or install reports.
- Skipped integrations are reported as skipped and are not claimed as installed.
- `.agents/skills/ARS_INSTALLED.md`, `.agents/skills/RBS_INSTALLED.md`, and `.agents/skills/SUBAGENT_ORCHESTRATOR_INSTALLED.md` exist when selected.
- `.agents/plugins/marketplace.json` points Research Book Skills and Subagent Orchestrator to vendored paths.
- Vendored upstream files remain unchanged.

Skill smoke tests are part of full release QA when the release claims ARS, Research Book Skills, or Subagent Orchestrator usability. Run smoke tests only against synthetic seed material or named read-only scaffold files, and record the result in the evidence log.

Loadability checks are not the same as live behavioral smoke tests. If QA only reads wrapper files, upstream `SKILL.md` files, plugin manifests, and marketplace paths, record the result as loadability coverage and do not claim full skill smoke-test coverage.

For each listed ARS wrapper:

1. Read the local wrapper `SKILL.md`.
2. Read the referenced vendored upstream `SKILL.md`.
3. Run only a bounded read-only prompt against synthetic seed files.
4. Record whether the skill loaded, which files it read, what it would check, and what uncertainty remains.

For each listed Research Book Skills wrapper:

1. Use the safe fixture prompt pattern below.
2. Confirm the skill stays within the seed fixture or named files.
3. Record whether it can be loaded and used without edits.

For Subagent Orchestrator skills:

1. Use the safe usage prompt below.
2. Confirm it classifies execution shape only.
3. Do not spawn agents as part of this smoke test.

Expected skill smoke-test result:

- Each claimed skill can be loaded.
- Each prompt remains read-only.
- The response identifies files read and uncertainty remaining.
- No skill output is treated as scholarly evidence.
- No vendored upstream command, Claude-specific command, hook, global config, or global agent is executed.

ARS wrapper usage:

- `ars-deep-research`
- `ars-academic-paper`
- `ars-academic-paper-reviewer`
- `ars-academic-pipeline`

Expected usage behavior:

- Read the wrapper first.
- Read the referenced upstream `SKILL.md`.
- Do not run Claude-specific commands, vendored scripts, hooks, or provider-specific commands.
- Verify citations, claims, page numbers, and source metadata independently.

Research Book Skills wrapper usage:

- `rbs-research-intent-router`
- `rbs-dyslexia-research-companion`
- `rbs-dictation-to-research-notes`
- `rbs-reading-load-reducer`
- `rbs-dyslexia-friendly-prose-editor`
- `rbs-research-book-orchestrator`
- `rbs-scholarly-research-agenda`
- `rbs-systematic-source-discovery`
- `rbs-discovery-runner-deduper`
- `rbs-annotation-to-source-note`
- `rbs-extraction-table-builder`
- `rbs-literature-review-mapper`
- `rbs-annotated-bibliography-builder`
- `rbs-methodology-source-auditor`
- `rbs-claim-evidence-ledger`
- `rbs-claim-traceability-graph`
- `rbs-argument-architecture`
- `rbs-counterargument-peer-review`
- `rbs-chapter-architecture`
- `rbs-scholarly-prose-editor`
- `rbs-citation-integrity-auditor`
- `rbs-figure-table-integrity-auditor`
- `rbs-scholarly-integrity-gate`
- `rbs-ai-human-workflow-log`
- `rbs-rights-privacy-release-auditor`
- `rbs-manuscript-continuity-editor`
- `rbs-case-study-integration`
- `rbs-book-proposal-scholarship`
- `rbs-book-comps-verifier`

Upstream skill names covered by those wrappers:

- `research-intent-router`
- `dyslexia-research-companion`
- `dictation-to-research-notes`
- `reading-load-reducer`
- `dyslexia-friendly-prose-editor`
- `research-book-orchestrator`
- `scholarly-research-agenda`
- `systematic-source-discovery`
- `discovery-runner-deduper`
- `annotation-to-source-note`
- `extraction-table-builder`
- `literature-review-mapper`
- `annotated-bibliography-builder`
- `methodology-source-auditor`
- `claim-evidence-ledger`
- `claim-traceability-graph`
- `argument-architecture`
- `counterargument-peer-review`
- `chapter-architecture`
- `scholarly-prose-editor`
- `citation-integrity-auditor`
- `figure-table-integrity-auditor`
- `scholarly-integrity-gate`
- `ai-human-workflow-log`
- `rights-privacy-release-auditor`
- `manuscript-continuity-editor`
- `case-study-integration`
- `book-proposal-scholarship`
- `book-comps-verifier`

Safe fixture prompt pattern:

```text
Use <skill-name> on the synthetic QA seed files only. Treat all seed material as test-only and not scholarly evidence. Report what the skill would check, which files it read, and what uncertainty remains. Do not edit files.
```

Expected result:

- The selected skill reads only the bounded seed fixture or named project files.
- It does not invent sources, citekeys, page numbers, quotations, studies, metadata, or final claims.
- It preserves source and citation limits.

Subagent Orchestrator guarded wrapper usage:

- `subagent-safe-using-subagent-orchestrator`
- `subagent-safe-subagent-orchestrator`

Upstream skill names covered by those wrappers:

- `using-subagent-orchestrator`
- `subagent-orchestrator`

Safe usage prompt:

```text
Use using-subagent-orchestrator for this synthetic QA task. Classify whether the task fits single-thread, sequential-plan, or parallel-subagents. Do not spawn agents. Do not edit files. Treat output as planning aid only, not evidence.
```

Expected result:

- The wrapper only provides execution-shape guidance.
- It does not override project rules, citation rules, manuscript rules, audit rules, or vendor rules.
- Subagent output is not treated as evidence.

## Render QA

Run this section only when export or render QA is in scope.

Run render preflight:

```sh
python3 scripts/research-writing/render_manuscript.py --to html
```

Run target renders when Quarto and render dependencies are installed:

```sh
make render-html
make render-docx
make render-pdf
make render
```

For browser inspection, serve generated HTML over local HTTP instead of using `file://` when Browser Use blocks local file URLs. Run `python3 -m http.server --directory exports/html 4173` from the project root:

```sh
python3 -m http.server --directory exports/html 4173
```

Inspect `http://127.0.0.1:4173/`, then stop the server after inspection.

Expected result:

- If render tooling is out of scope, record Quarto, Pandoc, or TeX as skipped with release impact.
- Missing Quarto, Pandoc, or TeX is a blocker only for releases that claim rendered artifacts.
- HTML and DOCX targets do not require a PDF engine.
- PDF and all-format render require the configured PDF engine, defaulting to `lualatex`.
- Rendered outputs appear under the configured Quarto output location in `exports/`.
- Generated files are manually inspected for title, table of contents, citations, bibliography, internal links, figures, tables, page breaks, headings, and absence of scaffold sample content.
- If sandboxed automation fails with `unable to open database file` but the same render passes with normal user permissions or a writable Quarto cache, record the sandbox failure as an environment constraint and keep the normal render log as evidence.
- If Quarto warns that it is refusing to remove `site_libs` outside the project directory, record it as non-blocking only when all expected outputs exist and manual inspection passes. The warning means the scaffold renders from the `manuscript/` Quarto project into `exports/html`, outside that Quarto project root. If warning-free logs become a release requirement, change the render workflow to render internally, such as to `manuscript/_book`, then copy final artifacts into `exports/`.

## Manual Scholarly QA

Scripts cannot verify every scholarly risk. Before production release, manually check:

- every manuscript citekey exists in `bibliography/references.bib`
- every source-dependent claim is traceable to source notes, claim ledgers, or chapter briefs
- page-specific claims have page numbers or locators in the relevant notes
- direct quotations are accurate and have locators
- paraphrases are not too close to source wording
- unsupported claims are removed, qualified, or recorded in an audit note
- counterevidence and caveats from claim notes remain visible in draft prose
- bibliography metadata has been checked against Zotero or the source
- rights, privacy, and sensitive material have been reviewed before sharing

## Release Evidence Log

Create a release QA record outside source-of-truth folders or in a release audit note if the project wants the record preserved:

```text
Release candidate:
Repository URL:
Branch, tag, or commit:
QA date:
QA operator:
Python version:
Quarto version:
Pandoc version:
TeX engine version:
Zotero or bibliography verification date:

Commands run:
- command:
  exit code:
  result:
  notes:

GUI evidence:
- check:
  screenshot or artifact:
  fallback observation:
  impact:

Skipped checks:
- check:
  reason:
  release impact:

Failures fixed:
- issue:
  fix:
  verification:

Unresolved risks:
- risk:
  owner:
  release decision:

Final decision:
```

Do not proceed with production release if any skipped check is required for the claimed release artifact.

## Final Release Decision

Release is ready when:

- `git status --short --branch` matches the intended release state.
- `git submodule status --recursive` has no `+`, `-`, or `U` markers.
- `make release-audit` passes.
- All required render targets pass and are manually inspected.
- External integrations required by the release pass `make check-external-skills`.
- Codex Panel setup required by the release passes `make check-obsidian-panel`.
- Scholarly QA has no unresolved blockers.
- The release evidence log records commands, versions, skipped checks, and remaining risks.

Release is not ready when:

- any required command exits nonzero
- missing citations, duplicate bibliography keys, unresolved placeholders, broken links, scaffold manuscript entries, or missing render tools remain unresolved
- a vendor submodule is dirty, uninitialized, conflicted, drifted from the parent index, or from an unexpected origin
- a script requires network access or system installation that was not approved and verified
- a claim, quotation, citation, or source metadata issue is unresolved but hidden from the release record
