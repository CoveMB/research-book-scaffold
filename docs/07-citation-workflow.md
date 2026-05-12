# Citation workflow

## Source of truth

Zotero or `bibliography/references.bib` is the citation source of truth. Notes and drafts must match it.

## Citekeys

- Use Better BibTeX citekeys when possible.
- Keep citekeys stable after notes or drafts reference them.
- Check manuscript citekeys against `bibliography/references.bib`.

## Syntax

Use Quarto or Pandoc citation forms:

```md
[@citekey]
[-@citekey]
[@first; @second]
```

## Missing support

Use visible markers for missing support until scripts are added:

```md
{{citation needed}}
{{verify}}
```

## Page numbers

Add page numbers when a claim depends on a specific passage. If page numbers are unknown, mark the gap.

## Web sources

Record title, author or organization, URL, access date when needed, and archive link when available.

## AI output

AI-generated citations are untrusted until verified against Zotero, BibTeX, or the source itself.
