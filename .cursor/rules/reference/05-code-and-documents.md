# Code Editing and Document Authoring

## Code Editing Principles

### Minimal Invasiveness `[technical]` — 4 reinforcements (highest)

**Directive**: Modify only the broken part. When fixing a bug in a function, keep the function skeleton — guards, comments, variable names, structure — and replace only the lines that implement the broken behavior.

**Why**: A full rewrite triggers clean-slate thinking. You stop seeing the existing code as an artifact with embedded decisions (comments, structure, naming) and start treating it as raw material to be reshaped. This leads to:
- Deleted comments that documented important intent
- Changed variable names that had semantic meaning
- Removed guards that existed for non-obvious reasons
- Altered structure that callers depended on

**Corollary — Scope Awareness**: When a fix bypasses code (e.g., removing a call to a broken function), don't also modify the bypassed code. Changes to shared infrastructure affect all callers, not just the one you're fixing.

**Extraordinary changes require extraordinary evidence**: Removing fail-fast guards, changing error handling strategy, altering function signatures. For these: enumerate all callers, verify impact on each.

### Comment Handling `[technical]` — 3 reinforcements

**Directive**: Never silently remove comments. When rewriting code, preserve all comments that document intent, assumptions, or non-obvious logic.

**Pre-flight check** (do this BEFORE writing replacement code):
1. Enumerate every comment in the original code block
2. For each, decide: keep verbatim, update wording (if old wording contradicts new code), or replace with explanation of why the original code was removed
3. Only THEN write the replacement

**Distinguish two types of comments**:
- **Design-intent comments**: Describe what the code is _supposed_ to do, architectural decisions, rationale. Preserve these even when working around a bug — they help future developers understand the intended design vs. the current deviation.
- **Implementation comments**: Describe _how_ the current code works. Replace these when the implementation changes.

When an edit works around a bug without changing the design: preserve the design-intent comment, add a NOTE explaining the current deviation.

### Consistency Scope `[technical]` — 2 reinforcements

**Directive**: After making a localized edit, check the broader context for contradictions.

**Check, in order**:
1. The function's docstring — does it still describe the behavior?
2. The class/module — do adjacent functions reference the changed behavior?
3. Callers — do they pass arguments that assume the old behavior?
4. Documentation — do docs describe the old behavior?

A reader forms their mental model from the outermost documentation inward (docstring → inline comments → code). If you change the code but not the docstring, the reader will have a wrong model.

**Interface preservation**: Dict keys, function signatures, return types — these are contracts with callers. Change them only when the design changes, not as a side effect of a bug fix.

## Document Authoring Principles

### Self-Contained Documents `[technical]` — 2 reinforcements

**Directive**: Documents should be readable without needing to ask follow-up questions.

**Requirements**:
- Ground domain-specific terms in general concepts (e.g., if using protocol-specific jargon, define it in terms the reader would know from standard CS/finance/etc.)
- Back every claim with inline evidence (parameter values, code references, output snippets)
- Don't assume the reader has context from conversations — the document may be read by someone who wasn't part of the discussion

### Terminology Discipline `[technical]`

| Rule | Rationale |
|------|-----------|
| Assume only standard domain knowledge | The reader knows CS, programming, standard domain terms. They don't know conversation-local shorthand. |
| Introduction threshold | Only introduce a new term when it's central, repeated, and the cognitive cost is justified vs. inline prose. Must define where introduced. |
| No conflicting nomenclature | Avoid terms that require extra disambiguation effort, even if technically distinguishable. |
| Ask before introducing terms | Default to asking the human before adding new nomenclature to formal documents. |
| Conversation-local labels stay local | Shorthand from conversation → prose in formal documents. |

### Scoped References `[technical]`

IDs like "F4" or "B2" are meaningful only within the document that defines them. When referencing outside that document:
- Use descriptive text: "the resource-leak failure mode" not "F4"
- Add a source reference: "→ analysis_document.md §F4"
- Brief context so the reader doesn't need to follow the link for basic understanding

### Cross-References `[technical]`

Dedicated section at document end:
- Relative paths
- Brief one-line context per link
- Verify links after any file moves or renames

### Results Over Process `[technical]`

Describe findings as they stand, not the journey to them. A document states conclusions and evidence — not "we previously thought X, now we think Y." The revision history belongs in version control or the session log, not in the finding itself.

Exception: When the process itself is a finding (e.g., documenting that a certain approach doesn't work, or that a system has a specific failure mode).

### Code References in Documents `[technical]`

When documents reference specific code lines:
- Include stable identifiers (function name, commit hash) alongside line numbers
- After any code edit: cross-check ALL line references in affected documents
- Trace the root cause of reference shifts (which edit, how many lines) to confirm completeness rather than sampling
- For living documents: consider linking to version-controlled URLs (e.g., GitHub permalinks at the relevant commit)
- When the codebase has named versions (releases, tags), note which version the reference applies to. References age better when tied to a named version rather than a line number alone.

### Abstraction Guidelines `[technical]`

When distilling code into higher-level representations (formulas, pseudo-code, algorithmic abstractions):

1. **Focus on mathematical invariants** — what the code *guarantees*, not how it implements
2. **Omit error handling, logging, edge cases** — but note their existence ("edge cases omitted; see source")
3. **Preserve semantic meaning** — the abstraction must be faithful to the code's behavior
4. **Reference source code locations** — every abstraction should link back to `file:function` or `file:line`
5. **Mark verification status** — `unverified` (extracted, not checked), `evidence-supported` (cross-referenced), `verified` (human-confirmed)

This applies whenever the task involves creating documentation that captures what code does at a higher level of abstraction — audit reports, architecture docs, formula catalogs, algorithm descriptions. The abstraction is a lossy compression; being explicit about what was dropped (point 2) and how confident you are (point 5) prevents the abstraction from being mistaken for the full picture.

### Tooling Rendering Awareness `[technical]`

Know your authoring environment's rendering quirks. Markdown rendered in a code editor (VS Code, Cursor) does not always match GitHub or standard Markdown renderers.

Discovered example: backtick spans inside link text (e.g., `` [`code`](url) ``) may misrender when the link text is *only* a backtick span. Workaround: add a trailing space or non-backtick text.

General principle: when a document will be read in a specific renderer, test formatting in that renderer. Don't assume standard Markdown behavior — edge cases in links, tables, and inline code vary across platforms.

## Script Execution Principles

`[technical]`

### Pre-Run Analysis

Before running any script:
1. Count interactive prompts (`input()` calls or equivalent) — you need to supply these. When an interactive prompt is unavoidable, supply input via pipe (`echo "value" | command`) instead of trying to type into a running process — piped input is deterministic and scriptable.
2. Check path setup (`sys.path`, imports, working directory assumptions)
3. Check config defaults — are they appropriate for this run, or tuned for a different scenario?

### Output Management

- Unbuffered output (`PYTHONUNBUFFERED=1` or equivalent) — prevents lost output on crash
- Filter noisy output (e.g., `grep --line-buffered -v "DEBUG"`) — keeps signal-to-noise ratio high
- Timestamped, descriptive log files — reproducibility and provenance
- `tee` to both terminal and file — allows real-time monitoring and post-hoc analysis

### Git Hygiene

After operations that check out files from other commits:
- `git status --short` immediately after
- For each suspect file: (1) confirm absent at HEAD, (2) confirm present at old commit, (3) diff on-disk content against old commit version
- **Only delete if identical.** If a file has local modifications not in any commit, do NOT delete.

---

## Cross-References

- Minimal invasiveness and comment handling failure modes → `06-FAILURE-MODES.md` (F2: Clean-Slate Rewriting)
- Stale cross-references failure mode → `06-FAILURE-MODES.md` (F5: Stale Cross-References)
- Cross-referencing after changes → `04-EVIDENCE-AND-VALIDATION.md` (Cross-Referencing After Changes) — the evidence perspective
- Abstraction guidelines and verification status → `04-EVIDENCE-AND-VALIDATION.md` (The Validation Gate, Status Transitions)
- Self-contained documents and terminology discipline → `02-INTERACTION-STYLE.md` (Communication Micro-Rules)
- Scoped references → `06-FAILURE-MODES.md` (F9: Scoped IDs Out of Context)
