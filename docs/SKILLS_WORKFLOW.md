# Skills workflow

Keep this file next to the upstream playbook when you need a prompt for a specific Research Book Skill. The upstream workflow remains in `vendor/research-book-skills/docs/WORKFLOW_PLAYBOOK.md`; this project file gives one practical example per skill without editing vendored docs.

Treat every prompt below as a way to organize work, not as evidence. Sources, citekeys, page numbers, quotations, and bibliographic metadata still need to come from Zotero, `bibliography/references.bib`, source notes, or material the user supplied.

## Intake and accessibility

### `research-intent-router`

Use this when a research request could fit several skills and you need the smallest sensible route.

```text
Use research-intent-router. I want to start research on [topic]. Classify the task, choose the smallest useful Research Book Skill, and say whether source lookup is needed.
```

The result should name the route, explain the lookup decision, list visible assumptions, and give one next action.

### `dyslexia-research-companion`

Use this when the bottleneck mixes rough notes, dictation, reading fatigue, spelling ambiguity, or prose repair.

```text
Use dyslexia-research-companion. I have rough notes, dictation fragments, and dense source excerpts. Choose the smallest low-load first step and keep ambiguities visible.
```

Expect a low-load route, a cleaned structure, ambiguity flags, and the next concrete step.

### `dictation-to-research-notes`

Use this for voice transcripts, meeting notes, and spoken fragments that need structure without changing the author's meaning.

```text
Use dictation-to-research-notes. Turn this voice transcript into cleaned notes, claims, questions, evidence needs, ambiguities, and next actions without changing my meaning.
```

The output should separate notes, possible claims, evidence needs, open questions, and next actions.

### `reading-load-reducer`

Use this when a source pile is too dense and the reader needs to know what deserves attention first.

```text
Use reading-load-reducer. Triage these abstracts and source excerpts into read closely, skim, park, or skip for my current chapter goal: [goal].
```

The result should sort the material into reading categories, point to close-reading targets, and name evidence gaps.

### `dyslexia-friendly-prose-editor`

Use this for local spelling, grammar, punctuation, sentence-boundary, and readability repair.

```text
Use dyslexia-friendly-prose-editor. Repair spelling, grammar, punctuation, and sentence boundaries in this passage without changing my argument or adding claims.
```

The output should include the revised passage, corrections to review, ambiguous fixes, and any claims that still need evidence.

## Planning and discovery

### `research-book-orchestrator`

Use this for a project or task that spans several stages of a research nonfiction workflow.

```text
Use research-book-orchestrator. My research book project is about [topic/thesis]. Build a staged research, writing, and verification workflow with quality gates.
```

The result should give a staged plan, a skill sequence, the immediate deliverable, quality gates, and limits.

### `scholarly-research-agenda`

Use this before source gathering or outlining, especially when the project idea is still too broad.

```text
Use scholarly-research-agenda. Turn this book idea into a central research question, subquestions, scope boundaries, contribution claim, key terms, and evidence plan: [idea].
```

Expect research questions, scope boundaries, a provisional thesis, an evidence plan, and risks to watch.

### `systematic-source-discovery`

Use this to plan source discovery in a way someone else could check later.

```text
Use systematic-source-discovery. Build search families, Boolean query strings, database targets, inclusion and exclusion rules, citation-chaining steps, and a search log for: [topic].
```

The output should include search families, query strings, venues, criteria, citation-chaining steps, and a search-log draft.

### `discovery-runner-deduper`

Use this after searches produce candidate records from an index, catalogue, bibliography manager, spreadsheet, or pasted list.

```text
Use discovery-runner-deduper. Dedupe these exported candidate sources, screen them against my criteria, and draft a search-log update. Here are the records: [CSV/BIB/RIS/pasted records].
```

The result should include a candidate matrix, duplicate clusters, keep/reject notes, a search-log update, and follow-up checks.

## Source notes and evidence extraction

### `annotation-to-source-note`

Use this to turn highlights, annotations, excerpts, or reading notes into source-bound notes.

```text
Use annotation-to-source-note. Turn these Zotero notes and PDF highlights into a source note with quote, paraphrase, summary, interpretation, metadata, and locator gaps marked.
```

The output should preserve source metadata, quote and locator needs, passage-specific claims, interpretation limits, and follow-up tasks.

### `extraction-table-builder`

Use this when source notes need comparable fields before synthesis, literature mapping, or claim drafting.

```text
Use extraction-table-builder. Turn these source notes into an extraction table and source matrix for the chapter question: [question].
```

Expect extraction fields, source-level rows, passage-level rows, a cross-source matrix, and flags where the material is uneven.

### `annotated-bibliography-builder`

Use this when verified sources need short annotations about argument, method, evidence, relevance, limits, and likely placement.

```text
Use annotated-bibliography-builder. Create an annotated bibliography from these verified sources, noting each source's argument, method, evidence, relevance, limitations, key terms, and likely chapter placement.
```

The result should give source-by-source annotations plus verification limits and user checks.

### `methodology-source-auditor`

Use this when source credibility or source-claim fit could change how the manuscript uses a source.

```text
Use methodology-source-auditor. Audit these sources for method quality, evidence strength, bias, generalizability, and what each source can or cannot support in my manuscript.
```

The output should identify high-risk sources, missing stronger evidence, and safer ways to use or replace weak sources.

## Literature, cases, and argument

### `literature-review-mapper`

Use this when a source set needs to become a map of schools of thought, debates, consensus, gaps, and thesis implications.

```text
Use literature-review-mapper. Map these sources and notes into schools of thought, major debates, consensus, gaps, and implications for my thesis: [thesis].
```

The result should make corpus limits visible before it summarizes the field, debates, gaps, and source needs.

### `case-study-integration`

Use this when examples or cases need to support an argument without cherry-picking or overgeneralization.

```text
Use case-study-integration. Select and compare case studies for this claim, include counter-cases, and explain what each case can and cannot support: [claim].
```

Expect case-selection logic, candidate cases, a recommended case set, counter-cases, safer wording, and a dossier template.

### `argument-architecture`

Use this when the book-level argument needs a clearer structure before chapter planning or drafting.

```text
Use argument-architecture. Build a thesis tree from this research agenda, literature map, and notes, including claims, warrants, evidence paths, assumptions, counterarguments, chapter sequence, and weak links.
```

The output should show the thesis tree, assumptions, chapter sequence, weak links, and a stronger formulation where the evidence allows it.

### `counterargument-peer-review`

Use this to stress-test a thesis, chapter, outline, proposal, or argument.

```text
Use counterargument-peer-review. Challenge this thesis like a skeptical peer reviewer, identify rival explanations and missing literatures, then suggest a stronger narrowed version.
```

The result should give serious objections, rival explanations, missing perspectives, claims to narrow, and a revised thesis if the source basis supports one.

## Chapter and prose work

### `chapter-architecture`

Use this when a chapter needs planning, restructuring, or diagnosis.

```text
Use chapter-architecture. Design this chapter from the notes and claim ledger, including purpose, central question, chapter thesis, key concepts, section sequence, evidence placement, counterarguments, opening, ending, and research gaps.
```

Expect a chapter purpose, central question, thesis, section outline, evidence placement, counterarguments, and revision risks.

### `scholarly-prose-editor`

Use this after the evidence and chapter logic are stable enough for prose work.

```text
Use scholarly-prose-editor. Revise this passage for clarity, precision, structure, rhythm, and readability while preserving nuance, uncertainty, voice, and evidence limits.
```

The output should include the revised passage, what changed, a meaning-preservation check, a new-claim check, and evidence flags.

### `manuscript-continuity-editor`

Use this across multiple chapters or a whole manuscript.

```text
Use manuscript-continuity-editor. Review these chapter summaries and drafts for thesis coherence, repetition, contradictions, concept tracking, tone consistency, chapter order, and priority revisions.
```

The result should map chapter functions, repetition, concept tracking, claim drift, contradictions, and priority revisions.

## Claims, citations, and integrity

### `claim-evidence-ledger`

Use this before claim tracing or citation audit, once a draft or outline contains claims that need evidence status.

```text
Use claim-evidence-ledger. Extract the major claims in this draft and classify claim type, evidence status, citation need, confidence, overclaiming risk, and safer wording.
```

The output should separate high-risk claims, interpretive claims, source priorities, and user checks.

### `claim-traceability-graph`

Use this when claims need to be tied back to notes, citekeys, locators, and repair actions.

```text
Use claim-traceability-graph. Map these claims to source notes, citekeys, locators, evidence status, missing links, orphan claims, and repair actions.
```

Expect a traceability table, orphan claims, nearby-citation risks, optional graph notation, and repair priorities.

### `citation-integrity-auditor`

Use this for citations, quotations, paraphrases, bibliography problems, and source-claim fit.

```text
Use citation-integrity-auditor. Check this chapter for unsupported claims, citation-source mismatch, quote and page-number needs, fabricated-reference risk, and bibliography issues.
```

The result should list claim-level findings, quotation issues, bibliography issues, and repairs that matter most.

### `figure-table-integrity-auditor`

Use this when figures, tables, charts, screenshots, maps, or image panels carry claims.

```text
Use figure-table-integrity-auditor. Audit these figures and tables for data provenance, caption and axis accuracy, source licensing, duplicate visual risk, manipulation risk, and claim support limits.
```

The output should name blockers, missing data or source files, provenance problems, rights issues, and repair actions.

### `scholarly-integrity-gate`

Use this before AI-assisted analyses, generated syntheses, computed results, or high-stakes evidence artifacts support manuscript claims.

```text
Use scholarly-integrity-gate. Gate this AI-assisted research artifact before it supports manuscript claims. Check for hallucinated evidence, methodology fabrication, implementation bugs, shortcut reliance, frame-lock, and missing human checkpoints.
```

The result should give a CLEAR, SUSPECTED, INSUFFICIENT EVIDENCE, or OVERRIDDEN decision, with blockers, repair priorities, and human checkpoints.

## Release, proposal, and workflow records

### `ai-human-workflow-log`

Use this when AI-assisted work is going to collaborators, reviewers, presses, committees, or public release.

```text
Use ai-human-workflow-log. Create a workflow record for this AI-assisted research task, including tool use, affected sections, human checkpoints, verification responsibilities, override reasons, unresolved risks, and disclosure notes.
```

Expect an AI assistance record, human checkpoints, disclosure notes, verification responsibilities, and follow-up risks.

### `rights-privacy-release-auditor`

Use this before sharing notes, source packets, proposals, manuscript exports, or research artifacts outside the project.

```text
Use rights-privacy-release-auditor. Check this manuscript export for privacy, copied source text, quote locator, copyright, license, credential, local metadata, and AI-disclosure risks before I share it.
```

The result should give a release verdict and identify privacy, copyright, license, metadata, credential, and disclosure risks.

### `book-proposal-scholarship`

Use this once the thesis, audience, source base, and chapter structure are stable enough for proposal work.

```text
Use book-proposal-scholarship. Draft a research nonfiction book proposal from this thesis, chapter structure, source base, audience notes, and sample-material plan, marking market and comps claims that still need verification.
```

The output should draft the proposal pieces and mark the audience, market, comparable-title, and submission risks that still need checking.

### `book-comps-verifier`

Use this to verify comparable titles and positioning claims before they appear in proposals, pitches, grants, or press materials.

```text
Use book-comps-verifier. Verify these comparable titles and positioning claims, and flag stale, mismatched, fabricated, or unverified claims before I use them in a proposal.
```

Expect a comps verification table, positioning notes, audience and market claim checks, and missing verification tasks.

## Suggested sequence

Pick the smallest skill that matches the artifact in front of you. A normal high-evidence path looks like this:

1. `research-intent-router`
2. `scholarly-research-agenda`
3. `systematic-source-discovery`
4. `discovery-runner-deduper`
5. `annotation-to-source-note`
6. `extraction-table-builder`
7. `literature-review-mapper`
8. `argument-architecture`
9. `chapter-architecture`
10. `claim-evidence-ledger`
11. `claim-traceability-graph`
12. `counterargument-peer-review`
13. `citation-integrity-auditor`
14. `figure-table-integrity-auditor`
15. `scholarly-integrity-gate`
16. `manuscript-continuity-editor`
17. `ai-human-workflow-log`
18. `rights-privacy-release-auditor`
19. `book-proposal-scholarship`
20. `book-comps-verifier`

When text friction blocks the work, start with the relevant accessibility skill: `dyslexia-research-companion`, `dictation-to-research-notes`, `reading-load-reducer`, or `dyslexia-friendly-prose-editor`.
