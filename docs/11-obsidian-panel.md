# Codex Panel For Obsidian

Codex Panel is the recommended Obsidian plugin that connects a vault to local Codex workflows. Default setup installs it unless `--skip-obsidian-panel` is passed.

## Access and value

It uses `codex app-server`, so sandboxing, approvals, model selection, MCP, and hooks remain governed by the local Codex CLI configuration. It is useful for bounded note work, draft passes, and audits inside Obsidian.

Use it carefully because vault notes can contain untrusted source text and personal material.

## Prerequisites

- Codex CLI installed and logged in.
- Obsidian installed.
- This project root, unless a different vault path is passed.
- Git or another backup method for important notes.

GUI apps may not inherit the shell `PATH`, so the plugin settings should use an absolute Codex executable path. The setup script writes `.obsidian/plugins/codex-panel/data.json` with `codexPath` when it can find one.

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
python3 scripts/operations/setup/setup_environment.py
```

This creates `.obsidian/` in the project root, installs the plugin at `.obsidian/plugins/codex-panel/`, adds `codex-panel` to `.obsidian/community-plugins.json`, removes any older agent-plugin enablement entry when present, and writes `.obsidian/plugins/codex-panel/data.json` when an absolute Codex executable path is available. It does not create a nested `obsidian-vault/` folder or write Obsidian workspace files. `--force` only allows replacing an existing plugin folder.

By default, setup does not modify Obsidian's app-level vault registry. If Obsidian has never opened this project root as a vault, a direct `obsidian://open?path=...` launch can report that the vault is not found even though the vault-local `.obsidian/` files exist.

For GUI QA or first-time local setup where direct Obsidian URLs should work immediately, opt in to app-level registration:

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
python3 scripts/operations/obsidian/check_obsidian_panel.py
```

Expected result:

- plugin files exist under `.obsidian/plugins/codex-panel/`
- `manifest.json` has ID `codex-panel`
- `.obsidian/community-plugins.json` lists `codex-panel`
- `.obsidian/plugins/codex-panel/data.json` contains an absolute executable `codexPath`
- `codex --version` exits 0 through that configured path
- `codex app-server --help` exits 0 through that configured path

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

Read `AGENTS.md`, `docs/03-agent-orchestration.md`, `docs/05-security.md`, and `docs/07-citation-workflow.md` before using it for edits.
