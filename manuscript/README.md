# Manuscript

Quarto book files live here.

Keep manuscript prose separate from notes, source matrices, and audits.

Obsidian can edit these files when the repository root is open as the vault.
For citation previews, use Zotero Integration and Pandoc Reference List as
described in `../docs/08-writing-workflow.md`; repository citation checks and
Quarto rendering remain authoritative.

Run the manuscript release gate before sharing manuscript output:

```sh
make manuscript-release-audit
```

From the repository root, use the scaffold render targets:

```sh
make render
make render-html
make render-pdf
make render-docx
```

These targets render the `manuscript/` Quarto project, run preflight checks for
Quarto and the PDF engine when needed, and mirror generated files from
`manuscript/_book` into `exports/`. Direct Quarto rendering also works from this
folder when the local render tools are installed:

```sh
quarto render
```
