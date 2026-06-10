# Manuscript

Quarto book files live here.

Keep manuscript prose separate from notes, source matrices, and audits.

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

These targets render the `manuscript/` Quarto project and run preflight checks
for Quarto and the PDF engine when needed. Direct Quarto rendering also works
from this folder when the local render tools are installed:

```sh
quarto render
```
