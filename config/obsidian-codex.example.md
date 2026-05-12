# Obsidian plugin safe settings

Use this file as a checklist. Do not store provider keys or personal credentials here.

## Recommended settings

- Use local CLI login where possible.
- Keep command approval enabled.
- Keep file-write approval enabled.
- Scope the working directory to the vault or this project.
- Test on non-critical notes first.
- Keep Git or another backup available before edits.
- Do not give broad shell access for routine note work.

## Provider keys

- Do not store custom provider keys unless necessary.
- If keys are required, store them in user-level or environment config outside this repository.
- Never paste keys into notes, prompts, or tracked config files.

## Safe first prompts

```text
Read AGENTS.md and summarize the project rules. Do not edit anything.
```

```text
Create a test note in notes/00-inbox/ named plugin-test.md. Do not modify existing notes.
```

```text
Run make doctor and summarize the result. Do not change files.
```

## Prompts to avoid

```text
Rewrite my whole vault.
Fix all files automatically.
Run whatever commands are needed.
Create citations from memory.
```

## Later commands

Default setup uses the project root as the vault root:

```sh
python3 scripts/setup_environment.py
```

Install into a different vault only when needed:

```sh
OBSIDIAN_VAULT=/path/to/vault bash scripts/install_obsidian_codex.sh
```

For a pinned install, pass a reviewed release URL and SHA-256 checksum to `scripts/setup_environment.py`.

Check installation:

```sh
python3 scripts/check_obsidian_codex.py
```
