# Scholarly research and writing boilerplate

Clean scaffold for source management, notes, manuscript drafting, citation checks, research audits, and local agent workflows. It is domain-neutral by design.

## Four-layer architecture

| Layer | Folder | Source of truth |
| --- | --- | --- |
| Sources and bibliography | `bibliography/`, Zotero | Zotero or `bibliography/references.bib` |
| Notes and knowledge base | `notes/`, `research/` | Structured notes and audit files |
| Manuscript production | `manuscript/`, `exports/` | Quarto source files |
| Agent orchestration | `AGENTS.md`, `.agents/skills/`, `docs/` | Repo-scoped instructions |

## Documentation map

Use `docs/README.md` as the short route through the documentation. It points to
the setup, workflow, citation, audit, Obsidian, external-skill, and pre-commit
docs without repeating every command from the Makefile.

## Default book-project setup

For a serious book project, set up a separate book repository before running
`setup.sh`. This preserves this scaffold as `upstream`, points `origin` at your
book repository, and keeps later scaffold updates mergeable.

```sh
git clone --recurse-submodules git@github.com:CoveMB/research-book-scaffold.git <book-repo>
cd <book-repo>
git remote rename origin upstream
git remote add origin git@github.com:<account>/<book-repo>.git
git push -u origin main
bash setup.sh
make doctor
make check-obsidian-panel
make check-obsidian-research-plugins
make audit
```

If you use GitHub's fork flow instead, fork
`CoveMB/research-book-scaffold`, clone your fork with submodules, and keep the
original scaffold remote available as `upstream` before running setup.

If the repository was cloned without submodules, run:

```sh
git submodule update --init --recursive
```

`bash setup.sh` requires Python 3.11 or newer. It treats the project root as the
Obsidian vault root, installs Codex Panel unless skipped, installs the
recommended Zotero/Pandoc/QMD Obsidian plugins unless skipped, initializes
external skill/plugin sources, refreshes repo-scoped wrappers under `.agents/skills`, and
keeps plugin marketplace entries optional.

Default setup uses network access for submodules and Obsidian plugin release
assets. Use `bash setup.sh --dry-run` first when you want a preview,
`bash setup.sh --skip-external-skills` when you only want local tool and
Obsidian plugin setup, or
`bash setup.sh --skip-external-skills --skip-obsidian-panel --skip-obsidian-research-plugins`
for an offline or CLI-only pass.

### Manual setup after `setup.sh`

The setup script writes project-local files, but a few GUI and tool settings still need a human pass. Do these before treating the project as ready for daily writing.

1. Read the final setup report.
   - Run every check it lists, especially `make doctor`, `make check-obsidian-panel`, `make check-obsidian-research-plugins`, and `make audit`.
   - If setup was run with `--skip-obsidian-panel` or `--skip-obsidian-research-plugins`, do not claim that plugin coverage until the matching install and check targets pass.

2. Open the correct Obsidian vault.
   - If setup was run with `--register-obsidian-vault`, open the project from Obsidian's vault list or with an `obsidian://open?path=...` URL.
   - Otherwise open Obsidian, select the vault switcher, choose `Manage Vaults...`, then use `Open folder as vault` and select this repository root.
   - Confirm `notes/`, `research/`, and `manuscript/` are visible. The default Obsidian visibility settings may hide selected repository infrastructure and `bibliography/` from the File Explorer, while keeping skill/plugin source documentation visible. See `docs/11-obsidian-panel.md` to change that behavior. If those working folders are not visible, Obsidian is probably showing a different vault.

3. Confirm the Obsidian plugins are visible and enabled.
   - In Obsidian, open `Settings -> Community plugins`.
   - If the plugin list looks out of date, click the refresh icon to reload plugins.
   - Confirm these installed plugins are enabled: `Codex Panel`, `Zotero Integration`, `Pandoc Reference List`, and `qmd as md`.
   - qmd as md requires Obsidian Desktop 1.8.0 or newer. It will not load on Obsidian mobile.
   - If Zotero Integration, Pandoc Reference List, or qmd as md is missing, run `make install-obsidian-research-plugins`, then `make check-obsidian-research-plugins`.

4. Check Codex Panel inside Obsidian.
   - Run the command palette action `Codex Panel: Open panel`.
   - If Codex Panel cannot find Codex, set the plugin's Codex executable setting to an absolute path, then rerun `make check-obsidian-panel`.
   - Use a read-only smoke prompt first: `Read AGENTS.md and summarize the project rules. Do not edit anything.`

5. Set up Zotero and Better BibTeX.
   - Install Better BibTeX in Zotero if it is not already installed.
   - Add or verify the project sources in a Zotero collection.
   - Right-click the project collection and choose `Export Collection...`.
   - Use format `Better BibTeX`, check `Keep updated`, and save the export as `bibliography/references.bib`.
   - Do not enable Better BibTeX git push from this working copy. Commit bibliography changes through the normal project workflow.
   - Run `python3 scripts/research-writing/check_citations.py --include-notes`.

6. Configure the Obsidian research plugins.
   - Keep Zotero open while using Zotero Integration.
   - Setup seeds Zotero Integration with a `Pandoc citekey` format and autocomplete template for citations such as `[@citekey]`.
   - Setup seeds Pandoc Reference List with `./bibliography/references.bib` and enables citekey completion from that file.
   - Setup also points Pandoc Reference List at the resolved absolute path for `bibliography/csl/ieee.csl`, the same IEEE CSL file used by the default Quarto manuscript config. The plugin resolves bibliography paths from the vault root, but local CSL paths must be absolute.
   - Setup seeds qmd as md so Obsidian opens `.qmd` manuscript files as Markdown text, shows YAML files such as `manuscript/_quarto.yml`, enables the Quarto outline, and leaves PDF auto-open off.
   - To insert from `references.bib`, open a Markdown note, type at least two characters after `@`, such as `@po`, then use the suggestion list. On macOS, `Cmd+Enter` inserts the bracketed Pandoc form `[@citekey]`; on Windows or Linux, use `Ctrl+Enter`.
   - Check those plugin settings in Obsidian before serious drafting, especially after manual plugin changes.
   - If the project later changes citation style, update both `manuscript/_quarto.yml` and the Pandoc Reference List custom CSL path.
   - Treat plugin output as a convenience layer. Zotero or `bibliography/references.bib` remains the citation source of truth, and Quarto remains the manuscript renderer.

7. Install render tools when export work is in scope.
   - Install Quarto before running `make render`, `make render-html`, `make render-pdf`, or `make render-docx`.
   - Install Pandoc, or confirm the Quarto-provided Pandoc is available, before relying on Pandoc Reference List live previews.
   - For PDF output, install TinyTeX with `quarto install tinytex --update-path`, open a new shell, then verify `lualatex --version` and `bibtex --version`.

8. Start the project files, then resolve the initializer's follow-up list.
   - Run `python3 scripts/start_project.py --dry-run` first.
   - Run `make start-project`.
   - Resolve any final-summary items about Zotero, Better BibTeX, empty bibliography files, citation style, target venue or publisher, Obsidian setup, placeholders, or missing Quarto.

After setup, read `AGENTS.md`, add verified sources to Zotero or `bibliography/references.bib`, create notes from `templates/`, and draft in `manuscript/`. Obsidian is the recommended vault interface for local agent and citation workflows; pass `--skip-obsidian-panel --skip-obsidian-research-plugins` for CLI or Markdown-editor-only work.

Pull scaffold improvements into the book repository at planned maintenance
points:

```sh
git fetch upstream --prune
git merge upstream/main
git submodule update --init --recursive
make audit
```

Keep book-specific material in `notes/`, `research/`, `bibliography/`,
`manuscript/`, and `project-start.yml`. Keep scaffold-owned files such as
`scripts/`, `.agents/`, `docs/`, `templates/`, and `skill-plugins/` generic when
possible so upstream merges stay small and reviewable. Packaging is better
reserved for reusable tools or checks later; the full scaffold is a living file
tree, not an installable library alone.

## Common commands

```sh
make doctor
make start-project
make install-hooks
make precommit-run
make scaffold-audit
make audit
make release-audit
make manuscript-release-audit
make render
make render-html
make render-pdf
make render-docx
make check-citations-strict
make install-external-skills
make install-obsidian-research-plugins
```

## Start a real project

Run the project initializer before serious writing begins:

```sh
python3 scripts/start_project.py --dry-run
make start-project
```

The script asks for project identity, scholarly framing, output preferences,
citation setup, and local workflow choices. It writes a normalized
`project-start.yml`, creates or updates a project charter from
`templates/project-charter-template.md`, updates scaffold-owned manuscript setup
files, creates empty chapter or section stubs, and creates an empty bibliography
placeholder only if the configured bibliography file is missing or blank.
Before the interactive questions, it prints a short preflight summary covering
the saved answers file, bibliography status, local render tools, the audit
target, and existing initializer targets.

For repeatable setup, provide answers from JSON or the simple YAML file the
script writes:

```sh
python3 scripts/start_project.py --answers project-start.yml --dry-run
python3 scripts/start_project.py --answers project-start.yml --non-interactive
```

If `project-start.yml` already exists and you run the interactive command, the
script uses that file as saved answers and asks only for missing values. Edit the
file first when you want to change an existing answer.

The initializer will not invent citations, sources, page numbers, quotations,
claims, chapter arguments, or bibliographic metadata. Unknown scholarly decisions
stay marked as unresolved; when strict placeholder detection is enabled, Markdown
outputs use release-check-visible markers. Existing non-scaffold
manuscript content is preserved unless `--force` is passed, and `--dry-run` shows
the planned diff before any file changes. Use `--force --dry-run` first when you
need to inspect protected files that would be replaced. Use `--skip-audit` or
`--skip-render` when you only want file initialization.

The final summary includes manual next steps. Expect it to call out Zotero and
Better BibTeX setup, empty bibliography files, unresolved citation style or
publisher decisions, Obsidian setup, release-visible placeholders, or missing
Quarto when those apply.

## Templates

Use `templates/` for local source notes, concept notes, claim notes, audits, source matrices, project charters, and synthesis memos. Plugin-owned chapter brief, search log, literature map, and case-study templates are listed in `templates/README.md`.

## Repo-scoped skills and plugins

Immediate Codex skill availability comes from wrapper skills in `.agents/skills/<skill-name>/SKILL.md`. Launch Codex Panel with this project root, or a path below it, as the working directory so Codex can discover those repo-scoped skills.

The external layers are separate:

- `skill-plugins/` stores upstream source copies pinned as submodules.
- `.agents/skills/` stores safe local wrappers that are immediately usable after setup.
- `.agents/plugins/marketplace.json` keeps optional plugin exposure for users who choose to install repo marketplace plugins later.

Available wrappers include local scaffold skills, `ars-*` Academic Research Skills wrappers, `rbs-*` Research Book Skills wrappers, guarded `subagent-safe-*` wrappers, and `obsidian-research-*` Obsidian Skills wrappers. Use them for bounded tasks such as accessibility support, research-intent routing, search planning, candidate dedupe, source-note conversion, evidence extraction, claim traceability, claim audits, figure/table integrity checks, scholarly-integrity checks, workflow logging, release/privacy review, proposal comps, drafting from notes, final manuscript checks, Obsidian syntax/mechanics, and orchestration planning when subagents would materially help. Marketplace exposure is useful, but it is not the immediate availability path.

## Default local agent integration

- Codex Panel connects this project root to local agent workflows as an Obsidian vault. `bash setup.sh` creates `.obsidian/`, installs Codex Panel in the repository root, enables `codex-panel` in `.obsidian/community-plugins.json`, and writes an absolute Codex executable path in the plugin settings when one is available. For first-time GUI QA, pass `--register-obsidian-vault` to also register the project root in Obsidian's app-level vault registry so `obsidian://open?path=...` can find it. Pass `--skip-obsidian-panel` to leave Obsidian/Codex Panel setup for later, or pass `--obsidian-vault PATH` only for a different vault.
- Zotero Integration and Pandoc Reference List are installed by default for citation work in Obsidian. Setup configures Zotero Integration to insert Pandoc-style citekeys such as `[@citekey]`. It points Pandoc Reference List at `./bibliography/references.bib`, uses an absolute path to the tracked IEEE CSL file at `bibliography/csl/ieee.csl`, and enables citekey completion. Type `@` plus at least two characters in a Markdown note to suggest citekeys from `bibliography/references.bib`; use `Cmd+Enter` on macOS or `Ctrl+Enter` on Windows or Linux to insert `[@citekey]`. Zotero Integration can also import Zotero notes or annotations. Pandoc Reference List previews references for citekeys in the current note. Better BibTeX remains a Zotero-side prerequisite and keeps `bibliography/references.bib` current.
- qmd as md is installed by default as the Quarto manuscript authoring plugin. Setup enables `.qmd` linking, points the plugin at `quarto` or the resolved Quarto executable when available, shows YAML files for `_quarto.yml`, enables the Quarto outline, and keeps plugin PDF auto-open disabled. Use it for Obsidian editing and preview, then use repository render targets and checks for export decisions.

## Optional external integrations

- Academic Research Skills can be added from `Imbad0202/academic-research-skills` and exposed through safe wrapper skills.
- Research Book Skills can be added from `CoveMB/research-book-skills`, exposed through immediate `rbs-*` wrappers, and optionally exposed as a repo marketplace plugin from `skill-plugins/research-book-skills/`.
- Subagent Orchestrator can be added from `CoveMB/subagent-orchestration-plugin` and exposed from `skill-plugins/subagent-orchestration-plugin/plugin/subagent-orchestrator/`.
- Obsidian Skills can be added from `kepano/obsidian-skills` and exposed through local wrappers for Obsidian Markdown, Bases, JSON Canvas, Obsidian CLI, and Defuddle guidance.

External repositories stay optional. Review upstream files before use. Default external-skill setup refreshes guarded Subagent Orchestrator wrappers and marketplace exposure without executing the external installer or enabling hooks, project agents, global config, or global agents. Obsidian Skills are checked out and wrapped locally; this scaffold does not install them globally.

Obsidian setup does not create a nested vault folder or write workspace files. It installs Codex Panel, Zotero Integration, Pandoc Reference List, and qmd as md from published release assets with SHA256 digests, adds their plugin IDs to `.obsidian/community-plugins.json`, writes `.obsidian/plugins/codex-panel/data.json`, and seeds safe citation and QMD plugin settings. Obsidian app-level vault registration is opt-in because it writes user app state outside the repository. `--force` only allows replacing an existing plugin folder.

The external repositories under `skill-plugins/` are Git submodules. `bash setup.sh` and `make install-external-skills` initialize them. To do that manually, run:

```sh
git submodule update --init --recursive
```

Use `bash setup.sh --skip-obsidian-panel --skip-obsidian-research-plugins` when all Obsidian plugin coverage is out of scope. Use `bash setup.sh --skip-external-skills` only when you do not want source initialization or wrapper refresh during setup.

In Codex Panel, verify repo-scoped skills with a read-only prompt:

```text
Read AGENTS.md and list the repo-scoped skills available from .agents/skills. Do not edit files.
```

See `docs/15-obsidian-skills.md` for Obsidian Skills usage, wrapper boundaries, optional agent-native installation notes, folder conventions, checks, and troubleshooting.

## Pre-commit hooks

Use lightweight hooks to catch obvious file hygiene, Python syntax, citation, and internal-link issues before commits:

```sh
python3 -m pip install pre-commit
make install-hooks
make precommit-run
```

The hooks wrap existing Makefile checks and avoid Quarto renders, network checks, source refresh workflows, and manuscript readiness enforcement during normal commits. Use `SKIP=<hook-id> git commit` or `git commit --no-verify` for intentional bypasses. See `docs/16-pre-commit-hooks.md` for hook scope, blocking behavior, manual runs, and release-only checks.

## Do not automate

- Secrets, API keys, or credentials.
- Citation creation from memory.
- Whole-vault rewrites.
- System installs without explicit permission.
- Execution of unreviewed external source scripts.

## License

This scaffold is MIT licensed. External integrations keep their upstream licenses; review `skill-plugins/README.md` before redistribution or commercial use.
