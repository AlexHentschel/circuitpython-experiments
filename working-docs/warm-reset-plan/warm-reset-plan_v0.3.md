# Warm-Reset Execution Plan — v0.3

**Status**: draft (v0.3; iteration 3 of the `_META.md` loop). **Authored**: 2026-06-14. **Consumer**: AI now; Alex at sign-off. **Loop governance**: `_META.md` (same folder). **Changes v0.2→v0.3**: see `notes_v0.3.md` (added placement gate to `04-multi-project.mdc`, added Phase 0.5 mandate pre-flight, noted OQ4/DN-MP-1 as non-blocking, glossed F1/F8/F10). Prior: `notes_v0.2.md`, `notes_v0.1.md`.
**Execution gate**: this plan is NOT executed until Alex says the exact phrase "warm reset" + gives go-ahead (per the mandate's strict-phrase rule).
**Source of truth for the target structure**: `/Users/alex/Development/VsCode/CircuitPython/.cursor/rules/mandates/multi-project.md` (the mandate). This plan operationalizes it; on any conflict the mandate wins unless this plan records a deliberate, Alex-approved deviation.

---

## 1. Target (FIXED — changes escalate to Alex)

Reorganize the flat CircuitPython memory at `.cursor/rules/memory/` into the mandate's multi-project layout so that:
- per-project technical/session/conclusions content is isolated (no cross-contamination — the M1 failure mode; *M1 = the mandate's active-project-identifier: match the most-recently-edited file path against `projects/_INDEX.md` path-globs to pick the active project; its failure mode is writing into the wrong project's memory*),
- cross-project patterns can be detected and promoted/demoted deliberately,
- behavioral memory (about Alex / general craft) is shared once, not forked,
- **all existing content is preserved** — warm reset is a *structural move + tag*, never a content rewrite or prune.

Outcome test (not artifact): a cold AI starting a session in any project retrieves that project's memory correctly and cannot accidentally write into another project's memory.

## 2. Constraints (FIXED — invariants that must hold)

- **C1 No content loss.** Every pre-reset entry survives, moved and/or tagged. Verifiable by diffing the pre-reset snapshot against the post-reset content (set of entries unchanged; only location/tags differ).
- **C2 Snapshot-before-touch.** Copy all of `memory/` to `.cursor/rules/memory-pre-warm-reset-<YYYYMMDD-HHMMSS>/` before the first mutation. Rollback path.
- **C3 Always-injected rules stay valid.** The `.mdc` files (`00-memory-system`, `02-domain-structure`, `03-memory-update-triggers`) reference memory paths; after the move, no rule may point at a dead path.
- **C4 Behavioral memory reachable by both projects.** Post-reset, `WORKING_STYLE.md` / `CODING_PRINCIPLES.md` / `MONITORING.md` must be loadable when working either CircuitPython or Bamboo-Lamp.
- **C5 Cold-AI retrieval intact.** Session-start active-retrieval (read living summary + relevant project memory) must still function after the layout change.
- **C6 No execution without the trigger.** Alex's exact "warm reset" phrase + go-ahead precedes any file mutation.
- **C7 Seed only on evidence; mark the new structure provisional.** Create only structures with content in evidence at move time — no empty domain folders, no per-concept files below volume threshold, no speculative `crossref` categories (guidelines §2 seed-on-evidence, §9 counter-bloat). Rationale anchored in the actual content: `TECHNICAL.md` has only two populated sections (CircuitPython memory-management, fonts) atop all-empty schema tables; `CONCLUSIONS.md` has one finding; domains power/i2c/deep-sleep/fuel-gauge/led-driving have zero content today. Tag the whole new layout `provisional (as of <move date>)` with a watch-for block that is itself cold-AI-testable (per cold-ai-paradigm §7 — a marker without confirm/refute + a trigger is decoration): **confirm** = a real post-reset query resolves one-hop (index→domain→concept) with no speculative search; **refute** = a query needs scanning multiple files / speculative search, or a new finding has no deterministic placement-gate home; **trigger** = re-evaluate after ~N real memory additions land post-reset (or at the next maintenance session). Remove the `provisional` marker once ~N additions land with no refute signal (guidelines §2).

## 3. Known unknowns / decisions to resolve BEFORE execution (ESCALATE to Alex)

Recorded as OPEN with options + a recommendation. None is decided in this plan. (**OQ4/DN-MP-1** — the mandate's new-project-spin-up heuristic — is intentionally *not* in this list: the mandate tracks it as a deferred design note that is **non-blocking** for warm reset ("blocks only on OQ1–OQ3"). Its heuristic lands in `projects/_INDEX.md` header and is revised after 3–5 projects of evidence, guidelines §6.)

- **D1 (OQ1) Project granularity.** Options: (a) per-experiment projects (`exp14`, `exp15`, …); (b) themed families ("ws2812-lighting" groups exp11+exp13); (c) mixed; (d) families spanning beyond CircuitPython. *Recommendation*: (a)+(d) — per-experiment projects under a `circuitpython` family, with Bamboo-Lamp as a separate family. Rationale: matches current reality (exp14/15 active; Bamboo-Lamp is non-CircuitPython electronics).
- **D2 (OQ2) Promotion autonomy.** How much can I promote patterns up the ladder without sign-off? Options: (a) propose-only; (b) auto-promote at the 2-project trigger, sign-off only for `universal`; (c) full autonomy + logged + demotable. *Recommendation*: (b).
- **D3 (OQ3) Scope-tagging of pre-existing entries.** Policy for untagged entries at move time. *Recommendation (from mandate)*: technical/conclusions → the single active project at move time; working-style → `[universal]`/`[user]`; flag ambiguous for review.
- **D4 (Recon-A — mandate Pre-exec-review: scope-model divergence).** Mandate's 3-tier `[universal]/[family]/[project]` vs current 4-tier `[universal]/[user]/[project]/[task]`. Options: merge with documented mapping; keep orthogonal; collapse. *Recommendation*: keep both as orthogonal dimensions (directive-scope = 4-tier; project-content-scope = family/project), since they already coexist (see SoT map in `SESSION_LOG.md`). (Label note: this is the mandate's reconciliation "Recon-A" — distinct from the `_META.md` review step R1.)
- **D5 (Recon-B — mandate Pre-exec-review: stale-tier divergence).** Remove residual `verified`/human-elevation-gate references inside the mandate + anywhere they linger. Mechanical once D4 is set. (Label note: mandate's "Recon-B" — distinct from review step R2.)
- **D6 (new) Behavioral-memory physical home.** Today it sits in the CircuitPython workspace, reachable by Bamboo-Lamp only because both are co-opened. Post-reset `universal/` is still inside `.cursor/rules/`. Does that satisfy C4 for Bamboo-Lamp standalone? Options: (a) accept co-open requirement; (b) relocate `universal/` to a user-level root reachable by all projects. *Recommendation*: decide with D7.
- **D7 (new) Bamboo-Lamp federation.** Bamboo-Lamp already has its own memory home at `/Users/alex/Projects/Family/Bamboo-Lamp/memory/` (outside this workspace). Does warm reset (a) absorb it into `projects/bamboo-lamp/`, or (b) leave it federated in-repo and have `_INDEX.md` point at it? *Recommendation*: (b) federated — Bamboo-Lamp memory should live with the Bamboo-Lamp repo (travels with the project); `_INDEX.md` records its external path. This also informs D6.
- **D8 (new) Concept-graph retrieval layer vs. mandate's flat per-project files.** The mandate's target architecture stores domain knowledge in per-project monolithic `TECHNICAL.md` / `CONCLUSIONS.md`. The design rubric (`microcontroller-multi-project-memory-guidelines.md` §3.1) **explicitly replaces** the "read the big file and scan" model with a **concept-graph**: an always-read `concepts/_INDEX.md`, a typed `concepts/_RELATIONS.md` edge list (lateral concept↔concept traversal — e.g. fonts↔display, memory-management↔led-driving), and one `concepts/<domain>.md` per evidenced domain. Retrieval-efficiency outranks parsimony (guidelines §0/§9), and the concept-graph is what serves it; the mandate predates the guidelines (guidelines Cross-refs flags exactly this reconciliation). **This is a deviation from the mandate, so it is Alex's call, not the plan's.** Options: **(a)** mandate-as-written — flat per-project `TECHNICAL`/`CONCLUSIONS`, accept that lateral concept-traversal is unsupported; **(b)** full concept-graph immediately; **(c)** *graduated* — keep `concepts/_INDEX.md` + `_RELATIONS.md` from day one (cheap retrieval skeleton), start each evidenced domain as one `concepts/<domain>.md` section-per-concept file, split to per-concept files only when a domain grows unwieldy (guidelines §3.1 graduation). *Recommendation*: **(c)** — gives one-hop topic→concept retrieval + lateral edges now, at minimal scaffolding, consistent with C7. **Relation to `crossref/`**: `_RELATIONS.md` is the concept↔concept axis; `crossref/BY_TOPIC|BY_PATTERN` is the cross-*project* axis (which projects touch a topic). They are orthogonal — neither replaces the other; if (a) is chosen, only the cross-project axis exists.

## 3a. Deviations from the literal mandate (each `proposed — needs Alex approval`)

The plan header states the mandate wins on conflict unless a deliberate, Alex-approved deviation is recorded. The deviations this plan proposes:

- **DV1 — `universal/` holds more than `WORKING_STYLE.md`.** Mandate step 4 says move only `WORKING_STYLE.md`. This plan also moves `CODING_PRINCIPLES.md` + `MONITORING.md` + `CHANGELOG.md` into `universal/`. Reason: those files were created 2026-04-21, *after* the mandate was declared (2026-04-17); they are behavioral/structural memory and belong with `WORKING_STYLE.md`. Risk: low (behavioral, shared by design).
- **DV2 — `reference/` stays in place.** The mandate does not move `reference/`; an earlier draft (v0.0 Phase 2) did. Moving it would orphan ~15+ `reference/<file>` path references across `00`/`01`/`03`-`.mdc` + mandate + `COLLABORATOR_GUIDE.md` for zero retrieval gain. Keep `reference/` at `.cursor/rules/reference/`. Risk of moving: high (dead paths); risk of keeping: none.
- **DV3 — Concept-graph layer (D8).** Adopting guidelines §3.1's concept-graph is a structural divergence from the mandate's flat per-project files. Gated on Alex's D8 decision.

## 4. Approach (PROVISIONAL — labelled; expected to evolve)

Follow the mandate's 12-step Warm Reset Protocol, decomposed into phases sized to the learning rate (§5). Decisions (§3) front-loaded into Phase 0 so execution phases are mostly mechanical. Each phase ends with a checkpoint (Observe→Evaluate→Revise→Continue) and a criteria-revision gate.

## 5. Phases (PROVISIONAL — sequence/shape may change; only Phase 0's first action is firm)

- **Phase 0 — Decisions & reconciliations.** Resolve D1–D8 with Alex. Update the mandate's §Pre-execution-review divergences accordingly. *Exit ramp*: do not enter Phase 1 until D1–D5 + D8 are resolved (D8 sets whether the concept-graph layer exists, which shapes Phase 3; D6/D7 may resolve in parallel but block Phase 4).
- **Phase 0.5 — Pre-flight (mandate checklist).** Before any mutation, run the mandate's `§ Pre-warm-reset checklist for the agent` in full: read failure-modes **F1 (Compaction Catastrophe), F8 (Purpose Conflation), F10 (Duplicated Data Drift)** in `reference/06-failure-modes.md`; re-read `00`/`01`/`02`-`.mdc` + `WORKING_STYLE.md` current state; confirm D1–D8 decisions are recorded; state the planned changes back to Alex; await explicit "go ahead". This is the bridge from Phase 0 (decisions) to Phase 1 (first mutation); it is part of the execution gate, not optional.
- **Phase 1 — Snapshot & scaffold.** C2 snapshot; create `universal/`, `projects/`, `crossref/`; create `universal/CHANGELOG.md` (or move existing) with the warm-reset entry as first line.
- **Phase 2 — Move universal.** Move `WORKING_STYLE.md`, `CODING_PRINCIPLES.md`, `MONITORING.md`, `CHANGELOG.md` into `universal/` (DV1). **Leave `reference/` in place** (DV2 — do not move). Create empty `universal/PATTERNS.md`.
- **Phase 3 — CircuitPython projects (seed by evidence, C7).** Create `projects/_INDEX.md` (roster + path globs). Create a full `projects/<slug>/` **only where content exists**: `circuitpython-exp14-display/` (full — both `TECHNICAL` sections, the `CONCLUSIONS` finding, ~20 session blocks); `circuitpython-exp15-*/` as a **minimal stub** (it is the active project but has only ~1 session entry). Do **not** pre-create folders for exp09/11/13 (residue-only — they get an `_INDEX.md` row only if/when content surfaces). Move + tag `TECHNICAL.md`/`CONCLUSIONS.md`/`SESSION_LOG.md` content per D3; create each `CONTEXT.md` (which should *reference* an existing project handoff doc — exp14 has `CONTEXT_HANDOFF.md` — as the canonical scope/goal source rather than copy it; one canonical home per fact, guidelines §9, avoids F10 drift). **If D8 = (b)/(c)**: also create `concepts/_INDEX.md` + `_RELATIONS.md` + one `concepts/<domain>.md` per evidenced domain (today: `circuitpython-runtime`, `fonts`, `display`) — no empty domains.
- **Phase 4 — Bamboo-Lamp integration.** Per D7: either absorb or federate; ensure `_INDEX.md` routes `Bamboo-Lamp/**`.
- **Phase 5 — crossref.** Create `crossref/BY_TOPIC.md` + `BY_PATTERN.md` with format headers.
- **Phase 6 — Rule-file updates.** Re-point `00-memory-system.mdc` paths; **update `01-interaction-style.mdc`** (it references `CONCLUSIONS.md`@36 and `WORKING_STYLE.md`@66/84/93 — omitted in v0.0); replace `02-domain-structure.mdc` Active-Experiment-Detection with the M1 active-project identifier; handle `03-memory-update-triggers.mdc` (split vs inline per mandate divergence note — default split into new `04-multi-project.mdc`); add `04-multi-project.mdc` (scope tagging M2, promotion ladder M3, attention scoping M5, demotion M6, **and the placement gate** — guidelines §4's deterministic-home decision procedure that routes every new finding to exactly one destination; this is what S7-3 tests. The gate is parameterized by D8: its "domain knowledge" branch routes to `concepts/<domain>` if D8≠(a), else to per-project `TECHNICAL.md`). Also re-point `COLLABORATOR_GUIDE.md` and the mandate's own path references (Phase 7 covers COLLABORATOR_GUIDE).
- **Phase 7 — Teardown & propagation.** Remove emptied top-level files; verify no orphaned path refs (grep); update `COLLABORATOR_GUIDE.md`.
- **Phase 8 — Verification.** Run §7 success criteria; log completion in `universal/CHANGELOG.md` with `status: warm-reset-completed`.

## 6. Authority handoffs (FIXED)

- **Autonomous**: mechanical moves, scaffolding, path re-pointing, tagging per the agreed D3 policy.
- **Escalate**: D1–D8; the §3a deviations (DV1–DV3); any content that resists clean tagging (ambiguous scope); any discovered mandate inconsistency.
- **Scope discipline**: if execution reveals the move is bigger/messier than planned (e.g. entries that don't fit one project), STOP and surface before expanding scope.

## 7. Success criteria (INITIAL — revisable at every checkpoint)

- **S1** Snapshot exists and is complete (C2).
- **S2** Content-preservation diff: entry set identical pre/post (C1).
- **S3** No dangling **qualified** path references after the move (C3). Grep ALL rule files (`00`,`01`,`02`,`03`, new `04`) + `COLLABORATOR_GUIDE.md` + the mandate for both **qualified** `memory/<file>` paths (these break when files move) and **bare-name** mentions (`WORKING_STYLE.md` etc. — these still resolve conceptually but update for accuracy). Acceptance = zero dangling qualified paths; bare-name mentions reviewed.
- **S4** Cold-AI session-start simulation succeeds for: CircuitPython exp14, exp15, Bamboo-Lamp (each retrieves its own memory; none can write another's) (C5, target test).
- **S5** Behavioral memory loads for both projects (C4).
- **S6** `universal/CHANGELOG.md` logs the reset; rollback documented.
- **S7** Retrieval acceptance tests pass (guidelines §8 — operationalizes the §1 outcome test, the rubric's #1 priority): (1) **domain one-hop** — a real domain question (e.g. "RP2040 GC heap doubling behaviour?") resolves via `_INDEX`→domain→concept with no speculative search; (2) **lateral relation** — a related-concept query surfaces the linked concept via `_RELATIONS` (applies only if D8≠(a)); (3) **cross-project pollination** — a pattern lands at exactly one deterministic placement-gate home. Run whichever apply given the D8 choice.

## 8. Exit ramps (FIXED)

Pause + surface if: a §3 decision blocks progress; C1 (no-loss) cannot be guaranteed for some entry; the mandate proves internally inconsistent; or the task drifts from "execute the mandate" toward "redesign the mandate".

## 9. Termination & checkpoints

Each phase close = a checkpoint running the full closed-loop cycle: **Observe** (what did this phase reveal?) → **Evaluate** (does it change targets/constraints/known-unknowns/criteria/approach?) → **Revise** (state a specific change *or* explicit "no change, continuing") → **Continue**. Plus a **criteria-revision gate**: re-ask "are S1–S7 still the right criteria?" *and* "did this phase surface a new criterion?" — if so, record it with dated provenance and escalate its adoption per §6 (do not silently absorb). Plan-execution terminates at Phase 8 success; the *planning loop* terminates per `_META.md` diminishing-returns rule.

## 10. Open question to Alex (highest priority)

Resolve D1–D8 (§3). **Load-bearing decision set = {D1 granularity, D4 scope-model, D8 concept-graph}** — if any of these is decided wrongly, the most phases invalidate (Phases 3–6 depend on them). Revisit these first at every checkpoint and weight them first in the risk register. D6/D7 (reachability/federation) block Phase 4 specifically. D2/D3/D5 are mostly mechanical once the keystones are set.
