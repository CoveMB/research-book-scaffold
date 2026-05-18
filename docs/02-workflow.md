# Workflow

## Short path

1. Create a project charter from `templates/project-charter-template.md`.
2. Plan repeatable searches in `research/search-logs/`.
3. Dedupe and screen candidate sources before adding them to the bibliography.
4. Store verified sources in Zotero or `bibliography/references.bib`.
5. Convert annotations into source notes in `notes/01-source-notes/`.
6. Extract comparable evidence into `research/extraction-tables/` or `research/source-matrices/`.
7. Map debates in `notes/02-literature-maps/`.
8. Track claims in `notes/04-claim-ledger/`.
9. Trace major claims back to notes, citekeys, and locators.
10. Draft chapter briefs in `notes/07-chapter-briefs/`.
11. Draft only from notes and briefs in `manuscript/`.
12. Audit citations, placeholders, links, claims, continuity, and release risks before export with `make release-audit`.
13. Render exports only after checks pass and known limitations are recorded.

## Full sequence

| Step | Purpose | Inputs | Outputs | Tool | Workflow support | Gate |
| --- | --- | --- | --- | --- | --- | --- |
| 1. Project charter | Set scope | User brief | Charter note | Create from `templates/project-charter-template.md` | RBS research agenda workflow | Boundaries clear |
| 2. Research question refinement | Narrow inquiry | Charter | Questions | Notes | RBS or ARS planning workflow | Questions testable |
| 3. Search planning | Plan discovery | Questions | Search plan | `vendor/research-book-skills/skills/systematic-source-discovery/assets/search-log-template.md` | RBS source discovery workflow | Query reproducible |
| 4. Source discovery | Find candidates | Search plan | Candidate list | Zotero, indexes | RBS source discovery workflow | Criteria applied |
| 5. Candidate dedupe and screening | Filter duplicates and search results | Candidate exports | Candidate matrix | CSV/BIB/RIS or pasted records | RBS discovery runner/deduper workflow | Duplicate and rejection reasons recorded |
| 6. Source triage | Assess source fit and credibility | Candidates | Keep/reject notes | Matrix | RBS methodology/source audit workflow | Reasons recorded |
| 7. Source storage | Preserve metadata | Kept sources | BibTeX records | Zotero | Citation workflow docs | Citekeys stable |
| 8. Reading and annotation | Extract evidence | Sources | Annotations | Zotero, notes | Manual first pass | Pages tracked |
| 9. Source notes | Convert annotations into source-bound notes | Annotations | Source note | Template | RBS annotation-to-source-note workflow | Quote, paraphrase, metadata, and locator gaps preserved |
| 10. Evidence extraction | Compare evidence across sources | Source notes | Extraction table or source matrix | Templates | RBS extraction-table workflow | Evidence is comparable before synthesis |
| 11. Literature mapping | Compare sources | Source notes, matrices | Literature map | `vendor/research-book-skills/skills/literature-review-mapper/assets/lit-map-template.md` | RBS literature map workflow | Debates visible |
| 12. Claim ledger | Track claims | Notes, map | Claim notes | Template | RBS claim-evidence workflow | Evidence status set |
| 13. Claim traceability | Link claims to evidence chain | Claims, notes, citekeys | Traceability map | Notes | RBS claim-traceability workflow | Orphan claims and missing locators visible |
| 14. Chapter brief | Plan section | Claims, map | Brief | `vendor/research-book-skills/skills/chapter-architecture/assets/chapter-brief-template.md` | RBS chapter architecture workflow | Gaps marked |
| 15. Drafting from notes | Draft prose | Brief, notes | Draft | Quarto | RBS prose/chapter workflows | No unsupported claims |
| 16. Citation audit | Check citations | Draft, BibTeX | Audit note | Script | RBS citation integrity workflow | Citekeys valid |
| 17. Claim audit | Check support | Draft, claims | Audit note | Notes | RBS claim-evidence workflow | Weak claims flagged |
| 18. Red-team review | Challenge argument | Draft | Review note | Notes | RBS peer-review workflows | Objections logged |
| 19. Continuity review | Check consistency | Drafts | Review note | Notes | RBS continuity workflow | Terms consistent |
| 20. Style revision | Improve prose | Audited draft | Revised draft | Editor | RBS prose editor workflow | Meaning preserved |
| 21. Release-risk audit | Check external-sharing risks | Notes, drafts, exports | Release audit | Notes | RBS rights/privacy release workflow | Privacy, quote, license, and copied-text risks marked |
| 22. Proposal comps verification | Check comparable titles | Proposal, comps | Comps table | Sources | RBS book-comps verifier workflow | Publication and positioning claims verified |
| 23. Final manuscript check | Prepare export | Draft, audits | Readiness note | `make release-audit` | Local export readiness workflow | Checks pass |
| 24. Export | Render output | Quarto source | HTML, PDF, DOCX | `make render-*` | Final check docs | Output reviewed |
| 25. Version/archive | Preserve state | Final files | Commit or archive | Git | Project rules in `AGENTS.md` | Status clean |
