# Production Release QA Runbook

Use this runbook to test a release candidate from a fresh clone through setup, script verification, seeded content checks, skill usage, manuscript gates, rendering, and release decision. Run destructive, mutating, networked, and intentionally failing checks only in a disposable QA clone.

The synthetic files under `test/qa/fixtures/release_seed/` and the tool `test/qa/tools/seed_release_qa.py` exist only to exercise repository QA paths. They are not scholarly evidence, not source support, and not releasable manuscript content.

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
- Codex CLI installed and logged in for local agent workflows
- Obsidian for the required project-root vault workflow

Optional until the matching workflow is tested:

- Node and npm, used by setup only if Codex CLI needs installation through npm
- Quarto, Pandoc, and a TeX engine such as `lualatex` for manuscript rendering
- Zotero and Better BibTeX for citation-library verification

Record versions before setup:

```sh
git --version
python3 --version
curl --version
unzip -v
codex --version
quarto --version
pandoc --version
lualatex --version
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
python3 scripts/setup_environment.py --dry-run
python3 scripts/setup_environment.py --dry-run --with-external-skills
```

Expected result:

- Dry runs exit 0.
- No files, packages, repositories, plugins, or vendor pointers are changed.
- Recommended checks include `bash scripts/doctor.sh`, external skill check, Obsidian check, citation check, and placeholder check.
- External skills are skipped unless `--with-external-skills` is passed.

Run setup in the disposable clone:

```sh
bash setup.sh
python3 scripts/check_obsidian_codex.py
```

Expected result:

- Required tools are found or reported with clear manual steps.
- `.agents/skills/` exists and local skill front matter validates.
- The project root is treated as the Obsidian vault root.
- `.obsidian/plugins/obsidian-codex/` is installed or an existing plugin folder is reported as skipped unless `--force` was intentionally used.
- Existing Obsidian settings are not overwritten.

If system package installation is managed outside setup, use:

```sh
bash setup.sh --skip-packages
```

Expected result:

- Package checks are explicitly skipped.
- Later `make doctor` still verifies required commands.

## Scaffold App Usability QA

Confirm that every required or recommended app can open and be used against the scaffolded project, not only that command-line checks pass.

Obsidian opens the scaffold project root as a vault:

1. Open Obsidian.
2. Choose the release QA clone root as the vault folder.
3. Confirm `AGENTS.md`, `notes/`, `research/`, `manuscript/`, and `test/qa/docs/production-release-qa.md` are visible.
4. Open a note from `notes/` and a manuscript file from `manuscript/`.

Expected result:

- The scaffold project root opens directly as the vault.
- Obsidian does not require a nested vault folder.
- Existing project files are readable without moving or copying them.

Obsidian Codex can run a bounded read-only prompt:

```text
Read AGENTS.md and summarize the project rules. Do not edit anything.
```

Expected result:

- The Obsidian Codex plugin is enabled for the project-root vault.
- The read-only prompt can inspect scaffold files.
- File writes and command execution remain approval-gated.

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
2. Confirm Better BibTeX is installed and enabled when citation-library QA is in scope.
3. Export or refresh BibTeX into `bibliography/references.bib` only from verified library records.
4. Run `python3 scripts/check_citations.py --include-notes --require-citations`.

Expected result:

- Zotero opens the relevant library.
- Better BibTeX can provide stable citekeys.
- `bibliography/references.bib` remains the repository citation source of truth.
- No generated or unverified bibliographic metadata is accepted as evidence.

Quarto, Pandoc, and the configured TeX engine can render from the scaffold:

```sh
quarto --version
pandoc --version
lualatex --version
make render-html
make render-docx
make render-pdf
```

Expected result:

- Quarto and Pandoc are available to the scaffold.
- The configured TeX engine is available before PDF QA.
- Rendered outputs are generated from `manuscript/` into `exports/`.

## Make Target QA Matrix

| Target | Purpose | Pass condition |
| --- | --- | --- |
| `make help` | Lists available targets | Includes setup, check, render, audit, and release-audit targets |
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
| `make check-manuscript-readiness` | Detects remaining scaffold manuscript entries | Exits 0 for production release |
| `make check-external-skills` | Validates vendor submodules, wrappers, plugins, marketplace, and old repo references | Exits 0 with zero failures |
| `make install-external-skills` | Vendors external skills and updates marketplace | Use only in disposable QA or intentional integration updates; verify resulting diff |
| `make install-subagent-orchestrator` | Installs only the optional subagent plugin path | Uses project scope and keeps the plugin available-only |
| `make update-skills-vendors` | Fast-forwards vendored skill repositories and refreshes integrations | Use only when the release includes vendor updates |
| `make check-obsidian-codex` | Verifies Obsidian Codex plugin install and Codex CLI | Exits 0 after plugin files and Codex CLI are present |
| `make install-obsidian-codex` | Installs Obsidian Codex plugin | Use only in disposable QA or intentional local setup |
| `make audit` | Runs normal scaffold health checks | Exits 0 |
| `make release-audit` | Runs strict pre-release manuscript checks | Exits 0 and all blockers are resolved |

Standard command sequence:

```sh
make doctor
make lint
make test
make audit
make release-audit
```

Expected result:

- `make doctor`, `make lint`, `make test`, `make audit`, and `make release-audit` exit 0 for a production manuscript.
- A generic scaffold may fail `make release-audit` until the title, sample chapter, sample appendix, and at least one verified citation are replaced by project material.

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
python3 test/qa/tools/seed_release_qa.py status
python3 test/qa/tools/seed_release_qa.py apply --dry-run
```

Apply the seed in a disposable QA clone:

```sh
python3 test/qa/tools/seed_release_qa.py apply
```

Run content gates against the seed:

```sh
python3 scripts/check_placeholders.py .
python3 scripts/check_citations.py
python3 scripts/check_citations.py --include-notes --require-citations
python3 scripts/check_broken_internal_links.py
python3 scripts/check_manuscript_readiness.py
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
python3 test/qa/tools/seed_release_qa.py clean --dry-run
python3 test/qa/tools/seed_release_qa.py clean
git status --short
```

Expected result:

- Seed-only files are removed.
- Tracked scaffold files are restored only when their content still matches the seed.
- Changed seed files are left for manual review instead of being removed silently.

## Script-by-Script QA

Entry points and support modules:

- `scripts/check_broken_internal_links.py`
- `scripts/check_citations.py`
- `scripts/check_external_skills.py`
- `scripts/check_manuscript_readiness.py`
- `scripts/check_obsidian_codex.py`
- `scripts/check_placeholders.py`
- `scripts/doctor.py`
- `scripts/doctor.sh`
- `scripts/environment_checks.py`
- `scripts/git_utils.py`
- `scripts/install_external_skills.py`
- `scripts/install_obsidian_codex.sh`
- `scripts/new_from_template.py`
- `scripts/obsidian_agent.py`
- `scripts/project_config.py`
- `scripts/render.sh`
- `scripts/render_manuscript.py`
- `scripts/script_env.sh`
- `scripts/script_utils.py`
- `scripts/setup_environment.py`
- `scripts/update-skills-vendors.sh`
- `scripts/update_skills_vendors.py`

Run support coverage:

```sh
python3 -m unittest discover scripts/tests
python3 -m unittest discover test/qa/tests
python3 -m compileall -q scripts test/qa/tools test/qa/tests
```

Expected result:

- Unit tests cover package detection, Obsidian install safety, git helpers, script utilities, render preflights, external skill checks, setup behavior, template creation, seeded QA, docs consistency, and direct QA runbook coverage.
- Compile check exits 0.

Targeted script checks:

```sh
bash scripts/doctor.sh
python3 scripts/doctor.py
python3 scripts/check_obsidian_codex.py
python3 scripts/install_external_skills.py --dry-run --yes
python3 scripts/check_external_skills.py
bash scripts/update-skills-vendors.sh --skip-checks
python3 scripts/check_placeholders.py .
python3 scripts/check_placeholders.py --include-templates templates
python3 scripts/check_citations.py
python3 scripts/check_citations.py --include-notes --require-citations
python3 scripts/check_citations.py --show-unused
python3 scripts/check_broken_internal_links.py
python3 scripts/check_manuscript_readiness.py
python3 scripts/new_from_template.py --help
python3 scripts/render_manuscript.py --to html
bash scripts/render.sh --to html
```

Expected result:

- Non-mutating checks exit 0 where prerequisites exist.
- Missing optional render tooling is reported as a tooling blocker, not a manuscript failure.
- Vendor checks fail if submodule pointers differ from the parent index, are uninitialized, conflicted, dirty, or from an unexpected origin.

## Negative Fixture Checks

Run these only in a disposable QA clone and clean up immediately afterward.

Placeholder failure:

```sh
mkdir -p .qa-fixtures
printf 'Unresolved marker: {{MISSING_VALUE}}\n' > .qa-fixtures/placeholder.md
python3 scripts/check_placeholders.py .qa-fixtures
rm -f .qa-fixtures/placeholder.md
rmdir .qa-fixtures 2>/dev/null || true
```

Citation failure:

```sh
printf '\nMissing citation test [-@qaMissingCitationKey].\n' >> manuscript/index.qmd
python3 scripts/check_citations.py
git restore manuscript/index.qmd
```

Internal-link failure:

```sh
mkdir -p notes/00-inbox
printf 'Broken link [[qa-missing-target]]\n' > notes/00-inbox/qa-link-fixture.md
python3 scripts/check_broken_internal_links.py
rm -f notes/00-inbox/qa-link-fixture.md
```

Template overwrite and invalid replacement failures:

```sh
mkdir -p .qa-fixtures
printf 'existing\n' > .qa-fixtures/existing.md
python3 scripts/new_from_template.py templates/source-note-template.md .qa-fixtures/existing.md
python3 scripts/new_from_template.py templates/source-note-template.md .qa-fixtures/bad.md --set invalid
rm -f .qa-fixtures/existing.md
rmdir .qa-fixtures 2>/dev/null || true
```

Expected result:

- Each checker exits nonzero while the bad fixture exists.
- Output identifies the failing file, marker, link, citekey, or argument.
- Cleanup returns the disposable clone to an intentional state.

## Obsidian Codex QA

Run dry and direct checks:

```sh
bash scripts/install_obsidian_codex.sh --dry-run
python3 scripts/obsidian_agent.py --dry-run
python3 scripts/check_obsidian_codex.py
```

When testing a real plugin install, use a reviewed release archive and checksum:

```sh
python3 scripts/setup_environment.py --force --obsidian-release-url <reviewed-zip-url> --obsidian-release-sha256 <sha256>
python3 scripts/check_obsidian_codex.py
```

Expected result:

- Dry run does not modify files.
- The plugin folder contains `manifest.json`, `main.js`, and `styles.css`.
- Checksum mismatch fails the install.
- Path traversal inside an archive is rejected by unit tests.
- Existing Obsidian settings are not overwritten.

Safe usage prompt:

```text
Read AGENTS.md and summarize the project rules. Do not edit anything.
```

Expected result:

- The plugin performs bounded read-only work.
- Any file-write or command action still requires approval.

## External Skills And Plugin QA

Run integration checks:

```sh
python3 scripts/install_external_skills.py --dry-run --yes
python3 scripts/install_external_skills.py --dry-run --yes --skip-ars
python3 scripts/install_external_skills.py --dry-run --yes --skip-rbs
python3 scripts/install_external_skills.py --dry-run --yes --skip-subagent-orchestrator
python3 scripts/install_external_skills.py --dry-run --yes --no-rbs-plugin
python3 scripts/install_external_skills.py --dry-run --yes --no-subagent-orchestrator-plugin
python3 scripts/check_external_skills.py
```

Expected result:

- Dry runs report vendor operations without changing submodules, wrappers, marketplace files, or install reports.
- Skipped integrations are reported as skipped and are not claimed as installed.
- `.agents/skills/ARS_INSTALLED.md`, `.agents/skills/RBS_INSTALLED.md`, and `.agents/skills/SUBAGENT_ORCHESTRATOR_INSTALLED.md` exist when selected.
- `.agents/plugins/marketplace.json` points Research Book Skills and Subagent Orchestrator to vendored paths.
- Vendored upstream files remain unchanged.

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

Research Book Skills plugin usage:

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

Subagent Orchestrator plugin usage:

- `using-subagent-orchestrator`
- `subagent-orchestrator`

Safe usage prompt:

```text
Use using-subagent-orchestrator for this synthetic QA task. Classify whether the task should be single-thread, sequential-plan, or parallel-subagents. Do not spawn agents. Do not edit files. Treat output as planning aid only, not evidence.
```

Expected result:

- The plugin only provides execution-shape guidance.
- It does not override project rules, citation rules, manuscript rules, audit rules, or vendor rules.
- Subagent output is not treated as evidence.

## Render QA

Run render preflight:

```sh
python3 scripts/render_manuscript.py --to html
```

Run target renders when Quarto and render dependencies are installed:

```sh
make render-html
make render-docx
make render-pdf
make render
```

Expected result:

- HTML and DOCX targets do not require a PDF engine.
- PDF and all-format render require the configured PDF engine, defaulting to `lualatex`.
- Rendered outputs appear under the configured Quarto output location in `exports/`.
- Generated files are manually inspected for title, table of contents, citations, bibliography, internal links, figures, tables, page breaks, headings, and absence of scaffold sample content.

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

Production release should not proceed if any skipped check is required for the claimed release artifact.

## Final Release Decision

Release is ready when:

- `git status --short --branch` matches the intended release state.
- `git submodule status --recursive` has no `+`, `-`, or `U` markers.
- `make release-audit` passes.
- All required render targets pass and are manually inspected.
- External integrations required by the release pass `make check-external-skills`.
- Obsidian Codex setup required by the release passes `make check-obsidian-codex`.
- Scholarly QA has no unresolved blockers.
- The release evidence log records commands, versions, skipped checks, and remaining risks.

Release is not ready when:

- any required command exits nonzero
- missing citations, duplicate bibliography keys, unresolved placeholders, broken links, scaffold manuscript entries, or missing render tools remain unresolved
- a vendor submodule is dirty, uninitialized, conflicted, drifted from the parent index, or from an unexpected origin
- a script requires network access or system installation that was not approved and verified
- a claim, quotation, citation, or source metadata issue is unresolved but hidden from the release record
