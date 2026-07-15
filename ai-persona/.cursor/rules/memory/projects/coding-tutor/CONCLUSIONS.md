# Conclusions — coding-tutor

Last updated: 2026-07-15 (project bootstrap).

Status tiers: `unverified` · `evidence-supported` · `disputed` · `invalidated`. On this project Alex **is** the authority
on project intent, success criteria, and Alice's profile (user-as-authority → treat his statements as design ground
truth, not domain claims needing corroboration). Pedagogy/learning-science claims are a genuine knowledge domain where
Alex is *not* the authority → those need independent, cited corroboration before promotion. Tag scope `[project]` unless
broader.

## Evidence-Supported

| Finding | Scope | Evidence | Date |
|---------|-------|----------|------|
| Two completed exemplar tutorials exist and define the target tone + pedagogy (mini-challenges, "your turn" branch-per-answer, Check/Self-test, decision tables, reflection worksheets, two-register tone). They are transfer-learning-linked (lighthouse reuses feeder ideas). | `[project]` | Read in full: `Isana/Crash-Sensor_Mini-Challenge/Tutorial_Complete.md`, `Isana/LightTower-challenge/2026-05-15_lighthouse-keeper_v1.0.md`. Digest: `CodingTutor/digests/exemplar-tutorials_pedagogy-and-stack_digest.md`. | 2026-07-15 |
| Hardware pin routing: Nezha2 J3 → micro:bit P14 (and on the 2-button PlanetX module, blue C→P13, red D→P14); on-board A→P5, B→P11. Hardware fact, independent of MakeCode vs CircuitPython. | `[project]` (overlaps `[family:circuitpython]`) | Exemplar prompts + LightTower §Test Rig table + PoC code. | 2026-07-15 |

## Unverified

| Finding | Scope | Why noted | Date |
|---------|-------|-----------|------|
| CircuitPython support for Nezha2/PlanetX (motors + sensors, event/interrupt model) is incomplete — Alex is building it separately. Concrete tutor code/API content cannot be finalized until it exists. | `[project]` | Stated by Alex in the init prompt; API surface not yet inspected (Q1). | 2026-07-15 |
| Exemplar block-level logic (sync/async motor commands, polling→event-bus interrupt progression) will map onto CircuitPython analogues, but the exact API shape is unknown. | `[project]` | Inferred from exemplars; unverified against a non-existent library. | 2026-07-15 |

## Disputed

| Finding | Scope | Conflicting evidence | Date |
|---------|-------|----------------------|------|

## Invalidated

| Former finding | Scope | What disproved it | Date |
|----------------|-------|-------------------|------|

## Open Questions

Canonical list: `CodingTutor/notes-learnings-insights_for_building_tutor/03_open-questions-todos.md` (Q1–Q6).

## Change Log

| Date | Item | Change | Evidence |
|------|------|--------|----------|
| 2026-07-15 | project bootstrap | seeded CONCLUSIONS at setup | this file |
