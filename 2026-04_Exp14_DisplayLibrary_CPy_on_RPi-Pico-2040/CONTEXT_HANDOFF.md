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
- **Broader-context review**: for every change, walk the call sites and downstream consumers. Internally construct a correctness argument -- why the updated component behaves correctly under all inputs and call orders -- and keep it in working memory. Include it in code comments or commit messages only when the code is non-trivial or explicitly requested.

### Documentation
- Plans and docs should reflect only the latest version. Do not document evolution history or reference "previous plan revision" -- just the current state.
- Introduce all terms and abbreviations before or at first use. This includes diagram node IDs, variable names in pseudocode, and domain-specific acronyms. A reader should never encounter an unexplained symbol.

### Engineering
- Minimize heap fragmentation: prefer pre-allocated buffers, `bytes` literals for static data, `bytearray` for mutable fixed-size buffers, and `__slots__` on classes. Avoid repeated small allocations in hot paths.
- Optimize for performance (runtime and RAM) wherever easily possible. Prefer O(1) lookups over repeated computation, pre-compute what can be pre-computed, and avoid unnecessary copies.
- Rely on existing libraries to a large extent. Only reimplement when an existing library has major disadvantages (excessive memory, missing critical functionality, unacceptable performance). Document the rationale when choosing not to use an available library.
- **Design discipline over workarounds**: code smells (duplicated constants, circular imports, ad-hoc import stubs) are signals that the structure is wrong, not problems to route around; an apologetic comment is usually a small refactor in disguise. Continuously evaluate -- as part of all work, not an afterthought -- whether a refactor would remove or encapsulate complexity; delegate larger analysis passes to a sub-agent. Surface beneficial refactors proactively.
- **Leverage existing abstractions**: prefer refining or composing existing project and library abstractions over introducing parallel ones. Refactor them judiciously when they no longer fit.
- **Core-logic design**: prioritise API clarity. Prefer the simplest sufficiently-general solution over a more clever or more complex one. Encapsulate complexity so each unit of business logic is intuitive and self-contained, with minimal cross-unit coupling; when a unit cannot be described in a sentence, it is probably doing too much.
- **Order of hardening**: stabilise core business logic first, then augment with tests, logging, and user-facing API exposition. Premature scaffolding against churning logic is waste.
- **Package hygiene**: new packages and sub-modules must be modular, orthogonal (minimal cross-module coupling), and future-proof. Each module's responsibility should fit in one sentence.
- **Parametric dimensions**:
  - *Naming discipline (required)*: business logic must never contain numeric literals that stand for display height or width. Such numbers must be named — via module-level constants (`WIDTH`, `HEIGHT`), function parameters, or clearly-scoped local variables — so intent is explicit at every use site. Exceptions: docstrings, explanatory comments, and data-definition constants describing the on-disk layout of a specific hardware target (e.g. icon ASCII art with 8 columns).
  - *Flexibility (aspirational, not guaranteed)*: resizing the library to a different matrix should be reasonably straightforward but is not required to be a single-constant swap. Small edits across a few sites are acceptable; end-to-end parameterization is pursued only when it does not add significant complexity.
  - *Format-imposed limits*: encoding constraints (e.g. 8 bits per byte in column-major storage, capping height at 8) are distinct from display dimensions. Name them separately (e.g. `_MAX_HEIGHT_PER_COLUMN_BYTE`, not a second `HEIGHT`). Error messages must distinguish "format limit" from "current display size". Exceeding a format limit, or using a non-multiple-of-8 height, is a conscious redesign of the storage format, not a parameter tweak.

### Code documentation
- Detail-dense and concise. Use sentence fragments where they aid brevity without hurting clarity. Avoid boilerplate that restates what variable names or code already convey.
- Only document non-trivial aspects -- skip what function names and parameter names already communicate.
- Define domain terminology by observable effect or behavior, not by restating the name in different abstract words. Relate terms to concrete things visible in the code.
- Inline comments for non-trivial logic (coordinate transforms, bit manipulation, boundary conditions): explain the *why* or *derivation*, not the *what*.
- Summarize key transforms and formulas in docstrings with the expression and a parenthetical grounding each term.
- Classes, modules, high-level design: document intention, context, and rationale.
- Public functions: focus on caller needs (behavior, edge cases, return semantics).
- Internal/private functions: document business logic, invariants, implementation rationale.
- **Public entities**: every public class, function, constant, and module has a docstring. Private helpers get docstrings when their logic is non-trivial.
- **First line**: imperative, present tense, one complete sentence summarising behaviour. Do not repeat the entity name (the signature sits directly above the docstring in Python).
- **Parameters / returns**: document *only* when they carry information beyond what the signature already conveys -- non-obvious constraints, formatting, cross-parameter relationships, sentinel values, or units.
- **Raised exceptions**: document exhaustively every exception *expected during normal operation*, with the condition that triggers it. Unexpected exceptions (bugs, corrupted state) are not listed individually. If a function raises nothing during normal operation, state so explicitly.
- **Async / cancellation semantics**: for `async` methods, state whether the method cancels ongoing animations (via `_acquire()`), whether it yields to the scheduler (`await`), and whether it mutates display state. Default assumption is "cancels ongoing animations"; document the exception, not the default.
- **Classes**: document purpose, invariants, lifecycle, and any coupling to module-level state (e.g. `Image`'s coupling to `_pixels` / `_LUT`).
- **Constants**: state purpose plus any hard constraint (hardware limit, encoding limit, format invariant).
- **Evolution**: when evolving a documented entity, preserve existing docstring content and refine it; do not delete unless the behaviour itself has changed.

---

## 1. Testing strategy

### 1.1 Package layout

`lib/display/` is a Python package composed of six modules, each with a
single-sentence charter. `_constants.py` is the single source of truth
for `WIDTH`, `HEIGHT`, `NUM_PIXELS`, and the encoding limit
`_MAX_HEIGHT_PER_COLUMN_BYTE`; this replaces the cross-module
duplication that the earlier flat layout forced.

| Module | Responsibility |
|--------|----------------|
| `_constants.py` | Dimensions, encoding-format limits, colors. Pure (no hardware imports). |
| `bitmap_codec.py` | Row-major ASCII art <-> column-major bytes. Design-time authoring tool. |
| `geometry.py` | Pure `build_lut(rotation)` + `xy_to_index(x, y, lut)`. |
| `icons.py` | 40 icon + 8 arrow bitmap data plus `ICON_NAMES` / `ARROW_NAMES` ordered name tuples (`Icons` / `Arrows` wrapper classes built in `core.py`). |
| `core.py` | `Display` + `Image` runtime, NeoPixel buffer, font, async methods. Only module importing `board` / `neopixel`. |
| `__init__.py` | Public-API re-exports; guards the core import so pure sub-modules remain importable on CPython without a device. |

See `lib/display/README.md` for architecture and rationale.

### 1.2 Three-tier test model

**(a) Tier 1 -- active**: pytest on CPython exercising the pure
sub-modules (`bitmap_codec`, `geometry`, `icons`, `_constants`). No
stubs, no mocks; only `pytest` required. Tier 1 imports resolve without
triggering `core.py` because `__init__.py` only imports `core` when
`board` is available.

**(b) Tier 2 -- deferred**: tests targeting `display.core` and the full
package entry point. Requires `circuitpython-mocks` (for `board`),
local stubs for `neopixel` and `rainbowio`, plus `pytest-asyncio` for
cancellation-token sequencing and `NeoPixel.show()` frame-snapshot
assertions.

**(c) On-device -- ongoing**: interactive scripts (`code_*.py`, future
`hwtest_*.py`) for hardware-integration validation, human-judged via
serial output.

### 1.3 External landscape (brief)

- `circuitpython-mocks`: scheduled for Tier 2 (provides `board` stubs).
- `Adafruit-Blinka`: rejected -- Pi-host-centric, heavier than needed.
- `Adafruit_CircuitPython_BoardTest`: on-device-only; not applicable to
  host-side testing.

### 1.4 Running Tier 1 locally

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
pytest tests/
```

---

## 2. Project purpose

Experiment 14 develops a **MakeCode Python-style display library** for an
**8×8 WS2812b NeoPixel LED matrix** driven by a **YD-RP2040** microcontroller
running **CircuitPython 10.1.4**.

The library (`lib/display/`) exposes patterns as `#`/`.` grid strings,
a color palette, and simple methods (`show_leds`, `set_pixel`, `clear`, etc.).

**Phase 1** (complete): basic 8×8 rendering, pattern display, color cycling.
**Phase 2** (implemented, hardware test pending): asyncio-based cooperative
multitasking with cancellation-token counter, two-tier API (sync rendering +
async MakeCode-compatible methods), Image class with scrolling, font rendering
via `adafruit_bitmap_font`, 40 hand-designed 8×8 icons, 8 arrows, unified
color/palette parameter. Full design in the Phase 2 plan file.

Restructure (Tier 1 tests): the library now lives in a package
(`lib/display/`) split into `_constants` / `bitmap_codec` / `geometry` /
`icons` / `core` sub-modules plus `__init__.py` re-exports. User-facing
imports (`from display import display, Icons, RED, ...`) are
unchanged in shape; Phase 2 renamed `IconNames` / `ArrowNames` -> `Icons` / `Arrows`
and the members are now `Image` instances rather than integer slot indices.

---

## 3. Hardware

### 3.1 MCU board — YD-RP2040

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

### 3.2 On-board peripherals

| Peripheral | GPIO | `board` alias | Notes |
|------------|------|---------------|-------|
| Green LED | GP25 | `board.LED` | Always available; active high |
| WS2812 RGB LED | GP23 | `board.NEOPIXEL` | **Requires solder jumper** to be bridged; not functional by default |
| USR button | GP24 | `board.BUTTON` | Active low; internal pull-up available |

**Important**: The firmware for `vcc_gnd_yd_rp2040` maps on-board
peripherals to aliases (`board.LED`, `board.NEOPIXEL`, `board.BUTTON`).
Direct `board.GP23`/`board.GP24`/`board.GP25` names are **not** available
for these pins. Use the aliases.

### 3.3 LED matrix

| Property | Value |
|----------|-------|
| Type | WS2812b (NeoPixel) |
| Size | 8 × 8 (64 pixels) |
| Wiring layout | Progressive left-to-right, bottom-up (index 0 = bottom-left) |
| Data pin | GP0 |
| Voltage | 5 V (requires 3.3 V → 5 V level shifter on data line) |

### 3.4 Wiring diagram

```
YD-RP2040 GP0 ──► Level-Shifter IN   (3.3 V side)
Level-Shifter OUT ──► WS2812b DIN    (5 V side)
5 V PSU (+)  ──► WS2812b VCC  +  Level-Shifter high-V VCC
GND          ──► all GNDs (board, shifter, LED matrix, PSU)
```

### 3.5 RP2040 hardware resource allocation

| Resource | Used by | Details |
|----------|---------|---------|
| PIO SM (1 of 8) | `neopixel` library | Drives WS2812b data on GP0 via PIO; does NOT consume SPI |
| SPI0 | Free | Available for future peripherals |
| SPI1 | Free | Available for future peripherals |

---

## 4. Software stack

### 4.1 CircuitPython 10.1.4 built-in modules (subset)

Key built-ins on this board: `board`, `digitalio`, `analogio`, `busio`,
`neopixel_write`, `rainbowio`, `displayio`, `fontio`, `time`, `os`, `gc`,
`json`, `math`, `random`, `struct`, `usb_cdc`, `microcontroller`, `rp2pio`.

Phase 2 uses `rainbowio` (for `colorwheel`), `displayio` and `fontio` (used internally by `adafruit_bitmap_font`).

Full list: see `docs/CircuitPython Notes.md` in the project.

### 4.2 External libraries (installed via circup)

| Library | File / Dir | Purpose | Phase |
|---------|------------|---------|-------|
| `neopixel` | `neopixel.mpy` | High-level NeoPixel driver | 1 |
| `adafruit_pixelbuf` | `adafruit_pixelbuf.mpy` | Pixel buffer base class (neopixel dependency) | 1 |
| `asyncio` | `asyncio/` | Cooperative multitasking | 2 |
| `adafruit_ticks` | `adafruit_ticks.mpy` | Tick-based timing for asyncio | 2 |
| `adafruit_bitmap_font` | `adafruit_bitmap_font/` | Font loading from PCF files | 2 |
| `font_free_mono_8` | `display/font_free_mono_8/` | 8-pixel monospace PCF font (bundled inside project package) | 2 |

Install commands:
```bash
# Phase 1 (already done)
circup install neopixel

# Phase 2 (pending)
circup bundle-add adafruit/circuitpython-fonts   # one-time: register fonts bundle
circup install asyncio adafruit_bitmap_font font_free_mono_8
```

Note: `circup` is in the project venv at `/Users/alex/Development/PythonVEs/CircuitPython_3.13_VsCode/bin/circup`. Use flags `--path <project-dir> --board-id vcc_gnd_yd_rp2040 --cpy-version 10.1.4` when not auto-detected.

### 4.3 Project library — `lib/display/` package

Core deliverable. Phase 2 is implemented (hardware test pending). The library is structured as a package; see `lib/display/README.md` for architecture and design rationale.

**Sub-modules** (each owns a single responsibility):

| Module | Responsibility |
|--------|----------------|
| `_constants.py` | `WIDTH` (8), `HEIGHT` (8), `NUM_PIXELS` (64), `_MAX_HEIGHT_PER_COLUMN_BYTE` (8), full color palette. Pure -- no hardware imports. |
| `bitmap_codec.py` | `pattern_to_colmajor` / `colmajor_to_pattern` design-time helpers. |
| `geometry.py` | Pure `build_lut(rotation)` returning a fresh `bytearray` + `xy_to_index(x, y, lut)`. |
| `icons.py` | `ICONS`, `ARROWS` bytes + ordered name tuples `ICON_NAMES` / `ARROW_NAMES` (kept together so slot ordering cannot drift). |
| `core.py` | `Display` + `Image` runtime, NeoPixel buffer, LUT, font, `PIXEL_PIN` (`board.GP0`), `BRIGHTNESS` (0.05). Only module importing `board` / `neopixel`. |
| `__init__.py` | Public-API re-exports. Core import is guarded by a `board` presence check so host-side tests can load pure sub-modules without a device. |

**Color palette**: Adafruit LED Animation standard colors (`RED`, `YELLOW`, `ORANGE`, `GREEN`, `TEAL`, `CYAN`, `BLUE`, `PURPLE`, `MAGENTA`, `WHITE`, `BLACK`, `GOLD`, `PINK`, `AQUA`, `JADE`, `AMBER`, `OLD_LACE`) plus LED-tuned extras (`GRAY`, `DARKSLATEBLUE`, `YELLOWGREEN`, `DEEPPINK`). `OFF` = alias for `BLACK`. Re-exports `colorwheel` from `rainbowio`.

**Coordinate mapping**: A pre-computed 64-byte lookup table (LUT) bakes rotation (0/90/180/270) and bottom-up progressive wiring into a single array: `LUT[x * HEIGHT + y]` yields the NeoPixel strip index for logical pixel `(x, y)` where `x` = column (0 = left) and `y` = row (0 = top). `set_rotation(degrees)` mutates the LUT in place so references stay valid.

**Cancellation-token counter**: A per-instance sequence counter `Display._seq` enables cooperative multitasking. `_acquire()` increments `_seq` and returns the new value as a token. `_is_cancelled(token)` returns `True` if `_seq` has advanced past that token, meaning a newer operation has taken control.

**Two-tier API**:
- **Tier 1 (sync)**: Immediate rendering to NeoPixel buffer. `render_pattern`, `render_icon`, `render_arrow`, `clear_screen`, `set_pixel`, `fill`, `set_brightness`, `set_rotation`, `get_pixel`. Display-mutating methods call `_acquire()` to cancel ongoing Tier 2 animations.
- **Tier 2 (async)**: MakeCode-compatible convenience methods with `await`. `show_leds`, `show_icon`, `show_arrow`, `show_string`, `show_number`, `pause`. Use `await asyncio.sleep()` and check `_is_cancelled(token)` between animation frames.

**Bitmap format — column-major bytes**: Monochrome bitmaps (icons, arrows, font glyphs, mono `Image` data) are stored as one byte per column, where bit N of a column byte indicates whether row N is lit. This layout enables efficient horizontal scrolling by iterating contiguous column bytes. Icons use 40 × 8 bytes in `ICONS`; arrows use 8 × 8 bytes in `ARROWS`. Lookup: `ICONS[icon_id * WIDTH : (icon_id + 1) * WIDTH]`.

**Image class**: Column-major bytes (mono) or per-pixel tuple array (multi-color). `from_pattern()`, `recolor()`, async `show_image()` / `scroll_image()`. Module-level factories: `create_image()`, `create_big_image()`.

**Parameter convention**: `color` is the single kwarg across the API; it accepts either an RGB tuple (single-color) or a palette `dict` (multi-color, for pattern-based methods). Time intervals are named with an explicit unit suffix, e.g. `interval_ms`, `pause(ms)`.

**Coordinate system**: Origin (0, 0) at top-left. x → right, y → down.

**Pattern string format**: 8 rows of 8 characters (`#` = ON, `.` = OFF, or palette chars when using a dict). Spaces are stripped. Missing rows/columns filled with OFF.

---

## 5. Project file manifest

```
2026-04_Exp14_DisplayLibrary_CPy_on_RPi-Pico-2040/
├── .circuitpyignore              Sync exclusions for CircuitPythonSync
├── .vscode/
│   ├── tasks.json                Serial monitor tasks (pyserial-miniterm)
│   ├── settings.json             Python venv path for CircuitPythonSync
│   └── cpfiles.txt               File copy manifest for CircuitPythonSync
├── code.py                       Demo script (Phase 2 asyncio showcase by default)
├── code_demo_phase2.py           Alternative Phase 2 demo
├── code_determine_LED-wiring.py  One-off wiring discovery script
├── requirements-dev.txt          Host-side test dependencies (Tier 1: pytest only)
├── lib/
│   ├── display/                  MakeCode-style display library (package)
│   │   ├── __init__.py           Public-API re-exports (guarded core import)
│   │   ├── _constants.py         Dimensions + encoding limit + colors (pure)
│   │   ├── bitmap_codec.py       Design-time ASCII art <-> column-major bytes
│   │   ├── geometry.py           Pure build_lut / xy_to_index
│   │   ├── icons.py              ICONS, ARROWS, ICON_NAMES, ARROW_NAMES
│   │   ├── core.py               Display + Image runtime, NeoPixel buffer, font
│   │   ├── font_free_mono_8/     PCF font (ships with the package)
│   │   └── README.md             Package architecture + design rationale
│   ├── README                    Library folder documentation
│   ├── neopixel.mpy              (external, installed via circup)
│   ├── adafruit_pixelbuf.mpy     (external, installed via circup)
│   ├── asyncio/                  (external, Phase 2, installed via circup)
│   ├── adafruit_ticks.mpy        (external, Phase 2, installed via circup)
│   └── adafruit_bitmap_font/     (external, Phase 2, installed via circup)
├── tests/                        Tier 1 pytest suite (host-side, no stubs)
│   ├── __init__.py
│   ├── conftest.py               sys.path setup (prepends lib/)
│   ├── test_pattern_codec.py
│   ├── test_geometry.py
│   └── test_icons_data.py
├── docs/
│   └── CircuitPython Notes.md    Built-in module listing (user-maintained)
├── CONTEXT_HANDOFF.md            This file
└── README.md                     Human-readable project documentation
```

---

## 6. Development environment

### 6.1 Host tools

| Tool | Location | Purpose |
|------|----------|---------|
| Python venv | `/Users/alex/Development/PythonVEs/CircuitPython_3.13_VsCode/` | Hosts `circup`, `pyserial-miniterm` |
| VS Code | Cursor IDE | Editor with CircuitPythonSync extension |
| `circup` | In venv | Installs CircuitPython libraries |
| `pyserial-miniterm` | In venv | Serial terminal (REPL access) |

### 6.2 Serial monitor

VS Code task "Serial Monitor (miniterm)" auto-detects the board's
`/dev/tty.usbmodem*` port at 115200 baud. Exit with `Ctrl+]`.

In the serial monitor:
- `Ctrl+C` — interrupt running code, drop into REPL
- `Ctrl+D` — soft-reboot, re-run `code.py`

### 6.3 File sync

CircuitPythonSync reads `.vscode/cpfiles.txt` and copies listed files
to the CIRCUITPY drive. Currently syncs: `code.py`.

The `lib/` folder (including the `display/` package and `.mpy` files)
is synced by CircuitPythonSync separately (it manages the `lib/`
folder automatically).

---

## 7. Milestone status

### Phase 1 — Basic 8×8 display library

| Task | Status |
|------|--------|
| Project setup (.vscode, .circuitpyignore, lib scaffold) | DONE |
| `lib/display.py` — 8×8 MakeCode-style library | DONE (superseded by package in Tier 1 restructure) |
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
| Refactor display library: LUT, cancellation counter, Tier 1/2 API split, color system | DONE |
| Implement `Image` class with column-major storage, `recolor()`, async show/scroll | DONE |
| Integrate `adafruit_bitmap_font` for text rendering (`_glyph_columns`) | DONE |
| Icon + arrow bitmap data (40 icons + 8 arrows, column-major bytes) | DONE |
| Implement async `show_string` / `show_number` with font scrolling | DONE |
| Implement async `show_icon` / `show_arrow` | DONE |
| Update `code.py` demo for Phase 2 (asyncio-based) | DONE |
| Update documentation (CONTEXT_HANDOFF.md, README.md) | DONE |
| Hardware test on YD-RP2040 | PENDING |

### Tier 1 — Package restructure + host-side tests

Full design documented in `tier-1-tests-setup_813976c6.plan.md`.

| Task | Status |
|------|--------|
| Restructure `lib/display.py` + `lib/display_icons.py` into `lib/display/` package (six sub-modules) | DONE |
| Move `font_free_mono_8/` into the package; fix font path to `__file__`-relative | DONE |
| CONTEXT_HANDOFF Section 0 additions + Testing-strategy section | DONE |
| Package `README.md` (developer-facing architecture doc) | DONE |
| `tests/` scaffold + conftest + `requirements-dev.txt` (pytest only) | DONE |
| `test_pattern_codec.py` round-trip + error paths | DONE |
| `test_geometry.py` LUT corner mappings for all four rotations | DONE |
| `test_icons_data.py` shape + byte-range + enum-count checks | DONE |
| Verify `pytest tests/` green on CPython | PENDING |
| Verify `code.py` / `code_demo_phase2.py` still run on device | PENDING |

---

## 8. Known issues and notes

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
