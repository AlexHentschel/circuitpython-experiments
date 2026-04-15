# CONTEXT HANDOFF — Experiment 14: MakeCode-Style Display Library for 8x8 WS2812b on YD-RP2040

> Exhaustive standalone context for AI assistant threads.
> No prior experiment knowledge is assumed.

---

## 0. General AI assistant guidelines

### Communication
- If the intended meaning or goal is unclear or ambiguous, ask clarifying questions rather than making assumptions.
- Focus directly on analysis and output, not reassurance. Provide direct, analytical feedback rather than automatic affirmation. If you agree, explain why briefly; if you disagree or see a stronger option, state it clearly and justify your reasoning.
- Skip all affirmations such as "Good question" etc.
- No fluff or unnecessary verbosity: every sentence should deliver value.

### Work style
- Work time-efficiently, yet remain detail-oriented.
- Work iteratively. Ask for direction and details for the next steps.
- Technical accuracy first: double-check all generated content for correctness before finalizing.

### Documentation
- Plans and docs should reflect only the latest version. Do not document evolution history or reference "previous plan revision" -- just the current state.
- Introduce all terms and abbreviations before or at first use. This includes diagram node IDs, variable names in pseudocode, and domain-specific acronyms. A reader should never encounter an unexplained symbol.

### Engineering
- Minimize heap fragmentation: prefer pre-allocated buffers, `bytes` literals for static data, `bytearray` for mutable fixed-size buffers, and `__slots__` on classes. Avoid repeated small allocations in hot paths.
- Optimize for performance (runtime and RAM) wherever easily possible. Prefer O(1) lookups over repeated computation, pre-compute what can be pre-computed, and avoid unnecessary copies.
- Rely on existing libraries to a large extent. Only reimplement when an existing library has major disadvantages (excessive memory, missing critical functionality, unacceptable performance). Document the rationale when choosing not to use an available library.

### Code documentation
- Detail-dense and concise. Use sentence fragments where they aid brevity without hurting clarity. Avoid boilerplate that restates what variable names or code already convey.
- Only document non-trivial aspects -- skip what function names and parameter names already communicate.
- Define domain terminology by observable effect or behavior, not by restating the name in different abstract words. Relate terms to concrete things visible in the code.
- Inline comments for non-trivial logic (coordinate transforms, bit manipulation, boundary conditions): explain the *why* or *derivation*, not the *what*.
- Summarize key transforms and formulas in docstrings with the expression and a parenthetical grounding each term.
- Classes, modules, high-level design: document intention, context, and rationale.
- Public functions: focus on caller needs (behavior, edge cases, return semantics).
- Internal/private functions: document business logic, invariants, implementation rationale.

---

## 1. Project purpose

Experiment 14 develops a **MakeCode Python-style display library** for an
**8×8 WS2812b NeoPixel LED matrix** driven by a **YD-RP2040** microcontroller
running **CircuitPython 10.1.4**.

The library (`lib/display.py`) exposes patterns as `#`/`.` grid strings,
a color palette, and simple methods (`show_leds`, `set_pixel`, `clear`, etc.).

**Phase 1** (complete): basic 8×8 rendering, pattern display, color cycling.
**Phase 2** (implemented, hardware test pending): asyncio-based cooperative
multitasking with cancellation-token counter, two-tier API (sync rendering +
async MakeCode-compatible methods), Image class with scrolling, font rendering
via `adafruit_bitmap_font`, 40 hand-designed 8×8 icons, 8 arrows, unified
color/palette parameter. Full design in the Phase 2 plan file.

---

## 2. Hardware

### 2.1 MCU board — YD-RP2040

| Property | Value |
|----------|-------|
| Manufacturer | VCC-GND Studio |
| MCU | RP2040 (dual-core Arm Cortex-M0+, 133 MHz) |
| Flash | 16 MB |
| SRAM | 264 KB |
| USB | Type-C |
| CircuitPython board-id | `vcc_gnd_yd_rp2040` |
| CircuitPython version | 10.1.4 |
| CircuitPython download | https://circuitpython.org/board/vcc_gnd_yd_rp2040/ |
| Board repo | https://github.com/initdc/YD-RP2040 |

### 2.2 On-board peripherals

| Peripheral | GPIO | `board` alias | Notes |
|------------|------|---------------|-------|
| Green LED | GP25 | `board.LED` | Always available; active high |
| WS2812 RGB LED | GP23 | `board.NEOPIXEL` | **Requires solder jumper** to be bridged; not functional by default |
| USR button | GP24 | `board.BUTTON` | Active low; internal pull-up available |

**Important**: The firmware for `vcc_gnd_yd_rp2040` maps on-board
peripherals to aliases (`board.LED`, `board.NEOPIXEL`, `board.BUTTON`).
Direct `board.GP23`/`board.GP24`/`board.GP25` names are **not** available
for these pins. Use the aliases.

### 2.3 LED matrix

| Property | Value |
|----------|-------|
| Type | WS2812b (NeoPixel) |
| Size | 8 × 8 (64 pixels) |
| Wiring layout | Progressive left-to-right, bottom-up (index 0 = bottom-left) |
| Data pin | GP0 |
| Voltage | 5 V (requires 3.3 V → 5 V level shifter on data line) |

### 2.4 Wiring diagram

```
YD-RP2040 GP0 ──► Level-Shifter IN   (3.3 V side)
Level-Shifter OUT ──► WS2812b DIN    (5 V side)
5 V PSU (+)  ──► WS2812b VCC  +  Level-Shifter high-V VCC
GND          ──► all GNDs (board, shifter, LED matrix, PSU)
```

### 2.5 RP2040 hardware resource allocation

| Resource | Used by | Details |
|----------|---------|---------|
| PIO SM (1 of 8) | `neopixel` library | Drives WS2812b data on GP0 via PIO; does NOT consume SPI |
| SPI0 | Free | Available for future peripherals |
| SPI1 | Free | Available for future peripherals |

---

## 3. Software stack

### 3.1 CircuitPython 10.1.4 built-in modules (subset)

Key built-ins on this board: `board`, `digitalio`, `analogio`, `busio`,
`neopixel_write`, `rainbowio`, `displayio`, `fontio`, `time`, `os`, `gc`,
`json`, `math`, `random`, `struct`, `usb_cdc`, `microcontroller`, `rp2pio`.

Phase 2 uses `rainbowio` (for `colorwheel`), `displayio` and `fontio` (used internally by `adafruit_bitmap_font`).

Full list: see `docs/CircuitPython Notes.md` in the project.

### 3.2 External libraries (installed via circup)

| Library | File / Dir | Purpose | Phase |
|---------|------------|---------|-------|
| `neopixel` | `neopixel.mpy` | High-level NeoPixel driver | 1 |
| `adafruit_pixelbuf` | `adafruit_pixelbuf.mpy` | Pixel buffer base class (neopixel dependency) | 1 |
| `asyncio` | `asyncio/` | Cooperative multitasking | 2 |
| `adafruit_ticks` | `adafruit_ticks.mpy` | Tick-based timing for asyncio | 2 |
| `adafruit_bitmap_font` | `adafruit_bitmap_font/` | Font loading from PCF files | 2 |
| `font_free_mono_8` | `font_free_mono_8/` | 8-pixel monospace PCF font | 2 |

Install commands:
```bash
# Phase 1 (already done)
circup install neopixel

# Phase 2 (pending)
circup bundle-add adafruit/circuitpython-fonts   # one-time: register fonts bundle
circup install asyncio adafruit_bitmap_font font_free_mono_8
```

Note: `circup` is in the project venv at `/Users/alex/Development/PythonVEs/CircuitPython_3.13_VsCode/bin/circup`. Use flags `--path <project-dir> --board-id vcc_gnd_yd_rp2040 --cpy-version 10.1.4` when not auto-detected.

### 3.3 Project library — `lib/display.py`

Core deliverable. Phase 2 is implemented (hardware test pending). Below describes the current architecture.

**Module-level constants**: `WIDTH` (8), `HEIGHT` (8), `NUM_PIXELS` (64), `PIXEL_PIN` (`board.GP0`), `BRIGHTNESS` (0.05).

**Color palette**: Adafruit LED Animation standard colors (`RED`, `YELLOW`, `ORANGE`, `GREEN`, `TEAL`, `CYAN`, `BLUE`, `PURPLE`, `MAGENTA`, `WHITE`, `BLACK`, `GOLD`, `PINK`, `AQUA`, `JADE`, `AMBER`, `OLD_LACE`) plus LED-tuned extras (`GRAY`, `DARKSLATEBLUE`, `YELLOWGREEN`, `DEEPPINK`). `OFF` = alias for `BLACK`. Re-exports `colorwheel` from `rainbowio`.

**Coordinate mapping**: A pre-computed 64-byte lookup table (LUT) bakes rotation (0/90/180/270) and bottom-up progressive wiring into a single array: `LUT[x * HEIGHT + y]` yields the NeoPixel strip index for logical pixel `(x, y)` where `x` = column (0 = left) and `y` = row (0 = top). Replaces Phase 1's per-call `_xy_to_index()` function (which is retained as a LUT-backed wrapper).

**Cancellation-token counter**: A module-level sequence counter `_seq` (int, starts at 0) enables cooperative multitasking. `_acquire()` increments `_seq` and returns the new value as a token. `_cancelled(token)` returns `True` if `_seq` has advanced past that token, meaning a newer operation has taken control.

**Two-tier API**:
- **Tier 1 (sync)**: Immediate rendering to NeoPixel buffer. `render_pattern`, `render_icon`, `render_arrow`, `clear_screen`, `set_pixel`, `fill`, `set_brightness`, `set_rotation`, `get_pixel`. Display-mutating methods call `_acquire()` to cancel ongoing Tier 2 animations.
- **Tier 2 (async)**: MakeCode-compatible convenience methods with `await`. `show_leds`, `show_icon`, `show_arrow`, `show_string`, `show_number`, `pause`. Use `await asyncio.sleep()` and check `_cancelled(token)` between animation frames.

**Bitmap format — column-major bytes**: Monochrome bitmaps (icons, arrows, font glyphs, mono `Image` data) are stored as one byte per column, where bit N of a column byte indicates whether row N is lit. This layout enables efficient horizontal scrolling by iterating contiguous column bytes. See Section 3.4 for icon/arrow storage.

**Image class**: Column-major bytes (mono) or per-pixel tuple array (multi-color). `from_pattern()`, `recolor()`, async `show_image()` / `scroll_image()`. Module-level factories: `create_image()`, `create_big_image()`.

**Parameter convention**: `color_palette` (tuple or dict) for pattern-based methods; `color` (tuple only) for single-color methods.

**Coordinate system**: Origin (0, 0) at top-left. x → right, y → down.

**Pattern string format**: 8 rows of 8 characters (`#` = ON, `.` = OFF, or palette chars when using a dict). Spaces are stripped. Missing rows/columns filled with OFF.

### 3.4 Project library — `lib/display_icons.py` (Phase 2)

Icon + arrow bitmap data stored as column-major `bytes` literals: each byte represents one column, where bit `n` (0 = LSB) corresponds to row `n` (1 = pixel lit). 40 icons (8 bytes each = 320 bytes) + 8 compass arrows (8 bytes each = 64 bytes). `IconNames` / `ArrowNames` enum-like classes defined in `display.py`.

---

## 4. Project file manifest

```
2026-04_Exp14_DisplayLibrary_CPy_on_RPi-Pico-2040/
├── .circuitpyignore              Sync exclusions for CircuitPythonSync
├── .vscode/
│   ├── tasks.json                Serial monitor tasks (pyserial-miniterm)
│   ├── settings.json             Python venv path for CircuitPythonSync
│   └── cpfiles.txt               File copy manifest for CircuitPythonSync
├── code.py                       Demo script (Phase 1: patterns + color cycling; Phase 2: asyncio showcase)
├── lib/
│   ├── display.py                MakeCode-style display library (project module)
│   ├── display_icons.py          Icon + arrow bitmap data (Phase 2)
│   ├── README                    Library folder documentation
│   ├── neopixel.mpy              (external, installed via circup)
│   ├── adafruit_pixelbuf.mpy     (external, installed via circup)
│   ├── asyncio/                  (external, Phase 2, installed via circup)
│   ├── adafruit_ticks.mpy        (external, Phase 2, installed via circup)
│   ├── adafruit_bitmap_font/     (external, Phase 2, installed via circup)
│   └── font_free_mono_8/         (external, Phase 2, PCF font via circup)
├── docs/
│   └── CircuitPython Notes.md    Built-in module listing (user-maintained)
├── CONTEXT_HANDOFF.md            This file
└── README.md                     Human-readable project documentation
```

---

## 5. Development environment

### 5.1 Host tools

| Tool | Location | Purpose |
|------|----------|---------|
| Python venv | `/Users/alex/Development/PythonVEs/CircuitPython_3.13_VsCode/` | Hosts `circup`, `pyserial-miniterm` |
| VS Code | Cursor IDE | Editor with CircuitPythonSync extension |
| `circup` | In venv | Installs CircuitPython libraries |
| `pyserial-miniterm` | In venv | Serial terminal (REPL access) |

### 5.2 Serial monitor

VS Code task "Serial Monitor (miniterm)" auto-detects the board's
`/dev/tty.usbmodem*` port at 115200 baud. Exit with `Ctrl+]`.

In the serial monitor:
- `Ctrl+C` — interrupt running code, drop into REPL
- `Ctrl+D` — soft-reboot, re-run `code.py`

### 5.3 File sync

CircuitPythonSync reads `.vscode/cpfiles.txt` and copies listed files
to the CIRCUITPY drive. Currently syncs: `code.py`.

The `lib/` folder (including `display.py` and `.mpy` files) is synced
by CircuitPythonSync separately (it manages the `lib/` folder
automatically).

---

## 6. Milestone status

### Phase 1 — Basic 8×8 display library

| Task | Status |
|------|--------|
| Project setup (.vscode, .circuitpyignore, lib scaffold) | DONE |
| `lib/display.py` — 8×8 MakeCode-style library | DONE |
| `code.py` — demo with patterns and color cycling | DONE |
| Documentation (README.md, CONTEXT_HANDOFF.md) | DONE |
| Install `neopixel` via circup | PENDING (run circup command) |
| Hardware test on YD-RP2040 | PENDING |

### Phase 2 — MakeCode-style async display library

Full design documented in the Phase 2 plan file (`phase_2_display_library_2e99c895.plan.md`).

| Task | Status |
|------|--------|
| Phase 2 design (plan file) | DONE |
| Install Phase 2 circup dependencies | DONE |
| Refactor `lib/display.py`: LUT, cancellation counter, Tier 1/2 API split, color system | DONE |
| Implement `Image` class with column-major storage, `recolor()`, async show/scroll | DONE |
| Integrate `adafruit_bitmap_font` for text rendering (`_glyph_columns`) | DONE |
| Create `lib/display_icons.py`: 40 icons + 8 arrows (column-major bytes) | DONE |
| Implement async `show_string` / `show_number` with font scrolling | DONE |
| Implement async `show_icon` / `show_arrow` | DONE |
| Update `code.py` demo for Phase 2 (asyncio-based) | DONE |
| Update documentation (CONTEXT_HANDOFF.md, README.md) | DONE |
| Hardware test on YD-RP2040 | PENDING |

---

## 7. Known issues and notes

1. **Wiring layout** (hardware-tested): Progressive left-to-right, bottom-up.
   All rows run left-to-right (no serpentine). Strip index 0 = bottom-left
   pixel. Strip index formula (before rotation):
   `idx = (HEIGHT - 1 - py) * WIDTH + px`, where `px` and `py` are the
   physical column and row after rotation is applied. `_build_lut` bakes
   this wiring plus rotation into the 64-byte LUT.

2. **Brightness**: Default is 0.05 (very dim) to avoid drawing excessive
   current during development. Increase carefully -- 64 WS2812b LEDs at
   full white draw approximately 3.8 A at 5 V.

3. **Level shifter required**: The RP2040 outputs 3.3 V logic. WS2812b
   requires 5 V data signal for reliable operation.

4. **On-board RGB LED (GP23)**: Not functional unless the solder jumper
   on the YD-RP2040 board is bridged. This project does not use the
   on-board RGB LED; the external 8×8 matrix on GP0 is the target.

5. **`board` module aliases**: Use `board.LED`, `board.NEOPIXEL`,
   `board.BUTTON` for on-board peripherals. Direct `board.GP23`/
   `board.GP24`/`board.GP25` are not available for those pins in the
   `vcc_gnd_yd_rp2040` firmware.

6. **circup install**: Must be run before first deployment. The `neopixel`
   library is not built into CircuitPython for RP2040.
