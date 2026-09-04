# notes_v0.1 — plan-refinement (parent R1; extractor still in flight)

**Date:** 2026-09-04. **From:** `plan_v0.0.md`. **Cadence:** P-plan Observe/Evaluate/Revise.

## Observe

v0.0 already carries Fix/Provisional/Open, font recommendation without a locked source, IO13/IO14 as hypothesis, overnight = host tests, cadence import, corpus pointers. Gaps vs NOTES/digests/G1–G7:

## R1 Substance (location → problem → change)

1. Success criteria → Watch I ops not all listed (`pause`, letter `show_string`, press handlers). → Add explicit overnight API bar matching `lighttower-student-ops.md`.
2. P6 / tests → implied importing `Display` on CPython (`board`/`neopixel` missing). → Overnight tests = pure submodules + fake EventQueue; hardware `core` import is device-side.
3. G7 → “student sketch” could be read as overnight work. → Overnight oracle = host test of `letter → icon → number` with fakes; full Watch I sketch is later.
4. P3 → DAL Apache-2.0 still unverified. → First atomic action: read license header before copying glyphs.
5. P7/P8 → sit in the same table as overnight phases. → Mark **out of overnight success bar**.
6. Fix layer → missing “stock CP 10.3.0 `bpi_bit_s2`” and “PoC + TODOs in code”. → Add.
7. P2 → conversion 25-byte row-major 0–9 → column-major left implicit. → State as hypothesis, not a helper-name mandate.

Portability re-open: G1–G4 intact; G6 still “no motor/light”; G7 narrowed as above. A2 still device-gated. **Criteria still right?** Yes, with the host-test narrowing (criteria-revision: drop “mocked Display show_*” as a required overnight path).

## R2 / R3

Deferred to v0.2 so this pass stays substance-first. Extractor payload (`returns/extract-plan-v0.0-gaps.md`) merges in v0.2.

## Change-magnitude summary

- **Breadth:** Success criteria, Phases (P2/P3/P6/P7/P8), Fix layer, Known unknowns (K4 clarified).
- **Depth:** T2 substantive (criteria + overnight test surface).
- **Unknowns discharged:** none of K1–K5; clarified K4 meaning.
- **Trend:** first refine. **Verdict:** `not-converged`.
- **Reflection:** next pass merges extractor + R2 cold-AI/flexible-plan + R3 trim. No target change.

## Learning

Nothing beyond `../learnings/p-plan-digest-collection.md`. This pass: **criteria-revision** — overnight does not require a hardware-backed `show_*` on host.
