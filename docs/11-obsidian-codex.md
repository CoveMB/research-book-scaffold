# Obsidian Codex

Obsidian Codex is an optional Obsidian plugin that connects a vault to local agent workflows.

## Access and value

It may read vault files, propose edits, and run approved commands depending on settings. It is useful for bounded note work, draft passes, and audits inside Obsidian.

Use it carefully because vault notes can contain untrusted source text and personal material.

## Prerequisites

- Codex CLI installed and logged in.
- Obsidian installed.
- A vault path selected by the user.
- Git or another backup method for important notes.

## Manual installation

1. Download the latest release from `https://github.com/AKin-lvyifang/obsidian-codex/releases/latest`.
2. Place the plugin folder at `<vault>/.obsidian/plugins/obsidian-codex/`.
3. Confirm `main.js`, `manifest.json`, and `styles.css` exist.
4. Restart Obsidian.
5. Enable Community Plugins.
6. Enable Codex for Obsidian.

## Scripted installation

Install only with an explicit vault path:

```sh
OBSIDIAN_VAULT=/path/to/vault bash scripts/install_obsidian_codex.sh
python3 scripts/setup_environment.py --with-obsidian-codex --obsidian-vault /path/to/vault
```

The installer refuses to replace an existing plugin folder unless `--force` is passed.
For reproducible installs, pass a reviewed release URL and checksum:

```sh
python3 scripts/setup_environment.py --with-obsidian-codex --obsidian-vault /path/to/vault --obsidian-release-url https://example.invalid/release.zip --obsidian-release-sha256 SHA256
```

Health check:

```sh
OBSIDIAN_VAULT=/path/to/vault python3 scripts/check_obsidian_codex.py
```

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
