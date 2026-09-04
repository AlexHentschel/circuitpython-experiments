# Learnings — overnight P1–P6 (2026-09-04)

Cadence: Observe → Evaluate → Revise-or-no-change → Extract → Record. Portability G1–G7 and A1–A4 reopened at each P-phase.

## P1 — Geometry + LUT

- **Observe:** Stage-2 `idx = py + HEIGHT*(WIDTH-1-px)` matches the hand-authored BananaPi sequential grid (top row `20 15 10 5 0`). Rotation branches kept; 90/270 use a stride accumulator. First F-pattern 90/270 ASCII fixtures were mirrored — composition tests (independent cell rotation) caught that the LUT was right and the fixture was wrong.
- **Evaluate:** Visual-fixture rule (shared-derivation hazard) earned its keep. Criteria still right.
- **Revise:** no change, continuing.
- **Extract:**
  - **Claim:** Independent visual grid + geometric rotation is a stronger LUT oracle than re-deriving `row+20-column*5` in the test.
  - **Evidence:** `tests/test_geometry.py` `_VISUAL_ROT0`; two fixture typos failed while permutation/corner tests passed.
  - **Status:** `evidence-supported` (host)
  - **Guideline:** G2 (LUT in swap file `geometry.py`)
  - **Action:** keep
  - **Date:** 2026-09-04

## P2 — Icons / arrows

- **Observe:** Exp09 25-byte row-major (any non-zero = on) converts to 5 column bytes via `col[c] |= 1<<r` when `src[r*5+c]`. LightTower names YES, NO, DIAMOND, NORTH/EAST/SOUTH/WEST all present. Arrows kept in `icons.py` (independently replaceable by `ARROW_*` block). CLOCK2 skipped (`shift_right`).
- **Evaluate:** G4 names present. Extra 8×8-only extras not an issue — GIRAFFE exists at 5×5 in Exp09 so it stayed.
- **Revise:** no change.
- **Extract:** G4 confirmed for the LightTower set. Nothing else.
- **Date:** 2026-09-04

## P3 — Font

- **Observe:** Default DAL MIT path taken. `pendolino3` 475 row-bytes converted to 475 column-major bytes. MIT notice at `lib/display/font_makecode_5/LICENSE`. Pitchfork GPLv3 **not** combined; no combination case required. Storage = raw 5-byte table (open item: PCF vs table → table, because overnight forbids `adafruit_bitmap_font` on host and FreeMono is gone). `_glyph_columns` remains the feeder hook; PCF metric algorithm stays in Exp14.
- **Evaluate:** License bar met (notice travels). Min A–D + 0–9 present; full ASCII 32–126 vendored as cheap superset. Legibility = P-human.
- **Revise:** no change to license bar or overnight min set.
- **Extract:**
  - **Claim:** DAL row format bit4=left column … bit0=right column converts with `(row_byte >> (4-c)) & 1 → col[c] |= 1<<r`.
  - **Evidence:** DAL `MicroBitFont.cpp` header `!` example `{0x08×3, 0, 0x08}` → column 1 bits 0,1,2,4; `tests/test_font.py`.
  - **Status:** `evidence-supported` (host conversion)
  - **Guideline:** none (font swap unit / G2)
  - **Action:** keep; pitchfork case still only if that path is chosen later
  - **Date:** 2026-09-04

## P4 — Pin, brightness, fused scan

- **Observe:** `PIXEL_PIN=board.NEOPIXEL`, `BRIGHTNESS=0.20`. Hardware import guard unchanged. `_write_pattern_on_the_fly` analyzed: same skip/pad/clip contract as the two-stage loop; wired as `render_pattern` hot path; `_iter_pattern_rows_fast` kept unused-by-render as the two-stage alternative.
- **Evaluate:** G2 constructor/config seam (pin in `core.py`). Brightness stays inside the library (hazard table).
- **Revise:** no change.
- **Extract:** Fused scan is a localize-and-utilize of an existing sketch, not a rewrite. Nothing further.

## P5 — Async buttons (P-api)

- **Observe:** Module path `lib/buttons.py`. Student names `on_a/b/c/d_pressed` (+ released, `clear`, `run`). Pins on constructor; host `event_queue=` fake. No student `update()`. Key index 0–3 = A–D. Fake FALL (`pressed=True`) fires C (index 2) and D (index 3).
- **Evaluate:** G1 semantic letters. G2 pins are config. Sync-`update()` hazard avoided. Would survive RP2350+8×8: handlers unchanged; pin args may change.
- **Revise:** no change to stability target.
- **Extract:** P-api first student-facing button names recorded. `on_*_released` present, not an overnight gate.

## P6 — Host suite

- **Observe:** 146 passed. No `import board` / `display.core` in the suite (`tests/test_no_board_core.py`). Optional `mpy-cross` 10.3.0 emitted mpy v6.3 for `lib/display/*.py`, `font_makecode_5/*.py`, `lib/buttons.py` (output in `/tmp/exp16-mpy-smoke`, not in tree).
- **Evaluate:** Overnight bar met. Criteria still the right ones. Diminishing returns: stop.
- **Revise:** no change. P7 `.vscode/` and P8 on-device stay log-only.
- **Extract:** K4 thin suite sufficient. K1/K2/K5 remain P8.

## G1–G7 / A1–A4 (overnight close)

| Id | Overnight | Note |
|----|-----------|------|
| G1 | confirm | Letters A–D; icons YES/NO/DIAMOND; arrows compass. No GPIO in handlers. |
| G2 | confirm | Pins / LUT / font dir / brightness are swap files or constructor args. |
| G3 | confirm (names) | `show_icon` / `show_string` / `show_number` / `show_arrow` / `pause` exist on `Display` (AST; not imported on host). |
| G4 | confirm | LightTower names present on 5×5. |
| G5 | n/a | Internals may change later; not tested by a platform switch. |
| G6 | confirm | No motor/light APIs invented. |
| G7 | stand-in | Public names exist; Watch I sketch **not** overnight (plan). |
| A1 | keep | Matrix remains the feedback channel. |
| A2 | unverified | `keypad` + user `asyncio` on device = P8. Host CPython asyncio ≠ CIRCUITPY bundle. |
| A3 | locked | Square WS2812 5×5. |
| A4 | unverified | PlanetX cable still P8; firmware names already known. |
