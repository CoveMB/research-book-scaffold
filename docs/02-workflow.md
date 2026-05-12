# Workflow

## Short path

1. Create a project charter in `templates/project-charter-template.md`.
2. Plan repeatable searches in `research/search-logs/`.
3. Store verified sources in Zotero or `bibliography/references.bib`.
4. Create source notes in `notes/01-source-notes/`.
5. Map debates in `notes/02-literature-maps/`.
6. Track claims in `notes/04-claim-ledger/`.
7. Draft chapter briefs in `notes/07-chapter-briefs/`.
8. Draft only from notes and briefs in `manuscript/`.
9. Audit citations, placeholders, links, claims, and continuity before export with `make release-audit`.
10. Render exports only after checks pass and known limitations are recorded.

## Full sequence

| Step | Purpose | Inputs | Outputs | Tool | Workflow support | Gate |
| --- | --- | --- | --- | --- | --- | --- |
| 1. Project charter | Set scope | User brief | Charter note | `templates/project-charter-template.md` | RBS research agenda workflow | Boundaries clear |
| 2. Research question refinement | Narrow inquiry | Charter | Questions | Notes | RBS or ARS planning workflow | Questions testable |
| 3. Search planning | Plan discovery | Questions | Search plan | `vendor/research-book-skills/skills/systematic-source-discovery/assets/search-log-template.md` | RBS source discovery workflow | Query reproducible |
| 4. Source discovery | Find candidates | Search plan | Candidate list | Zotero, indexes | RBS source discovery workflow | Criteria applied |
| 5. Source triage | Filter sources | Candidates | Keep/reject notes | Matrix | RBS methodology/source audit workflow | Reasons recorded |
| 6. Source storage | Preserve metadata | Kept sources | BibTeX records | Zotero | Citation workflow docs | Citekeys stable |
| 7. Reading and annotation | Extract evidence | Sources | Annotations | Zotero, notes | Manual first pass | Pages tracked |
| 8. Source notes | Summarize source | Annotations | Source note | Template | RBS bibliography/source workflows | Limits included |
| 9. Literature mapping | Compare sources | Source notes | Literature map | `vendor/research-book-skills/skills/literature-review-mapper/assets/lit-map-template.md` | RBS literature map workflow | Debates visible |
| 10. Claim ledger | Track claims | Notes, map | Claim notes | Template | RBS claim-evidence workflow | Evidence status set |
| 11. Chapter brief | Plan section | Claims, map | Brief | `vendor/research-book-skills/skills/chapter-architecture/assets/chapter-brief-template.md` | RBS chapter architecture workflow | Gaps marked |
| 12. Drafting from notes | Draft prose | Brief, notes | Draft | Quarto | RBS prose/chapter workflows | No unsupported claims |
| 13. Citation audit | Check citations | Draft, BibTeX | Audit note | Script | RBS citation integrity workflow | Citekeys valid |
| 14. Claim audit | Check support | Draft, claims | Audit note | Notes | RBS claim-evidence workflow | Weak claims flagged |
| 15. Red-team review | Challenge argument | Draft | Review note | Notes | RBS peer-review workflows | Objections logged |
| 16. Continuity review | Check consistency | Drafts | Review note | Notes | RBS continuity workflow | Terms consistent |
| 17. Style revision | Improve prose | Audited draft | Revised draft | Editor | RBS prose editor workflow | Meaning preserved |
| 18. Final manuscript check | Prepare export | Draft, audits | Readiness note | `make release-audit` | RBS continuity/citation workflows | Checks pass |
| 19. Export | Render output | Quarto source | HTML, PDF, DOCX | `make render-*` | Final check docs | Output reviewed |
| 20. Version/archive | Preserve state | Final files | Commit or archive | Git | Project rules in `AGENTS.md` | Status clean |
