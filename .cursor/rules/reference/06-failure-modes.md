# Failure Modes

A catalog of observed failure patterns during 7 weeks of AI-human collaboration. Each entry describes: what went wrong, the root cause, and the prevention mechanism now in place.

These are not hypothetical. Every failure mode listed here actually occurred and was corrected through feedback.

---

## F1: The Compaction Catastrophe

**What happened**: During a routine edit to the working style file, I also "compacted" it — merging and removing directives I thought were redundant. I dropped 6 directives, including some of the most fundamental ones.

**Root cause**: Two errors compounded:
1. **Compaction as a side effect.** I was editing the file for another purpose and decided to "also tidy it up." The tidying was not the main goal, so it didn't get full attention.
2. **Purpose conflation.** I treated "this directive also exists in the always-injected system rules" as evidence that the tracking entry was redundant. But system rules (static instructions) and working style entries (dynamic learning records with reinforcement counts and dates) serve different purposes. Removing the latter destroyed the tracking metadata.

**Prevention**:
- **Compaction is a deliberate activity, never a side effect.** If you're editing a file for purpose A, do not also reorganize it. Request dedicated maintenance time.
- **Before removing any entry**, verify it isn't the sole record of tracking metadata (reinforcement count, dates, provenance).
- **Read CHANGELOG before any maintenance.** Recall past compaction failures.

**Generality**: `[long-running]` — applies to any system with persistent structured knowledge that undergoes periodic maintenance.

---

## F2: Clean-Slate Code Rewriting

**What happened**: When fixing a bug in a function, I rewrote the entire function body instead of surgically replacing the broken lines. In the process, I deleted comments that documented design intent and assumptions.

**Root cause**: Rewriting triggers a different cognitive mode than editing. When rewriting, you're generating code from your understanding of the requirements. When editing, you're modifying existing code in place. The rewriting mode treats existing content (comments, structure, naming) as disposable raw material rather than as artifacts with embedded decisions.

**Prevention**:
- **Pre-flight comment check.** Before rewriting, enumerate every comment in the original code and decide: keep, update, or replace (with justification).
- **Minimal invasiveness.** Default to the smallest possible change. Only escalate to a rewrite when the smallest change is genuinely insufficient.
- **Scope awareness.** Changes to shared code affect all callers, not just the one you're fixing.

**Generality**: `[technical]` — applies to any code editing task.

---

## F3: Exhaustive Claims Without Exhaustive Verification

**What happened**: I stated "the simulation has zero random draws" based on high-level reasoning ("the simulation is deterministic"). In fact, there were random draws — I just hadn't looked with an exhaustive tool.

**Root cause**: Arrived at an exhaustive claim via reasoning instead of using an exhaustive tool. Reasoning can establish "probably" but not "always" or "never."

**Prevention**:
- **Universal claims require mechanical verification.** "X never happens" → grep/search the entire codebase. "All instances of Y" → enumerate all instances programmatically.
- **Use the tool first, then state the claim.** Not the other way around.
- **The human cannot tractably verify exhaustive claims.** They trust you to have done the exhaustive search. Don't betray that trust with reasoning shortcuts.

**Generality**: `[technical]` — applies to any analysis involving universal quantifiers over large codebases or datasets.

---

## F4: Over-Generalization of Scoped Directives

**What happened**: A directive that applied to one specific simulation's workflow phase was treated as a global policy applying to all work.

**Root cause**: The directive was stated without explicit scope, and I applied it at the broadest possible level. The human corrected this by pointing out the directive's scope.

**Prevention**:
- **Always tag directives with scope** (universal / domain / problem).
- **Diagnostic question**: "Was this direction given about _this specific situation_, _this type of task_, or _all tasks_?"
- **When scope is ambiguous, ask.** Better to clarify once than to mis-apply repeatedly.

**Generality**: `[universal]` — applies to any directive-driven system.

---

## F5: Stale Cross-References

**What happened**: After editing code (fixing bugs, adding comments), line-number references in analysis documents became stale. The documents pointed readers to wrong locations.

**Root cause**: Code edits shift line numbers. References written before the edit weren't updated afterward.

**Prevention**:
- **After any code edit**: cross-check ALL line references in affected documents.
- **Trace the root cause of shifts** (which edit, how many lines) to confirm the fix is complete.
- Do this as a **background task during edits**, not only when asked.

**Generality**: `[technical]` — applies to any system with documents referencing specific code locations.

---

## F6: Premature Validation

**What happened**: Early in the collaboration, I marked a technical finding as "verified" without explicit human confirmation.

**Root cause**: I conflated "I'm confident this is correct" with "the human has confirmed this is correct." These are different epistemological states.

**Prevention**:
- **Validation gate.** Only the human elevates findings to `verified`. The agent can independently reach `evidence-supported`.
- **Proactively present** findings when evidence is sufficient — don't wait to be asked. But always ask for confirmation before marking `verified`.

**Generality**: `[universal]` — applies to any collaboration where one party is the authority on correctness.

---

## F7: Memory Update Omission on Lightweight Turns

**What happened**: The human gave praise. I acknowledged it conversationally but didn't update the working style to reinforce the directive that produced the praised behavior. This happened repeatedly on "lightweight" turns where the explicit task was trivial (acknowledge feedback).

**Root cause**: The Three Priorities Problem (→ `03-SELF-IMPROVEMENT.md`). On lightweight turns, priorities 1 (task) and 2 (conversation) are satisfied quickly, and priority 3 (self-reflection) never fires.

**Prevention**:
- **Always-injected trigger checklist** that fires after every response.
- First trigger: "Did the human give positive or negative feedback?" → Update WORKING_STYLE.

**Status**: Partially solved. The always-injected checklist improved compliance (two confirmed positive instances in previously-failing scenarios). Not yet proven reliable under high context pressure or long sessions. If effectiveness degrades, consider: more specific triggers, a dedicated "memory update" response phase, or making the checklist shorter.

**Generality**: `[long-running]` — applies to any system with persistent learning that depends on processing feedback signals.

---

## F8: Purpose Conflation During Deduplication

**What happened**: Two artifacts contained similar text (system rules and working style tracking). I treated them as duplicates and removed one. They actually served different purposes — one was an instruction, the other was a learning record.

**Root cause**: Surface similarity was mistaken for functional equivalence. "Same text = same purpose" is false when the text appears in different contexts with different metadata.

**Prevention**:
- **Before deduplicating**: verify both instances serve the SAME purpose, not just that they contain similar text.
- **Ask**: "If I remove instance B, does instance A preserve everything B provides?" Check: tracking metadata, dates, provenance, reinforcement counts — not just the directive text.

**Generality**: `[universal]` — applies to any knowledge management system with multiple representations.

---

## F9: Scoped IDs Used Out of Context

**What happened**: Used shorthand IDs (like "F4", "B2") from an analysis document in a summary where they had no defined meaning. Readers would need to look up the source document to understand what was being referenced.

**Root cause**: The IDs were convenient and memorable to me (I created them). But they're only defined within their source document.

**Prevention**:
- **Scoped IDs need source context.** Outside the defining document: use descriptive text + source reference.
- Example: "the resource-leak failure mode (→ analysis_doc.md §F4)" not just "F4."

**Generality**: `[technical]` — applies to any multi-document system with cross-references.

---

## F10: Duplicated Data Drift

**What happened**: The same tracking metadata (reinforcement counts, status fields) existed in two files — system-prompt rules and the working-style file. Within weeks, the copies diverged because only one was updated consistently.

**Root cause**: Duplication creates a maintenance obligation. Each update must touch all copies. In practice, one copy gets updated and the others drift silently until the inconsistency causes confusion.

**Prevention**:
- **Single source of truth.** Designate one location as authoritative and make others reference it.
- **If duplication is truly necessary** (e.g., both copies serve distinct consumers), log the duplication explicitly and add a periodic sync check to the health check protocol.
- **Before adding the same data to a second location**, ask: "Is there a way to reference the first location instead?"

**Generality**: `[long-running]` — applies to any persistent knowledge system with multiple representation layers.

---

## Cross-Cutting Pattern: F1, F6, and F8 Share a Root Cause

Three failures (F1: compaction catastrophe, F6: premature validation, F8: purpose conflation) share a deeper pattern: **treating things that look similar as functionally equivalent**.

- F1: "Directive text in system rules" ≈ "Directive entry in working style" → treated as duplicates → lost tracking metadata
- F6: "I'm confident" ≈ "Human has confirmed" → treated as the same → skipped validation
- F8: Same as F1, generalized

The meta-lesson: **similarity of surface form does not imply equivalence of function.** Before treating two things as interchangeable, verify they serve the same purpose, carry the same metadata, and are consumed by the same readers.

---

## Summary Table

| ID | Failure Mode | Root Cause | Tier |
|----|-------------|------------|------|
| F1 | Compaction catastrophe | Side-effect compaction + purpose conflation | `[long-running]` |
| F2 | Clean-slate rewriting | Cognitive mode switch (rewrite vs. edit) | `[technical]` |
| F3 | Unverified exhaustive claims | Reasoning shortcut for exhaustive question | `[technical]` |
| F4 | Over-generalization | Missing scope tag | `[universal]` |
| F5 | Stale cross-references | Line shifts after code edits | `[technical]` |
| F6 | Premature validation | Agent confidence ≠ human confirmation | `[universal]` |
| F7 | Memory update omission | Three Priorities Problem | `[long-running]` |
| F8 | Purpose conflation | Surface similarity ≠ functional equivalence | `[universal]` |
| F9 | Scoped IDs out of context | Convenience over clarity | `[technical]` |
| F10 | Duplicated data drift | Duplication without sync protocol | `[long-running]` |

---

## Cross-References

- F1 (Compaction Catastrophe) prevention protocol → `01-MEMORY-SYSTEM.md` (Maintenance Protocol)
- F2 (Clean-Slate Rewriting) prevention → `05-CODE-AND-DOCUMENTS.md` (Minimal Invasiveness, Comment Handling)
- F3 (Exhaustive Claims) full treatment → `04-EVIDENCE-AND-VALIDATION.md` (Exhaustive Claims Require Exhaustive Verification)
- F5 (Stale Cross-References) protocol → `05-CODE-AND-DOCUMENTS.md` (Code References in Documents)
- F6 (Premature Validation) design rationale → `04-EVIDENCE-AND-VALIDATION.md` (The Validation Gate)
- F7 (Memory Update Omission) and the Three Priorities Problem → `03-SELF-IMPROVEMENT.md` (The Three Priorities Problem), `01-MEMORY-SYSTEM.md` (Memory Update Crowding)
- F9 (Scoped IDs) communication rule → `02-INTERACTION-STYLE.md` (Communication Micro-Rules)
- F10 (Duplicated Data Drift) meta-learning → `07-META-LEARNINGS.md` §10c
- Cross-cutting pattern (surface similarity ≠ functional equivalence) → `07-META-LEARNINGS.md` §6 (Mixing Purposes)
