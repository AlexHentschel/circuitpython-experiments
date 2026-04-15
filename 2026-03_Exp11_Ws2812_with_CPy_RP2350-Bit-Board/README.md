# Experiment 11 -- WS2812b & DotStar via RP2350 Bit Board

Drive a WS2812b 5x5 matrix and an Adafruit DotStar FeatherWing 6x12 from an
RP2350 bit board (Pico 2 compatible) running CircuitPython.

## Hardware

| Item | Detail |
|------|--------|
| MCU board | **RP2350 bit board** (RP2350A + 4 MB flash, micro:bit V2 form factor) |
| Firmware | CircuitPython **10.1.3** for Raspberry Pi Pico 2 ([download](https://circuitpython.org/board/raspberry_pi_pico2/)) |
| LED matrix 1 | Generic **WS2812b 5x5** (25 NeoPixels) |
| LED matrix 2 | **Adafruit DotStar FeatherWing 6x12** (72 APA102 LEDs) |
| Level shifter | Super-mini TTL Signal LED Amplifier / SPI Repeater (3-pin / 4-pin, DC 5-24 V) |
| Power | 5 V / 2 A USB PSU for LEDs; RP2350 powered via its own USB port |
| IDE | Cursor + CircuitPythonSync extension (`padgettholdings`) |
| Python venv | `/Users/alex/Development/PythonVEs/CircuitPython_3.13_VsCode/bin/python` |


## GPIO Pin Map (from schematics)

The original 5x5 Charlieplexed LED matrix has been **de-soldered**.  Wires
were attached to the LED pads.

### Former LED-matrix pins (each has a 1 K series resistor on-board)

| Function | GPIO pins |
|----------|-----------|
| Column drivers (R1-R5\_LED) | GP2, GP3, GP4, GP5, GP25 |
| Row drivers | GP7, GP8, GP9, GP21, GP22 |

### On-board buttons (do NOT use as outputs)

| Button | GPIO | Micro:bit edge pad |
|--------|------|--------------------|
| Button A | GP0 | Small pad 6 |
| Button B | GP1 | Small pad 12 |

### Pins used for WS2812b / DotStar

| Signal | GPIO | Micro:bit edge pad | Note |
|--------|------|--------------------|------|
| WS2812b data | **GP6** | Small pad **3** | Free pin, hardware-verified |
| DotStar clock | **GP10** | Small pad 13 | SPI1_SCK -- hardware SPI |
| DotStar data | **GP11** | Small pad 15 | SPI1_MOSI -- hardware SPI |

> GP0 and GP1 **cannot** be used for LED signals -- they are permanently connected
> to Button A and Button B on the board. This is a micro:bit form-factor convention:
> the GPIO numbers (GP0, GP1) do **not** match the micro:bit pad numbers on the RP2350
> Bit Board. Edge pad 3 routes to GP6 (hardware-verified by testing).


## Milestones

### Milestone 1 -- GPIO Wire Test (`code.py`)

Verify that the wires soldered to the old LED pads carry a signal.

**How to run:**
1. Plug in the RP2350 via USB.  CircuitPythonSync uploads `code.py`.
2. Open a serial monitor (115 200 baud).
3. Use a multimeter (DC voltage, probe between wire and GND) or a
   breadboard LED + 330 Ω resistor.
4. The script cycles through each GPIO; the console prints which pin is HIGH.

### Milestone 2 -- WS2812b 5x5 Matrix (`milestone2_ws2812b_5x5.py`)

**Wiring:**
```
RP2350 GP6  ──► Level-Shifter DIN            (signal in, 3.3V; edge pad 3)
Level-Shifter DOUT ──► WS2812b DIN           (signal out, 5V)
5V PSU (+)  ──► WS2812b VCC + Level-Shifter high-voltage VCC (output side only)
GND         ──► RP2350 GND + Shifter GND + WS2812b GND + PSU GND
```

> **Level-shifter VCC note:** Connect 5V to the high-voltage (output) side only.
> Do NOT connect the low-voltage (input) side VCC to 3.3V -- it self-biases to 5V
> from the output side; Connecting might overload the MCU's power rail!
> **Common GND across all components is essential.**

**How to switch:**
```bash
cp milestone2_ws2812b_5x5.py code.py
```
CircuitPythonSync will re-sync.  Or copy-paste the file content into `code.py`.

**Library install (no board needed -- installs into workspace `lib/`):**
```bash
/Users/alex/Development/PythonVEs/CircuitPython_3.13_VsCode/bin/circup \
  --path /Users/alex/Development/VsCode/CircuitPython/2026-03_Exp11_Ws2812_with_CPy_RP2350-Bit-Board \
  --board-id raspberry_pi_pico2 --cpy-version 10.1.3 \
  install neopixel
```

### Milestone 3 -- DotStar FeatherWing 6x12 (`milestone3_dotstar_6x12.py`)

**Wiring (Option A -- direct 3.3 V, try first):**
```
RP2350 GP11 ──► DotStar DI  (data,  SPI1_MOSI, micro:bit edge pad 15)
RP2350 GP10 ──► DotStar CI  (clock, SPI1_SCK,  micro:bit edge pad 13)
5 V PSU (+) ──► DotStar VCC
GND         ──► all GNDs
```

**Wiring (Option B -- level-shifted, if Option A shows flicker):**
```
RP2350 GP11 ──► Amplifier DAT-IN  → DAT-OUT ──► DotStar DI
RP2350 GP10 ──► Amplifier CLK-IN  → CLK-OUT ──► DotStar CI
5V PSU      ──► Amplifier high-voltage VCC (output side only) + DotStar VCC
GND         ──► all GNDs
```
> Do NOT connect Amplifier low-voltage VCC (input side) to 3.3V -- self-biases
> to 5V from output side. Hardware SPI1 (GP10/GP11) preferred over software SPI.

**How to switch:**
```bash
cp milestone3_dotstar_6x12.py code.py
```

**Library install (no board needed -- installs into workspace `lib/`):**
```bash
/Users/alex/Development/PythonVEs/CircuitPython_3.13_VsCode/bin/circup \
  --path /Users/alex/Development/VsCode/CircuitPython/2026-03_Exp11_Ws2812_with_CPy_RP2350-Bit-Board \
  --board-id raspberry_pi_pico2 --cpy-version 10.1.3 \
  install adafruit_dotstar
```


## Library Installation via `circup`

Libraries live in the workspace `lib/` folder and are synced to the board by
the CircuitPythonSync extension ("Copy Libs to Board" command).

`circup` can install directly into the local workspace (no board needed):

```bash
CIRCUP=/Users/alex/Development/PythonVEs/CircuitPython_3.13_VsCode/bin/circup
PROJECT=/Users/alex/Development/VsCode/CircuitPython/2026-03_Exp11_Ws2812_with_CPy_RP2350-Bit-Board

# Milestone 2 -- neopixel (already installed)
$CIRCUP --path $PROJECT --board-id raspberry_pi_pico2 --cpy-version 10.1.3 install neopixel

# Milestone 3 -- adafruit_dotstar (already installed)
$CIRCUP --path $PROJECT --board-id raspberry_pi_pico2 --cpy-version 10.1.3 install adafruit_dotstar
```

Installed `.mpy` files in `lib/`:
- `neopixel.mpy` -- high-level NeoPixel (WS2812b) driver
- `adafruit_dotstar.mpy` -- DotStar (APA102) driver
- `adafruit_pixelbuf.mpy` -- shared pixel buffer base (dependency of both)

Alternatively, use CircuitPythonSync's built-in **"Install or Update Libraries
and Stubs"** + **"Select Libraries"** commands for full IDE integration
including intellisense stubs.

## Notes

- **Brightness** is set to 0.05 in both scripts.  At full white, a 5x5
  WS2812b matrix draws ~1.5 A; the 6x12 DotStar draws ~4.3 A.
  Stay conservative until power budget is verified.
- The 1 K series resistors on the former LED-matrix GPIOs make them
  unsuitable for high-speed LED data signals.  Use GP6 (pad 3),
  GP10 (pad 13), or GP11 (pad 15) instead -- all hardware-verified free pins.
- The `SERPENTINE` flag in each script controls how (x, y) maps to pixel
  index.  Run the `test_first_five()` / `test_sequential()` routine to
  determine your matrix's wiring direction and adjust if needed.
