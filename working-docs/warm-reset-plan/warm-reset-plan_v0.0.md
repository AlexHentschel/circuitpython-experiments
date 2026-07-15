# Warm-Reset Execution Plan — v0.0

**Status**: draft (v0.0, initial). **Authored**: 2026-06-14. **Consumer**: AI now; Alex at sign-off. **Loop governance**: `_META.md` (same folder).
**Execution gate**: this plan is NOT executed until Alex says the exact phrase "warm reset" + gives go-ahead (per the mandate's strict-phrase rule).
**Source of truth for the target structure**: `/Users/alex/Development/VsCode/CircuitPython/.cursor/rules/mandates/multi-project.md` (the mandate). This plan operationalizes it; on any conflict the mandate wins unless this plan records a deliberate, Alex-approved deviation.

---

## 1. Target (FIXED — changes escalate to Alex)

Reorganize the flat CircuitPython memory at `.cursor/rules/memory/` into the mandate's multi-project layout so that:
- per-project technical/session/conclusions content is isolated (no cross-contamination — the M1 failure mode),
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

## 3. Known unknowns / decisions to resolve BEFORE execution (ESCALATE to Alex)

Recorded as OPEN with options + a recommendation. None is decided in this plan.

- **D1 (OQ1) Project granularity.** Options: (a) per-experiment projects (`exp14`, `exp15`, …); (b) themed families ("ws2812-lighting" groups exp11+exp13); (c) mixed; (d) families spanning beyond CircuitPython. *Recommendation*: (a)+(d) — per-experiment projects under a `circuitpython` family, with Bamboo-Lamp as a separate family. Rationale: matches current reality (exp14/15 active; Bamboo-Lamp is non-CircuitPython electronics).
- **D2 (OQ2) Promotion autonomy.** How much can I promote patterns up the ladder without sign-off? Options: (a) propose-only; (b) auto-promote at the 2-project trigger, sign-off only for `universal`; (c) full autonomy + logged + demotable. *Recommendation*: (b).
- **D3 (OQ3) Scope-tagging of pre-existing entries.** Policy for untagged entries at move time. *Recommendation (from mandate)*: technical/conclusions → the single active project at move time; working-style → `[universal]`/`[user]`; flag ambiguous for review.
- **D4 (R1) Scope-model reconciliation.** Mandate's 3-tier `[universal]/[family]/[project]` vs current 4-tier `[universal]/[user]/[project]/[task]`. Options: merge with documented mapping; keep orthogonal; collapse. *Recommendation*: keep both as orthogonal dimensions (directive-scope = 4-tier; project-content-scope = family/project), since they already coexist (see SoT map in `SESSION_LOG.md`).
- **D5 (R2) Stale tier cleanup.** Remove residual `verified`/human-elevation-gate references inside the mandate + anywhere they linger. Mechanical once D4 is set.
- **D6 (new) Behavioral-memory physical home.** Today it sits in the CircuitPython workspace, reachable by Bamboo-Lamp only because both are co-opened. Post-reset `universal/` is still inside `.cursor/rules/`. Does that satisfy C4 for Bamboo-Lamp standalone? Options: (a) accept co-open requirement; (b) relocate `universal/` to a user-level root reachable by all projects. *Recommendation*: decide with D7.
- **D7 (new) Bamboo-Lamp federation.** Bamboo-Lamp already has its own memory home at `/Users/alex/Projects/Family/Bamboo-Lamp/memory/` (outside this workspace). Does warm reset (a) absorb it into `projects/bamboo-lamp/`, or (b) leave it federated in-repo and have `_INDEX.md` point at it? *Recommendation*: (b) federated — Bamboo-Lamp memory should live with the Bamboo-Lamp repo (travels with the project); `_INDEX.md` records its external path. This also informs D6.

## 4. Approach (PROVISIONAL — labelled; expected to evolve)

Follow the mandate's 12-step Warm Reset Protocol, decomposed into phases sized to the learning rate (§5). Decisions (§3) front-loaded into Phase 0 so execution phases are mostly mechanical. Each phase ends with a checkpoint (Observe→Evaluate→Revise→Continue) and a criteria-revision gate.

## 5. Phases (PROVISIONAL — sequence/shape may change; only Phase 0's first action is firm)

- **Phase 0 — Decisions & reconciliations.** Resolve D1–D7 with Alex. Update the mandate's §Pre-execution-review divergences accordingly. *Exit ramp*: do not enter Phase 1 until D1–D5 are resolved (D6/D7 may resolve in parallel but block Phase 4).
- **Phase 1 — Snapshot & scaffold.** C2 snapshot; create `universal/`, `projects/`, `crossref/`; create `universal/CHANGELOG.md` (or move existing) with the warm-reset entry as first line.
- **Phase 2 — Move universal.** Move `WORKING_STYLE.md`, `CODING_PRINCIPLES.md`, `MONITORING.md`, `CHANGELOG.md`, and `reference/` into `universal/`. Create empty `universal/PATTERNS.md`.
- **Phase 3 — CircuitPython projects.** Create `projects/_INDEX.md` (roster + path globs); create `projects/circuitpython-exp14-display/` and `-exp15-*/`; move + tag the `TECHNICAL.md`/`CONCLUSIONS.md`/`SESSION_LOG.md` content per D3; create each `CONTEXT.md`.
- **Phase 4 — Bamboo-Lamp integration.** Per D7: either absorb or federate; ensure `_INDEX.md` routes `Bamboo-Lamp/**`.
- **Phase 5 — crossref.** Create `crossref/BY_TOPIC.md` + `BY_PATTERN.md` with format headers.
- **Phase 6 — Rule-file updates.** Re-point `00-memory-system.mdc` paths; replace `02-domain-structure.mdc` Active-Experiment-Detection with the M1 active-project identifier; handle `03-memory-update-triggers.mdc` (split vs inline per mandate divergence note — default split into new `04-multi-project.mdc`); add `04-multi-project.mdc` (scope tagging, promotion ladder, attention scoping, demotion).
- **Phase 7 — Teardown & propagation.** Remove emptied top-level files; verify no orphaned path refs (grep); update `COLLABORATOR_GUIDE.md`.
- **Phase 8 — Verification.** Run §7 success criteria; log completion in `universal/CHANGELOG.md` with `status: warm-reset-completed`.

## 6. Authority handoffs (FIXED)

- **Autonomous**: mechanical moves, scaffolding, path re-pointing, tagging per the agreed D3 policy.
- **Escalate**: D1–D7; any content that resists clean tagging (ambiguous scope); any discovered mandate inconsistency.
- **Scope discipline**: if execution reveals the move is bigger/messier than planned (e.g. entries that don't fit one project), STOP and surface before expanding scope.

## 7. Success criteria (INITIAL — revisable at every checkpoint)

- **S1** Snapshot exists and is complete (C2).
- **S2** Content-preservation diff: entry set identical pre/post (C1).
- **S3** No dead path references in any `.mdc` (grep clean) (C3).
- **S4** Cold-AI session-start simulation succeeds for: CircuitPython exp14, exp15, Bamboo-Lamp (each retrieves its own memory; none can write another's) (C5, target test).
- **S5** Behavioral memory loads for both projects (C4).
- **S6** `universal/CHANGELOG.md` logs the reset; rollback documented.

## 8. Exit ramps (FIXED)

Pause + surface if: a §3 decision blocks progress; C1 (no-loss) cannot be guaranteed for some entry; the mandate proves internally inconsistent; or the task drifts from "execute the mandate" toward "redesign the mandate".

## 9. Termination & checkpoints

Each phase close = a checkpoint: state Observe/Evaluate/Revise (specific change or explicit no-change)/Continue, and re-ask "are S1–S6 still the right criteria?". Plan-execution terminates at Phase 8 success; the *planning loop* terminates per `_META.md` diminishing-returns rule.

## 10. Open question to Alex (highest priority)

Resolve D1–D7 (§3). D1, D4 are the structural keystones — most of Phases 3–6 depend on them.
