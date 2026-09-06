# Skill/Plugin Sources

External repositories may be placed here for review and optional use.

Do not trust or run external source scripts until inspected.

Expected external repositories are Git submodules:

- `academic-research-skills-codex/`: pinned native plugin source from `https://github.com/Imbad0202/academic-research-skills-codex.git`.
- `research-book-skills/`: source checkout from `https://github.com/CoveMB/research-book-skills.git`.
- `obsidian-skills/`: reviewed Obsidian workflow source checkout from `https://github.com/kepano/obsidian-skills.git`.

Preserve upstream files unchanged.

After cloning this scaffold, initialize them with:

```sh
git submodule update --init --recursive
```

`make install-external-skills` initializes these submodules. Default `bash setup.sh`
also initializes the sources, exposes optional marketplace plugins, and refreshes
RBS and Obsidian wrappers unless `--skip-external-skills` is passed. During the
one-time ARS migration, setup removes an initialized legacy checkout only when
it is clean and at its recorded gitlink; its separate Git module directory and
refs are preserved.
