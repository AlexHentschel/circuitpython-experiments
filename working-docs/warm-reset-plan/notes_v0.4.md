# notes_v0.4 — review of warm-reset-plan toward v0.4

**Consumer**: AI only, dense. **Produced**: 2026-06-14. **Governance**: `_META.md`. **Reviews v0.3**; applied into `warm-reset-plan_v0.4.md`.
No new crawls. Pure R1–R3. Expectation entering this iteration: substantive gaps closed in v0.1–v0.3; looking for residual T2 + confirming convergence.
Finding format: `[id] location → problem → change`.

---

## R1 — Structure-fit (substance) [ran FIRST]

- **[R1-8] Active-Retrieval order vs M5 attention-scoping: Phase 6 understates the change as a "path re-point".** §5 Phase 6 ("re-point `00-memory-system.mdc` paths") → `00-memory-system.mdc § Active Retrieval` currently prescribes a **flat** session-start read order (SESSION_LOG → WORKING_STYLE → CODING_PRINCIPLES → MONITORING → CONCLUSIONS → TECHNICAL → CHANGELOG). After warm reset, session-start behavior must become **project-scoped (M5)**: always read `universal/*` + `projects/_INDEX.md`; read the *active* project's `CONTEXT`/`SESSION_LOG`(last 1–2)/`TECHNICAL`/`CONCLUSIONS` only; (+ `concepts/_INDEX.md` if D8≠(a)); other projects only via `crossref/`. That is a **behavioral rewrite of the read order**, not a path re-point — and if `00`'s flat order is left in place alongside `04`'s M5, a cold AI faces two conflicting read-order instructions (F8 Purpose Conflation / F10 Duplicated Data Drift). → Change: in Phase 6, split the `00-memory-system.mdc` task into (i) re-point paths *and* (ii) replace § Active Retrieval's flat order with the M5 project-scoped order (or make it explicitly defer to `04-multi-project.mdc § Attention scoping` as the single source of truth — one canonical home). Add this as an explicit S3-adjacent check: no two files prescribe different session-start read orders.

## R2 — Paradigm-compliance (form) [ran SECOND]

- **[R2-10] S6 "rollback documented" is not concrete enough to be a test.** §7 S6 → "rollback documented" leaves a cold executor unsure what satisfies it. cold-AI §2 (signals must be mechanical). → Change: make S6 concrete — "rollback procedure stated as an exact restore command (`rm -rf` the new tree + `cp -R` the `memory-pre-warm-reset-<ts>/` snapshot back to `memory/`, or equivalent), present in `universal/CHANGELOG.md`; the snapshot's existence is S1." Cheap, makes S6 checkable.
- **[R2-11] No further decode/layering gaps found.** M1 decoded (§1); M2/M3/M5/M6 glossed inline (Phase 6); F1/F8/F10 expanded (Phase 0.5); D/DV/Recon/S/C/phase label spaces are internally consistent (verified by range-grep this iteration). Flexible-plans layering intact (fixed §1/§2/§6/§8, provisional §4/§5/§7, open artifact shapes; checkpoints + criteria gate §9; exit ramps §8). No change.

## R3 — Focus/economy (vs v0.3) [ran LAST]

- **[R3-11] Both additions justified, minimal.** R1-8 closes a real dual-source-of-truth hazard (and it is the last mechanism-coordination gap between the `.mdc` layer and the new structure); S6 concreteness is a one-clause clarity fix. No bloat; no relocation/cut needed.
- **[R3-12] Plan size is stable.** v0.1 added the big structural scaffolding (D8/C7/§3a); v0.2–v0.4 have only refined and closed gaps without growing the section count (Phase 0.5 was the only structural insert, in v0.3). Context cost is flat. This is the diminishing-returns signature.

---

## Change-Magnitude Summary (v0.4)

- **Breadth**: 2 plan elements changed — §5 Phase 6 (Active-Retrieval/M5 split), §7 S6 (rollback concreteness). (2 touch-points.)
- **Depth** (highest tier present):
  - **T3 structural**: none.
  - **T2 substantive**: R1-8 (Phase 6 now mandates the M5 read-order rewrite + single-source-of-truth check — a behavioral correction the plan previously mis-scoped). → **T2 ceiling, but only one T2.**
  - T1 clarity: S6 concreteness.
- **Known-unknowns about plan adequacy discharged (1)**:
  1. *Does the plan correctly update session-start behavior (not just paths) and avoid dual conflicting read-orders?* → No → R1-8.
- **Trend vs v0.3**: highest tier T2→T2 (flat) but **count of T2 findings 1→1 and breadth 4→2 (halved); unknowns 2→1 (halved).** Magnitude clearly decreasing; the T2 found this round is the last mechanism-coordination gap.
- **Convergence verdict**: **converging → expect converged next.** One T2 remained (a genuine coordination gap, now closed) so not converged at v0.4. Per `_META` C-converged (≤T1 + zero adequacy-unknowns) is not yet met, and the trend is decreasing-but-borderline → run **one more** iteration (v0.5) to confirm: predict v0.5 yields only T1/T0 with zero adequacy-unknowns → converged at the cap. (This also coincides with C-cap = 5 iterations.)
