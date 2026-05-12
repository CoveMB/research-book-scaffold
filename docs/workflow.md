# Simple “open this, do that” workflow

This workflow translates the research-and-writing system into practical actions: what to open, what tool or skill to use, what to ask, and where the result should be saved.

---

## Mode 1 — You want to plan research

### Open

```text
Obsidian
today.md
project-charter.md
Codex sidebar inside Obsidian
```

### Use

```text
Skill: research-question-refiner
Skill: literature-search-planner
Codex mode: Plan / read-only
MCP: off
```

### Do

Ask Codex:

```text
Use $literature-search-planner.

I want to research how DAO governance can inspire bias-resistant democratic systems without reproducing plutocracy or technical capture.

Read project-charter.md and propose:
- research questions
- search terms
- disciplines to search
- inclusion criteria
- exclusion criteria
- source types needed

Do not edit files yet.
```

### Save output to

```text
research/search_plans/dao-governance-search-plan.md
```

### You manually decide

```text
Which searches to run
Which tools to use
Which questions matter
```

---

## Mode 2 — You want to find sources

### Open

```text
Zotero
Browser
Elicit
Semantic Scholar / Google Scholar / OpenAlex
ChatGPT Deep Research if you need a broad landscape
```

### Use

```text
Elicit            = empirical papers
Semantic Scholar  = citation chains
Deep Research     = broad map and source leads
Scite             = whether key claims are supported or challenged
Zotero            = save everything
```

### Do

1. Open the search plan from:

```text
research/search_plans/
```

2. Search one topic at a time.

Example:

```text
DAO governance token voting plutocracy empirical study
liquid democracy delegation concentration
cognitive bias deliberative democracy group polarization
adaptive governance systems theory institutions feedback loops
```

3. Save good sources to Zotero.

4. Put them in the right Zotero collection.

5. Tag them:

```text
status/unread
topic/dao-governance
role/candidate
```

6. Record what you searched in:

```text
research-log.md
```

### Do not

Do not let AI summaries replace source collection.

Correct path:

```text
AI suggests source → you verify source → source goes into Zotero
```

Wrong path:

```text
AI says something → you treat it as evidence
```

---

## Mode 3 — You want to read a source

### Open

```text
Zotero
PDF or book
Obsidian
```

### Use

```text
Zotero PDF reader
Zotero annotations
No AI at first
```

### Do

1. Read or skim the source.
2. Highlight important passages.
3. Add your own annotation comments.
4. Mark pages for key claims.
5. Decide whether this source is actually useful.

### Save

The source itself stays in:

```text
Zotero
```

Your reading interpretation later goes into:

```text
notes/01_source_notes/
```

---

## Mode 4 — You want to create a source note

### Open

```text
Obsidian
Codex sidebar
Zotero annotations export, if available
```

### Use

```text
Skill: source-credibility-auditor
Codex mode: Agent only if writing note
MCP: Zotero read-only if configured
```

### Ask Codex

```text
Use $source-credibility-auditor.

Create a source note from the provided Zotero annotations and metadata.

Use the source-note template.
Do not add facts from memory.
If page numbers are missing, write [page needed].
If the source cannot support a strong claim, say so.

Write the result to:
notes/01_source_notes/@citekey-short-title.md
```

### Output

```text
notes/01_source_notes/@polanyi1944great - The Great Transformation.md
```

### Your job

Check that the note matches the actual source.

---

## Mode 5 — You want to understand a whole field

Example:

```text
current democracy failures
capitalism critique
DAO governance
systems theory
bias-resistant decision-making
```

### Open

```text
Obsidian
Codex sidebar
notes/01_source_notes/
notes/02_literature_maps/
```

### Use

```text
Skill: literature-review-mapper
Codex mode: Plan first
MCP: off
```

### Ask Codex

```text
Use $literature-review-mapper.

Read the source notes related to DAO governance and democratic legitimacy.

Do not edit files yet.

Create a literature map with:
- schools of thought
- major debates
- consensus claims
- contested claims
- weak evidence areas
- sources that support my thesis
- sources that challenge my thesis
- missing perspectives
```

### After you approve

Ask:

```text
Write the approved map to:
notes/02_literature_maps/dao-governance-map.md
```

### Output

```text
notes/02_literature_maps/dao-governance-map.md
```

---

## Mode 6 — You want to track claims

This is crucial.

### Open

```text
Obsidian
Codex sidebar
manuscript chapter or chapter brief
notes/04_claim_ledger/
```

### Use

```text
Skill: claim-evidence-ledger
Codex mode: Agent
MCP: off
```

### Ask Codex

```text
Use $claim-evidence-ledger.

Scan notes/07_chapter_briefs/ch05-dao-governance-lessons-brief.md.

Extract every major claim.
Classify each claim as:
- empirical
- historical
- causal
- normative
- philosophical
- technical
- speculative

For each claim, create or update a claim note in:
notes/04_claim_ledger/

Do not edit the manuscript.
```

### Output

```text
notes/04_claim_ledger/C-031 - token voting may reproduce plutocracy.md
notes/04_claim_ledger/C-032 - delegation can create new informal elites.md
notes/04_claim_ledger/C-033 - transparency can conflict with privacy.md
```

### Your job

Decide which claims are strong enough for the book.

---

## Mode 7 — You want to create a chapter plan

### Open

```text
Obsidian
project-charter.md
literature maps
claim ledger
case studies
Codex sidebar
```

### Use

```text
Skill: chapter-architect
Codex mode: Plan first
MCP: off
```

### Ask Codex

```text
Use $chapter-architect.

Design chapter 05: DAO Governance Lessons.

Read:
- project-charter.md
- notes/02_literature_maps/dao-governance-map.md
- notes/04_claim_ledger/
- notes/05_case_studies/

Do not draft prose yet.

Create:
- chapter purpose
- central question
- main claim
- argument sequence
- key sources
- case studies
- counterarguments
- missing evidence
- transition to next chapter
```

### Save

```text
notes/07_chapter_briefs/ch05-dao-governance-lessons-brief.md
```

Do not write the chapter before this exists.

---

## Mode 8 — You want to draft a chapter section

### Open

```text
Obsidian or your editor
manuscript/chapters/chapter.qmd
Codex sidebar
Zotero open beside it
```

### Use

```text
Skill: chapter-drafter-from-notes
Codex mode: Agent
MCP: off
```

### Ask Codex

```text
Use $chapter-drafter-from-notes.

Draft section 5.2 of:
manuscript/chapters/05_dao_governance_lessons.qmd

Use only:
- notes/07_chapter_briefs/ch05-dao-governance-lessons-brief.md
- relevant source notes
- relevant claim notes
- relevant case studies

Rules:
- Do not invent citations.
- Do not invent page numbers.
- If evidence is missing, write {{citation needed}}.
- If a claim is speculative, label it as speculative.
- Preserve a serious scholarly tone.
```

### Output

A draft section inside:

```text
manuscript/chapters/05_dao_governance_lessons.qmd
```

### Your job

Read it as author, not as passive reviewer.

---

## Mode 9 — You want to improve style

### Open

```text
Obsidian
chapter file
Codex sidebar or obsidian-codex writing harness
```

### Use

```text
Skill: style-voice-preserver
Codex writing mode: Strict
```

### Ask Codex

```text
Use $style-voice-preserver.

Rewrite this selected passage for clarity and rhythm.

Rules:
- Do not add new facts.
- Do not remove citations.
- Do not make claims stronger.
- Preserve uncertainty.
- Preserve my voice.
- If the evidence is weak, make the wording more cautious.
```

### Use this for

```text
clarity
flow
transitions
reader accessibility
removing repetition
```

### Do not use this for

```text
adding evidence
adding citations
making arguments stronger than sources allow
```

---

## Mode 10 — You want to audit citations

### Open

```text
Obsidian
Zotero
chapter draft
Codex sidebar
Scite if checking contested papers
```

### Use

```text
Skill: citation-auditor
Codex mode: Plan / read-only first
MCP: Zotero read-only if configured
Web/search MCP only if verifying current or external sources
```

### Ask Codex

```text
Use $citation-auditor.

Audit manuscript/chapters/05_dao_governance_lessons.qmd.

Check:
- unsupported factual claims
- missing citations
- citation-needed markers
- citations that do not support the sentence
- empirical claims supported only by theory sources
- normative claims pretending to be empirical
- missing page numbers for quotations

Do not edit the chapter.
Write the audit to:
notes/08_audits/ch05-citation-audit.md
```

### Output

```text
notes/08_audits/ch05-citation-audit.md
```

### Your job

Open Zotero and verify the source manually.

---

## Mode 11 — You want to red-team a chapter

### Open

```text
Obsidian
chapter draft
claim ledger
Codex sidebar
```

### Use

```text
Skill: power-dynamics-red-team
Skill: democracy-failure-mode-auditor
Skill: bias-resistant-democracy-auditor
Skill: systems-governance-modeler
Codex mode: Plan / read-only
```

### Ask Codex

```text
Use $power-dynamics-red-team.

Attack chapter 08 as if you are a skeptical political theorist, institutional economist, DAO governance critic, and systems theorist.

Focus on:
- elite capture
- agenda-setting
- technical exclusion
- participation inequality
- information overload
- delegation concentration
- metric gaming
- manipulation
- legitimacy failure

Do not edit the chapter.
Write findings to:
notes/08_audits/ch08-power-dynamics-red-team.md
```

### Output

```text
notes/08_audits/ch08-power-dynamics-red-team.md
```

This is where the book gets stronger.

---

## Mode 12 — You want to build/export the book

### Open

```text
Terminal or Codex sidebar
BookProject/
Quarto
```

### Use

```text
Quarto
Codex only as helper
```

### Command

```bash
quarto render manuscript
```

Or, if your Quarto project is directly inside `manuscript/`:

```bash
cd manuscript
quarto render
```

### Output

```text
exports/pdf/
exports/docx/
exports/epub/
exports/html/
```

### Use Codex only like this

```text
Run quarto render manuscript.
If it fails, explain the error.
Do not edit files until I approve the fix.
```

---

# Simple rule

```text
Search externally → save source in Zotero → read/annotate → create Obsidian source note → map literature → create claim ledger → plan chapter → draft from notes → audit claims/citations → revise → export with Quarto
```
