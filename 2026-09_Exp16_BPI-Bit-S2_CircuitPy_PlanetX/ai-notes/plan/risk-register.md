# Irreducible-risk scan — plan_v1.0

**Date:** 2026-09-04 (R2 restated: copyleft-into-`lib/` needs a written case, not a blanket GPLv3 ban). **Rule:** only items execution of P1–P6 **cannot** settle. Known-unknowns K1–K5 stay in the plan (device, pins, conversion/notice/combination-case, test-layout, A/B names).
**How to check:** every high item below has a disposition in `plan_v1.0.md` (decided / open / MISSING).

| ID | Assumption / choice | Why overnight execution won’t settle it | Blast radius if wrong | Disposition | Hedge |
|----|---------------------|------------------------------------------|------------------------|-------------|-------|
| R1 | Student ops stay stable on a later RP2350+8×8 WS2812 | No second board in this milestone; G7 oracle is a later sketch | Handlers/`show_*` names would need a second redesign at platform switch | **decided** (Alex lock + G1–G7); still `unverified` as a whole-goal claim | Re-open G1–G7 at every P-phase; escalate if a name can’t survive 8×8 |
| R2 | A 5×5 glyph source can be vendored into this public repo under its actual grant (DAL MIT is the low-friction default) | DAL header already MIT. Pitchfork GPLv3 is **promising** (already 5×5) but combining converted tables into `lib/` is likely a combined work — needs a written case, not a coarse ban. Overnight may pick DAL to avoid the case. | Missing notice; or silent GPL-on-`lib/` without Alex accepting that blast radius | **decided** (restated bar: case-by-case; copyleft-into-`lib/` is the bite). Glyph source still open | Default P3 = DAL + MIT sidecar. Pitchfork only after written case. Hand-author if both drop |
| R3 | Host-green 5×5 LUT/icons imply the Exp14 async `show_*` engine still behaves at WIDTH=5 | Overnight tests explicitly **avoid** importing `Display`/`core` on host | Scroll/ring/`_glyph_columns` bugs only show on device or with a heavier mock | **decided** (overnight bar = host, no `board`) | P8 / P-human; optional later mock of NeoPixel is a criterion add → escalate before requiring it overnight |
| R4 | MakeCode 5×5 look is “good enough” without Alex seeing it | Legibility is P-human | Students can’t read letters | **decided** deferred to P-human | Min glyph set still lands; swap font directory later |
| R5 | `keypad.Keys` + asyncio is the right student programming model | 10.3.0 presence is K1 (P8). Pedagogy vs MakeCode events is not a test | If 10.3.0 lacks modules, student API would be tempted toward `update()` | **decided** (don’t silently revert); K1 escalate | Keep public `on_*_pressed` even if backend changes |
| R6 | Not implementing Watch I as a student sketch overnight | Won’t learn whether G1–G4 names actually compose | Portability bugs hide until a sketch exists | **decided** (criteria-revision v0.1; G7 stand-in = names) | First sketch is a later phase, not MISSING from overnight |
| R7 | Shared CircuitPythonSync stays on Exp14 board | Host pytest doesn’t use it; first device sync without P7 targets the wrong board | Brick-time / wrong CIRCUITPY | **decided** — P7 later; escalate before shared edit | Don’t treat USB deploy as overnight |

**MISSING from plan:** none of the high items above. Copy residue (`lib/display/__pycache__`, `.DS_Store`) is not a product risk; no delete grant — leave.

**Not in this scan (execution will tell):** K1–K5, LUT formula vs board, icon conversion bugs, pytest layout.
