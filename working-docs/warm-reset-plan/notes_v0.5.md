# notes_v0.5 — review of warm-reset-plan toward v0.5 (CONFIRMATION / cap iteration)

**Consumer**: AI only, dense. **Produced**: 2026-06-14. **Governance**: `_META.md`. **Reviews v0.4**; applied into `warm-reset-plan_v0.5.md`.
No new crawls. Pure R1–R3. This is both the borderline-confirmation iteration (per `_META` C-converged "run one more if borderline") and the `_META` C-cap (5th iteration).
Finding format: `[id] location → problem → change`.

---

## R1 — Structure-fit (substance) [ran FIRST]

- **[R1-9] (T1) `crossref/` starts empty by necessity — say so, so a cold executor doesn't read it as a defect.** §5 Phase 5 → `crossref/BY_TOPIC|BY_PATTERN` records cross-*project* patterns, which require 2+ projects with real content. At reset, only exp14 has substantial content (exp15 is a stub) → there are **no** cross-project patterns to record yet, so these files are header-only at reset. That is expected (the header is the retrieval skeleton, kept from day one per guidelines §3.1), not empty scaffolding forbidden by C7. → Change: one clause in Phase 5 — "header-only at reset is expected (no 2-project patterns exist yet); first entries appear when a second project accrues content — not a C7 violation (skeleton index, not speculative domain)."
- **[R1-10] No further structure-fit findings.** Concept-graph (D8), seed-on-evidence (C7), evidence-based granularity (Phase 3), retrieval acceptance tests (S7), placement gate + lateral relations + M5 attention scoping (Phase 6) all present and mutually consistent. Structure-fit is satisfied against the rubric.

## R2 — Paradigm-compliance (form) [ran SECOND]

- **[R2-12] (T1) §4 Approach: add a pointer that phase↔mandate-step mapping is per-phase.** §4 → §4 says "Follow the mandate's 12-step Warm Reset Protocol, decomposed into phases" without stating where the mapping lives. Cheap clarity: note that each phase names the mandate steps / M-mechanisms it realizes inline (Phases reference M1/M2/M3/M5/M6, DV1–3, C-constraints already). → Change: one clause in §4. (Deliberately not building an explicit 12-row mapping table — flexible-plans: step sequences stay open; the per-phase inline references suffice.)
- **[R2-13] No decode/lifecycle/layering gaps.** Re-verified: all label spaces (D1–D8, DV1–3, Recon-A/B, M1–M6, S1–S7, C1–C7, Phases 0/0.5/1–8) are internally consistent and decodable; forward-looking items (C7 provisional marker, S7 tests, success criteria) carry signals/triggers; flexible-plans layering and authority map intact. No change.

## R3 — Focus/economy (vs v0.4) [ran LAST]

- **[R3-13] Two one-clause clarity additions; zero net growth of substance.** Both R1-9 and R2-12 are single clauses that prevent cold-executor misreads; neither adds a mechanism or changes a decision. No bloat, nothing to cut/relocate.
- **[R3-14] Diminishing-returns confirmed.** Across v0.1→v0.5: T3 (v0.1) → T2 (v0.2) → T2 (v0.3) → T2 (v0.4) → **T1 (v0.5)**; adequacy-unknowns 3→2→2→1→**0**; breadth 8→4→4→2→2(both T1). The substance curve has flattened to clarity-only. Plan carries all necessary context without accretion.

---

## Change-Magnitude Summary (v0.5)

- **Breadth**: 2 plan elements changed — §5 Phase 5 (crossref-empty-expected clause), §4 (phase↔step mapping pointer). (2 touch-points, both clarity.)
- **Depth** (highest tier present):
  - **T3 structural**: none.
  - **T2 substantive**: **none.**
  - **T1 clarity**: R1-9 (crossref note), R2-12 (Approach pointer). → **T1 ceiling.**
  - T0: none.
- **Known-unknowns about plan adequacy discharged**: **0** (no question about whether the plan is *good enough* was answered this round — both changes are reader-clarity, not adequacy).
- **Trend vs v0.4**: highest tier T2→**T1** (dropped below the substantive line); adequacy-unknowns 1→**0**; trend non-increasing.
- **Convergence verdict**: **CONVERGED.** Meets `_META` C-converged: highest depth tier ≤ T1 (no T2/T3) **AND** zero adequacy-unknowns discharged **AND** non-increasing trend. Also coincides with C-cap (5th iteration). The borderline-confirmation requirement is satisfied — this iteration is itself the confirming pass and it came back clean. **Exit the loop → Post-loop close** (`cp` v0.5 → v1.0; cross-notes risk scan → `risk-register.md`).
