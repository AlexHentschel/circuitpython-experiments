# `display` package -- architecture and design

Developer-facing architecture doc for the ``lib/display/`` package.
For install + usage see the project root [README.md](../../README.md).

## Purpose

MakeCode-style Python display library driving an 8x8 WS2812b NeoPixel
matrix from a YD-RP2040 running CircuitPython 10.1.4.

## Hardware context

| Component | Detail |
|-----------|--------|
| MCU board | YD-RP2040 (RP2040, 264 KB SRAM, 16 MB flash) |
| LED matrix | 8x8 WS2812b (64 NeoPixels) |
| Data pin | GP0 -> 3.3V-to-5V level shifter -> WS2812b DIN |
| Wiring | Progressive left-to-right, bottom-up (strip index 0 = bottom-left) |
| Level shifter | Required (RP2040 is 3.3 V logic, WS2812b wants 5 V) |

The library hides the physical wiring behind a pre-computed coordinate
LUT (see [geometry.py](geometry.py)); callers use logical coordinates
with origin (0, 0) at top-left.

## Two-tier API

**Tier 1 -- synchronous rendering primitives** (immediate writes to the
NeoPixel buffer; no ``await``):

- `render_pattern(pattern, color_palette=WHITE)` -- parse-and-render a
  `#`/`.` grid string or palette dict.
- `render_icon(icon, color=WHITE)` -- display an icon from `ICONS`.
- `render_arrow(direction, color=WHITE)` -- display an arrow from `ARROWS`.
- `set_pixel(x, y, color)` / `fill(color)` / `clear_screen()` /
  `clear()` / `get_pixel(x, y)`.
- `set_brightness(value)` / `set_rotation(degrees)`.

**Tier 2 -- async MakeCode-compatible methods** (require
`await`, cancellable):

- `show_leds` / `show_icon` / `show_arrow` -- render + hold.
- `show_string(text, color, interval)` -- scroll text (single character
  displays centered).
- `show_number(n, ...)` -- delegate to `show_string`.
- `pause(ms)` -- cancellable async sleep.
- `forever(callback)` -- sync convenience wrapper running a callback in
  an asyncio `while True` loop.

Image methods (`show_image`, `scroll_image`) are also Tier 2.

## Cooperative multitasking & `_seq`

`Display._seq` is a monotonically-increasing sequence counter. Every
display-mutating method calls `_acquire()`, which increments `_seq` and
returns the new value as a **cancellation token**. Tier 2 animations
capture the token at start and re-check it between frames via
`_cancelled(token)` (``True`` if `_seq` has advanced past the token).
This lets a new render pre-empt an ongoing scroll without explicit
task cancellation; the scroll coroutine simply returns early.

Discipline: always `await asyncio.sleep(...)` between frames in Tier 2
methods, and check `_cancelled(token)` on both sides of the await.

## Column-major bytes (monochrome bitmap format)

Icons, arrows, font glyphs, and mono Images all share the same internal layout: one byte per column
(column 0 = leftmost). Within each byte, bit N has numeric value 2^N (so bit 0 is the least-significant bit)
and indicates row N is lit (row 0 = top). An 8x8 mono bitmap is therefore exactly 8 bytes.

For example, let's consider letter `F`:

```
. # # # # # # .          col 0: . . . . . . . .  -> 0x00
. # . . . . . .          col 1: # # # # # # # .  -> 0x7F
. # . . . . . .          col 2: # . . # . . . .  -> 0x09
. # # # # . . .          col 3: # . . # . . . .  -> 0x09
. # . . . . . .          col 4: # . . # . . . .  -> 0x09
. # . . . . . .          col 5: # . . . . . . .  -> 0x01
. # . . . . . .          col 6: # . . . . . . .  -> 0x01
. . . . . . . .          col 7: . . . . . . . .  -> 0x00
```

Bytes: `0x00 0x7F 0x09 0x09 0x09 0x01 0x01 0x00`.

Reading the bytes back: col 1 = `0x7F` = bits 0-6 set = the vertical stem (lit rows 0-6, dark row 7). Cols 2-4 = `0x09` = bits 0 and 3 = the two horizontal bars' overlap with the stem's interior columns. Cols 5-6 = `0x01` = bit 0 only = where only the top bar extends. The duplicate-value columns (`0x09` thrice, `0x01` twice, `0x00` at both ends) are *expected* -- adjacent columns in a glyph typically share a bit pattern.

Why column-major? It makes horizontal scrolling a window-slide over a
contiguous byte array -- each frame is `buf[offset:offset+WIDTH]` with
no per-pixel recomputation.

**Persistent vs one-shot**: `Image` converts to column-major at parse
time (once, amortised over repeated `show_image`/`scroll_image` calls).
`Display.render_pattern` deliberately skips the intermediate and writes
pixels directly from the parse loop -- chosen for one-shot display
speed.

**Encoding limit**: the single-byte-per-column format caps height at 8
rows (`_MAX_HEIGHT_PER_COLUMN_BYTE`). This is distinct from display
geometry; a taller display is a storage-format redesign, not a
parameter tweak.

## `Image` coupling to module state

`Image.show_image` / `scroll_image` reference module-level
`display` / `_LUT` / `_pixels` directly rather than receiving them as
arguments or holding a reference via `__init__`. For a single-display
MCU library this tight coupling is acceptable: there is exactly one
display, and keeping Image lean (via `__slots__` with four fields) is
preferred over plumbing the singletons through every instance.

## Sub-module responsibilities

| Module | Responsibility (one sentence) |
|--------|-------------------------------|
| [`_constants.py`](_constants.py) | Dimensions, encoding-format limits, and color constants -- single source of truth, pure (no hardware imports). |
| [`bitmap_codec.py`](bitmap_codec.py) | Design-time conversion between row-major ASCII art and column-major bytes. |
| [`geometry.py`](geometry.py) | Pure `build_lut(rotation)` + `xy_to_index(x, y, lut)` -- no hardware dependency. |
| [`icons.py`](icons.py) | Icon + arrow bitmap data and `IconNames` / `ArrowNames` enums (kept together so ordering cannot drift). |
| [`core.py`](core.py) | `Display` + `Image` runtime: NeoPixel buffer, LUT, font, async methods. Only module that imports `board` / `neopixel`. |
| [`__init__.py`](__init__.py) | Public-API re-exports; guarded core import lets host-side tests load pure sub-modules without a device. |

## Dependency diagram

```mermaid
flowchart LR
  init[__init__.py re-exports]
  const[_constants.py]
  codec[bitmap_codec.py]
  geom[geometry.py]
  icons[icons.py]
  core[core.py]
  font[font_free_mono_8/font.pcf]
  codec --> const
  geom --> const
  icons --> const
  core --> const
  core --> geom
  core --> icons
  core --> font
  init --> const
  init --> icons
  init --> core
```

## Cross-refs

- Project root: [README.md](../../README.md) -- user-facing install, hardware, demo quick-starts.
- [CONTEXT_HANDOFF.md](../../CONTEXT_HANDOFF.md) -- AI-assistant handoff document, including Section 0 guidelines and the Testing-strategy section (three-tier test model).
