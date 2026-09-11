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
| BananaPi Docs site-wide footer licenses page content (including `bpi_bit_v2_goldfinger.jpg` and `bpi_bit_v2_interface_en.jpg`) as CC BY-SA by BananaPi. Unmodified copies may sit in a public experiment as collection items; ShareAlike does not infect the rest of the tree. Site does not print a CC version. | `[exp16]` | Footer text on https://docs.banana-pi.org/en/BPI-Bit-S2/BananaPi_BPI-Bit-S2. Sidecars: exp16 `Notes/*.jpg.license`. README caption attributes the interface figure. | 2026-09-04 |
| Official 5×5 WS2812 sequential list matches Exp09 (top row `20 15 10 5 0` … bottom `24 19 14 9 4`). | `[exp16]` `[cross-experiment]` | Same BananaPi Bit-S2 page, “5*5 LED Sequential List”. | 2026-09-04 |
| Host visual-fixture tests pin the 5×5 LUT (corners, interior, rotations) to that sequential grid. | `[exp16]` | `tests/test_geometry.py` `_VISUAL_ROT0` (not the wiring formula). On-device LUT still P8. | 2026-09-04 |
| DAL `pendolino3` row-bytes convert to Exp14 column-major via `(row_byte >> (4-c)) & 1`. MIT notice vendored beside the table. | `[exp16]` `[domain:fonts]` | DAL header `!` example + Exp16 `lib/display/font_makecode_5/` + `tests/test_font.py`. | 2026-09-04 |
| Exp09 `Image.GHOST` / `Image.TRIANGLE_LEFT` are **not** the MakeCode grids. Exp16 `GHOST` and `LEFT_TRIANGLE` now follow MakeCode (rounded head; right-triangle with full base). Other icons remain Exp09 ports. | `[exp16]` | Exp09 `lib/microbit.py` vs MakeCode screenshots 2026-09-04. Fixtures: `tests/test_icons_data.py` `MAKECODE_ICON_PATTERNS`. | 2026-09-04 |
| Exp16 `lib/` and `tests/*.py` contain **no** absolute host filesystem paths. Host pytest locates `lib/` via `Path(__file__)` in `tests/conftest.py`. There are no experiment shell scripts. A different checkout’s venv needs **no code edits** — only a local interpreter with pytest. Absolute `/Users/alex/…` paths are prose (example in `tests/README.md`, locks in `ai-notes/NOTES.md`). Shared workspace CircuitPythonSync is **outside** this experiment. | `[exp16]` | Grep 2026-09-04: no `/Users/`, `/Volumes/`, `PythonVEs` under `lib/` or `tests/*.py`. | 2026-09-04 |
| **This plugged-in unit** (UID `0740D10F1BE9`) ran CircuitPython **10.3.0** `bpi_bit_s2` as of 2026-09-11 Path A UF2 copy (was 10.0.3). Other BPI-Bit-S2s in the fleet are **not** assumed to match; re-read `boot_out.txt` per board. | `[exp16]` | `/Volumes/CIRCUITPY/boot_out.txt` after Path A: `Adafruit CircuitPython 10.3.0 on 2026-08-31; BPI-Bit-S2 with ESP32S2`; USB `303A:80E6`. Prior 10.0.3 on same UID. Alex: multiple boards, do not share version. | 2026-09-11 |
| Path A (CP `.uf2` onto `BITS2BOOT` with TinyUF2 already **0.35.0**) upgraded this unit 10.0.3 → 10.3.0 and **kept** CIRCUITPY (`code.py`, `lib/`, `sd/`, `settings.toml`); prior LED-icon sketch still ran. | `[exp16]` `[domain:tooling]` | Alex report + `boot_out.txt` 10.3.0 same UID; listing still had those files. TinyUF2 not rewritten. | 2026-09-11 |
| UID `0740D10F1BE9` CIRCUITPY FAT volume is **983040 bytes** (~941 KiB `df`; ~745 KiB free with current sketch). That **is** TinyUF2 `ffat` 960K — **same size** on dual-OTA and no-OTA 4MB tables. TinyUF2 `Flash Size: 0x002C0000` is **`ota_0`** (~2.75 MiB), not CIRCUITPY. Prior chat claim “pre-0.33 CIRCUITPY would be larger” is **invalidated**. | `[exp16]` `[domain:tooling]` | TinyUF2 0.32/0.35 CSVs (`ffat` 960K both); `diskutil` 2026-09-11; Adafruit Learn CP10 4MB page. Tables: `../../concepts/tooling-4mb-partitions.md`. | 2026-09-11 |
| BPI-Bit-S2 TinyUF2 mass-storage volume is **`BITS2BOOT`**. Enter it with tap **RESET** then tap **BOOT** within ~1 s (matrix purple), not Adafruit’s generic double-RESET as the first try. ROM download mode (esptool) remains hold **BOOT**, tap **RESET**, release **BOOT**. BananaPi Bit-S2 pages that say `esptool --chip esp32s3` are a **wrong chip** — use `esp32s2`. | `[exp16]` `[domain:tooling]` | Board page + BPI-Steam `update_circuitpython.html` (BITS2BOOT / RST then BOOT); circuitpython.org ROM-mode recipe; TinyUF2 0.35.0 + CP 10.3.0 URLs HTTP 200 on 2026-09-11. Full recipe: `../../concepts/tooling.md`. | 2026-09-11 |

## Unverified

| Finding | Scope | Why noted | Date |
|---------|-------|-----------|------|
| 20% brightness cap = `NeoPixel(brightness=0.2)` (Exp09 used 0.1). | `[exp16]` | Set in `core.py` (`BRIGHTNESS = 0.20`); on-device LED current still P8. | 2026-09-04 |
| PlanetX C/D **connectors** electrically hit goldfinger P13/P14. | `[exp16]` | Firmware maps those edge names to GPIO36/37; physical PlanetX cable not probed this project. Overnight tests fake FALL events. | 2026-09-04 |
| Device `import asyncio` works after copying the **bundle** `asyncio` + `adafruit_ticks` onto CIRCUITPY (not CPython stdlib). | `[exp16]` `[domain:circuitpython-runtime]` | Adafruit learn: library is not built in; matrix lists `_asyncio` only. P8 `circup install asyncio`. | 2026-09-04 |
| No local emulator discharges on-device K1/K2 for stock CP 10.3.0 `bpi_bit_s2`. Wokwi is the only plausible pre-P8 smoke; CircuitPython-on-S2 in Wokwi is unverified. espressif QEMU and Renode have no usable ESP32-S2 story. | `[exp16]` | Web-docs scan 2026-09-07 in local `ai-notes/digests/local-mcu-emulation.md`. Re-check before spending time. P8 stays the on-device gate. | 2026-09-07 |
| Stock CircuitPython `raspberry_pi_pico2` does not boot in a local emulator (2026-09-07). Host-pytest remains the hardware-free oracle for an RP2350 switch. | `[exp16]` | Web research 2026-09-07 in local `ai-notes/design/rp2350-emulation-macos.md` (projects' own statements, not runs). Revisit if QEMU #3125 lands or an emulator demonstrates CP-on-RP2350. | 2026-09-07 |

## Disputed

| Finding | Scope | Positions | Date |
|---------|-------|-----------|------|
| PlanetX C/D GPIOs on BPI-Bit-S2 goldfinger | `[exp16]` | **Was:** Exp09 `board.IO13`/`IO14` vs official GPIO36/GPIO37 vs “GPIO13/14 = photoresistors”. **2026-09-04 pins.c:** those were two numbering schemes, not two pin pairs — CP `IO13`=`GPIO36`=goldfinger P13; photoresistors = `LUM2`/`LUM1`. Contradiction **resolved** as a naming clash; row kept for history. Remaining: physical PlanetX cable (Unverified). | 2026-09-04 |

## Invalidated

| Finding | Scope | Correction | Date |
|---------|-------|------------|------|
| `board.IO13` / `IO14` on BPI-Bit-S2 CircuitPython mean ESP32 GPIO13/14 (photoresistors). | `[exp16]` | `pins.c` 10.3.0 maps `IO13`→GPIO36, `IO14`→GPIO37. GPIO13 is `LUM2`. | 2026-09-04 |
