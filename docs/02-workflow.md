# Workflow

| Step | Purpose | Inputs | Outputs | Tool | Skill | Gate |
| --- | --- | --- | --- | --- | --- | --- |
| 1. Project charter | Set scope | User brief | Charter note | Notes | project-orchestrator | Boundaries clear |
| 2. Research question refinement | Narrow inquiry | Charter | Questions | Notes | research-question-refiner | Questions testable |
| 3. Search planning | Plan discovery | Questions | Search plan | Search log | literature-search-planner | Query reproducible |
| 4. Source discovery | Find candidates | Search plan | Candidate list | Zotero, indexes | literature-search-planner | Criteria applied |
| 5. Source triage | Filter sources | Candidates | Keep/reject notes | Matrix | source-credibility-auditor | Reasons recorded |
| 6. Source storage | Preserve metadata | Kept sources | BibTeX records | Zotero | citation-auditor | Citekeys stable |
| 7. Reading and annotation | Extract evidence | Sources | Annotations | Zotero, notes | source-note-generator | Pages tracked |
| 8. Source notes | Summarize source | Annotations | Source note | Template | source-note-generator | Limits included |
| 9. Literature mapping | Compare sources | Source notes | Literature map | Template | literature-review-mapper | Debates visible |
| 10. Claim ledger | Track claims | Notes, map | Claim notes | Template | claim-evidence-ledger | Evidence status set |
| 11. Chapter brief | Plan section | Claims, map | Brief | Template | chapter-architect | Gaps marked |
| 12. Drafting from notes | Draft prose | Brief, notes | Draft | Quarto | chapter-drafter-from-notes | No unsupported claims |
| 13. Citation audit | Check citations | Draft, BibTeX | Audit note | Script | citation-auditor | Citekeys valid |
| 14. Claim audit | Check support | Draft, claims | Audit note | Notes | claim-evidence-ledger | Weak claims flagged |
| 15. Red-team review | Challenge argument | Draft | Review note | Notes | red-team-reviewer | Objections logged |
| 16. Continuity review | Check consistency | Drafts | Review note | Notes | continuity-editor | Terms consistent |
| 17. Style revision | Improve prose | Audited draft | Revised draft | Editor | continuity-editor | Meaning preserved |
| 18. Final manuscript check | Prepare export | Draft, audits | Readiness note | Scripts | final-manuscript-check | Checks pass |
| 19. Export | Render output | Quarto source | HTML, PDF, DOCX | Quarto | final-manuscript-check | Output reviewed |
| 20. Version/archive | Preserve state | Final files | Commit or archive | Git | project-orchestrator | Status clean |
