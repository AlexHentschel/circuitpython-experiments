# Experiment 13 -- Context Handoff for AI Thread

> This file persists all context for spinning up a new Cursor AI thread.
> Written 2026-03-26. Read this first before doing anything.

---

## 1. What this project is

Driving a WS2812b LED matrix from a YD-RP2040 microcontroller running CircuitPython.
Two milestones, executed sequentially:

| # | Goal | Status |
|---|------|--------|
| 1 | Verify board & GPIO pins (on-board LED, button, external GPIOs) | **DONE** -- all phases passed |
| 2 | Drive generic WS2812b 5x5 matrix (25 NeoPixels) via GP0 | **NEXT** -- code written, not yet wired/tested |

`code.py` on the board currently contains the **Milestone 1 GPIO test**.
To switch milestones, copy the appropriate milestone script into `code.py`,
or edit the `.vscode/cpfiles.txt` manifest.

---

## 2. Hardware

| Item | Detail |
|------|--------|
| MCU | **YD-RP2040** by VCC-GND Studio |
| Chip | RP2040 -- dual-core Arm Cortex-M0+ @ 133 MHz, 264 KB SRAM |
| Flash | 16 MB (W25Q128) |
| USB | Type-C |
| Firmware | **CircuitPython 10.1.4** for `vcc_gnd_yd_rp2040` |
| Board ID | `vcc_gnd_yd_rp2040` |
| Bootloader drive | `RPI-RP2` (appears when holding BOOT and pressing RESET) |
| Firmware download | https://circuitpython.org/board/vcc_gnd_yd_rp2040/ |
| GitHub (board info) | https://github.com/initdc/YD-RP2040 |
| LED matrix | Generic **WS2812b 5x5** (25 pixels, single data wire) |
| Level shifter | "Super-mini TTL Signal LED Amplifier SPI Repeater" (3pin/4pin, DC 5-24V) |
| Power | 5V / 2A USB PSU for LEDs; YD-RP2040 powered separately via its own USB-C port |
| Pinout diagram | `docs/RP-Pico clone YD-2040 Pinout.jpg` |

### YD-RP2040 board extras (vs standard Raspberry Pi Pico)

| Feature | board.* name | GPIO | Detail |
|---------|-------------|------|--------|
| On-board green LED | `board.LED` | GP25 | Works out of the box. **Do not use `board.GP25`** (not defined) |
| On-board WS2812 RGB LED | `board.NEOPIXEL` / `board.RGB` | GP23 | **Requires solder jumper** (NOT yet soldered) |
| USR button | `board.BUTTON` | GP24 | Active low. **Do not use `board.GP24`** (not defined) |
| Reset button | -- | -- | Physical button (BOOT + RESET enters bootloader) |
| PWR LED | -- | -- | Always-on power indicator |

### Flashing CircuitPython

1. Connect the board via USB-C.
2. Hold **BOOT**, press and release **RESET**, then release **BOOT**.
3. A USB drive named `RPI-RP2` appears.
4. Drag and drop the `.uf2` file onto the drive. The board reboots automatically.
5. A `CIRCUITPY` drive should appear.

See `docs/CircuitPython Notes.md` for additional firmware details and the
complete list of built-in modules.

---

## 3. GPIO pin map

### RP2040 hardware resource allocation

The RP2040 has 2 SPI buses and 8 PIO state machines (2 PIO blocks x 4 SM each).

| Resource | Used by | Pins | Note |
|----------|---------|------|------|
| **PIO** (1 state machine) | WS2812b NeoPixel | GP0 | `neopixel` / `neopixel_write` uses PIO, NOT SPI |
| **PIO** (7 remaining) | *Free* | -- | Available for additional NeoPixel strips, custom protocols, etc. |
| **SPI0** | *Free* | -- | Available for SD card, display, sensors, etc. |
| **SPI1** | *Free* | -- | Available for additional peripherals |

**Key insight:** On the RP2040, NeoPixel (WS2812b) data is driven via a PIO
state machine, not SPI. This means NeoPixel strips can coexist with both SPI
buses being used for other peripherals. All resources can operate simultaneously
without conflict.

### Pins used for external LED matrix

| Signal | GPIO | Physical pin | HW resource | Note |
|--------|------|-------------|-------------|------|
| WS2812b data | **GP0** | Pin 1 (left header, top) | PIO state machine | NeoPixel data line to level shifter |

### On-board peripherals

| Peripheral | board.* name | GPIO | Note |
|------------|-------------|------|------|
| Green LED | `board.LED` | GP25 | Works immediately. **GP25 is NOT in `dir(board)`** -- must use `board.LED` |
| WS2812 RGB LED | `board.NEOPIXEL` (or `board.RGB`) | GP23 | Solder jumper must be closed (currently open). **GP23 exists in `dir(board)` but `board.NEOPIXEL` is the canonical name** |
| USR button | `board.BUTTON` | GP24 | Active low with pull-up, works immediately. **GP24 is NOT in `dir(board)`** -- must use `board.BUTTON` |

**CRITICAL:** The `vcc_gnd_yd_rp2040` firmware does not expose GP24 or GP25 as
named pins. Code using `board.GP25` or `board.GP24` will crash with
`AttributeError: 'module' object has no attribute 'GP25'`. Always use the
aliases above.

### Additional GPIOs tested in Milestone 1

| GPIO | Purpose in M1 |
|------|---------------|
| GP2 | General GPIO verification |
| GP3 | General GPIO verification |
| GP4 | General GPIO verification |
| GP5 | General GPIO verification |

All GPIOs on the YD-RP2040 (GP0-GP22, GP25-GP28) are available for use.
GP23 and GP24 are used by the on-board RGB LED and USR button respectively.
GP25 is the on-board green LED. GP26-GP28 are also ADC-capable.

---

## 4. Level-shifter wiring note

The "Super-mini TTL Signal LED Amplifier" has both a low-voltage (input) and
high-voltage (output) VCC pin. Required wiring:

- **Connect 5V to the high-voltage VCC (output side) only.**
- **Do NOT connect the low-voltage VCC (input side) to 3.3V.**
  The input side self-biases to 5V from the output rail.
  Connecting 3.3V would fight this and potentially overload the MCU's 3.3V regulator.
- Common GND across MCU, level shifter, LEDs, and PSU is essential.

---

## 5. Workspace & IDE setup

| Item | Path / value |
|------|-------------|
| Project folder | `/Users/alex/Development/VsCode/CircuitPython/2026-03_Exp13_Ws2812_CPy_on_RPi-Pico-2040` |
| Cursor workspace file | `/Users/alex/Development/Cursor Workspaces/circuitpython.code-workspace` |
| Python venv | `/Users/alex/Development/PythonVEs/CircuitPython_3.13_VsCode/bin/python` |
| circup | `/Users/alex/Development/PythonVEs/CircuitPython_3.13_VsCode/bin/circup` |
| CircuitPythonSync ext | `padgettholdings.circuitpythonsync` |
| Board drive | `/Volumes/CIRCUITPY` (when plugged in) |
| Serial port | `/dev/tty.usbmodem*` (changes on replug) |
| Baud rate | 115200 |

### Serial monitor

The Microsoft Serial Monitor extension is **broken in Cursor**. Instead, a
`.vscode/tasks.json` task launches `pyserial-miniterm` in the integrated terminal:

- **Connect:** `Cmd+Shift+P` -> `Tasks: Run Task` -> `Serial Monitor (miniterm)`
- **Exit miniterm:** `Ctrl+]`
- **REPL:** `Ctrl-C` (stop program) / `Ctrl-D` (restart program)
- **Kill stuck session:** `Cmd+Shift+P` -> `Tasks: Run Task` -> `Serial Monitor: disconnect`

### CircuitPythonSync file copy manifest

`.vscode/cpfiles.txt` controls which file gets uploaded as `code.py`:
```
code.py                                      <- active (uploads code.py as-is)
# milestone2_ws2812b_5x5.py -> /code.py     <- uncomment to upload M2 as code.py
```

---

## 6. Libraries

### Built into CircuitPython 10.1.4 firmware (no lib/ install needed)

Full list documented in `docs/CircuitPython Notes.md`. Key modules for this project:

| Module | Purpose |
|--------|---------|
| `neopixel_write` | Low-level NeoPixel driver (Milestone 1 on-board RGB test) |
| `adafruit_pixelbuf` | Pixel buffer base class (dependency of neopixel lib) |
| `adafruit_bus_device` | I2C/SPI device helpers |
| `digitalio` | GPIO control (Milestone 1 pin test) |
| `_pixelmap` | Pixel mapping support |
| `rp2pio` | RP2040 PIO state machines |
| `_asyncio` | Cooperative multitasking |

### External libs needed in lib/ (install via circup)

| File | Purpose | Milestone |
|------|---------|-----------|
| `neopixel.mpy` | High-level WS2812b driver | 2 |
| `adafruit_pixelbuf.mpy` | Pixel buffer base (pulled as dependency, also built-in) | 2 |

Install command (works offline, no board needed):
```bash
/Users/alex/Development/PythonVEs/CircuitPython_3.13_VsCode/bin/circup \
  --path /Users/alex/Development/VsCode/CircuitPython/2026-03_Exp13_Ws2812_CPy_on_RPi-Pico-2040 \
  --board-id vcc_gnd_yd_rp2040 --cpy-version 10.1.4 \
  install <library_name>
```

Milestone 1 uses **only built-in modules**. No external library installation is
needed until Milestone 2.

---

## 7. Project files

| File | Purpose | Synced to board? |
|------|---------|-----------------|
| `code.py` | Active script on board (currently M1 GPIO test) | Yes |
| `milestone1_test_pins.py` | M1: GPIO & board test (archived) | No (.circuitpyignore) |
| `milestone2_ws2812b_5x5.py` | M2: WS2812b 5x5 test | No (.circuitpyignore) |
| `README.md` | Project documentation | No (.circuitpyignore) |
| `CONTEXT_HANDOFF.md` | This file -- AI context | No (.circuitpyignore) |
| `docs/CircuitPython Notes.md` | Firmware install notes & built-in module list | No |
| `docs/RP-Pico clone YD-2040 Pinout.jpg` | Board pinout diagram | No |
| `lib/` | CircuitPython libraries (.mpy) | Yes (via "Copy Libs") |
| `.circuitpyignore` | Controls CircuitPythonSync exclusions | N/A |
| `.vscode/cpfiles.txt` | File copy manifest for CircuitPythonSync | N/A |
| `.vscode/tasks.json` | Serial monitor task (miniterm) | N/A |
| `.vscode/settings.json` | Folder-level settings (Python venv) | N/A |

---

## 8. Milestone 1 -- Board & GPIO Test

**Script:** `milestone1_test_pins.py` (currently in `code.py`)

No external wiring needed for on-board tests. The script runs five phases
in a loop:

1. **Phase 1 -- Blink GP25:** Toggles the on-board green LED 6 times (immediate
   visual confirmation that CircuitPython is running).

2. **Phase 2 -- RGB LED GP23:** Cycles red, green, blue, white, off via
   `neopixel_write`. Requires solder jumper to be closed to see the LED; the
   test is harmless without it.

3. **Phase 3 -- USR button GP24:** Reads button state for 5 seconds and prints
   press/release events to serial console.

4. **Phase 4 -- External GPIOs:** Drives GP0, GP10, GP11, GP2-GP5 HIGH for 3
   seconds each. Verify with multimeter (DC voltage between pin and GND) or
   breadboard LED + 330 Ohm resistor.

5. **Phase 5 -- All GPIOs HIGH:** All 7 external pins HIGH simultaneously for
   5 seconds (quick continuity check).

---

## 9. Milestone 2 -- WS2812b 5x5 Matrix

**Script:** `milestone2_ws2812b_5x5.py`

**Wiring:**
```
YD-RP2040 GP0 ──► Level-Shifter DIN             (signal in, 3.3V)
Level-Shifter DOUT ──► WS2812b DIN              (signal out, 5V)
5V PSU (+)  ──► WS2812b VCC + Level-Shifter high-voltage VCC (output side only)
GND         ──► YD-RP2040 GND + Shifter GND + WS2812b GND + PSU GND
```

Do NOT connect Level-Shifter low-voltage VCC to 3.3V (self-biases from output side).

**Configuration:**
- `PIXEL_PIN = board.GP0`
- `NUM_PIXELS = 25` (5x5)
- `BRIGHTNESS = 0.05`
- `SERPENTINE = True` (adjust after running `test_first_five()`)

**Test routines included:**
- `test_first_five()` -- lights pixels 0-4 to identify wiring direction
- `test_xy_grid()` -- walks every (col,row) to verify coordinate mapping
- `test_fill_colors()` -- full-matrix colour sweep
- `test_patterns()` -- heart, cross, frame, checker in various colours
- `test_brightness_ramp()` -- fades brightness 0 -> 30% -> 0

**Required library:** `neopixel` (install via circup before running).

---

## 10. Known issues & gotchas

- **GP23 solder jumper is NOT closed.** The on-board WS2812 RGB LED will not
  light up until the jumper on the YD-RP2040 board is soldered shut.
- **Serial port name changes on replug.** Run `ls /dev/tty.usbmodem*` to find
  the current name.
- **Microsoft Serial Monitor extension is broken in Cursor.** Use the miniterm
  task instead.
- **2A PSU budget.** 5x5 WS2812b at full white ~1.5A (OK). Keep brightness low.
- **Board lib may need manual sync.** If wrong libs end up on the board, clean
  via Finder or terminal: `ls /Volumes/CIRCUITPY/lib/` and remove stale files.
- **CircuitPythonSync copies from the active folder.** Always ensure an Exp13
  file is focused before "Copy Files/Libs to Board".
- **CircuitPython firmware flashing:** `docs/CircuitPython Notes.md` includes a
  WARNING that the standard BOOT+RESET procedure may not work as expected.
  Verify the procedure on your specific board.
