# Digest — Exp14 `lib/display/` (8×8 WS2812, YD-RP2040)

**Status:** `evidence-supported` for structure/API (read from source 2026-09-04). On-device Exp16 behaviour: not this digest.
**Date:** 2026-09-04.
**Purpose:** enough for a cold AI to work on the **Exp16 copy** without re-deriving architecture. Work on the copy; do not edit Exp14.
**Copied tree (new files, 2026-09-04):** `/Users/alex/Development/VsCode/CircuitPython/2026-09_Exp16_BPI-Bit-S2_CircuitPy_PlanetX/lib/display/`
**Upstream (do not mutate for Exp16):** `/Users/alex/Development/VsCode/CircuitPython/2026-04_Exp14_DisplayLibrary_CPy_on_RPi-Pico-2040/lib/display/`
**Architecture SoT:** `lib/display/README.md` in either tree (identical at copy time).

Copy residue (not source of truth): `__pycache__/`, `.DS_Store`. Leave them; no delete grant.

---

## One-line purpose

MakeCode-shaped two-tier library: sync primitives + cancellable async `show_*`, driving one square WS2812 matrix via a coordinate Look-Up Table [LUT] and column-major bytes.

---

## Work on the copy — swap units vs leave-alone

Locked Exp16 target: 5×5 ↔ 8×8 by **file replacement and/or localized edits**, not a second library, not a `core.py` rewrite.

| Unit | File(s) | Exp14 today | Exp16 first edit |
|------|---------|-------------|------------------|
| Geometry constants | `_constants.py` | `WIDTH=HEIGHT=8` | → 5; `NUM_PIXELS` follows |
| Encoding cap | `_constants.py` `_MAX_HEIGHT_PER_COLUMN_BYTE = 8` | format limit, **not** geometry | **keep 8** (5×5 and 8×8 both fit) |
| LUT wiring | `geometry.py` `build_lut` | 8×8 progressive **bottom-up** L→R: `idx = (HEIGHT-1-py)*WIDTH + px` | replace with Exp09 5×5 formula (see `exp09-lut-icons.md`); rotation branches stay |
| Icons + arrows | `icons.py` (`ICONS` **and** `ARROWS`; `ICON_NAMES` / `ARROW_NAMES`) | 8×8, 40 icons + 8 compass arrows | replace bitmaps with Exp09 5×5 `Image.*`; **keep LightTower names** YES, NO, DIAMOND, NORTH/EAST/SOUTH/WEST. Whether arrows split to `arrows.py` is shape — open |
| Font | `font_free_mono_8/font.pcf` + `_FONT_PATH` in `core.py` | FreeType auto-raster of FreeMono at 8 px — **illegible** (`concepts/fonts.md`) | swap directory + `_FONT_PATH` only; rendering (`_glyph_columns`) is metric-agnostic. **Do not lock a glyph source in this digest** |
| Hardware pin / brightness | `core.py` `PIXEL_PIN`, `BRIGHTNESS` | `board.GP0`, `0.05` | BPI-Bit-S2 pixel pin (Exp09) + brightness **0.20** cap (NOTES) |
| Runtime engine | `core.py` | Display/Image, `_seq` cancel, NeoPixel, hot/cold parsers, `_write_pattern_on_the_fly` sketch | **keep entire algorithms**; localized hooks only (see plan § Exp14 engine). Style SoT = Exp14 upstream |
| Codec | `bitmap_codec.py` | ASCII ↔ column-major; height cap 8 | keep; already parameterized by WIDTH/HEIGHT |
| Public re-exports | `__init__.py` | hardware import guarded for host pytest | keep |

`core.py` / `bitmap_codec.py` are geometry-agnostic **except** those hooks. Do not redesign column-major storage.

---

## Two-tier API (student vs power-user)

**Tier 1 — sync, no `await`:** `render_pattern`, `render_icon`, `render_arrow`, `set_pixel` / `fill` / `clear_screen` / `clear` / `get_pixel`, `set_brightness`, `set_rotation`. Immediate NeoPixel buffer writes.

**Tier 2 — async MakeCode-compatible (LightTower student ops):** `show_leds`, `show_icon`, `show_arrow`, `show_string`, `show_number`, `pause`, plus `Image.show_image` / `scroll_image`. `forever(callback)` is a sync wrapper around `asyncio` `while True`.

Portability (G3): student sketches use Tier 2 names; Tier 1 may remain for tests. See `../design/student-api-portability.md`.

**Cancellation:** `Display._seq` token. Mutating display calls `_acquire()`; in-progress Tier 2 loops `_is_cancelled(token)` around `await asyncio.sleep(...)`. Non-cancelling: `get_pixel`, `set_brightness`, `set_rotation`.

**Singleton:** module-level `display`, `_pixels`, `_LUT`, font. `deinit()` tears down PIO/pin; **no re-init**. Host tests import pure sub-modules via `__init__.py` `try: import board`.

---

## Column-major bytes (do not change)

One byte per column; bit N (value `2**N`, bit 0 = LSB) = row N lit (row 0 = top). 8×8 icon = 8 bytes; 5×5 icon = 5 bytes (high bits unused). Height > 8 = storage redesign — **out of Exp16 hardware scope** (square WS2812, N≤8).

LUT index convention (matches this layout): `lut[x * HEIGHT + y]` — x outer stride. Not NumPy row-major.

---

## Hardware hooks in `core.py` (the only board imports)

```
PIXEL_PIN = board.GP0          # Exp14 YD-RP2040
BRIGHTNESS = 0.05
_FONT_PATH = …/font_free_mono_8/font.pcf
```

Exp14 LUT assumes **bottom-up progressive** strip (index 0 = bottom-left). Exp09 5×5 is a **different** wiring (`row + 20 - column * 5`) — do not reuse Exp14 `build_lut` stage-2 formula on BPI-Bit-S2.

---

## LightTower names already in Exp14 `ICON_NAMES` / `ARROW_NAMES`

Icons include `YES`, `NO`, `DIAMOND` (also `SMALL_DIAMOND`). Arrows: `NORTH`, `NORTH_EAST`, `EAST`, `SOUTH_EAST`, `SOUTH`, `SOUTH_WEST`, `WEST`, `NORTH_WEST`. 8×8-only extras (e.g. `GIRAFFE`) may vanish on 5×5; LightTower names must not.

---

## Tests (host)

Exp14: `2026-04_Exp14_…/tests/` — pytest, 137/137 green as of 2026-06-11 (persona CONTEXT). Overnight Exp16 success bar = host tests + libs on disk (`../NOTES.md`). Copy of tests is **not** done this digest; plan should decide whether to copy `tests/` or write a thin 5×5 suite against the same codec/LUT contracts.

---

## Font constraint (recommendation deferred to plan)

- Outline TTF→PCF at ≤~10 px is structurally illegible — `evidence-supported`, `concepts/fonts.md`.
- Exp14 `font_free_mono_8` exhibits that failure; code is exonerated. GNU FreeFont copy **removed from Exp16 2026-09-04** (Alex cleanup). P3 vendors the 5×5 font.
- Swap = new `font_<name>/` + `_FONT_PATH`; **keep** `_glyph_columns` algorithm (localized metric comments only).
- 5×5 wants a hand-designed bitmap / MakeCode-style 5-row font. **Source not locked.** License: written case if combining copyleft into `lib/` (`plan_v1.0.md` § Font).

---

## See also

- `../NOTES.md` — product locks (brightness 0.20, swap units, WS2812 square N≤8)
- `../design/student-api-portability.md` — G1–G7
- Exp14 `CONTEXT_HANDOFF.md` — exhaustive internals (further reading, not required to start 5×5 edits)
- Persona `projects/circuitpython-exp14-display/CONTEXT.md`
