# Digest — Exp09 5×5 LUT, orientation, icons, pins

**Status:** LUT/wiring `evidence-supported` (code + on-device Exp09). C/D pins = **hypothesis** (Exp09 example, confirm at wiring). Font source in Exp09 = **do not copy blindly** (license).
**Date:** 2026-09-04.
**Purpose:** swap-unit facts for adapting the Exp16 copy of Exp14 `lib/display/` to BPI-Bit-S2 5×5.
**Sources:** `/Users/alex/Development/VsCode/CircuitPython/2026-02_Exp09_BPI-Bit-S2-LED-Matrix/` — `lib/display_v0.py`, `lib/microbit.py`, `generate_font.py`, `lib/elecfreaks_planetx/button.py`.

---

## Pixel pin + brightness

| Hook | Exp09 value | Exp16 lock |
|------|-------------|------------|
| Data pin | `board.NEOPIXEL` (= GPIO18 / `board.IO18`, `code_old.py`) | use this in `core.py` `PIXEL_PIN` |
| Count | 25 | `WIDTH=HEIGHT=5` |
| Brightness | 0.10 | **0.20** cap (`../NOTES.md`) — do not copy 0.10 |

---

## LUT (logical top-left → strip index)

Logical: `(column, row)`, origin **top-left**, micro:bit convention. Edge connector at the bottom.

```
idx = row + 20 - column * 5
```

Physical strip (Exp09 docstring, rotation=0):

```
Top of board
 (20) (15) (10) (5) (0)     ← logical row 0, columns 0→4
 (21) (16) (11) (6) (1)
 (22) (17) (12) (7) (2)
 (23) (18) (13) (8) (3)
 (24) (19) (14) (9) (4)     ← logical row 4
          edge connector
```

**Not** Exp14’s 8×8 formula `idx = (HEIGHT-1-py)*WIDTH + px` (bottom-up progressive L→R). Replacing `geometry.build_lut` stage 2 is mandatory. Stage 1 (logical rotation) can stay; apply rotation then this wiring.

Host-test the LUT with a visual fixture (F-pattern / numbered cells) — shared-derivation hazard if the test reuses the same formula (`CODING_PRINCIPLES` test-design).

---

## Icons / arrows (LightTower names exist)

Exp09 `Image.*` is **25-byte row-major**, brightness 0–9 (`\t` = 9 = on). Exp14 `icons.py` is **WIDTH column-major bytes**, 1-bit. Port = convert, not paste.

LightTower-required names present:

| MakeCode / tutorial | Exp09 | Exp14 name to keep |
|---------------------|-------|--------------------|
| Icon YES (✓) | `Image.YES` | `Icons.YES` |
| Icon NO (X) | `Image.NO` | `Icons.NO` |
| Icon DIAMOND (◆) | `Image.DIAMOND` | `Icons.DIAMOND` |
| Arrow N/S/E/W | `Image.ARROW_N` … `ARROW_W` | `Arrows.NORTH` … `WEST` (also NE/SE/SW/NW) |

Also present: HEART, HAPPY, SAD, clocks, animals, etc. — optional on 5×5; GIRAFFE-class extras may drop.

---

## PlanetX C/D pins — hypothesis

Exp09 `lib/elecfreaks_planetx/button.py` example: `Button(board.IO13, board.IO14)`. Electrical: pull-up, **LOW = pressed**. J3 MakeCode map C→P13, D→P14 (same as LightTower tutorial).

**Exp16 (2026-09-04):** C/D pin identity is **disputed**. Exp09 side: `board.IO13` / `board.IO14`. Official BananaPi goldfinger (`Notes/bpi_bit_v2_goldfinger.jpg`, [docs](https://docs.banana-pi.org/en/BPI-Bit-S2/BananaPi_BPI-Bit-S2)): P13/P14 = **GPIO36 / GPIO37**; GPIO13/14 are the onboard photoresistors. CircuitPython `board.*` name for those GPIOs unconfirmed. Constructor takes pins (G2 seam). Overnight smoke = C/D only with fake events (identity unused). Onboard A/B: official GPIO38 / GPIO33; leave as constructor args (`board.BUTTON_A` / `BUTTON_B` is the usual CircuitPython name; verify on device).

Do **not** use Exp09 `Button` class as the student API (sync `c_pressed` poll). Internals only as electrical evidence.

---

## Font facts (source not locked; license bar restated 2026-09-04)

Public-repo bar: hobby use + vendor **with notice**. Copyleft **into `lib/`** only after a written case on that candidate. Not a coarse GPLv3 ban.

1. **`generate_font.py` + `microbit.py` `_FONT`** — `https://github.com/stef/pitchfork-5x5` (**GPLv3**). **Promising** (already 5×5). Combining converted tables into `lib/display` is likely a combined work. Do **not** copy until the case is written; default overnight path is DAL.
2. **MakeCode look** — Lancaster DAL `MicroBitFont.cpp` `pendolino3`. **MIT** (BBC / Lancaster by arrangement with the BBC) — `evidence-supported` 2026-09-04 from file header + repo `LICENSE`. Low-friction default if the MIT notice is vendored beside the glyphs. Encoding: **row bytes** (bit4…bit0 = col1…col5), not Exp14 column-major — convert if used. https://github.com/lancaster-university/microbit-dal `source/core/MicroBitFont.cpp`

Overnight need: letters A–D + digits 0–2 for Watch I traces. Full ASCII nice-to-have.

Plan: `../plan/plan_v1.0.md` § Font. No FreeMono-at-8px.

---

## See also

- `exp14-display-lib.md` — swap-unit list
- `../NOTES.md` — LUT formula already locked at product level
- LightTower pin table in `lighttower-student-ops.md` (P5/P11/P13/P14 on stock micro:bit — **not** BPI-Bit-S2 GPIO names)
