# notes_v0.2 — review of warm-reset-plan toward v0.2

**Consumer**: AI only, dense. **Produced**: 2026-06-14. **Governance**: `_META.md`. **Reviews v0.1**; applied into `warm-reset-plan_v0.2.md`.
No new sub-agent crawls this iteration — content + path inventories from cycle 1 (`experiment-log.md` exp-1/exp-2) still current; this is pure R1–R3 reasoning.
Finding format: `[id] location → problem → change`.

---

## R1 — Structure-fit (substance) [ran FIRST]

- **[R1-5] Success criteria not tied to the retrieval rubric.** §7 (S1–S6) → S4 covers cross-contamination (cold-AI can't write another project's memory = guidelines §8 acceptance-test-3, partial) but the plan never tests the two *retrieval* capabilities the rubric ranks #1: domain **one-hop** (§8 test 1) and **lateral relation** traversal (§8 test 2). A plan whose success criteria omit the top-priority property can pass while failing its actual goal. → Change: add **S7 — Retrieval acceptance tests (guidelines §8)**: (1) domain one-hop — a real domain question (e.g. "what's the RP2040 GC heap doubling behaviour?") resolves via `_INDEX`→domain→concept with no speculative search; (2) lateral relation — a related-concept query surfaces the linked concept via `_RELATIONS` (only if D8≠(a)); (3) cross-project pollination — a pattern lands at one deterministic home (placement gate yields one destination). Run whichever apply given the D8 choice. Make S7 the *outcome test* operationalized (§1 already names "a cold AI retrieves correctly" as the outcome — S7 is its measurement).

- **[R1-6] CONTEXT.md risks duplicating the existing exp14 handoff doc.** §5 Phase 3 ("create each CONTEXT.md") → exp14 already has a rich `CONTEXT_HANDOFF.md` in its project dir (referenced throughout `SESSION_LOG.md`). Authoring a fresh `projects/circuitpython-exp14-display/CONTEXT.md` with scope/goals/phase risks duplication-and-drift (failure-mode F10, which the mandate's pre-flight requires reading). → Change (light — leave shape open per flexible-plans): add a note to Phase 3 "CONTEXT.md should *reference* an existing project handoff doc (exp14: `CONTEXT_HANDOFF.md`) as the canonical scope/goal source rather than copy it — one canonical home per fact (guidelines §9)."

## R2 — Paradigm-compliance (form) [ran SECOND]

- **[R2-5] C7's `provisional` watch-for block is not yet cold-AI-testable.** §2 C7 → It mandates "a 2–4 line watch-for block" but doesn't require the block to carry confirm/refute signals + a re-evaluation trigger. Per cold-ai-paradigm §7, an experiment claim ("this structure works") with no confirm/refute + no trigger is a wish, not a test; the `provisional` marker would be decorative. → Change: refine C7 — the watch-for block must state **confirm** (e.g. a real post-reset query resolved one-hop), **refute** (e.g. a query required scanning multiple files / speculative search, or a new finding had no deterministic home), and a **re-evaluation trigger** (e.g. "after ~N real memory additions land post-reset, or at the next maintenance session"). Then the `provisional`→settled transition (guidelines §2: remove the marker after ~N additions without a refute signal) is mechanically decidable.

- **[R2-6] Label collision: D4 "(R1)" / D5 "(R2)" clash with the review steps R1/R2/R3.** §3 D4/D5 → The parentheticals tag the mandate's Pre-execution-review divergences, but `R1`/`R2`/`R3` are *also* the `_META.md` review-step names — a cold reader cross-referencing notes_v*.md will conflate them. `_META.md § Authority handoffs` explicitly flags this and asks to unify labels. The mandate calls these reconciliations **Recon-A** (scope-model) and **Recon-B** (drop stale `verified`/human-elevation tier). → Change: relabel D4 "(R1)"→"(Recon-A — mandate Pre-exec-review: scope-model divergence)" and D5 "(R2)"→"(Recon-B — mandate Pre-exec-review: stale-tier divergence)". Removes the collision; aligns plan vocabulary with both the mandate and `_META`.

## R3 — Focus/economy (vs v0.1) [ran LAST]

- **[R3-5] Additions are justified and bounded.** S7 (ties criteria to the #1 priority — high value), C7 refinement (makes the provisional marker real, not decorative — required by the paradigm), D4/D5 relabel (pure clarity, kills a cross-doc collision — cheap), R1-6 CONTEXT note (one-line, prevents F10 drift). None bloats. The §3 D-list is now D1–D8 — long, but each is a genuine distinct decision (no padding); keep.
- **[R3-6] Compression: keep C7 within ~4 lines.** The C7 refinement risks growing; cap it — state confirm/refute/trigger as a terse triple, don't prose it. Applied in the edit.
- **[R3-7] No relocation/cut needed.** Guidelines content is still referenced, not duplicated (R3-3 from v0.1 held). No context-bloat introduced this iteration.

---

## Change-Magnitude Summary (v0.2)

- **Breadth**: 4 plan elements changed — §2 (C7 refined), §3 (D4/D5 relabel), §5 Phase 3 (CONTEXT.md note), §7 (+S7). (4 touch-points / 4 sections.)
- **Depth** (highest tier present):
  - **T3 structural**: none (no target/constraint/phase added·removed·redefined; the memory-structure *design* is unchanged — D8 already existed).
  - **T2 substantive**: S7 (new success criterion); C7 refinement (constraint substance — makes provisional testable). → **T2 is the ceiling.**
  - T1 clarity: D4/D5 relabel; CONTEXT.md note.
- **Known-unknowns about plan adequacy discharged (2)**:
  1. *Do the success criteria measure the rubric's #1 property (retrieval one-hop + lateral)?* → No → S7.
  2. *Is the `provisional` marker an actual test or decoration?* → Decoration → C7 confirm/refute/trigger.
  (The D4/D5 relabel is clarity, not an adequacy unknown.)
- **Trend vs v0.1**: highest tier T3→**T2** (dropped); breadth 8→4 (dropped); unknowns 3→2 (dropped). **Clearly decreasing.**
- **Convergence verdict**: **converging** — magnitude and tier both down; no T3 this round. Not yet converged (T2 substantive changes + 2 adequacy unknowns discharged). Continue to v0.3; expect v0.3 to be the borderline check.
