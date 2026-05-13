# Vendor

External repositories may be placed here for review and optional use.

Do not trust or run vendored scripts until inspected.

Expected external repositories are Git submodules:

- `academic-research-skills/`: vendored from `https://github.com/Imbad0202/academic-research-skills.git`.
- `research-book-skills/`: vendored from `https://github.com/CoveMB/research-book-skills.git`.
- `subagent-orchestration-plugin/`: optional plugin vendored from `https://github.com/CoveMB/subagent-orchestration-plugin.git`.

Preserve upstream files unchanged.

After cloning this scaffold, initialize them with:

```sh
git submodule update --init --recursive
```

The setup script also initializes these submodules.
