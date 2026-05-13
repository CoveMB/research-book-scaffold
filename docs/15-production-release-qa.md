# Production Release QA Runbook

Use this document to test a release candidate from a fresh clone through setup, script verification, manuscript checks, rendering, and release decision. Run it in a disposable QA clone, not in a working authoring clone with unpublished notes.

## Release Standard

A production release is ready only when:

- the repository can be cloned with submodules from the intended remote, branch, tag, or commit
- setup completes or reports only explicitly accepted skipped optional tools
- required local integrations are installed and checked
- every relevant script has a passing positive test
- every release gate passes without hiding evidence, citation, placeholder, or link problems
- render targets required for the release are generated and manually inspected
- all skipped checks, warnings, and residual scholarly risks are recorded

Warnings are not automatic failures, but they need an explicit release decision. Failures from `make release-audit` are release blockers.

## QA Principles

- Test from a clean clone so local state does not mask missing setup steps.
- Keep secrets, API keys, cookies, and credentials out of the repository and out of QA logs.
- Treat Zotero or `bibliography/references.bib` as the citation source of truth.
- Treat script success as technical readiness, not proof that claims are supported by sources.
- Do destructive or intentionally failing tests only in the disposable QA clone.
- Capture command output for the release record.

## Prerequisites

Required for the core scaffold:

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

- `git status --short --branch` shows the intended branch or detached release tag.
- The working tree is clean before setup.
- Submodules are initialized.
- The commit hash is recorded in the QA report.

If a release is cut from an existing branch, confirm the local branch is not behind its upstream:

```sh
bash scripts/doctor.sh
```

Expected result:

- Required files and directories pass.
- Required tools pass.
- Git tracking is either up to date or the release report explains why the checkout is intentionally detached.

## Setup QA

Run a dry run first:

```sh
bash setup.sh --dry-run
```

Expected result:

- The output starts with a dry-run notice.
- No files, packages, repositories, or plugins are changed.
- The final setup report lists recommended follow-up checks.

Run setup:

```sh
bash setup.sh
```

Expected result:

- Required tools are found or reported with clear manual steps.
- `.agents/skills/` exists and local skill front matter validates.
- The project root is treated as the Obsidian vault root.
- `.obsidian/plugins/obsidian-codex/` is installed or an existing plugin folder is reported as skipped unless `--force` was intentionally used.
- The final setup report contains no failed items.

If system package installation is managed outside setup, use:

```sh
bash setup.sh --skip-packages
```

Expected result:

- Package checks are explicitly skipped.
- Later `make doctor` still verifies the required commands.

External skills are skipped by default during `setup.sh`. To include them during setup:

```sh
bash setup.sh --with-external-skills
```

Expected result:

- Vendor submodules initialize from the configured remotes.
- ARS wrapper skills are created under `.agents/skills/`.
- Research Book Skills and Subagent Orchestrator marketplace entries are exposed from `vendor/`, not copied into unrelated paths.
- Vendored scripts are not run except the bounded project-scoped Subagent Orchestrator installer after its boundary checks pass.

## Standard Check Sequence

Run this sequence after setup and before any targeted negative tests:

```sh
make doctor
make lint
make test
make audit
make release-audit
```

Expected result:

- `make doctor` exits 0 and has no required-tool or required-file failures.
- `make lint` exits 0.
- `make test` exits 0.
- `make audit` exits 0.
- `make release-audit` exits 0 for a production manuscript.

Known scaffold blockers:

- A fresh generic scaffold may fail `make release-audit` until the title, sample chapter, sample appendix, and at least one verified citation are replaced by project material.
- These failures are expected during scaffold development but are blockers for production manuscript release.
- To test every content-sensitive script before real project material exists, apply the seeded fixture below in a disposable QA clone.

## Seeded Content Fixture QA

Use this only in a disposable QA clone. The seed is synthetic test material for script verification. It is not scholarly evidence, not a real citation source, and must not be released as manuscript content.

The fixture creates:

- one BibTeX entry in `bibliography/references.bib`
- one source note in `notes/01-source-notes/`
- one claim note in `notes/04-claim-ledger/`
- one chapter brief in `notes/07-chapter-briefs/`
- one search log in `research/search-logs/`
- one manuscript index page
- one manuscript chapter page
- one release-ready `manuscript/_quarto.yml` that removes scaffold sample chapter and appendix entries

Apply the seed:

```sh
python3 - <<'PY'
from pathlib import Path


def write_text(path, text):
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text.strip() + "\n", encoding="utf-8")


references_path = Path("bibliography/references.bib")
references_text = references_path.read_text(encoding="utf-8") if references_path.exists() else ""
seed_entry = """
@book{qaSeed2026,
  author = {Seed, Quinn},
  title = {Synthetic Source for Release QA},
  year = {2026},
  publisher = {Local QA Press},
  address = {Test City},
  note = {Synthetic fixture used only for repository QA}
}
"""
if "@book{qaSeed2026" not in references_text:
    references_path.parent.mkdir(parents=True, exist_ok=True)
    references_path.write_text(references_text.rstrip() + "\n\n" + seed_entry.strip() + "\n", encoding="utf-8")

write_text(
    "manuscript/_quarto.yml",
    """
project:
  type: book
  output-dir: ../exports/html

book:
  title: "QA Seed Manuscript"
  chapters:
    - index.qmd
    - chapters/00-front-matter.qmd
    - chapters/qa-seed-chapter.qmd
    - chapters/99-back-matter.qmd

bibliography: ../bibliography/references.bib

format:
  html:
    toc: true
  pdf:
    toc: true
  docx:
    toc: true
""",
)

write_text(
    "manuscript/index.qmd",
    """
# QA Seed Manuscript

This disposable manuscript index verifies that citation scanning can find a seeded citation [@qaSeed2026].

The seeded chapter links to [[qa-seed-source]], [[qa-seed-claim]], and [[qa-seed-brief]] so internal-link checks have positive coverage.
""",
)

write_text(
    "manuscript/chapters/qa-seed-chapter.qmd",
    """
# Seeded Chapter

The seeded chapter uses one bibliography key [@qaSeed2026] and one internal source link [[qa-seed-source]].

It also refers to the seeded claim note [[qa-seed-claim]] and seeded chapter brief [[qa-seed-brief]].

This page is intentionally short so render failures point to tooling or configuration rather than manuscript complexity.
""",
)

write_text(
    "notes/01-source-notes/qa-seed-source.md",
    """
---
type: source-note
citekey: qaSeed2026
title: "Synthetic Source for Release QA"
authors:
  - "Quinn Seed"
year: "2026"
source_type: synthetic-fixture
evidence_type: qa-fixture
reading_status: fixture
---

# QA seed source

## Summary

This synthetic note gives the QA suite one source note with a valid citekey [@qaSeed2026].

## Evidence or method

- Fixture evidence only. Do not use this as a real source.

## What it supports

- [[qa-seed-claim]]

## Possible manuscript use

- Supports the seeded manuscript chapter during script QA only.
""",
)

write_text(
    "notes/04-claim-ledger/qa-seed-claim.md",
    """
---
type: claim-note
claim_id: QA-SEED-001
status: fixture
confidence: test-only
---

# QA seed claim

## Claim

The repository QA seed contains a traceable citation and internal links for script testing [@qaSeed2026].

## Evidence

- Source note: [[qa-seed-source]]

## Limits

- Synthetic fixture only. It proves script behavior, not scholarly correctness.
""",
)

write_text(
    "notes/07-chapter-briefs/qa-seed-brief.md",
    """
---
type: chapter-brief
status: fixture
---

# QA seed brief

## Purpose

Provide a minimal chapter brief so link, citation, and manuscript checks can run against connected project layers.

## Sources

- [[qa-seed-source]]

## Claims

- [[qa-seed-claim]]

## Draft target

- `manuscript/chapters/qa-seed-chapter.qmd`
""",
)

write_text(
    "research/search-logs/qa-seed-search-log.md",
    """
# QA seed search log

## Scope

This synthetic search log exists so research-folder scanning has a known good Markdown file.

## Kept source

- Synthetic fixture source [@qaSeed2026]

## Decision

- Use only for script QA in a disposable clone.
""",
)
PY
```

Run the content gates against the seeded fixture:

```sh
python3 scripts/check_placeholders.py .
python3 scripts/check_citations.py
python3 scripts/check_citations.py --include-notes --require-citations
python3 scripts/check_broken_internal_links.py
python3 scripts/check_manuscript_readiness.py
```

Expected result:

- Placeholder check exits 0.
- Citation checks exit 0 and find `qaSeed2026`.
- Strict citation mode exits 0 because the manuscript, notes, and research fixture contain at least one valid citation.
- Internal-link check exits 0 because all seeded wiki links resolve.
- Manuscript-readiness check exits 0 because the seeded Quarto config has a real title and no sample scaffold chapter or appendix entries.

Run the broader release gates after external integrations are installed:

```sh
make audit
make release-audit
```

Expected result:

- Both targets exit 0 when external skill integration checks also pass.
- If these fail only at `check-external-skills`, complete external-skill setup or record that external integrations were intentionally out of scope.

Render the seeded manuscript when Quarto and render dependencies are installed:

```sh
make render-html
make render-docx
make render-pdf
```

Expected result:

- HTML and DOCX render without requiring a TeX engine.
- PDF render passes only when the configured PDF engine is installed.
- Outputs contain the seeded title, seeded chapter, rendered citation, and bibliography entry.

Clean up the seed before returning to normal release QA:

```sh
git restore bibliography/references.bib manuscript/_quarto.yml manuscript/index.qmd
rm -f manuscript/chapters/qa-seed-chapter.qmd
rm -f notes/01-source-notes/qa-seed-source.md
rm -f notes/04-claim-ledger/qa-seed-claim.md
rm -f notes/07-chapter-briefs/qa-seed-brief.md
rm -f research/search-logs/qa-seed-search-log.md
git status --short
```

Expected result:

- Seeded source files are removed.
- Modified scaffold files are restored.
- `git status --short` shows only intentional QA artifacts, such as generated exports if they were kept for inspection.

## Make Target QA Matrix

| Target | Purpose | Pass condition |
| --- | --- | --- |
| `make help` | Lists available targets | Includes setup, check, render, audit, and release-audit targets |
| `make doctor` | Checks local tools, required files, required folders, and git tracking | Exits 0 and has no `FAIL` lines |
| `make lint` | Compile-checks Python scripts | Exits 0 |
| `make test` | Runs script unit tests | Exits 0 with all tests passing |
| `make check-placeholders` | Scans Markdown and QMD files for unresolved markers | Exits 0 and reports no unresolved markers |
| `make check-citations` | Checks manuscript citekeys against `bibliography/references.bib` | Exits 0 and missing citekey count is zero |
| `make check-citations-strict` | Checks manuscript and notes citekeys and requires at least one citation | Exits 0 for production release |
| `make check-links` | Checks wiki-style internal links in notes, manuscript, and research files | Exits 0 and reports no broken or ambiguous links |
| `make check-manuscript-readiness` | Detects remaining scaffold manuscript entries | Exits 0 for production release |
| `make check-external-skills` | Validates vendored skills, wrappers, plugin JSON, marketplace entries, and old repo references | Exits 0 with zero failures |
| `make check-obsidian-codex` | Verifies the Obsidian Codex plugin install and Codex CLI | Exits 0 after Obsidian plugin files and Codex CLI are present |
| `make audit` | Runs repository checks for normal scaffold health | Exits 0 |
| `make release-audit` | Runs strict pre-release manuscript checks | Exits 0 and all blockers are resolved |
| `make render-html` | Renders HTML only | Exits 0 and generated HTML is present under `exports/` |
| `make render-docx` | Renders DOCX only | Exits 0 and generated DOCX is present under `exports/` |
| `make render-pdf` | Renders PDF only | Exits 0 and generated PDF is present under `exports/` |
| `make render` | Renders all enabled Quarto formats | Exits 0 and all required outputs are present |

## Script-by-Script QA

### `setup.sh` and `scripts/setup_environment.py`

Positive tests:

```sh
bash setup.sh --dry-run
python3 scripts/setup_environment.py --dry-run
python3 scripts/setup_environment.py --dry-run --with-external-skills
```

Expected result:

- Dry runs exit 0.
- The report says no files, packages, repositories, or plugins will be changed.
- Recommended checks include `bash scripts/doctor.sh`, external skill check, Obsidian check, citation check, and placeholder check.
- External skills are skipped unless `--with-external-skills` is passed.

Full setup test:

```sh
bash setup.sh
python3 scripts/check_obsidian_codex.py
```

Expected result:

- Setup exits 0 with no failed items.
- The Obsidian plugin folder contains `manifest.json`, `main.js`, and `styles.css`.
- Existing Obsidian settings are not overwritten.

Failure-path test in a disposable clone:

```sh
python3 scripts/setup_environment.py --dry-run --skip-packages
```

Expected result:

- Package checks are reported as skipped.
- The script still validates local skills and reports next manual checks.

### `scripts/install_obsidian_codex.sh`

This wrapper routes to `scripts/setup_environment.py`.

```sh
bash scripts/install_obsidian_codex.sh --dry-run
```

Expected result:

- Same dry-run behavior as setup.
- The command does not modify files during dry run.

When testing a real install, use a reviewed release archive and checksum when available:

```sh
python3 scripts/setup_environment.py --force --obsidian-release-url <reviewed-zip-url> --obsidian-release-sha256 <sha256>
python3 scripts/check_obsidian_codex.py
```

Expected result:

- The plugin is replaced atomically.
- Checksum mismatch fails the install.
- Path traversal inside an archive is rejected by unit tests.

### `scripts/doctor.sh` and `scripts/doctor.py`

```sh
bash scripts/doctor.sh
python3 scripts/doctor.py
```

Expected result:

- Core tools `git`, `python3`, `curl`, `unzip`, and `codex` are found.
- Optional tools `node`, `npm`, `quarto`, and `pandoc` either pass or warn.
- Required files `bibliography/references.bib` and `manuscript/_quarto.yml` exist.
- Required directories `.agents/skills`, `templates`, `notes`, and `research` exist.
- Git tracking status is reported.
- Exit code is 0 when there are warnings but no failures.

### `scripts/check_obsidian_codex.py`

Default project-root vault:

```sh
python3 scripts/check_obsidian_codex.py
```

Explicit vault path:

```sh
python3 scripts/check_obsidian_codex.py /path/to/vault
```

Environment-driven vault path:

```sh
OBSIDIAN_VAULT=/path/to/vault python3 scripts/check_obsidian_codex.py
```

Expected result:

- Vault exists.
- `.obsidian/` exists or gives a warning.
- Plugin directory exists.
- `manifest.json`, `main.js`, and `styles.css` exist.
- `community-plugins.json` confirms enablement or gives a warning to enable the plugin manually.
- `codex --version` succeeds.

### `scripts/install_external_skills.py`

Dry run:

```sh
python3 scripts/install_external_skills.py --dry-run --yes
```

Expected result:

- Reports the vendor operations it would run.
- Does not change submodules, wrappers, marketplace files, or install reports.
- Ends with a warning that external repositories are untrusted until inspected.

Pinned install:

```sh
make install-external-skills
python3 scripts/check_external_skills.py
```

Expected result:

- Submodules initialize at pinned commits unless update flags are passed.
- ARS wrappers exist in `.agents/skills/ars-*`.
- `.agents/skills/ARS_INSTALLED.md`, `.agents/skills/RBS_INSTALLED.md`, and `.agents/skills/SUBAGENT_ORCHESTRATOR_INSTALLED.md` exist when their integrations are selected.
- `.agents/plugins/marketplace.json` exposes Research Book Skills and Subagent Orchestrator from the expected vendored paths.
- Vendored upstream files remain unmodified.

Selective install tests:

```sh
python3 scripts/install_external_skills.py --dry-run --yes --skip-ars
python3 scripts/install_external_skills.py --dry-run --yes --skip-rbs
python3 scripts/install_external_skills.py --dry-run --yes --skip-subagent-orchestrator
python3 scripts/install_external_skills.py --dry-run --yes --no-rbs-plugin
python3 scripts/install_external_skills.py --dry-run --yes --no-subagent-orchestrator-plugin
```

Expected result:

- Skipped integrations are reported as skipped.
- Plugin exposure skip flags remove or avoid only the matching marketplace entry.
- The command does not claim skipped integrations are installed.

### `scripts/check_external_skills.py`

```sh
python3 scripts/check_external_skills.py
```

Expected result:

- `.gitmodules` exists.
- ARS, Research Book Skills, and Subagent Orchestrator vendor paths are registered as submodules.
- Vendor origins match the expected repositories.
- Vendor submodules are clean.
- ARS upstream skills and local wrappers exist.
- Plugin JSON files exist and contain expected names.
- Marketplace entries point at the expected vendored paths.
- No old ARS repo references remain in local docs or scripts.
- Summary reports `0 fail`.

Failure-path checks:

- Make a disposable clone with one intentionally dirty vendor file and verify the script reports that exact dirty path.
- Restore the dirty file before continuing with release QA.

### `scripts/update-skills-vendors.sh` and `scripts/update_skills_vendors.py`

Only run this when the release includes updating vendored external repositories.

```sh
bash scripts/update-skills-vendors.sh --skip-checks
```

Expected result:

- The parent repository branch is printed.
- Parent refs are fetched.
- Selected vendor submodules are synced and initialized.
- Dirty vendor submodules are rejected before update.
- Selected vendors are fast-forwarded only.
- Local skill integrations are refreshed.

Full update QA:

```sh
bash scripts/update-skills-vendors.sh
python3 scripts/check_external_skills.py
bash scripts/doctor.sh
git status --short --branch
git submodule status --recursive
```

Expected result:

- Post-update health checks pass.
- Submodule pointer changes are visible for review.
- No unexpected files are modified.

### `scripts/check_placeholders.py`

Positive production check:

```sh
python3 scripts/check_placeholders.py .
```

Expected result:

- Exits 0.
- Reports no unresolved placeholder markers.
- Ignores `vendor/`, `.git`, `.quarto`, `_book`, `plugins`, and `templates/` by default.

Template-inclusive check:

```sh
python3 scripts/check_placeholders.py --include-templates templates
```

Expected result:

- Template placeholders may be reported because templates intentionally contain replacement markers.
- This is useful for template QA but not a production-release blocker by itself.

Negative fixture test in a disposable clone:

```sh
mkdir -p .qa-fixtures
printf 'Unresolved marker: {{MISSING_VALUE}}\n' > .qa-fixtures/placeholder.md
python3 scripts/check_placeholders.py .qa-fixtures
git restore .qa-fixtures/placeholder.md 2>/dev/null || rm -f .qa-fixtures/placeholder.md
rmdir .qa-fixtures 2>/dev/null || true
```

Expected result:

- The checker exits nonzero while the fixture exists.
- The output includes the file, line number, and marker.

### `scripts/check_citations.py`

Normal manuscript check:

```sh
python3 scripts/check_citations.py
```

Expected result:

- Exits 0 when all manuscript citekeys exist in `bibliography/references.bib`.
- Prints the number of scanned files, citation keys, and bibliography keys.
- Warns if no citations are found unless strict mode is used.

Strict release check:

```sh
python3 scripts/check_citations.py --include-notes --require-citations
```

Expected result:

- Exits 0 only when scanned manuscript, notes, and research files have no missing citekeys and at least one citation exists.
- Exits nonzero if no citations are found.

Unused-key report:

```sh
python3 scripts/check_citations.py --show-unused
```

Expected result:

- Exits 0 if all cited keys exist.
- Prints bibliography keys that are not cited in scanned files.
- Unused keys are informational unless the release policy decides otherwise.

Negative fixture test in a disposable clone:

```sh
printf '\nMissing citation test [-@qaMissingCitationKey].\n' >> manuscript/index.qmd
python3 scripts/check_citations.py
git restore manuscript/index.qmd
```

Expected result:

- The checker exits nonzero before restore.
- The output lists `qaMissingCitationKey` and the manuscript file where it appears.

### `scripts/check_broken_internal_links.py`

```sh
python3 scripts/check_broken_internal_links.py
```

Expected result:

- Exits 0.
- Reports no broken wiki links.
- Reports ambiguous wiki links as failures when a short target matches multiple files.

Negative fixture test in a disposable clone:

```sh
mkdir -p notes/00-inbox
printf 'Broken link [[qa-missing-target]]\n' > notes/00-inbox/qa-link-fixture.md
python3 scripts/check_broken_internal_links.py
git restore notes/00-inbox/qa-link-fixture.md 2>/dev/null || rm -f notes/00-inbox/qa-link-fixture.md
```

Expected result:

- The checker exits nonzero while the fixture exists.
- The output lists the broken wiki link and source file line.

### `scripts/check_manuscript_readiness.py`

```sh
python3 scripts/check_manuscript_readiness.py
```

Expected result for production:

- Exits 0.
- Reports no scaffold manuscript entries in release configuration.

Failure conditions:

- `manuscript/_quarto.yml` is missing.
- The title is still `Untitled Scholarly Manuscript`.
- `chapters/01-chapter-template.qmd` is still included.
- `appendices/appendix-template.qmd` is still included.

Any failure is a production release blocker.

### `scripts/new_from_template.py`

Positive test in a disposable clone:

```sh
mkdir -p .qa-fixtures
printf '# {{Title}}\n\n{{Body}}\n' > .qa-fixtures/template.md
python3 scripts/new_from_template.py .qa-fixtures/template.md .qa-fixtures/generated.md --set Title='QA Source' --set Body='Resolved body'
test -f .qa-fixtures/generated.md
python3 scripts/check_placeholders.py .qa-fixtures/generated.md
rm -f .qa-fixtures/template.md .qa-fixtures/generated.md
rmdir .qa-fixtures 2>/dev/null || true
```

Expected result:

- The new file is created.
- Provided placeholders are replaced.
- The placeholder check passes because all fixture markers were supplied.

Overwrite protection test:

```sh
mkdir -p .qa-fixtures
printf 'existing\n' > .qa-fixtures/existing.md
python3 scripts/new_from_template.py templates/source-note-template.md .qa-fixtures/existing.md
rm -f .qa-fixtures/existing.md
rmdir .qa-fixtures 2>/dev/null || true
```

Expected result:

- The command exits nonzero.
- The output says the destination exists and recommends `--force` for intentional overwrite.

Invalid replacement test:

```sh
python3 scripts/new_from_template.py templates/source-note-template.md .qa-fixtures/bad.md --set invalid
```

Expected result:

- The command exits nonzero.
- The output says the replacement value must use `KEY=VALUE`.

### `scripts/render.sh` and `scripts/render_manuscript.py`

Preflight check without render tools:

```sh
python3 scripts/render_manuscript.py --to html
```

Expected result:

- If Quarto is missing, the script exits nonzero with installation guidance.
- If Quarto exists, HTML rendering runs without requiring a TeX engine.

Targeted render QA:

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
- Generated files are manually opened and inspected for title, table of contents, citations, links, figures, and layout.

Render failure conditions:

- Quarto missing.
- `manuscript/_quarto.yml` missing.
- PDF engine missing when PDF is requested or enabled.
- Quarto exits nonzero because of citation, bibliography, syntax, or rendering errors.

### Support Modules

These files are libraries rather than direct release commands:

- `scripts/environment_checks.py`
- `scripts/git_utils.py`
- `scripts/obsidian_agent.py`
- `scripts/project_config.py`
- `scripts/script_env.sh`
- `scripts/script_utils.py`

QA coverage:

```sh
python3 -m unittest discover scripts/tests
python3 -m compileall -q scripts
```

Expected result:

- Unit tests cover package detection, Obsidian install safety, git helpers, script utilities, render preflights, external skill checks, setup behavior, template creation, and docs consistency.
- Compile check exits 0.

## End-to-End Release Workflow

Run this after script-level QA passes:

1. Confirm the tested commit and submodule state.

```sh
git status --short --branch
git submodule status --recursive
git log -1 --oneline
```

2. Confirm setup and local integrations.

```sh
make doctor
make check-obsidian-codex
make check-external-skills
```

3. Confirm script health.

```sh
make lint
make test
```

4. Confirm repository gates.

```sh
make audit
```

5. Confirm strict manuscript gates.

```sh
make release-audit
```

6. Render every production target.

```sh
make render-html
make render-docx
make render-pdf
```

7. Inspect generated outputs manually.

Check:

- title and author metadata
- chapter order
- appendix order
- table of contents
- citation rendering
- bibliography rendering
- internal links
- figures and tables
- page breaks and headings in PDF and DOCX
- absence of unresolved placeholders
- absence of scaffold sample chapter or appendix content

8. Run final status checks.

```sh
git status --short --branch
git diff --stat
```

Expected result:

- Generated export files may be present if the release process tracks or packages them.
- No unexpected source, note, bibliography, script, vendor, or configuration changes are present.

## Manual Scholarly QA

Scripts cannot verify every scholarly risk. Before production release, manually check:

- Every manuscript citation key exists in `bibliography/references.bib`.
- Every source-dependent claim is traceable to source notes, claim ledgers, or chapter briefs.
- Page-specific claims have page numbers or locators in the relevant notes.
- Direct quotations are accurate and have locators.
- Paraphrases are not too close to source wording.
- Unsupported claims are removed, qualified, or recorded in an audit note.
- Counterevidence and caveats from claim notes remain visible in draft prose.
- Bibliography metadata has been checked against Zotero or the source.
- Rights, privacy, and sensitive material have been reviewed before sharing.

## Release Evidence Log

Create a release QA record outside the source-of-truth folders or in a release audit note if the project wants the record preserved:

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
- `make release-audit` passes.
- All required render targets pass and are manually inspected.
- External integrations required by the release pass `make check-external-skills`.
- Obsidian Codex setup required by the release passes `make check-obsidian-codex`.
- Scholarly QA has no unresolved blockers.
- The release evidence log records commands, versions, skipped checks, and remaining risks.

Release is not ready when:

- Any required command exits nonzero.
- Missing citations, duplicate bibliography keys, unresolved placeholders, broken links, scaffold manuscript entries, or missing render tools remain unresolved.
- A vendor submodule is dirty or from an unexpected origin.
- A script requires network access or system installation that was not approved and verified.
- A claim, quotation, citation, or source metadata issue is unresolved but hidden from the release record.
