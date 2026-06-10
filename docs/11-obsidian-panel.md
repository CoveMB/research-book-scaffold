# Obsidian Plugin Setup

Codex Panel is the recommended Obsidian plugin that connects a vault to local Codex workflows. Default setup installs it unless `--skip-obsidian-panel` is passed.

Codex Panel is separate from Obsidian Skills. Obsidian Skills are vendored reference skills with local wrappers for Obsidian syntax and vault mechanics; see `docs/15-obsidian-skills.md`.

Default setup also installs Zotero Integration and Pandoc Reference List unless `--skip-obsidian-research-plugins` is passed. Those plugins support the citation workflow in `docs/07-citation-workflow.md`; they do not replace Zotero, Better BibTeX, or repository citation checks.

## Access and value

It uses `codex app-server`, so sandboxing, approvals, model selection, MCP, and hooks remain governed by the local Codex CLI configuration. It is useful for bounded note work, draft passes, and audits inside Obsidian.

Use it carefully because vault notes can contain untrusted source text and personal material.

Open the repository root as the Obsidian vault. Launch Codex Panel with the vault/repo root as the working directory, or with a path below it. Codex discovers repo-scoped skills from `.agents/skills` in the working directory and parent directories up to the repository root; if the panel starts outside the repo tree, the wrappers will not be visible.

## Prerequisites

- Codex CLI installed and logged in.
- Obsidian installed.
- This project root, unless a different vault path is passed.
- Git or another backup method for important notes.

GUI apps may not inherit the shell `PATH`, so use an absolute Codex executable path in the plugin settings. The setup script writes `.obsidian/plugins/codex-panel/data.json` with `codexPath` when it can find one.

## Manual installation

1. Install and log in to Codex CLI.
2. Download the latest `main.js`, `manifest.json`, and `styles.css` release assets from `https://github.com/murashit/codex-panel/releases/latest`.
3. Place those files at `<vault>/.obsidian/plugins/codex-panel/`.
4. Confirm `manifest.json` has `"id": "codex-panel"`.
5. Write `<vault>/.obsidian/plugins/codex-panel/data.json` with an absolute Codex executable path:

```json
{
  "codexPath": "/absolute/path/to/codex"
}
```

6. Enable Community Plugins in Obsidian.
7. If Codex Panel does not appear, open Settings -> Community plugins and click Reload plugins.
8. Enable Codex Panel.
9. Run the command palette action `Codex Panel: Open panel`.

## Scripted installation

Default setup treats the repository root as the vault root:

```sh
bash setup.sh
```

This creates `.obsidian/` in the project root, installs Codex Panel at `.obsidian/plugins/codex-panel/`, installs Zotero Integration at `.obsidian/plugins/obsidian-zotero-desktop-connector/`, installs Pandoc Reference List at `.obsidian/plugins/obsidian-pandoc-reference-list/`, adds all three plugin IDs to `.obsidian/community-plugins.json`, removes any older agent-plugin enablement entry when present, writes `.obsidian/plugins/codex-panel/data.json` when an absolute Codex executable path is available, and refreshes immediate-use wrappers in `.agents/skills`. It does not create a nested `obsidian-vault/` folder or write Obsidian workspace files. `--force` only allows replacing an existing plugin folder.

The downloaded plugin directories under `.obsidian/plugins/` are ignored because setup can recreate them and plugin settings may contain machine-specific paths. `.obsidian/community-plugins.json` is not ignored so a fork can intentionally commit vault-level plugin enablement defaults after review.

If `.obsidian/plugins/codex-panel/` already exists, setup will not replace it unless `--force` is passed. The research plugin installer accepts existing Zotero Integration and Pandoc Reference List folders only after checking their required files and manifest IDs. When a stale or broken plugin folder is suspected, rerun setup with `--force`, then run the matching check.

By default, setup does not modify Obsidian's app-level vault registry. If Obsidian has never opened this project root as a vault, a direct `obsidian://open?path=...` launch can report that the vault is not found even though the vault-local `.obsidian/` files exist.

For GUI QA or first-time local setup where direct Obsidian URLs need to work immediately, opt in to app-level registration:

```sh
python3 scripts/operations/setup/setup_environment.py --register-obsidian-vault
```

This writes the project path into the platform Obsidian app registry, such as `~/Library/Application Support/obsidian/obsidian.json` on macOS. It preserves existing vault entries, does not duplicate an already registered vault path, and does not bypass Obsidian trust or plugin approval prompts. Use the normal Obsidian `Open folder as vault` flow instead when you do not want setup to write user app state outside the repository.

If `.obsidian/community-plugins.json` exists but is not a JSON list, setup fails instead of overwriting it. Fix the file manually or let Obsidian regenerate it before rerunning setup.

Skip Obsidian/Codex Panel setup when local agent work will stay in the CLI or another Markdown editor:

```sh
python3 scripts/operations/setup/setup_environment.py --skip-obsidian-panel
```

After a skipped setup, do not claim Codex Panel coverage until `make install-obsidian-panel` and `make check-obsidian-panel` pass.

Use an explicit path only when installing into a different vault:

```sh
OBSIDIAN_VAULT=/path/to/vault bash scripts/operations/obsidian/install_obsidian_panel.sh
python3 scripts/operations/setup/setup_environment.py --obsidian-vault /path/to/vault
```

The installer refuses to replace an existing plugin folder unless `--force` is passed. It installs from published release assets only and rejects zip archive inputs.

Health check:

```sh
make check-obsidian-panel
make check-obsidian-research-plugins
```

Expected result:

- plugin files exist under `.obsidian/plugins/codex-panel/`
- `manifest.json` has ID `codex-panel`
- `.obsidian/community-plugins.json` lists `codex-panel`
- `.obsidian/plugins/codex-panel/data.json` contains an absolute executable `codexPath`
- `codex --version` exits 0 through that configured path
- `codex app-server --help` exits 0 through that configured path
- research plugin files exist under `.obsidian/plugins/obsidian-zotero-desktop-connector/` and `.obsidian/plugins/obsidian-pandoc-reference-list/`
- research plugin manifests have the expected IDs
- `.obsidian/community-plugins.json` lists both research plugin IDs

If the check fails:

- missing or non-executable `codexPath`: rerun setup from the shell where `codex --version` works, or edit `.obsidian/plugins/codex-panel/data.json` to an absolute executable path
- disabled community plugin: enable Codex Panel in Obsidian Community plugins, then rerun the check
- manifest ID mismatch or missing plugin files: rerun `bash setup.sh --force`, then rerun the check
- `codex app-server --help` failure: update or reinstall Codex CLI before using Codex Panel
- missing research plugin directory: rerun `make install-obsidian-research-plugins`, then rerun `make check-obsidian-research-plugins`
- invalid existing research plugin folder or manifest mismatch: rerun `python3 scripts/operations/obsidian/obsidian_research_plugins.py install --force`, then rerun `make check-obsidian-research-plugins`
- missing `pandoc`: the plugin can still be installed, but Pandoc Reference List cannot render the sidebar references until Pandoc is available

This check verifies the local plugin install and Codex command. It cannot prove the runtime working directory used by the panel. Use the read-only prompts below inside Codex Panel to verify the vault/repo root context and repo-scoped skill discovery.

## Recommended modes

| Mode | Use |
| --- | --- |
| Reading mode | Summarize project rules or one note |
| Note-generation mode | Create one structured note from supplied material |
| Drafting mode | Edit one section from existing notes |
| Audit mode | Review claims, citations, or continuity |
| Command mode | Run narrow checks with approval |

## Use and avoid

Use it for one note, one section, one audit, or one check at a time.

Avoid prompts such as:

```text
Rewrite my whole vault.
Fix all files automatically.
Run whatever commands are needed.
Create citations from memory.
```

Safe first prompt:

```text
Read AGENTS.md and summarize the project rules. Do not edit anything.
```

Skill availability prompt:

```text
Read AGENTS.md and list the repo-scoped skills available from .agents/skills. Do not edit files.
```

Obsidian wrapper test:

```text
Use $obsidian-research-markdown to inspect notes/README.md and explain which Obsidian Markdown rules apply. Do not edit files.
```

If Codex Panel does not see repo-scoped skills, verify that Obsidian opened the project root as the vault root and that Codex Panel launched Codex from the repo root or a path below it. Then run `python3 scripts/operations/vendors/check_external_skills.py` to confirm wrappers and vendors are present.

Read `AGENTS.md`, `docs/03-agent-orchestration.md`, `docs/05-security.md`, `docs/07-citation-workflow.md`, and `docs/15-obsidian-skills.md` before using it for edits that involve Obsidian-specific syntax, Bases, Canvas files, CLI operations, or web ingest.

## Research Plugin Workflow

Use Zotero Integration to search Zotero and insert Pandoc-style citations into notes or manuscript files. Keep the inserted form as `[@citekey]`, `[-@citekey]`, or `[@first; @second]` so Quarto and the citation checker can read it.

Use Pandoc Reference List while drafting to preview the references for citekeys in the active note. Configure it with `bibliography/references.bib`; add a CSL path only when the project has selected a citation style.

Imported annotations and Zotero notes belong in `notes/01-source-notes/` after review. Keep direct quotations, paraphrases, interpretation, and missing locators separate. Run `make check-citations` before treating inserted citekeys as manuscript-ready.
