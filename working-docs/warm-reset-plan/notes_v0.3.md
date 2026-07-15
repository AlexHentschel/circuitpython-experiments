# notes_v0.3 — review of warm-reset-plan toward v0.3

**Consumer**: AI only, dense. **Produced**: 2026-06-14. **Governance**: `_META.md`. **Reviews v0.2**; applied into `warm-reset-plan_v0.3.md`.
No new crawls — inventories from cycle 1 still current. Pure R1–R3 reasoning.
Finding format: `[id] location → problem → change`.

---

## R1 — Structure-fit (substance) [ran FIRST]

- **[R1-7] Placement gate is tested (S7-3) but never created.** §5 Phase 6 / §7 S7 → S7(3) "cross-project pollination — a pattern lands at exactly one deterministic placement-gate home" depends on a **placement gate** existing post-reset. Phase 6's `04-multi-project.mdc` content is listed as "scope tagging (M2), promotion ladder (M3), attention scoping (M5), demotion (M6)" — but **not** the placement gate (guidelines §4: the deterministic-home decision procedure that routes every new finding to exactly one destination). Without it, S7(3) tests a mechanism the plan didn't build. → Change: add the placement gate (guidelines §4) to `04-multi-project.mdc`'s content list in Phase 6. (Note interaction with D8: the gate's "domain knowledge → `concepts/<domain>`" branch exists only if D8≠(a); under (a) it routes to per-project `TECHNICAL.md` instead — state the gate is parameterized by the D8 choice.)

## R2 — Paradigm-compliance (form) [ran SECOND]

- **[R2-7] The mandate's pre-warm-reset checklist is not represented as an execution step.** §5 Phase 1 / header execution-gate → The mandate has a mandatory **pre-warm-reset checklist** (read failure-modes F1/F8/F10; re-read `00`/`01`/`02`-`.mdc` + `WORKING_STYLE.md`; confirm OQ1–3 recorded; state planned changes back; await explicit "go ahead"). The plan covers the *trigger* (C6, §8) but never surfaces the pre-flight as a step a cold executor must run before Phase 1's first mutation. A cold AI executing this plan could snapshot-and-scaffold without doing the mandate's required reading. → Change: add **Phase 0.5 — Pre-flight (mandate checklist)** before Phase 1: run the mandate's `§ Pre-warm-reset checklist for the agent` in full (failure-mode reads, rule re-reads, decision-recording confirmation, state-changes-back, await go-ahead). This is the bridge between Phase 0 (decisions) and Phase 1 (first mutation).

- **[R2-8] OQ4 / DN-MP-1 not noted as intentionally non-blocking.** §3 → The plan resolves D1(OQ1)/D2(OQ2)/D3(OQ3) but is silent on the mandate's **OQ4** (new-project-spin-up heuristic), which the mandate explicitly tracks as deferred design-note **DN-MP-1** and declares *non-blocking* ("warm reset may execute with DN-MP-1 unresolved; it only blocks on OQ1–OQ3"). A cold reader could mistake the omission for a missing decision. → Change: add a one-line note to §3 — "OQ4/DN-MP-1 (when to spin up a new project vs. extend) is intentionally deferred per the mandate; non-blocking; its heuristic lands in `projects/_INDEX.md` header and is revised after 3–5 projects of evidence (guidelines §6)."

- **[R2-9] cold-AI decode: `F10` / `F1`/`F8` used without inline gloss.** §5 Phase 3 note ("avoids F10 drift") + (new) Phase 0.5 → Spell out at first use: F1 = Compaction Catastrophe, F8 = Purpose Conflation, F10 = Duplicated Data Drift (per `reference/06-failure-modes.md`). → Change: gloss F10 at the Phase 3 first use; the Phase 0.5 addition carries the F1/F8/F10 expansion.

## R3 — Focus/economy (vs v0.2) [ran LAST]

- **[R3-8] Additions justified, all small.** Placement gate (closes the S7-3 build/test gap — necessary), Phase 0.5 pre-flight (closes a mandate-compliance gap — necessary, and it's a reference to the mandate's own checklist, not a restatement), OQ4 note + F10 gloss (clarity, one line each). No bloat.
- **[R3-9] Watch for phase-count creep.** Adding Phase 0.5 keeps the phase list readable (0, 0.5, 1–8); acceptable. No renumbering churn (avoids the cost of resequencing 1–8). 
- **[R3-10] No cuts/relocations.** Guidelines still referenced not duplicated; mandate checklist referenced not copied. Plan remains focused.

---

## Change-Magnitude Summary (v0.3)

- **Breadth**: 4 plan elements changed — §3 (OQ4/DN-MP-1 note), §5 Phase 6 (+placement gate), §5 (+Phase 0.5 pre-flight), §5 Phase 3 (F10 gloss). (4 touch-points.)
- **Depth** (highest tier present):
  - **T3 structural**: none (no target/constraint redefined; no phase *resequenced* — Phase 0.5 is inserted between existing phases without renumbering; the memory-structure design is unchanged).
  - **T2 substantive**: placement gate added to the `04-multi-project.mdc` artifact (a mechanism the success criteria depend on); Phase 0.5 pre-flight (an execution step the mandate requires). → **T2 ceiling.**
  - T1 clarity: OQ4/DN-MP-1 note; F10 gloss.
- **Known-unknowns about plan adequacy discharged (2)**:
  1. *Does the plan build the placement gate that S7-3 tests?* → No → R1-7.
  2. *Does the plan enforce the mandate's required pre-flight before mutating?* → No → R2-7 (Phase 0.5).
- **Trend vs v0.2**: highest tier T2→T2 (flat); breadth 4→4 (flat); unknowns 2→2 (flat). **Plateauing at T2, not yet decreasing to T1.**
- **Convergence verdict**: **converging (borderline)** — still T2 + 2 adequacy unknowns, but these are closing genuine build/test and compliance gaps rather than design changes (no T3 for two iterations). Per `_META` C-converged needs ≤T1 + zero unknowns; not met. Continue to v0.4; expect v0.4 to drop to T1/T0 (the substantive gaps are now closed) — v0.4 is the confirmation iteration.
