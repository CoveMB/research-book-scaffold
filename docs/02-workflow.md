# Workflow

## Short path

1. Create a project charter from `templates/project-charter-template.md`.
2. Plan repeatable searches in `research/search-logs/`.
3. Dedupe and screen candidate sources before adding them to the bibliography.
4. Store verified sources in Zotero or `bibliography/references.bib`.
5. Convert annotations into source notes in `notes/10-evidence/source-notes/`.
6. Extract comparable evidence into `research/extraction-tables/` or `research/source-matrices/`.
7. Map debates in `notes/20-analysis/literature-maps/`.
8. Clarify reusable terms in `notes/20-analysis/concept-notes/`.
9. Write cautious synthesis in `notes/20-analysis/synthesis-memos/`.
10. Track claims in `notes/30-claims-and-argument/claim-ledger/`.
11. Test claim order and objections in `notes/30-claims-and-argument/argument-maps/`.
12. Trace major claims back to notes, citekeys, and locators.
13. Draft chapter briefs in `notes/40-writing-bridge/chapter-briefs/`.
14. Draft only from notes and briefs in `manuscript/`.
15. Audit citations, placeholders, links, claims, continuity, and release risks before manuscript export with `make manuscript-release-audit`.
16. Render exports only after checks pass and known limitations are recorded.

## Full sequence

| Step | Purpose | Inputs | Outputs | Tool | Workflow support | Gate |
| --- | --- | --- | --- | --- | --- | --- |
| 1. Project charter | Set scope | User brief | Charter note | Create from `templates/project-charter-template.md` | RBS research agenda workflow | Boundaries clear |
| 2. Research question refinement | Narrow inquiry | Charter | Questions | Notes | RBS or ARS planning workflow | Questions testable |
| 3. Search planning | Plan discovery | Questions | Search plan | `skill-plugins/research-book-skills/skills/systematic-source-discovery/assets/search-log-template.md` | RBS source discovery workflow | Query reproducible |
| 4. Source discovery | Find candidates | Search plan | Candidate list | Zotero, indexes | RBS source discovery workflow | Criteria applied |
| 5. Candidate dedupe and screening | Filter duplicates and search results | Candidate exports | Candidate matrix | CSV/BIB/RIS or pasted records | RBS discovery runner/deduper workflow | Duplicate and rejection reasons recorded |
| 6. Source triage | Assess source fit and credibility | Candidates | Keep/reject notes | Matrix | RBS methodology/source audit workflow | Reasons recorded |
| 7. Source storage | Preserve metadata | Kept sources | BibTeX records | Zotero | Citation workflow docs | Citekeys stable |
| 8. Reading and annotation | Extract evidence | Sources | Annotations | Zotero, notes | Manual first pass | Pages tracked |
| 9. Source notes | Convert annotations into source-bound notes | Annotations | Source note | Template | RBS annotation-to-source-note workflow | Quote, paraphrase, metadata, and locator gaps preserved |
| 10. Evidence extraction | Compare evidence across sources | Source notes | Extraction table or source matrix | Templates | RBS extraction-table workflow | Evidence is comparable before synthesis |
| 11. Literature mapping | Compare sources | Source notes, matrices | Literature map | `skill-plugins/research-book-skills/skills/literature-review-mapper/assets/lit-map-template.md` | RBS literature map workflow | Debates visible |
| 12. Concept notes | Stabilize terms | Sources, maps | Concept note | Template | RBS argument or chapter workflows | Definitions and limits clear |
| 13. Synthesis memo | Interpret across sources | Source notes, matrices, maps | Synthesis memo | Template | RBS literature and synthesis workflows | Counterevidence and uncertainty visible |
| 14. Claim ledger | Track claims | Notes, map, synthesis | Claim notes | Template | RBS claim-evidence workflow | Evidence status set |
| 15. Claim traceability | Link claims to evidence chain | Claims, notes, citekeys | Traceability map | Notes | RBS claim-traceability workflow | Orphan claims and missing locators visible |
| 16. Argument map | Test sequence and objections | Claims, traceability notes | Argument map | Notes | RBS argument architecture workflow | Weak links marked |
| 17. Chapter brief | Plan section | Claims, map | Brief | `skill-plugins/research-book-skills/skills/chapter-architecture/assets/chapter-brief-template.md` | RBS chapter architecture workflow | Gaps marked |
| 18. Drafting from notes | Draft prose | Brief, notes | Draft | Quarto | RBS prose/chapter workflows | No unsupported claims |
| 19. Citation audit | Check citations | Draft, BibTeX | Audit note | Script | RBS citation integrity workflow | Citekeys valid |
| 20. Claim audit | Check support | Draft, claims | Audit note | Notes | RBS claim-evidence workflow | Weak claims flagged |
| 21. Red-team review | Challenge argument | Draft | Review note | Notes | RBS peer-review workflows | Objections logged |
| 22. Continuity review | Check consistency | Drafts | Review note | Notes | RBS continuity workflow | Terms consistent |
| 23. Style revision | Improve prose | Audited draft | Revised draft | Editor | RBS prose editor workflow | Meaning preserved |
| 24. Release-risk audit | Check external-sharing risks | Notes, drafts, exports | Release audit | Notes | RBS rights/privacy release workflow | Privacy, quote, license, and copied-text risks marked |
| 25. Proposal comps verification | Check comparable titles | Proposal, comps | Comps table | Sources | RBS book-comps verifier workflow | Publication and positioning claims verified |
| 26. Final manuscript check | Prepare export | Draft, audits | Readiness note | `make manuscript-release-audit` | Local export readiness workflow | Checks pass |
| 27. Export | Render output | Quarto source | HTML, PDF, DOCX | `make render-*` | Final check docs | Output reviewed |
| 28. Version/archive | Preserve state | Final files | Commit or archive | Git | Project rules in `AGENTS.md` | Status clean |
