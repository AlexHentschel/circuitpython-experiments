# Experiment 14 -- MakeCode-Style Display Library for 8x8 WS2812b on YD-RP2040

A CircuitPython display library that provides a MakeCode Python-style API for
driving an 8x8 WS2812b (NeoPixel) LED matrix from a [YD-RP2040 board](https://github.com/initdc/YD-RP2040).

Features: asyncio-based cooperative multitasking with cancellation, two-tier
API (sync rendering + async MakeCode-compatible methods), Image class with
scrolling, font rendering, 40 icons, 8 arrows, multi-color palette support.

## Hardware

| Component | Detail |
|-----------|--------|
| **MCU board** | YD-RP2040 by VCC-GND Studio (RP2040, 16 MB flash, USB-C) |
| **CircuitPython** | 10.1.4 -- board-id `vcc_gnd_yd_rp2040` |
| **LED matrix** | 8x8 WS2812b (64 NeoPixels), progressive bottom-up L-to-R wiring |
| **Data pin** | GP0 -> level shifter -> WS2812b DIN |
| **Level shifter** | 3.3 V -> 5 V (required -- RP2040 is 3.3 V logic) |

### Wiring

```
YD-RP2040 GP0 --> Level-Shifter IN   (3.3 V side)
Level-Shifter OUT --> WS2812b DIN    (5 V side)
5 V PSU (+)  --> WS2812b VCC  +  Level-Shifter high-voltage VCC
GND          --> all GNDs (board, shifter, LED matrix, PSU)
```

## Library API -- `lib/display/` package

The library is structured as a Python package (`lib/display/`) with six
sub-modules. User-facing imports (`from display import ...`) are
unchanged. See [lib/display/README.md](lib/display/README.md) for the
package architecture and design rationale.


### Quick start (async, recommended)

```python
import asyncio
from display import display, IconNames, RED, GREEN, create_image

async def main():
    await display.show_icon(IconNames.HEART, color=RED, interval_ms=800)
    await display.show_string("Hello!", color=GREEN, interval_ms=150)
    display.clear_screen()

asyncio.run(main())
```

### Quick start (sync, no multitasking)

```python
from display import display, IconNames, RED

display.render_icon(IconNames.HEART, color=RED)
# image persists on LEDs until next display call
```

### Tier 1 -- Synchronous rendering (instant, no await)

| Method | Description |
|--------|-------------|
| `render_pattern(pattern, color=WHITE)` | Render `#`/`.` pattern or palette dict to LEDs. `color` accepts an RGB tuple (mono) or a palette dict. |
| `render_icon(icon, color=WHITE)` | Render icon bitmap to LEDs. |
| `render_arrow(direction, color=WHITE)` | Render arrow bitmap to LEDs. |
| `clear_screen()` | All pixels off. Cancels ongoing animations. |
| `clear()` | Alias for `clear_screen()`. |
| `set_pixel(x, y, color)` | Set one pixel. Cancels ongoing animations. |
| `fill(color)` | Fill all pixels. Cancels ongoing animations. |
| `get_pixel(x, y)` | Read buffered pixel color. |
| `set_brightness(value)` | Adjust 0.0-1.0. Does not cancel animations. |
| `set_rotation(degrees)` | Rebuild LUT for 0/90/180/270. |

### Tier 2 -- Async (require `await`)

| Method | Description |
|--------|-------------|
| `show_leds(pattern, color=WHITE, interval_ms=0)` | Render + hold. `color` accepts an RGB tuple (mono) or a palette dict. |
| `show_icon(icon, color=WHITE, interval_ms=0)` | Render icon + hold. |
| `show_arrow(direction, color=WHITE, interval_ms=0)` | Render arrow + hold. |
| `show_string(text, color=WHITE, interval_ms=150)` | Scroll text. `interval_ms` = milliseconds per column step. |
| `show_number(n, color=WHITE, interval_ms=150)` | Single digit: centered. Multi-digit: scroll. |
| `pause(ms)` | Cancellable async sleep. |
| `forever(callback)` | Sync convenience: while-True loop via asyncio. |

### Image class

```python
from display import create_image, create_big_image, RED

img = create_image("""
    # . # .
    . # . #
    # . # .
    . # . #
""", color=RED)

await img.show_image(offset=0, interval_ms=500)
img.recolor((0, 255, 0))
await img.scroll_image(offset=1, interval_ms=200)
```

### Color palette

**Adafruit standard:** `RED`, `YELLOW`, `ORANGE`, `GREEN`, `TEAL`, `CYAN`,
`BLUE`, `PURPLE`, `MAGENTA`, `WHITE`, `BLACK`, `GOLD`, `PINK`, `AQUA`,
`JADE`, `AMBER`, `OLD_LACE`, `RAINBOW`

**LED-tuned extras:** `GRAY`, `DARKSLATEBLUE`, `YELLOWGREEN`, `DEEPPINK`

**Aliases:** `OFF` = `BLACK`

**Helpers:** `color(r, g, b)`, `colorwheel(pos)` (re-exported from `rainbowio`)

### Multi-color palette example

```python
from display import display, color, OFF

palette = {
    'R': color(255, 0, 0),
    'B': color(0, 0, 255),
    '.': OFF,
}
await display.show_leds("""
    R . R . R . R .
    . B . B . B . B
""", color=palette, interval_ms=2000)
```

### Coordinate system

Origin `(0, 0)` at top-left. `x` increases rightward (column), `y` increases
downward (row).

The physical LED strip uses **progressive bottom-up wiring**: all rows run
left-to-right, but strip index 0 starts at the bottom-left corner. The library
handles this mapping transparently via a pre-computed **LUT** (lookup table) --
a 64-byte array where `LUT[x * 8 + y]` gives the NeoPixel strip index for
logical pixel `(x, y)`. Users never need to think about physical wiring.

Example (no rotation):

Logical coordinates (x, y):

```
         x=0   x=1   x=2   x=3   x=4   x=5   x=6   x=7
y=0    (0,0) (1,0) (2,0) (3,0) (4,0) (5,0) (6,0) (7,0)
y=1    (0,1) (1,1) (2,1) (3,1) (4,1) (5,1) (6,1) (7,1)
y=2    (0,2) (1,2) (2,2) (3,2) (4,2) (5,2) (6,2) (7,2)
y=3    (0,3) (1,3) (2,3) (3,3) (4,3) (5,3) (6,3) (7,3)
y=4    (0,4) (1,4) (2,4) (3,4) (4,4) (5,4) (6,4) (7,4)
y=5    (0,5) (1,5) (2,5) (3,5) (4,5) (5,5) (6,5) (7,5)
y=6    (0,6) (1,6) (2,6) (3,6) (4,6) (5,6) (6,6) (7,6)
y=7    (0,7) (1,7) (2,7) (3,7) (4,7) (5,7) (6,7) (7,7)
```

Physical NeoPixel strip indices (progressive bottom-up L-to-R, no rotation):

```
         x=0   x=1   x=2   x=3   x=4   x=5   x=6   x=7
y=0    (56)  (57)  (58)  (59)  (60)  (61)  (62)  (63)   top row
y=1    (48)  (49)  (50)  (51)  (52)  (53)  (54)  (55)
y=2    (40)  (41)  (42)  (43)  (44)  (45)  (46)  (47)
y=3    (32)  (33)  (34)  (35)  (36)  (37)  (38)  (39)
y=4    (24)  (25)  (26)  (27)  (28)  (29)  (30)  (31)
y=5    (16)  (17)  (18)  (19)  (20)  (21)  (22)  (23)
y=6    ( 8)  ( 9)  (10)  (11)  (12)  (13)  (14)  (15)
y=7    ( 0)  ( 1)  ( 2)  ( 3)  ( 4)  ( 5)  ( 6)  ( 7)   bottom row (strip start)
```

Display rotation (0/90/180/270 degrees via `set_rotation()`) is also baked
into the LUT, so all rendering code stays the same regardless of how the
physical matrix is mounted.

### Pattern string format

8 rows of 8 characters. `#` = ON, `.` = OFF (mono mode). With a dict palette,
any single character maps to a color. Spaces stripped.

## Icons and arrows

40 built-in icons (`IconNames.*`) and 8 arrows (`ArrowNames.*`). See
[lib/display/icons.py](lib/display/icons.py) for the full list and
ASCII art designs.

## Library installation

```bash
# Phase 1 dependencies
circup install neopixel

# Phase 2 dependencies
circup bundle-add adafruit/circuitpython-fonts
circup install asyncio adafruit_bitmap_font font_free_mono_8
```

Use `circup` flags `--path <project-dir> --board-id vcc_gnd_yd_rp2040 --cpy-version 10.1.4` when auto-detection isn't available.

## Project structure

```
2026-04_Exp14_DisplayLibrary_CPy_on_RPi-Pico-2040/
+-- .circuitpyignore          Sync exclusions
+-- .vscode/
|   +-- tasks.json            Serial monitor tasks
|   +-- settings.json         Python venv path
|   +-- cpfiles.txt           CircuitPythonSync manifest
+-- code.py                   Demo script (asyncio-based Phase 2 showcase)
+-- requirements-dev.txt      Host-side test dependencies (pytest)
+-- lib/
|   +-- display/              MakeCode-style display library (package)
|   |   +-- __init__.py       Public-API re-exports
|   |   +-- _constants.py     Dimensions + encoding limit + colors (pure)
|   |   +-- bitmap_codec.py   ASCII art <-> column-major bytes codec
|   |   +-- geometry.py       Pure build_lut / xy_to_index
|   |   +-- icons.py          ICONS, ARROWS, IconNames, ArrowNames
|   |   +-- core.py           Display + Image runtime (hardware-coupled)
|   |   +-- font_free_mono_8/ PCF font (ships with package)
|   |   +-- README.md         Package architecture + design rationale
|   +-- neopixel.mpy          (installed by circup)
|   +-- adafruit_pixelbuf.mpy (installed by circup)
|   +-- asyncio/              (installed by circup)
|   +-- adafruit_ticks.mpy    (installed by circup)
|   +-- adafruit_bitmap_font/ (installed by circup)
+-- tests/                    Tier 1 pytest suite (host-side)
+-- CONTEXT_HANDOFF.md        AI context document
+-- README.md                 This file
```

## Running tests (host-side, Tier 1)

Pure sub-modules (`bitmap_codec`, `geometry`, `icons`, `_constants`)
are exercised on CPython without any CircuitPython stubs. The
`display.core` runtime (NeoPixel buffer, font) is covered by Tier 2
tests (deferred; will add `circuitpython-mocks` + local stubs).

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
pytest tests/
```

## Development workflow

1. **Serial monitor** -- VS Code task "Serial Monitor (miniterm)" or:
   ```bash
   pyserial-miniterm --raw /dev/tty.usbmodem* 115200
   ```
   Exit with `Ctrl+]`.

2. **Sync to board** -- CircuitPythonSync extension uploads files listed
   in `.vscode/cpfiles.txt` to the CIRCUITPY drive.

3. **REPL** -- Press `Ctrl+C` in the serial monitor to drop into the
   CircuitPython REPL. `Ctrl+D` soft-reboots and re-runs `code.py`.
