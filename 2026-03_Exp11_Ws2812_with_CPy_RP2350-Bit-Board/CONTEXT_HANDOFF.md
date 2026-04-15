# Experiment 11 -- Context Handoff for AI Thread

> This file persists all context for spinning up a new Cursor AI thread.
> Written 2026-03-11. Read this first before doing anything.

---

## 1. What this project is

Driving LED matrices from an RP2350 microcontroller running CircuitPython.
Three milestones, executed sequentially:

| # | Goal | Status |
|---|------|--------|
| 1 | Verify GPIO wires (de-soldered LED pads) | **DONE** -- all 13 pins tested with multimeter |
| 2 | Drive generic WS2812b 5x5 matrix (25 NeoPixels) | **NEXT** -- code written, not yet wired/tested |
| 3 | Drive Adafruit DotStar FeatherWing 6x12 (72 APA102 LEDs) | Pending -- code written, not yet wired/tested |

`code.py` on the board currently contains the **Milestone 3 DotStar test** (was
swapped in during testing). To go back to Milestone 2, copy `milestone2_ws2812b_5x5.py`
content into `code.py`, or use the `cpfiles.txt` manifest (see section 7).

---

## 2. Hardware

| Item | Detail |
|------|--------|
| MCU | **RP2350 bit board** -- RP2350A + 4 MB flash, BBC micro:bit V2 form factor |
| Firmware | **CircuitPython 10.1.3** for Raspberry Pi Pico 2 |
| Board ID | `raspberry_pi_pico2` (used this firmware image since no dedicated RP2350-bit-board image exists) |
| LED matrix 1 | Generic **WS2812b 5x5** (25 pixels, single data wire) |
| LED matrix 2 | **Adafruit DotStar FeatherWing 6x12** (72 APA102 pixels, SPI clock + data) |
| Level shifter | "Super-mini TTL Signal LED Amplifier SPI Repeater" (3pin/4pin, DC 5-24V) |
| Power | 5V / 2A USB PSU for LEDs; RP2350 powered separately via its own USB port |
| Schematics | `/Volumes/Alexs_Files/Isana/MicroBit/MCU alternatives/RP2350-bit-Board Schematics.pdf` |

### Board modifications

The original 5x5 **Charlieplexed LED matrix was de-soldered** from the RP2350 bit board.
Breadboard-friendly wires were soldered to the pads. These connect to 10 GPIOs through
1K series resistors (R1-R5_LED) still on the board. The 1K resistors make these GPIOs
unsuitable for high-speed LED data signals.

---

## 3. GPIO pin map (hardware-verified)

### Buttons (do NOT use as outputs)

| Button | GPIO | Edge pad |
|--------|------|----------|
| A | GP0 | 6 |
| B | GP1 | 12 |

**Critical:** GP0/GP1 are **not** on the micro:bit large pads. The RP2350 bit board's
GPIO numbering does NOT match micro:bit pad numbering.

### Former LED-matrix pins (1K series resistor, wires attached)

| Function | GPIOs |
|----------|-------|
| Column drivers | GP2, GP3, GP4, GP5, GP25 |
| Row drivers | GP7, GP8, GP9, GP21, GP22 |

### Pins used for WS2812b / DotStar

| Signal | GPIO | Edge pad | Note |
|--------|------|----------|------|
| WS2812b data | **GP6** | Small pad 3 | Hardware-verified |
| DotStar clock | **GP10** | Small pad 13 | SPI1_SCK (hardware SPI) |
| DotStar data | **GP11** | Small pad 15 | SPI1_MOSI (hardware SPI) |

All three are small pads on the micro:bit edge connector (not large pads).

---

## 4. Level-shifter wiring note

The "Super-mini TTL Signal LED Amplifier" has both a low-voltage (input) and
high-voltage (output) VCC pin. Measured behaviour:

- **Connect 5V to the high-voltage VCC (output side) only.**
- **Do NOT connect the low-voltage VCC (input side) to 3.3V.**
  The input side self-biases to 5V from the output rail.
  Connecting 3.3V would fight this and potentially overload the MCU's 3.3V regulator.
- Common GND across MCU, level shifter, LEDs, and PSU is essential.

---

## 5. Workspace & IDE setup

| Item | Path / value |
|------|-------------|
| Project folder | `/Users/alex/Development/VsCode/CircuitPython/2026-03_Exp11_Ws2812_with_CPy_RP2350-Bit-Board` |
| Cursor workspace file | `/Users/alex/Development/Cursor Workspaces/circuitpython.code-workspace` |
| Python venv | `/Users/alex/Development/PythonVEs/CircuitPython_3.13_VsCode/bin/python` |
| circup | `/Users/alex/Development/PythonVEs/CircuitPython_3.13_VsCode/bin/circup` (v3.0.1) |
| CircuitPythonSync ext | `padgettholdings.circuitpythonsync` v2.2.1 |
| Board drive | `/Volumes/CIRCUITPY` (when plugged in) |
| Serial port | `/dev/tty.usbmodem112401` (may change on replug) |
| Baud rate | 115200 |

### Workspace folders

The `.code-workspace` file includes:
1. **Exp11** (active) -- the RP2350 bit board project
2. **Exp09** (reference only) -- old BPI-Bit-S2 LED matrix project, do NOT upload from it

CircuitPythonSync operates on whichever folder has the active editor tab.
**Always ensure an Exp11 file is focused before "Copy Files/Libs to Board".**

### Serial monitor

The Microsoft Serial Monitor extension is **broken in Cursor**. Instead, a
`.vscode/tasks.json` task launches `pyserial-miniterm` in the integrated terminal:

- **Connect:** `Cmd+Shift+P` → `Tasks: Run Task` → `Serial Monitor (miniterm)`
- **Exit miniterm:** `Ctrl+]`
- **REPL:** `Ctrl-C` (stop program) / `Ctrl-D` (restart program)
- **Kill stuck session:** `Cmd+Shift+P` → `Tasks: Run Task` → `Serial Monitor: disconnect`

### CircuitPythonSync file copy manifest

`.vscode/cpfiles.txt` controls which file gets uploaded as `code.py`:
```
code.py                                      ← active (uploads code.py as-is)
# milestone2_ws2812b_5x5.py -> /code.py     ← uncomment to upload M2 as code.py
# milestone3_dotstar_6x12.py -> /code.py    ← uncomment to upload M3 as code.py
```

---

## 6. Libraries installed in `lib/`

All `.mpy` files, CircuitPython 10.x bundle (tag 20260305):

| File | Purpose |
|------|---------|
| `neopixel.mpy` | WS2812b driver (Milestone 2) |
| `adafruit_dotstar.mpy` | APA102/DotStar driver (Milestone 3) |
| `adafruit_pixelbuf.mpy` | Pixel buffer base (dep of both; also built into firmware) |
| `adafruit_ticks.mpy` | Rollover-safe ms ticks for non-blocking timing |
| `adafruit_led_animation/` | Pre-built animation library (comet, rainbow, sparkle, etc.) |

Install command (works offline, no board needed):
```bash
/Users/alex/Development/PythonVEs/CircuitPython_3.13_VsCode/bin/circup \
  --path /Users/alex/Development/VsCode/CircuitPython/2026-03_Exp11_Ws2812_with_CPy_RP2350-Bit-Board \
  --board-id raspberry_pi_pico2 --cpy-version 10.1.3 \
  install <library_name>
```

### Built into firmware (no lib/ needed)

`neopixel_write`, `adafruit_pixelbuf`, `adafruit_bus_device`, `_asyncio`,
`digitalio`, `analogio`, `busio`, `board`, `time`, `rp2pio`, `nvm`, `rotaryio`,
`pwmio`, `pulseio`, and many more. Full list at
https://circuitpython.org/board/raspberry_pi_pico2/

`asyncio` is fully built-in for cooperative multitasking. No lib/ copy needed.

---

## 7. Project files

| File | Purpose | Synced to board? |
|------|---------|-----------------|
| `code.py` | Active script on board (currently M3 DotStar test) | Yes |
| `milestone1_test_pins.py` | M1: GPIO wire test (archived) | No (.circuitpyignore) |
| `milestone2_ws2812b_5x5.py` | M2: WS2812b 5x5 test | No (.circuitpyignore) |
| `milestone3_dotstar_6x12.py` | M3: DotStar 6x12 test | No (.circuitpyignore) |
| `README.md` | Project documentation | No (.circuitpyignore) |
| `lib/` | CircuitPython libraries (.mpy) | Yes (via "Copy Libs") |
| `.circuitpyignore` | Controls CircuitPythonSync exclusions | N/A |
| `.vscode/cpfiles.txt` | File copy manifest for CircuitPythonSync | N/A |
| `.vscode/tasks.json` | Serial monitor task (miniterm) | N/A |
| `.vscode/settings.json` | Folder-level settings (minimal) | N/A |
| `libArchive/` | Bundle metadata + libstubs for intellisense | N/A |
| `stubArchive/` | CP stubs metadata | N/A |

---

## 8. Milestone 2 wiring (WS2812b -- next step)

```
RP2350 GP6  ──► Level-Shifter DIN            (signal in, 3.3V; edge pad 3)
Level-Shifter DOUT ──► WS2812b DIN           (signal out, 5V)
5V PSU (+)  ──► WS2812b VCC + Level-Shifter high-voltage VCC (output side only)
GND         ──► RP2350 GND + Shifter GND + WS2812b GND + PSU GND
```

Do NOT connect Level-Shifter low-voltage VCC to 3.3V (self-biases from output side).

The `milestone2_ws2812b_5x5.py` script starts at 5% brightness and includes:
- `test_first_five()` -- lights pixels 0-4 to identify wiring direction
- `test_xy_grid()` -- walks every (col,row) to verify coordinate mapping
- `test_fill_colors()` -- full-matrix colour sweep
- `test_patterns()` -- heart, cross, frame, checker in various colours
- `test_brightness_ramp()` -- fades brightness 0→30%→0

Config flag `SERPENTINE = True` controls zigzag vs sequential pixel mapping.
Adjust after running `test_first_five()`.

---

## 9. Milestone 3 wiring (DotStar -- after M2)

**Option A (direct 3.3V, try first):**
```
RP2350 GP11 ──► DotStar DI  (data,  SPI1_MOSI, edge pad 15)
RP2350 GP10 ──► DotStar CI  (clock, SPI1_SCK,  edge pad 13)
5V PSU (+)  ──► DotStar VCC
GND         ──► all GNDs
```

**Option B (level-shifted, if flicker):**
```
RP2350 GP11 ──► Amplifier DAT-IN  → DAT-OUT ──► DotStar DI
RP2350 GP10 ──► Amplifier CLK-IN  → CLK-OUT ──► DotStar CI
5V PSU      ──► Amplifier high-voltage VCC (output side only) + DotStar VCC
GND         ──► all GNDs
```

Uses hardware SPI1 via `busio.SPI(clock=board.GP10, MOSI=board.GP11)`.
APA102 logic-high threshold is 0.7×VCC = 3.5V at 5V supply; 3.3V is marginal.
Option A often works in practice.

---

## 10. Known issues & gotchas

- **Serial port name changes on replug.** Run `ls /dev/tty.usbmodem*` to find current name.
- **CircuitPythonSync copies from the active folder.** If Exp09 file is focused, it uploads Exp09's lib. Always focus an Exp11 file first.
- **Microsoft Serial Monitor extension is broken in Cursor.** Use the miniterm task instead.
- **`code.py` currently contains M3 DotStar code.** To return to M2, copy `milestone2_ws2812b_5x5.py` content into `code.py`.
- **Board lib may need manual sync.** If wrong libs end up on the board, clean via Finder or terminal: `ls /Volumes/CIRCUITPY/lib/` and remove stale files.
- **2A PSU budget.** 5x5 WS2812b at full white = ~1.5A (OK). 6x12 DotStar at full white = ~4.3A (exceeds PSU). Keep brightness low.

---

## 11. Reference: previous experiment

Exp09 (`2026-02_Exp09_BPI-Bit-S2-LED-Matrix`) used a **BPI-Bit-S2** (ESP32-S2)
with a built-in 5x5 WS2812b matrix on `board.NEOPIXEL` (GPIO18). It has a custom
`display_v0.py` driver and `microbit.py` shim. Different board, different GPIO map,
different firmware. Do not reuse its code directly -- only for reference patterns.
