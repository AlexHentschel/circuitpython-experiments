# notes_v0.2 — R2 paradigm + R3 economy (parent)

**Date:** 2026-09-04. **From:** `plan_v0.1.md`. Extractor payload still pending → any lock-misses it finds go to v0.3.

## Observe

v0.1 fixed overnight test surface and Watch I API bar. Remaining: undecoded DAL; execution stop-rule (digits-only OK); first atomic action for the *execution* chat; pytest how-to-check; trim duplicate “don’t implement in this chat”.

## R1

No further target/design change. Portability: no revision. Criteria: add diminishing-returns for overnight (min glyphs + P6 green).

## R2 Paradigm

1. Header / Font → decode **DAL** = Lancaster micro:bit Device Abstraction Layer (the C runtime that ships MakeCode’s 5×5 font).
2. Success criteria → overnight **done** when P6 is green with A–D and 0–9 even if full ASCII is missing (diminishing returns). Extra glyphs are not a gate.
3. Phases → execution chat’s **first atomic action** = P1 set `WIDTH=HEIGHT=5`. Later step sequences stay open.
4. How-to-check → name the pytest invocation: designated venv `…/bin/pytest` from Exp16 root (path open if tests/ layout is thin).
5. Cold-AI: `pendolino3` = glyph blob name inside DAL `MicroBitFont.cpp` — one gloss.

Flexible-plans: layered table already present; add execution diminishing-returns to Fix? No — that’s a **provisional criterion**, keep in success-criteria section.

## R3 Economy

1. Drop repeated “planning chat does not implement” (keep once, in header).
2. Do not duplicate electrical facts in phases.
3. Keep corpus digest, cadence import, authority map (R3 must not trim reflection machinery).

## Change-magnitude

- **Breadth:** Font gloss, Success criteria (stop rule), Phases (first atomic action), header.
- **Depth:** T2 (overnight stop criterion) + T1 (decode/trim).
- **Unknowns discharged:** 0.
- **Trend:** narrowing. **Verdict:** `not-converged` (extractor not merged; one confirm pass after that).
- **Reflection:** continue to v0.3 to merge extractor; if extractor is empty/T1-only and v0.3 is T1, confirm then promote.

## Learning

- **Claim:** Overnight success can stop at letters+digits; full ASCII is not a gate.
- **Evidence:** Watch I traces only need A–D and 0–2 actually; 0–9 is cheap margin. Hypothesis.
- **Status:** `unverified` until P3
- **Guideline:** G3 (MakeCode-shaped display) — min set still covers traces
- **Action:** keep as criterion
- **Date:** 2026-09-04
