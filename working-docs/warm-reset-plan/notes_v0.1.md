# notes_v0.1 — review of warm-reset-plan toward v0.1

**Consumer**: AI only, dense. **Produced**: 2026-06-14. **Governance**: `_META.md` (iteration loop, review order R1→R2→R3, CMS schema).
**Reviews v0.0** (`warm-reset-plan_v0.0.md`); changes here are applied into `warm-reset-plan_v0.1.md`.
**Evidence base this iteration**: sub-agent crawls exp-1 (memory content-by-domain) + exp-2 (memory-path references) — see `experiment-log.md`; plus direct parent reads of `TECHNICAL.md` (2 populated sections atop empty schema) and `CONCLUSIONS.md` (1 finding).
Finding format: `[id] location → problem → change (what + how)`.

---

## R1 — Structure-fit (substance) [ran FIRST]

Rubric: `microcontroller-multi-project-memory-guidelines.md` (§0 one-hop target; §2 seed-on-evidence; §3 concept-graph + graduation; §6 granularity; §9 parsimony-vs-retrieval, tie-break = retrieval > parsimony).

- **[R1-1] Missing concept-graph retrieval layer.** §1+§5 (whole target structure) → The plan operationalizes the *mandate's* architecture: per-project monolithic `TECHNICAL.md` / `CONCLUSIONS.md`. But the R1 rubric (guidelines §3.1) **explicitly replaces** "read the big technical file and scan" with **domain-indexed concept entries + a relation graph** (`concepts/_INDEX.md` always-read, `concepts/_RELATIONS.md`, `concepts/<domain>.md`). Retrieval-efficiency is the #1 priority and outranks parsimony (§0, §9), and it is served by the concept-graph, *not* by per-project big files. The plan has **no** concept-graph layer at all → largest structure-fit gap. **Authority caveat**: adopting the concept-graph is a deviation from the mandate (mandate wins on conflict unless Alex approves a deviation), so this is NOT mine to bake in — it must escalate. → Change: add **D8 (new escalation)** "Adopt the guidelines' concept-graph retrieval layer (in graduated form) instead of / alongside the mandate's flat per-project `TECHNICAL`/`CONCLUSIONS`?" with options [(a) mandate-as-written flat files; (b) concept-graph fully; (c) graduated: `concepts/_INDEX.md` + `_RELATIONS.md` from day 1, one `concepts/<domain>.md` per evidenced domain, split-to-files later] + recommendation (c), rationale retrieval>parsimony + mandate predates guidelines (guidelines Cross-refs already flags the reconciliation). Add to §3 + §10; note in new §Deviations.

- **[R1-2] Seed-on-evidence not a stated constraint; plan risks empty scaffolding.** §5 (Phases 3, 5) → Actual content is *tiny + concentrated*: `TECHNICAL.md` populated sections = only **circuitpython-runtime/memory-management** + **fonts** (display formula is exp14-tagged inside fonts); ALL schema tables (Terminology, Boards, Library Map, Hardware Patterns, Pin/Peripheral, Toolchain, Code Map) are **empty**. `CONCLUSIONS.md` = **1** evidence-supported finding. Domains power/i2c/deep-sleep/fuel-gauge/led-driving = **zero** content. Guidelines §2/§3.1/§9 forbid pre-creating empty domains / per-concept files / speculative crossref categories. → Change: add **Constraint C7** "Seed only structures with content in evidence at move time — no empty domain folders, no per-concept files below volume, no speculative `crossref` categories (guidelines §2). Mark the entire new structure `provisional` + attach a 2–4 line watch-for block (what would show it works/fails)." Add to §2; reference from Phases 3/5.

- **[R1-3] Project-granularity must track evidence, not roster ambition.** §5 Phase 3 → exp14 = dominant (~20 session blocks, both TECHNICAL sections, the CONCLUSIONS finding); exp15 = **1** session entry (active, bootstrap); exp09/11/13 = **residue mentions only** (no dedicated memory). Creating folders for exp09/11/13 = empty scaffolding (violates C7). → Change: refine Phase 3 — create a full `projects/<slug>/` only where content exists (exp14 full; exp15 minimal stub because it is the *active* project); exp09/11/13 get an `_INDEX.md` roster row **only if** content surfaces, never a pre-created folder. Cross-ref C7.

- **[R1-4] Lateral-relation layer absent; crossref ≠ relations.** §5 Phase 5 → Guidelines §0/§8 acceptance-test-2 require lateral traversal (concept↔related-concept, e.g. fonts↔display, memory-management↔led-driving) via a typed `_RELATIONS.md` edge list. Plan's `crossref/BY_TOPIC|BY_PATTERN` is a **cross-project** index (which projects touch topic X), a *different axis* from concept-relations. → Change: inside D8, state that if the concept-graph is adopted, `_RELATIONS.md` is the lateral (concept→concept) layer and `crossref/` remains the cross-*project* pollination layer — the two are orthogonal, neither replaces the other. If D8 picks (a) flat files, flag that lateral traversal is then unsupported (a known retrieval cost to accept explicitly).

## R2 — Paradigm-compliance (form) [ran SECOND]

Gates: cold-AI (`cold-ai-paradigm.md`: decode/purpose/signals/lifecycle/how-to-check) + flexible-plans (`flexible-plans-for-ai-execution.md`: fixed/provisional/open layering, checkpoint + criteria-revision gate, diminishing-returns termination, scope-escalation, sketches-as-hypotheses).

- **[R2-1] Cold-AI decode gap: "M1".** §1 ("the M1 failure mode"), §5 Phase 6 ("the M1 active-project identifier") → "M1" is decodable only by opening the mandate. → Change: ground inline at first use — "(M1 = the mandate's active-project-identifier: match most-recently-edited file path against `projects/_INDEX.md` path-globs to pick the active project; its failure mode is writing into the wrong project's memory)".

- **[R2-2] Flexible-plans: criteria-revision gate under-specified.** §7 (criteria marked INITIAL ✓) + §9 (re-asks "are S1–S6 still right?") → §9 checks criterion *existence* but not criterion *additions* surfaced by execution (the paradigm's explicit gate: "are the criteria still the right ones? + record newly-surfaced criteria with dated provenance, escalate adoption"). → Change: extend §9 to the full Observe→Evaluate→Revise→Continue cycle and add "any criterion newly surfaced this phase → record with dated provenance + escalate adoption per §6 (don't silently absorb)".

- **[R2-3] Flexible-plans: load-bearing assumptions not tagged distinctly.** §3/§10 → §10 calls D1, D4 keystones (partial). Paradigm wants load-bearing assumptions tagged so they're revisited first when evidence arrives. → Change (light, fold into §10 — do NOT add a new section): mark the load-bearing decision set explicitly = {D1 granularity, D4 scope-model, D8 concept-graph}; "if any of these is decided wrongly, the most phases invalidate — revisit these first at every checkpoint and weight them first in the risk register." Avoid duplicating the risk-register content.

- **[R2-4] Deviations from the literal mandate are unrecorded.** Plan header promises "on conflict the mandate wins unless this plan records a deliberate, Alex-approved deviation" — but the plan silently deviates: Phase 2 moves CODING_PRINCIPLES.md + MONITORING.md + CHANGELOG.md + reference/ into `universal/`, whereas mandate step 4 only says "move WORKING_STYLE.md". → Change: add a short **§Deviations from the literal mandate** subsection enumerating each deviation with status `proposed / needs-Alex-approval`: (a) `universal/` also holds CODING_PRINCIPLES.md + MONITORING.md (post-mandate files, 2026-04-21) — low-risk, behavioral; (b) reference/ handling — see R3-1; (c) concept-graph layer — D8. Keeps the authority contract honest for a cold reader.

## R3 — Focus/economy (vs v0.0) [ran LAST]

Net out R1+R2 additions; for each ask "does this earn its context cost, or compress / move to guidelines / cut?".

- **[R3-1] DROP the reference/ move — high dead-path cost, ~zero retrieval benefit.** §5 Phase 2 moves `.cursor/rules/reference/` → `universal/`. exp-2 found **~15+ `reference/<file>` path references** across 00-/01-/03-memory-system .mdc + mandate + COLLABORATOR_GUIDE that this move would orphan (e.g. `reference/06-failure-modes.md`, `reference/08-bootstrapping.md`). `reference/` is on-demand persona doctrine, not project memory, and the mandate does **not** require moving it (step 4 = WORKING_STYLE only). → Change: remove `reference/` from Phase 2; leave it at `.cursor/rules/reference/`. Record in §Deviations: "reference/ stays in place (mandate does not move it; moving it would orphan ~15+ refs for no retrieval gain)." Net: removes work + removes a whole dead-path class.

- **[R3-2] Phase 6 / S3 rule-file set is incomplete.** §5 Phase 6 names only 00/02/03; exp-2 shows **01-interaction-style.mdc** references memory files (CONCLUSIONS.md@36, WORKING_STYLE.md@66/84/93) and so does COLLABORATOR_GUIDE.md + the mandate. → Change: add 01-interaction-style.mdc to Phase 6 scope; reframe **S3** to "grep ALL rule files (00,01,02,03, new 04) + COLLABORATOR_GUIDE + mandate for both **qualified** `memory/<file>` paths (these break on move) and **bare-name** mentions (these still resolve but should be updated for accuracy); zero dangling qualified paths.". Note the qualified-vs-bare distinction so the cold executor knows which class actually breaks.

- **[R3-3] Don't restate guidelines content in the plan.** §3 D1 + §5 paraphrase domain/granularity reasoning that lives in the guidelines doc. → Change: have the new C7/D8 cite guidelines §-numbers instead of restating; do not copy the candidate-domain list into the plan (point to guidelines §3.1). One canonical home per fact (guidelines §9).

- **[R3-4] Net verdict on R1/R2 additions: justified.** D8 (closes the #1 structure-fit gap), C7 (prevents empty-scaffold bloat), §Deviations (authority contract), the reference/-drop (economy + dead-path), 01-mdc addition (correctness) all earn their cost. Compression applied: R2-3 folds into §10 (no new section); R3-3 keeps the plan referencing the guidelines rather than duplicating. No additions cut.

---

## Change-Magnitude Summary (v0.1)

- **Breadth**: ~8 distinct plan elements changed — §1 (M1 decode), §2 (+C7), §3 (+D8; load-bearing note relocated to §10), §5 Phase 2 (−reference/ move), §5 Phase 3 (granularity-by-evidence), §5 Phase 6 (+01-mdc), §7/§9 (criteria-revision gate), §10 (load-bearing set), +new §Deviations, +S3 reframe. (10 touch-points across 8 sections.)
- **Depth** (highest tier present = what matters):
  - **T3 structural**: D8 added (a decision that can change the memory-structure design itself); C7 constraint added (seed-on-evidence); reference/-move removed from scope (phase content changed). → **T3 present.**
  - T2 substantive: criteria-revision gate (§9), granularity-by-evidence (Phase 3), Phase 6 scope, S3 reframe, §Deviations, load-bearing set.
  - T1 clarity: M1 decode.
- **Known-unknowns about plan adequacy discharged (3)**:
  1. *Does the target structure match the actual content volume/shape?* → No; content is tiny + exp14-concentrated → C7 seed-on-evidence + Phase-3 granularity-by-evidence.
  2. *Does the plan cover all dead-path surfaces?* → No; reference/-move orphans ~15+ refs and 01-mdc was missing → R3-1 + R3-2.
  3. *Does the target satisfy the R1 retrieval rubric?* → No; concept-graph layer absent → D8.
- **Trend vs v0.0**: first iteration — no prior to compare; magnitude expected high (it is).
- **Convergence verdict**: **not-converged** — T3 changes present + 3 adequacy known-unknowns discharged. Continue to v0.2.
