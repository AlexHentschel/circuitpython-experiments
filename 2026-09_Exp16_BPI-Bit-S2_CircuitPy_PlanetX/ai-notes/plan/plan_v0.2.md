# Execution plan v0.2 — Exp16 first milestone (overnight PoC)

**Status:** refinement 2 (paradigm + economy). **Date:** 2026-09-04. **Loop:** cap 8; sign-off = `plan_v1.0.md`.
**Purpose:** a cold AI executes the overnight PoC from this plan after Alex signs `v1.0`. Do not implement during the planning loop.
**How to check:** from the Exp16 project root, designated venv pytest is green on LUT + LightTower icons + button dispatcher **without** `import board`; `lib/display/` is 5×5; an async button module exists under `lib/`.

Cadence (import, do not copy): [`reflection-cadence.md`](reflection-cadence.md). Rubric: [`../design/student-api-portability.md`](../design/student-api-portability.md). Locks: [`../NOTES.md`](../NOTES.md). Digests: [`../digests/INDEX.md`](../digests/INDEX.md). This version’s notes: [`notes_v0.2.md`](notes_v0.2.md).

---

## Corpus digest (pointers)

| Discipline | One line | Open |
|------------|----------|------|
| Chat = cache; resume = INDEX + NOTES | working-notes-lean-context.md | `/Users/alex/Git/rnd-ai-skills/generalized-agent-learnings/working-notes-lean-context.md` |
| Layered commitment + audible checkpoints | Flexible Plans for AI Execution.md | same corpus folder |
| Destructive-ops; park ≠ delete grant | ledger empty; move to `ai-notes/_parked/` | `destructive-operations.md`; `../_parked/README.md` |
| Reflect **and** extract every gate | `reflection-cadence.md`; 09-RECURSIVE-LEARNING.md | this folder (import) |
| Router | corpus README / 00-OVERVIEW.md | corpus root |

Persona copies: `ai-persona/.cursor/rules/reference/`.

---

## Layered commitment

### Fix (escalate if these change)

- **Outcome:** async 5×5 display (icons + MakeCode-style font) **and** async PlanetX buttons.
- **Overnight bar:** host tests + libraries on disk. On-device = later human window (physical reset OK).
- **Firmware:** CircuitPython **10.3.0** `bpi_bit_s2`. Host: `/Users/alex/Development/PythonVEs/CircuitPython_3.13_VsCode`.
- **Quality:** PoC; library code upgradable with moderate effort; TODOs in code; reasoning in `ai-notes/`.
- **Display hardware:** square WS2812/NeoPixel, N≤8; **5×5** now, **8×8** later. Charlieplexed out of scope.
- **Swap units:** geometry/LUT, icons, arrows, font — file replace / localized edits. Not a second library. Not a `core.py` rewrite.
- **Tree:** work on `/Users/alex/Development/VsCode/CircuitPython/2026-09_Exp16_BPI-Bit-S2_CircuitPy_PlanetX/lib/display/` (Exp14 copy, 2026-09-04). Do not edit Exp14 for this milestone.
- **Portability:** student **operations** stable across RP2350+8×8; constructors/config may change. Revisit G1–G7. No Hardware Abstraction Layer [HAL] in the PoC.
- **Buttons:** A/B/C/D names; overnight C/D via host fakes; A/B on constructor. Backend `keypad.Keys` → dispatcher → asyncio pump. Student path is **not** sync `update()`.
- **Brightness** 0.20 inside the library.
- **Working setup:** do not rewrite shared CircuitPythonSync. `.vscode/` override = later execution chat.
- **Destructive ops / git:** ledger empty; park `_parked/`; no commit unless asked.
- **Cadence:** Observe→Evaluate→Revise-or-no-change **and** extract/record at every gate.

### Provisional

Phase order; font source; copy-vs-thin tests; button package path; arrows in `icons.py` vs split.

### Open

Helper names, glyph storage (Portable Compiled Font [PCF] vs raw 5-byte table), pytest filenames, optional `code.py`.

---

## Font recommendation (source not locked)

**Look:** MakeCode 5×5. Exp14 FreeMono-at-8px is illegible (`concepts/fonts.md`).

**Recommend:** glyphs from the Lancaster micro:bit Device Abstraction Layer [DAL] `MicroBitFont` (`pendolino3` blob in `MicroBitFont.cpp`). **P3 first action:** read that file’s license header (Apache-2.0 is a hypothesis). Then convert to column-major **or** a 5-byte table.

**Overnight minimum:** `A`–`D` and `0`–`9`. Full ASCII is optional; **not** a P6 gate.

**Do not silently ship:** Exp09 pitchfork-5x5 / `microbit.py` `_FONT` (**GPLv3**) — escalate first.

---

## Pins (hypothesis)

| Role | Hypothesis | Overnight |
|------|------------|-----------|
| Matrix DIN | `board.NEOPIXEL` (= IO18) | unused on host |
| C / D | `board.IO13` / `board.IO14` | fake falling-edge events |
| A / B | constructor; likely `board.BUTTON_A` / `BUTTON_B` | API only |

Pull-up, LOW = pressed.

---

## Phases (provisional — **execution** chat after v1.0)

**First atomic action (only this step is prescribed):** P1 set `_constants.WIDTH` and `HEIGHT` to 5. Sequences after that stay open; table below is a target map, not a script.

P1–P6 close with cadence **P-phase** + G1–G7. First student-facing name: **P-api**. **P-device** / **P-human** are not overnight.

| ID | Target | First action / note | Exit |
|----|--------|---------------------|------|
| P0 | Digests + copy | **Done** | — |
| P1 | Geometry + LUT | Stage-2 wiring `idx = row + 20 - column * 5`; visual-fixture tests | Grid vs formula disagree → stop |
| P2 | Icons/arrows | Hypothesis: Exp09 25-byte row-major 0–9 → 5 column bytes; keep YES, NO, DIAMOND, compass | G4 names missing → fix before P6 |
| P3 | Font | License header, then convert; min A–D + 0–9 | GPLv3 → Alex. Legibility → P-human |
| P4 | Pin + brightness | `PIXEL_PIN=board.NEOPIXEL`, `BRIGHTNESS=0.20`; keep hardware import guard | — |
| P5 | Async buttons | Fake EventQueue tests; A/B/C/D on constructor | Student `update()` → escalate |
| P6 | Host suite | `{venv}/bin/pytest` from Exp16 root (exact `tests/` layout open) | Overnight bar |
| P7 | `.vscode/` override | Later chat | Escalate before **shared** CircuitPythonSync |
| P8 | On-device 10.3.0 `keypad`/asyncio, C/D + LUT | Human window | Log-only until then |

---

## Success criteria (initial — revise at phase close)

1. Exp16 `lib/display/` is 5×5; Exp14 untouched.
2. Host tests, no `board`: LUT corners+interior; YES, NO, DIAMOND (+ one arrow); codec rejects height>8; `on_c_pressed` / `on_d_pressed` on fake FALL; `clear` works; A/B on constructor.
3. Glyph path yields column bytes for `A`–`D` and `0`–`9` without FreeMono.
4. No student path needs `buttons.update()` or GPIO inside handlers.
5. TODOs in code; extracts in `ai-notes/learnings/`.

**G7 stand-in:** public names exist for `show_string`, `pause`, `show_icon`, `show_number`, `on_*_pressed`. Full Watch I sketch is not overnight.

**Overnight diminishing returns:** P6 green with the min glyph set **ends** overnight work even if full ASCII or `.vscode/` is undone.

**How to check:** `/Users/alex/Development/PythonVEs/CircuitPython_3.13_VsCode/bin/pytest` from `/Users/alex/Development/VsCode/CircuitPython/2026-09_Exp16_BPI-Bit-S2_CircuitPy_PlanetX/` (create `tests/` during execution).

---

## Known unknowns

| ID | Unknown | Discharges | If wrong |
|----|---------|------------|----------|
| K1 | CP 10.3.0 has `keypad` + asyncio | P8 | Escalate; no silent `update()` student API |
| K2 | IO13/IO14 = C/D | P8 | Constructor pins (allowed) |
| K3 | DAL license + conversion | P3 | Hand-author min glyphs; GPLv3 still escalate |
| K4 | Copy Exp14 tests vs thin suite | P1–P6 | Thin suite OK |
| K5 | Onboard A/B names | P7/P8 | Constructor stubs |

---

## Authority-handoff

| Change | Who |
|--------|-----|
| LUT, icon bytes, font conversion, test layout, button module path | Agent |
| Stability **target**, cadence, hardware scope, overnight bar, GPLv3, shared CircuitPythonSync, destructive ops, git commit | **Alex** |
| Watch II motor / light / HAL / extra criteria | Escalate first |

Park: `../_parked/`. Ledger: `memory/PERMITTED_DESTRUCTIVE_ACTIONS.md` (empty).

---

## Checkpoints

P-plan · P-phase (P1–P6) · P-api · P-device · P-human · P-surprise · P-done.

---

## See also

`../digests/` · `../../lib/display/README.md` · Exp09 `lib/display_v0.py`
