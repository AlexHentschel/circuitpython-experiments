# Experiment 13 -- WS2812b via YD-RP2040

Drive a WS2812b 5x5 matrix from a YD-RP2040 board (Pico form factor) running
CircuitPython.

## Hardware

| Item | Detail |
|------|--------|
| MCU board | **YD-RP2040** by VCC-GND Studio (RP2040, USB-C, 16 MB flash W25Q128) |
| Firmware | CircuitPython **10.1.4** for `vcc_gnd_yd_rp2040` ([download](https://circuitpython.org/board/vcc_gnd_yd_rp2040/)) |
| Board ID | `vcc_gnd_yd_rp2040` |
| Bootloader drive | `RPI-RP2` |
| LED matrix | Generic **WS2812b 5x5** (25 NeoPixels) |
| Level shifter | Super-mini TTL Signal LED Amplifier / SPI Repeater (3-pin / 4-pin, DC 5-24 V) |
| Power | 5 V / 2 A USB PSU for LEDs; YD-RP2040 powered via its own USB-C port |
| IDE | Cursor + CircuitPythonSync extension (`padgettholdings`) |
| Python venv | `/Users/alex/Development/PythonVEs/CircuitPython_3.13_VsCode/bin/python` |


## YD-RP2040 Board Specifics

The YD-RP2040 is a Raspberry Pi Pico clone with these extras:

| Feature | Detail |
|---------|--------|
| USB | Type-C (not micro-USB) |
| Flash | 16 MB W25Q128 (vs 2 MB on standard Pico) |
| Reset button | BOOT + RESET for bootloader entry |
| On-board green LED | `board.LED` (GP25) -- **do not use `board.GP25`**, it is not defined |
| On-board WS2812 RGB LED | `board.NEOPIXEL` / `board.RGB` (GP23) -- requires solder jumper to be closed |
| USR button | `board.BUTTON` (GP24) -- active low, **do not use `board.GP24`** |
| PWR LED | Always-on power indicator |

**Pinout diagram:** `docs/RP-Pico clone YD-2040 Pinout.jpg`
**GitHub:** https://github.com/initdc/YD-RP2040


## GPIO Pin Map

| Signal | GPIO | Physical pin | Note |
|--------|------|-------------|------|
| WS2812b data | **GP0** | Pin 1 (left header) | External 5x5 matrix via level shifter |
| On-board green LED | `board.LED` (GP25) | N/A (on-board) | `board.GP25` is NOT defined -- use `board.LED` |
| On-board RGB LED | `board.NEOPIXEL` (GP23) | Pin 37 (right header) | WS2812, solder jumper required. Also `board.RGB` |
| USR button | `board.BUTTON` (GP24) | N/A (on-board) | `board.GP24` is NOT defined -- use `board.BUTTON` |

### RP2040 hardware resource allocation

On the RP2040, NeoPixel (WS2812b) uses a **PIO state machine** for its
single-wire protocol -- it does **not** consume an SPI bus. This means
NeoPixel strips and SPI peripherals can run simultaneously without conflict:

| Resource | Used by | Available |
|----------|---------|-----------|
| PIO (1 of 8 state machines) | WS2812b on GP0 | 7 remaining for additional strips / custom protocols |
| SPI0 | *Free* | Available for SD card, display, sensors, etc. |
| SPI1 | *Free* | Available for additional peripherals |


## Milestones

### Milestone 1 -- Board & GPIO Test (`milestone1_test_pins.py`)

Verify the board is running and GPIO pins are functional. No external wiring
needed for the on-board tests (GP25 LED, GP24 button, GP23 RGB).

**How to run:**
1. Flash CircuitPython 10.1.4 onto the board.
2. Copy `milestone1_test_pins.py` content into `code.py`.
3. Open a serial monitor (115200 baud).
4. The script blinks GP25, cycles GP23 RGB colours, reads GP24 button,
   then toggles each external GPIO pin.
5. Verify external GPIOs with a multimeter or breadboard LED + 330 Ohm resistor.

> **GP23 note:** The on-board WS2812 RGB LED test requires the solder jumper
> to be closed. The test is harmless to run without it.

### Milestone 2 -- WS2812b 5x5 Matrix (`milestone2_ws2812b_5x5.py`)

**Wiring:**
```
YD-RP2040 GP0 ──► Level-Shifter DIN             (signal in, 3.3V)
Level-Shifter DOUT ──► WS2812b DIN              (signal out, 5V)
5V PSU (+)  ──► WS2812b VCC + Level-Shifter high-voltage VCC (output side only)
GND         ──► YD-RP2040 GND + Shifter GND + WS2812b GND + PSU GND
```

> **Level-shifter VCC note:** Connect 5V to the high-voltage (output) side only.
> Do NOT connect the low-voltage (input) side VCC to 3.3V -- it self-biases to
> 5V from the output side. Common GND across all components is essential.

**How to switch:**
```bash
cp milestone2_ws2812b_5x5.py code.py
```
CircuitPythonSync will re-sync. Or copy-paste the file content into `code.py`.

**Library install (no board needed -- installs into workspace `lib/`):**
```bash
/Users/alex/Development/PythonVEs/CircuitPython_3.13_VsCode/bin/circup \
  --path /Users/alex/Development/VsCode/CircuitPython/2026-03_Exp13_Ws2812_CPy_on_RPi-Pico-2040 \
  --board-id vcc_gnd_yd_rp2040 --cpy-version 10.1.4 \
  install neopixel
```

## Library Installation via `circup`

Libraries live in the workspace `lib/` folder and are synced to the board by
the CircuitPythonSync extension ("Copy Libs to Board" command).

`circup` can install directly into the local workspace (no board needed):

```bash
CIRCUP=/Users/alex/Development/PythonVEs/CircuitPython_3.13_VsCode/bin/circup
PROJECT=/Users/alex/Development/VsCode/CircuitPython/2026-03_Exp13_Ws2812_CPy_on_RPi-Pico-2040

# Milestone 2 -- neopixel
$CIRCUP --path $PROJECT --board-id vcc_gnd_yd_rp2040 --cpy-version 10.1.4 install neopixel
```

### Built into CircuitPython 10.1.4 firmware (no lib/ needed)

Full list in `docs/CircuitPython Notes.md`. Key modules for this project:
`neopixel_write`, `adafruit_pixelbuf`, `adafruit_bus_device`,
`digitalio`, `_pixelmap`, `rp2pio`, `_asyncio`.

### External libs needed in lib/

- `neopixel.mpy` -- high-level NeoPixel (WS2812b) driver
- `adafruit_pixelbuf.mpy` -- shared pixel buffer base (dependency of neopixel)

Milestone 1 uses only built-in modules. No external libs needed until Milestone 2.


## Notes

- **Brightness** is set to 0.05.  At full white, a 5x5 WS2812b matrix draws
  ~1.5 A. Stay conservative until power budget is verified.
- The **GP23 WS2812 RGB LED** requires a solder jumper to be closed on the
  YD-RP2040 board. Without it, the LED will not light up but the GPIO is
  still safe to drive.
- **Serial port name changes on replug.** Run `ls /dev/tty.usbmodem*` to find
  the current name.
- The **Microsoft Serial Monitor extension is broken in Cursor.** Use the
  miniterm task instead (see `.vscode/tasks.json`).
