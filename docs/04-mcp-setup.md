# MCP setup

MCP lets an agent use local tools through explicit servers and permissions. Keep access narrow.

## Safe server categories

| Category | Typical use | Default |
| --- | --- | --- |
| filesystem | Read project files | Read-only |
| Zotero | Search local library | Read-only |
| browser/search | Look up source metadata | Prompted |
| Git | Inspect status and diffs | Read-only |
| shell | Run checks | Restricted |
| database | Query structured research data | Read-only |

## Permission modes

| Mode | Access |
| --- | --- |
| Discovery mode | Read docs, list files, inspect metadata |
| Reading mode | Read notes, sources, and bibliography |
| Synthesis mode | Create notes from supplied material |
| Drafting mode | Edit bounded manuscript sections |
| Audit mode | Read draft and write audit findings |
| Export mode | Run render and check commands |

## Rules

- Start read-only.
- Grant write access only for a named folder and task.
- Keep shell access restricted to known checks and scripts.
- Do not expose secrets through MCP config.
- Review MCP server settings before enabling them.
