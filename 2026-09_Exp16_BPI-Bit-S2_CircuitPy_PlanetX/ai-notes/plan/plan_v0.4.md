# Execution plan v0.4 — Exp16 first milestone (overnight PoC)

**Status:** refinement 4 (T1). **Date:** 2026-09-04. **Loop:** cap 8; sign-off = `plan_v1.0.md`.
**Spec:** [`../../Notes/overall_goal.md`](../../Notes/overall_goal.md). **Locks:** [`../NOTES.md`](../NOTES.md).
**Purpose:** after Alex signs v1.0, a cold AI executes the overnight PoC from this file. Do not implement during the planning loop.
**How to check:** `{venv}/bin/pytest` from the Exp16 root is green on Look-Up Table [LUT] + LightTower icons + button dispatcher **without** `import board`; `lib/display/` is 5×5; an async button module exists under `lib/`.

Cadence (import, do not copy): [`reflection-cadence.md`](reflection-cadence.md). Rubric: [`../design/student-api-portability.md`](../design/student-api-portability.md) (re-open **G1–G7 and A1–A4** at P-phase). Digests: [`../digests/INDEX.md`](../digests/INDEX.md). Notes: [`notes_v0.4.md`](notes_v0.4.md). Loop lock: [`loop-setup.md`](loop-setup.md) (cap 8, sub-agents authorized).

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

### Fix (escalate to Alex if these change)

- **Outcome:** async 5×5 display (icons + MakeCode-style font) **and** async PlanetX buttons.
- **Overnight bar:** host tests + libraries on disk. On-device = later human window (physical reset OK). Human testing is **rare and strategic** (P8 / P-human only).
- **Firmware / host:** CircuitPython **10.3.0** `bpi_bit_s2`. Venv: `/Users/alex/Development/PythonVEs/CircuitPython_3.13_VsCode`.
- **Quality:** PoC; library code upgradable with moderate effort; TODOs in code; reasoning in `ai-notes/`.
- **Template:** Exp14 is the project template **and** the display-lib source. Executing chat may copy further Exp14 project bits (tests, gitignore patterns). **Do not** rewrite shared CircuitPythonSync. Per-experiment `.vscode/` = later execution chat.
- **Display hardware:** square WS2812/NeoPixel, N≤8; realistic sizes **5×5** and **8×8** only. Do not treat 4×4/6×6/7×7 as first-class. Charlieplexed out of scope. Column-major encoding cap `_MAX_HEIGHT_PER_COLUMN_BYTE = 8` stays (format, not geometry).
- **Swap units:** geometry/LUT, icons, **arrows (independently replaceable)**, font — file replace / localized edits. Not a second library. Not a `core.py` rewrite. `core.py` / `bitmap_codec.py` stay geometry-agnostic except thin hooks (`WIDTH`/`HEIGHT`, `_FONT_PATH`, `PIXEL_PIN`, `BRIGHTNESS`).
- **Prior art split:** Exp09 supplies 5×5 LUT, orientation, pictogram bitmaps **only**. Not the font (license). Not the student button API.
- **Tree:** work on `/Users/alex/Development/VsCode/CircuitPython/2026-09_Exp16_BPI-Bit-S2_CircuitPy_PlanetX/lib/display/` (copied from Exp14, 2026-09-04). Do not edit Exp14 for this milestone.
- **Portability:** student **operations** stable across RP2350+8×8; constructors/config may change. Revisit G1–G7. No Hardware Abstraction Layer [HAL]. Motor (Watch II) and light sensor (Watch III) deferred — do not invent those APIs this milestone. Library must **not** encode `LighthouseMode` (student handlers own that table).
- **Buttons:** names A/B/C/D; overnight host-fakes fire C/D; A/B on constructor. Backend: `keypad.Keys` → dispatcher (key index → letter) → asyncio pump. Student path is **not** sync `update()` and **not** Exp09 `elecfreaks_planetx.Button`.
- **Brightness** 0.20 inside the library.
- **Agent scripts:** max 5; spec + uninstall in `ai-notes/`; prefer zero this overnight.
- **Destructive ops / git:** ledger empty; park `_parked/`; no commit unless asked.
- **Cadence:** Observe→Evaluate→Revise-or-no-change **and** extract/record at every gate.

### Provisional

Phase order; font source; copy-vs-thin tests; button package path; arrows file split; `on_*_released` on the API (not an overnight gate).

### Open

Helper names; glyph storage (Portable Compiled Font [PCF] vs raw 5-byte table); pytest filenames; optional `code.py`.

---

## Font recommendation (source not locked)

**Look:** MakeCode 5×5. Exp14 FreeMono-at-8px is illegible (`concepts/fonts.md`).

**Recommend:** glyphs from the Lancaster micro:bit Device Abstraction Layer [DAL] `MicroBitFont` (`pendolino3` = the default 5×5 glyph blob in `MicroBitFont.cpp`). **P3 first action:** read that file’s license header (Apache-2.0 is a hypothesis). Convert to column-major **or** a 5-byte table.

**Overnight minimum:** `A`–`D` and `0`–`9` (digest Watch I only needs `0`–`2`; 0–9 is a cheap superset). Full ASCII optional — **not** a P6 gate.

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

## Phases (provisional — execution chat after v1.0)

**First atomic action:** set `_constants.WIDTH` and `HEIGHT` to 5. Later sequences stay open.

LUT = logical (x,y) → NeoPixel strip index. Codec = `bitmap_codec` ASCII `#`/`.` ↔ column-major bytes. EventQueue = `keypad`’s bounded native press/release queue (debounce already done). Dispatcher = EventQueue key index → A/B/C/D. **Visual fixture** = expected strip indices authored by hand (or a second algorithm), **not** by copying `row + 20 - column * 5` into the test — otherwise a wrong formula blesses itself (shared-derivation hazard).

P1–P6 close: cadence **P-phase** + G1–G7 **and A1–A4**. First student-facing name: **P-api**. P-device / P-human are not overnight.

| ID | Target | Note | Exit |
|----|--------|------|------|
| P0 | Digests + copy | **Done** | — |
| P1 | Geometry + LUT | Stage-2 `idx = row + 20 - column * 5`; visual-fixture tests | Grid vs formula disagree → stop |
| P2 | Icons/arrows | Exp09 25-byte row-major 0–9 → 5 column bytes (hypothesis). Names: YES, NO, DIAMOND, N/S/E/W | G4 names missing → fix before P6 |
| P3 | Font | License header, then convert; min A–D + 0–9 | GPLv3 → Alex. Legibility → P-human |
| P4 | Pin + brightness | `PIXEL_PIN=board.NEOPIXEL`, `BRIGHTNESS=0.20`; keep hardware import guard | — |
| P5 | Async buttons | Fake EventQueue; C/D fire tests; A/B/C/D **names** on constructor. Do not wrap Exp09 `Button` as student API | Student `update()` → escalate |
| P6 | Host suite | `/Users/alex/Development/PythonVEs/CircuitPython_3.13_VsCode/bin/pytest` from Exp16 root | Overnight bar |
| P7 | `.vscode/` override | Later chat | Escalate before **shared** CircuitPythonSync |
| P8 | On-device 10.3.0 `keypad`/asyncio, C/D + LUT | Human window | Log-only until then |

---

## Success criteria (initial — revise at phase close)

1. Exp16 `lib/display/` is 5×5; Exp14 untouched.
2. Host tests, no `board`: LUT corners+interior (visual fixture); YES, NO, DIAMOND; **Arrows.NORTH/EAST/SOUTH/WEST** names+bitmaps; codec rejects height>8; `on_c_pressed` and `on_d_pressed` fire on fake FALL; `clear` works; `on_a_pressed` / `on_b_pressed` **exist** (need not fire overnight).
3. Glyph path yields column bytes for `A`–`D` and `0`–`9` without FreeMono.
4. Public names exist for `show_string`, `pause`, `show_icon`, `show_number`, `on_*_pressed`. No student path needs `buttons.update()` or GPIO inside handlers.
5. TODOs in code; extracts in `ai-notes/learnings/`.

**G7 stand-in:** those names are enough to write `letter → icon → number` later. Full Watch I sketch is **not** overnight.

**Overnight diminishing returns:** P6 green with the min glyph set **ends** overnight work.

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
| Watch II motor / light / HAL / extra overnight criteria (e.g. requiring `on_*_released` or a full student sketch) | Escalate first |

Park: `../_parked/`. Ledger: `memory/PERMITTED_DESTRUCTIVE_ACTIONS.md` (empty).

---

## Checkpoints

P-plan · P-phase (P1–P6, G1–G7 + A1–A4) · P-api · P-device · P-human · P-surprise · P-done.

---

## See also

`../digests/` · `../../lib/display/README.md` · Exp09 `lib/display_v0.py` · `../../Notes/overall_goal.md`
