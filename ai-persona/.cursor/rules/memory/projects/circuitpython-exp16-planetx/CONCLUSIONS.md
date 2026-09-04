# Conclusions — circuitpython-exp16-planetx

Status tiers: `unverified` · `evidence-supported` · `disputed` · `invalidated`.

## Evidence-Supported

| Finding | Scope | Evidence | Date |
|---------|-------|----------|------|
| BPI-Bit-S2 5×5 WS2812 logical (col, row) with origin top-left maps to strip index `row + 20 - column * 5` (column-major, right-to-left physically). | `[exp16]` `[cross-experiment]` (from exp09) | Formula + ASCII map in `2026-02_Exp09_…/lib/display_v0.py` and `lib/microbit.py`. On-device origin unverified in this project. | 2026-09-03 |
| Stock CircuitPython **10.3.0** `bpi_bit_s2` firmware includes `_asyncio`, `keypad` / `keypad.Keys` / `keypad.EventQueue`, `rainbowio`, and frozen `neopixel`. User-facing `asyncio` is **not** in the firmware (see `concepts/circuitpython-runtime.md`). | `[exp16]` | 10.3.0 support matrix board cell `docs.circuitpython.org/en/10.3.0/shared-bindings/support_matrix.html` (BPI-Bit-S2); `ports/espressif/mpconfigport.mk` `CIRCUITPY_FULL_BUILD ?= 1`; `py/circuitpy_mpconfig.mk` `CIRCUITPY_KEYPAD ?= $(CIRCUITPY_FULL_BUILD)`; board `mpconfigboard.mk` `FROZEN_MPY_DIRS += …/Adafruit_CircuitPython_NeoPixel`. **On-device `help("modules")` still P8.** | 2026-09-04 |
| CircuitPython `board.IO13` / `IO14` on this firmware **are** goldfinger P13/P14 (GPIO36/GPIO37). `board.NEOPIXEL` = GPIO18. Photoresistors are `board.LUM1`/`LUM2` (GPIO12/13), not `IO13`/`IO14`. | `[exp16]` | `ports/espressif/boards/bpi_bit_s2/pins.c` tag `10.3.0`: `IO13`→`pin_GPIO36` (also `SCK`/`D13`); `IO14`→`pin_GPIO37` (also `MISO`/`D14`); `NEOPIXEL`→`GPIO18`; `BUTTON_A`/`BUTTON_B`→GPIO38/33; `LUM1`/`LUM2`→GPIO12/13. Unifies Exp09 names with BananaPi GPIO numbers (different namespaces). | 2026-09-04 |
| Exp09 5×5 `_FONT` is derived from pitchfork-5x5 (**GPLv3**). | `[exp16]` | Source comment in `2026-02_Exp09_…/lib/microbit.py` (~line 310) + `generate_font.py`. | 2026-09-04 |
| Lancaster DAL `MicroBitFont.cpp` / `pendolino3` is **MIT** (Copyright 2016 BBC; Lancaster by arrangement with the BBC). | `[exp16]` `[domain:fonts]` | File header + https://github.com/lancaster-university/microbit-dal/blob/master/LICENSE (fetched 2026-09-04). Apache-2.0 hypothesis **invalidated**. | 2026-09-04 |
| BananaPi Docs site-wide footer licenses page content (including `bpi_bit_v2_goldfinger.jpg`) as CC BY-SA by BananaPi. Unmodified copy may sit in a public repo as a collection item; ShareAlike does not infect the rest of the tree. Site does not print a CC version. | `[exp16]` | Footer text on https://docs.banana-pi.org/en/BPI-Bit-S2/BananaPi_BPI-Bit-S2 (and other docs.banana-pi.org pages). Sidecar: exp16 `Notes/bpi_bit_v2_goldfinger.jpg.license`. | 2026-09-04 |
| Official 5×5 WS2812 sequential list matches Exp09 (top row `20 15 10 5 0` … bottom `24 19 14 9 4`). | `[exp16]` `[cross-experiment]` | Same BananaPi Bit-S2 page, “5*5 LED Sequential List”. | 2026-09-04 |

## Unverified

| Finding | Scope | Why noted | Date |
|---------|-------|-----------|------|
| 20% brightness cap = `NeoPixel(brightness=0.2)` (Exp09 used 0.1). | `[exp16]` | Literal reading of the goal; not yet implemented. | 2026-09-03 |
| PlanetX C/D **connectors** electrically hit goldfinger P13/P14. | `[exp16]` | Firmware maps those edge names to GPIO36/37; physical PlanetX cable not probed this project. Overnight tests fake FALL events. | 2026-09-04 |
| Device `import asyncio` works after copying the **bundle** `asyncio` + `adafruit_ticks` onto CIRCUITPY (not CPython stdlib). | `[exp16]` `[domain:circuitpython-runtime]` | Adafruit learn: library is not built in; matrix lists `_asyncio` only. P8 `circup install asyncio`. | 2026-09-04 |

## Disputed

| Finding | Scope | Positions | Date |
|---------|-------|-----------|------|
| PlanetX C/D GPIOs on BPI-Bit-S2 goldfinger | `[exp16]` | **Was:** Exp09 `board.IO13`/`IO14` vs official GPIO36/GPIO37 vs “GPIO13/14 = photoresistors”. **2026-09-04 pins.c:** those were two numbering schemes, not two pin pairs — CP `IO13`=`GPIO36`=goldfinger P13; photoresistors = `LUM2`/`LUM1`. Contradiction **resolved** as a naming clash; row kept for history. Remaining: physical PlanetX cable (Unverified). | 2026-09-04 |

## Invalidated

| Finding | Scope | Correction | Date |
|---------|-------|------------|------|
| `board.IO13` / `IO14` on BPI-Bit-S2 CircuitPython mean ESP32 GPIO13/14 (photoresistors). | `[exp16]` | `pins.c` 10.3.0 maps `IO13`→GPIO36, `IO14`→GPIO37. GPIO13 is `LUM2`. | 2026-09-04 |
