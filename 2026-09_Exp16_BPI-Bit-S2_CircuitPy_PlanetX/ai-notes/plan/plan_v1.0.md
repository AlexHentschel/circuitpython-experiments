# Execution plan v1.0 — Exp16 first milestone (overnight PoC)

**Status:** **accepted**; overnight **P1–P6 kickoff authorized** (Alex, 2026-09-04, handoff to a new executing chat). Host venv: pytest 9.1.1 + pytest-asyncio + Adafruit `mpy-cross` 10.3.0 + `circuitpython-stubs` 10.3.0 (CPython 3.13 Miniconda). Overnight git: coarse commits on `alex/display-mvp_5x5`. **Board stays unplugged** until Alex says otherwise (P8). **Date:** 2026-09-04.
**Executing chat: start P1–P6 from this file.** Risk scan: [`risk-register.md`](risk-register.md). Lineage: `plan_v0.0.md` … `plan_v0.4.md` + `notes_v0.1.md` … `notes_v0.5.md`.
**Spec:** [`../../Notes/overall_goal.md`](../../Notes/overall_goal.md). **Locks:** [`../NOTES.md`](../NOTES.md).
**Purpose:** after Alex signs v1.0, a cold AI executes the overnight PoC from this file. Do not implement during the planning loop.
**How to check:** `/Users/alex/Development/PythonVEs/CircuitPython_3.13_VsCode/bin/pytest` from the Exp16 root is green on Look-Up Table [LUT] + LightTower icons + button dispatcher **without** `import board`; `lib/display/` is 5×5; an async button module exists under `lib/`. That venv is the Mac/Cursor host Python (not the board).

Cadence (import, do not copy): [`reflection-cadence.md`](reflection-cadence.md). Rubric: [`../design/student-api-portability.md`](../design/student-api-portability.md) (re-open **G1–G7 and A1–A4** at P-phase). Digests: [`../digests/INDEX.md`](../digests/INDEX.md). Notes: [`notes_v0.5.md`](notes_v0.5.md) (confirm: no change). Loop lock: [`loop-setup.md`](loop-setup.md) (cap 8, sub-agents authorized).

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
- **Firmware / host:** CircuitPython **10.3.0** `bpi_bit_s2`. Mac (Cursor) host Python: `/Users/alex/Development/PythonVEs/CircuitPython_3.13_VsCode` — use this venv for pytest and any host scripts. Do not invent another.
- **Quality:** PoC; library code upgradable with moderate effort; TODOs in code; reasoning in `ai-notes/`.
- **Template:** Exp14 is the project template **and** the display-lib source. Executing chat may copy further Exp14 project bits (tests, gitignore patterns). **Do not** rewrite shared CircuitPythonSync. Per-experiment `.vscode/` = later execution chat.
- **Exp14 engine (Alex, 2026-09-04):** the copy in Exp16 `lib/display/` contains **reviewed, hand-optimized** algorithms (hot/cold parsers, fused scan sketch `_write_pattern_on_the_fly`, column-major renderers, cancel token). **Analyze in depth and keep them.** Entire algorithms stay; changes are **localized** (geometry hooks, LUT formula, pin, brightness, font path). Style example = Exp14 upstream `lib/display/` (comments, docstrings, hot-vs-cold split). Do **not** strip comments unless the whole segment is removed; update comments/docs as the code evolves. Do not let a 5×5 port become a `core.py` rewrite. Detail: § Exp14 engine below.
- **Display hardware:** square WS2812/NeoPixel, N≤8; realistic sizes **5×5** and **8×8** only. Do not treat 4×4/6×6/7×7 as first-class. Charlieplexed out of scope. Column-major encoding cap `_MAX_HEIGHT_PER_COLUMN_BYTE = 8` stays (format, not geometry).
- **Swap units:** geometry/LUT, icons, **arrows (independently replaceable)**, font — file replace / localized edits. Not a second library. Not a `core.py` rewrite. `core.py` / `bitmap_codec.py` stay geometry-agnostic except thin hooks (`WIDTH`/`HEIGHT`, `_FONT_PATH`, `PIXEL_PIN`, `BRIGHTNESS`).
- **Prior art split:** Exp09 supplies 5×5 LUT, orientation, pictogram bitmaps **only**. Not the font. Not the student button API.
- **Font license (Alex, 2026-09-04; restated same day):** PoC is **public**. Hobby use **and** a copy into this repo **with the upstream notice**. Bar is **not** “no GPLv3 files anywhere.” Copyleft (GPLv3, CC BY-SA, …) **combined into `lib/`** (imported or converted into library code) needs a **written case analysis** of that candidate’s actual grant (exceptions, dual-license, mere-aggregation vs combined work) **before** combining. Use the freedoms the license grants. Do not coarse-dismiss a promising source on the license *name* alone. Unmodified collection items (e.g. `Notes/bpi_bit_v2_goldfinger.jpg`) are a separate analysis. Glyph *look* still MakeCode 5×5; glyph *file* still not locked.
- **Tree:** work on `/Users/alex/Development/VsCode/CircuitPython/2026-09_Exp16_BPI-Bit-S2_CircuitPy_PlanetX/lib/display/` (copied from Exp14, 2026-09-04). Do not edit Exp14 for this milestone.
- **Portability:** student **operations** stable across RP2350+8×8; constructors/config may change. Revisit G1–G7. No Hardware Abstraction Layer [HAL]. Motor (Watch II) and light sensor (Watch III) deferred — do not invent those APIs this milestone. Library must **not** encode `LighthouseMode` (student handlers own that table).
- **Buttons:** names A/B/C/D; overnight host-fakes fire C/D; A/B on constructor. Backend: `keypad.Keys` → dispatcher (key index → letter) → asyncio pump. Student path is **not** sync `update()` and **not** Exp09 `elecfreaks_planetx.Button`.
- **Brightness** 0.20 inside the library.
- **Agent scripts:** max 5; spec + uninstall in `ai-notes/`; prefer zero this overnight.
- **Destructive ops / git:** ledger empty; park `_parked/`. **Overnight commits authorized** (Alex, 2026-09-04): coarse commits on current branch `alex/display-mvp_5x5` when a phase chunk lands. No force-push. No commit of secrets/`settings.toml`.
- **Cadence:** Observe→Evaluate→Revise-or-no-change **and** extract/record at every gate.

### Provisional

Phase order; font source; copy-vs-thin tests; button package path; arrows file split; `on_*_released` on the API (not an overnight gate).

### Open

Helper names; glyph storage (Portable Compiled Font [PCF] vs raw 5-byte table); pytest filenames; optional `code.py`.

---

## Font recommendation (source not locked; **license bar restated**)

**Look:** MakeCode 5×5. Exp14 FreeMono-at-8px is illegible (`concepts/fonts.md`).

**License bar (Fix):** hobby-usable **and** vendorable into this public repo **with the upstream notice**. Copyleft **combined into `lib/`** is allowed only after a written case on *this* candidate (read the actual grant — exceptions, dual-license, whether converting glyphs into Python tables imported by `core.py` is a combined work). Do not reject on the string “GPLv3” alone. Collection items outside `lib/` are not this bar (goldfinger JPEG).

**Recommend (low-friction default):** Lancaster Device Abstraction Layer [DAL] `MicroBitFont` blob `pendolino3` in `MicroBitFont.cpp`. **License is MIT**, not Apache-2.0 (hypothesis **invalidated** 2026-09-04 — file header + repo `LICENSE`: Copyright 2016 BBC, provided by Lancaster University by arrangement with the BBC). MIT allows copy/modify/distribute for hobby and public repos if the copyright + permission notice travels with the glyphs.

**Also promising (do not coarse-dismiss):** Exp09 pitchfork-5x5 / `microbit.py` `_FONT` (`https://github.com/stef/pitchfork-5x5`, **GPLv3**). Already 5×5. Combining converted tables into `lib/display` is likely a combined work → that module would need to ship as GPLv3 unless a written analysis finds an exception. **P3:** if this path is chosen, write the case (grant text + combined-vs-aggregation + blast radius on `lib/`) **before** copying; escalate if the case says `lib/` becomes GPL. Default overnight path remains DAL MIT.

**P3 first action (DAL path):** vendor glyphs **and** that MIT notice (e.g. `font_makecode_5/LICENSE`) next to the table. Then convert DAL **row bytes** (bit4…bit0 = columns) to Exp14 column-major **or** a 5-byte table.

**Overnight minimum:** `A`–`D` and `0`–`9` (digest Watch I only needs `0`–`2`; 0–9 is a cheap superset). Full ASCII optional — **not** a P6 gate.

**Fallback if no vendored candidate clears its case:** original hand-authored min glyphs (our copyright).

**Already in the Exp16 copy:** `lib/display/font_free_mono_8/` **removed by Alex 2026-09-04** (cleanup). P3 vendors the 5×5 font + notice. `core.py` `_FONT_PATH` still names that path until P3.

---

## Exp14 engine (keep; localized edits only)

**Style / algorithm SoT (do not mutate for Exp16):** `/Users/alex/Development/VsCode/CircuitPython/2026-04_Exp14_DisplayLibrary_CPy_on_RPi-Pico-2040/lib/display/`
**Work tree:** Exp16 `lib/display/` (copy). Match Exp14 comment/docstring/hot-path style.

These have been reviewed and to some extent **hand-optimized** for CircuitPython GC + readability. **Analyze in depth before touching. Keep the entire algorithm; localized changes only.**

| Keep (do not rewrite) | What it is |
|-----------------------|------------|
| `_iter_pattern_rows` vs `_iter_pattern_rows_fast` + `_HOTPATH_WS` | Cold vs hot pattern parsers; allocation/GC split is intentional |
| `_write_pattern_on_the_fly` | Fused one-pass scan → NeoPixel buffer. Docstring: candidate replacement for the fast parser in `render_pattern`; **intentionally unused**. Analyze and **utilize** (wire up or keep as the hot path); do not delete the sketch |
| `_render_colmajor` | Column-major → LUT writes; LOAD_FAST locals; stride accumulator |
| `_glyph_columns` | PCF metrics → column bytes |
| `_render_ring_window` | Scroll ring; `x_base += HEIGHT` invariant |
| `Display._seq` / `_acquire` / `_is_cancelled` | Cancel token |

**Allowed localized edits:** `_constants.WIDTH`/`HEIGHT`, `geometry.build_lut` stage-2 formula, `PIXEL_PIN`, `BRIGHTNESS`, `_FONT_PATH` / font directory, icon/arrow bytes, comments/docs that track those edits.

**Comments:** do not remove unless the whole code segment is removed. Update comments and documentation as the code evolves (correctness arguments, hot-vs-cold, invariants).

First atomic action (P1) is still `WIDTH=HEIGHT=5` — that is a localized constant change, not a renderer rewrite.

---

## Pins (firmware names source-verified 2026-09-04; PlanetX cable unverified)

Overnight host tests fake FALL events, so C/D GPIO identity is unused until P8. Do not import Blinka `board` as evidence.

| Role | Exp09 prior | Official BananaPi goldfinger ([docs](https://docs.banana-pi.org/en/BPI-Bit-S2/BananaPi_BPI-Bit-S2); in-repo `Notes/bpi_bit_v2_goldfinger.jpg`) | CP 10.3.0 `pins.c` | Overnight |
|------|-------------|------------------------------------------------------------------------------------------------------------------------------------------|-------------------|-----------|
| Matrix DIN | `board.NEOPIXEL` (= IO18) | GPIO18 | `NEOPIXEL` → GPIO18 | unused on host |
| C / D (J3 = micro:bit P13 / P14) | `board.IO13` / `board.IO14` | P13/P14 = **GPIO36 / GPIO37**. Page’s GPIO13/14 = photoresistors (`LUM2`/`LUM1`), not the edge. | `IO13`→GPIO36 (`SCK`); `IO14`→GPIO37 (`MISO`). Naming clash **resolved** in firmware; PlanetX cable still unverified. | fake falling-edge events |
| A / B | constructor; likely `board.BUTTON_A` / `BUTTON_B` | GPIO38 / GPIO33 | `BUTTON_A`/`BUTTON_B` match | API only |

Pull-up, LOW = pressed. Official LED sequential list matches Exp09 (top row `20 15 10 5 0` …). Gotcha, not overnight: buzzer = GPIO17 = goldfinger **P0**.

---

## Phases (provisional — execution chat after v1.0)

**First atomic action:** set `_constants.WIDTH` and `HEIGHT` to 5. Later sequences stay open.

LUT = logical (x,y) → NeoPixel strip index. Codec = `bitmap_codec` ASCII `#`/`.` ↔ column-major bytes. EventQueue = `keypad`’s bounded native press/release queue (debounce already done). Dispatcher = EventQueue key index → A/B/C/D. **Visual fixture** = expected strip indices authored by hand (or a second algorithm), **not** by copying `row + 20 - column * 5` into the test — otherwise a wrong formula blesses itself (shared-derivation hazard).

P1–P6 close: cadence **P-phase** + G1–G7 **and A1–A4**. First student-facing name: **P-api**. P-device / P-human are not overnight.

| ID | Target | Note | Exit |
|----|--------|------|------|
| P0 | Digests + copy | **Done** | — |
| P1 | Geometry + LUT | Stage-2 `idx = row + 20 - column * 5`; visual-fixture tests. **Localized** `build_lut` edit only — keep rotation-branch structure and comments | Grid vs formula disagree → stop |
| P2 | Icons/arrows | Exp09 25-byte row-major 0–9 → 5 column bytes (hypothesis). Names: YES, NO, DIAMOND, N/S/E/W | G4 names missing → fix before P6 |
| P3 | Font | Default: vendor MIT notice + DAL glyphs. Alt: written copyleft-combination case then pitchfork. Convert; min A–D + 0–9. Keep `_glyph_columns` algorithm | Combining copyleft into `lib/` with no written case, or missing notice → stop. Legibility → P-human |
| P4 | Pin + brightness | `PIXEL_PIN=board.NEOPIXEL`, `BRIGHTNESS=0.20`; keep hardware import guard | — |
| P5 | Async buttons | Fake EventQueue; C/D fire tests; A/B/C/D **names** on constructor. Do not wrap Exp09 `Button` as student API | Student `update()` → escalate |
| P6 | Host suite | `/Users/alex/Development/PythonVEs/CircuitPython_3.13_VsCode/bin/pytest` from Exp16 root | Overnight bar |
| P7 | `.vscode/` override | Later chat | Escalate before **shared** CircuitPythonSync |
| P8 | On-device 10.3.0 `keypad`/asyncio, C/D + LUT. **Flash board to 10.3.0 first** if still on older firmware | Human window | Log-only until then |

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
| K1 | Device has **user-facing** `asyncio` after bundle copy (`asyncio` + `adafruit_ticks`). Firmware already lists `_asyncio` + `keypad.Keys` (10.3.0 matrix, source-verified 2026-09-04). Host CPython `asyncio` ≠ that library. | P8 `circup install asyncio` + `help("modules")` | Escalate; no silent `update()` student API |
| K2 | PlanetX C/D **cable** on goldfinger P13/P14. Firmware names: `board.IO13`/`IO14` = GPIO36/37 (was disputed as a numbering clash; resolved in `pins.c`). | P8 wiring | Constructor pins (allowed). |
| K3 | Conversion cheap enough; notice placed; if copyleft candidate, written combination case | P3 | Hand-author min glyphs (our copyright), or escalate GPL-on-`lib/` |
| K4 | Copy Exp14 tests vs thin suite | P1–P6 | Thin suite OK |
| K5 | Onboard A/B names | P7/P8 | Constructor stubs |

---

## Authority-handoff

| Change | Who |
|--------|-----|
| LUT, icon bytes, font conversion, test layout, button module path, wiring `_write_pattern_on_the_fly` after analysis | Agent |
| Stability **target**, cadence, hardware scope, overnight bar, font **license** bar (including accepting GPL on `lib/` if a case recommends it), shared CircuitPythonSync, destructive ops, git commit | **Alex** |
| Watch II motor / light / HAL / extra overnight criteria (e.g. requiring `on_*_released` or a full student sketch) | Escalate first |

Park: `../_parked/`. Ledger: `memory/PERMITTED_DESTRUCTIVE_ACTIONS.md` (empty).

---

## Checkpoints

P-plan · P-phase (P1–P6, G1–G7 + A1–A4) · P-api · P-device · P-human · P-surprise · P-done.

---

## See also

`../digests/` · Exp14 style SoT `/Users/alex/Development/VsCode/CircuitPython/2026-04_Exp14_DisplayLibrary_CPy_on_RPi-Pico-2040/lib/display/` · Exp16 work copy `../../lib/display/` · Exp09 `lib/display_v0.py` · `../../Notes/overall_goal.md` · host venv `/Users/alex/Development/PythonVEs/CircuitPython_3.13_VsCode`
