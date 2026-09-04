# Execution plan v0.0 — Exp16 first milestone (overnight PoC)

**Status:** initial draft. **Date:** 2026-09-04. **Loop:** cap 8 (`loop-setup.md`); this file is not the sign-off candidate (`plan_v1.0.md` is).
**Purpose:** a cold AI can execute the overnight PoC without re-deriving locks. **This chat stops at v1.0** — do not implement from this draft.
**How to check later:** host pytest green on LUT + LightTower icons + button dispatcher; `lib/display/` is 5×5; `lib/` has an async button module. On-device is a later human window.

Cadence (import): [`reflection-cadence.md`](reflection-cadence.md). Portability rubric (re-open at every gate): [`../design/student-api-portability.md`](../design/student-api-portability.md). Locks: [`../NOTES.md`](../NOTES.md). Digests: [`../digests/INDEX.md`](../digests/INDEX.md).

---

## Corpus digest (lean context — pointers, not dumps)

| Discipline | One line | Open |
|------------|----------|------|
| Chat = cache; detail on disk; resume = INDEX + NOTES | working-notes-lean-context.md | `/Users/alex/Git/rnd-ai-skills/generalized-agent-learnings/working-notes-lean-context.md` |
| Layered commitment + audible checkpoints | Flexible Plans for AI Execution.md | same corpus folder |
| Destructive-ops hard gate; Exp16 park not a delete grant | ledger empty; move to `ai-notes/_parked/` | corpus `destructive-operations.md`; `../_parked/README.md` |
| Reflect **and** extract at every gate | `reflection-cadence.md`; 09-RECURSIVE-LEARNING.md | cadence file in this folder |
| Anything else | corpus README / 00-OVERVIEW.md | corpus root |

Persona durable copies: `ai-persona/.cursor/rules/reference/`.

---

## Layered commitment

### Fix (escalate to Alex if these change)

- **Outcome:** first milestone = async 5×5 display (icons + MakeCode-style font) **and** async PlanetX buttons. Overnight bar = **host tests + libraries on disk**. On-device = later human window (physical reset OK then).
- **Display hardware:** square WS2812 only, N≤8; sizes 5×5 now, 8×8 later. Charlieplexed out of scope.
- **5×5 ↔ 8×8:** file replacement / localized edits of geometry+LUT, icons, arrows, font. Not a second library. Not a `core.py` rewrite.
- **Work on the Exp16 copy** already at `…/2026-09_Exp16_…/lib/display/` (copied 2026-09-04 from Exp14).
- **Student ops** stay stable across later RP2350+8×8; constructors/config may change. Guidelines G1–G7 — revisit, don’t freeze a Hardware Abstraction Layer [HAL].
- **Buttons:** names A/B/C/D; overnight smoke C/D; A/B on API. Backend `keypad.Keys` → dispatcher → asyncio pump. Do not ship micro:bit-v2 `update()` as the student path.
- **Brightness cap** 0.20 inside the library.
- **No working-setup mutation** (shared CircuitPythonSync still Exp14 board). Per-experiment `.vscode/` is allowed in a **later execution chat**, not as a silent rewrite of workspace settings. **This planning chat does not scaffold it.**
- **Destructive ops:** ledger empty. Move-don’t-delete to `_parked/`. No git commit unless Alex asks.
- **Cadence:** every checkpoint Observe→Evaluate→Revise-or-no-change **and** extract/record (`reflection-cadence.md`).

### Provisional (expected to evolve)

- Phase list and order below.
- Font **source** (recommendation in § Font; not locked in NOTES).
- Host-test layout (copy Exp14 `tests/` vs thin 5×5 suite).
- Button package path / class name.
- Whether arrows stay in `icons.py`.

### Open (shape at execution)

- Exact helper names, file splits, glyph storage (PCF vs raw 5-byte table), `code.py` demo choreography, pytest file names.

---

## Font recommendation (do not lock a source)

**Target look:** MakeCode 5×5 (what LightTower students already see). Exp14 FreeMono-at-8px is known-illegible (`concepts/fonts.md`).

**Recommend (provisional):** Lancaster DAL `MicroBitFont` / MakeCode `pendolino3` (typically Apache-2.0). Convert into Exp14’s column-major convention **or** a 5-byte-per-glyph table the renderer can consume. Overnight minimum glyphs: `A`–`D`, digits `0`–`9` (Watch I traces). Full ASCII if conversion is cheap.

**Do not silently ship:** Exp09 `pitchfork-5x5` / `microbit.py` `_FONT` — **GPLv3**. Escalate before copying.

**Leave open:** PCF-for-`_glyph_columns` vs bypassing PCF on 5×5. Font swap unit remains a directory + `_FONT_PATH` (or a replacement module of similar isolation).

Evidence: `../digests/exp09-lut-icons.md` · `../digests/exp14-display-lib.md`.

---

## Pins (hypothesis, confirm at wiring / device)

| Role | Hypothesis | Overnight |
|------|------------|-----------|
| Matrix DIN | `board.NEOPIXEL` (IO18) | required for later device; host tests mock |
| C (blue) | `board.IO13` | host-test with fake events; smoke on device later |
| D (red) | `board.IO14` | same |
| A/B onboard | constructor args; likely `board.BUTTON_A` / `BUTTON_B` | API only overnight |

Electrical: pull-up, LOW = pressed = FALL.

---

## Phases (provisional; execution chat)

Each phase closes with a `reflection-cadence.md` gate (P-phase) + portability re-open. P-api on first student-facing name. P-device / P-human are **not** overnight.

| ID | Target | First atomic action | Exit / escalate |
|----|--------|---------------------|-----------------|
| P0 | Knowledge in tree | **Done** — `ai-notes/digests/` + `lib/display/` copy | — |
| P1 | 5×5 geometry + LUT | Set `WIDTH=HEIGHT=5`; replace `build_lut` stage-2 with `idx = row + 20 - column * 5`; host-test LUT with a **visual fixture** (not the same formula) | If formula disagrees with Exp09 docstring grid, stop and compare both |
| P2 | Icons/arrows 5×5 | Convert Exp09 `Image.YES/NO/DIAMOND` + compass arrows to column-major; keep names | G4: LightTower names must exist |
| P3 | Font | Implement recommended path **or** the chosen alternative; letters+digits | License: GPLv3 → escalate. Legibility = P-human |
| P4 | Hardware hooks | `PIXEL_PIN=board.NEOPIXEL`, `BRIGHTNESS=0.20` | Host import of `core` still guarded |
| P5 | Async buttons | `keypad.Keys` + A/B/C/D dispatch + asyncio pump; host tests with a fake EventQueue | If design wants student `update()`, that’s a target conflict → escalate |
| P6 | Host suite green | Pytest in designated venv `/Users/alex/Development/PythonVEs/CircuitPython_3.13_VsCode` | Overnight success bar |
| P7 | (later) `.vscode/` per-experiment | Only when Alex’s executing chat is allowed to scaffold | **Escalate** before any shared CircuitPythonSync edit |
| P8 | (later human) on-device | Confirm CP 10.3.0 `keypad`+asyncio; C/D smoke; LUT smoke | Log-only until that window |

Do **not** adapt 5×5 / write the button library / scaffold `.vscode/` in the planning chat that produced this file.

---

## Success criteria (initial — revision gate at each phase)

1. `lib/display/` on Exp16 is 5×5; Exp14 tree untouched.
2. Host tests: LUT corners + interior; YES/NO/DIAMOND (+ one arrow); codec still rejects height>8; `show_string`/`show_number` don’t crash on host with a mocked display **or** are covered via glyph/column helpers without hardware.
3. Button module: registering `on_c_pressed` fires when a fake FALL is pumped; `clear` drops it; A/B exist on the constructor.
4. No student example requires `buttons.update()` or GPIO inside handlers.
5. TODOs in code for future work; reasoning in `ai-notes/learnings/`.

Revise these if a phase shows a criterion is the wrong one (flexible-plans criteria-revision gate).

---

## Known unknowns

| ID | Unknown | When it discharges | If it blows up |
|----|---------|--------------------|----------------|
| K1 | CP 10.3.0 has `keypad` + asyncio on this board | P8 / first device | Escalate; do not silently make `update()` the student API |
| K2 | IO13/IO14 really C/D on this wiring | P8 wiring | Constructor pins change (allowed) |
| K3 | DAL/MakeCode glyph conversion cheap enough | P3 | Fall back to hand-authored A–D + digits; still not FreeMono |
| K4 | Exp14 host tests port to WIDTH=5 with little pain | P1–P6 | Thin suite instead of copy |
| K5 | Onboard A/B CircuitPython names | P7/P8 | Leave unset / documented stubs |

---

## Authority-handoff

| Change | Who |
|--------|-----|
| Target-preserving API tweaks, LUT/icon/font *implementation*, test layout | Agent (autonomous) |
| Student-API **stability target**, cadence rules, hardware scope, overnight bar, GPLv3 font, shared CircuitPythonSync, destructive ops, git commit | **Alex** |
| Criteria additions, scope expansions (Watch II motor, HAL) | Escalate before expanding |

Park: `../_parked/`. Ledger: persona `memory/PERMITTED_DESTRUCTIVE_ACTIONS.md` (empty).

---

## Checkpoints (minimum)

P-plan (each loop pass — this file’s lineage) · P-phase (P1–P6 close) · P-api (first `on_*_pressed` / `show_*` demo names) · P-device · P-human (font feel, button feel) · P-surprise · P-done.

Silence at a checkpoint is the failure mode. Write `learnings/` on first extract (create folder then).

---

## See also

- Digests: `../digests/{exp14-display-lib,exp09-lut-icons,lighttower-student-ops,button-research}.md`
- Exp14 architecture: `../../lib/display/README.md` (the copy)
- Exp09 LUT source: `2026-02_Exp09_…/lib/display_v0.py`
