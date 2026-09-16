# Concepts — LED driving (WS2812 / NeoPixel output)

`[domain:led-driving]` `[cross-experiment]` — **seeded 2026-09-12** (first concrete concept; candidate domain reserved since the warm reset). WS2812/NeoPixel signal generation across MCU families. Retrieval: `_INDEX.md` → here → `#concept`; lateral edges in `_RELATIONS.md`. Applies to the WS2812 experiments (exp09/11/13/14/16).

## Concepts

### WS2812/NeoPixel output peripheral is MCU-family-specific (RP2 → PIO; ESP32 → RMT) — `evidence-supported`

**Claim.** CircuitPython's `neopixel_write.neopixel_write(pin, buf)` — the low-level primitive under `neopixel.NeoPixel` — emits the ~800 kHz WS2812 protocol via a **platform-specific hardware peripheral**, selected per MCU family, *not* by bit-banging:
- **RP2040 / RP2350 (raspberrypi port)** → a **PIO state machine**. `ports/raspberrypi/common-hal/neopixel_write/__init__.c` constructs an `rp2pio_statemachine` running a small `neopixel_program` at 12.8 MHz (8-bit auto-pull, shift-left / MSB-first, data pin as sideset); teardown "resets the pin and releases it from the PIO".
- **ESP32 family incl. ESP32-S2 / S3 (espressif port)** → the **RMT (Remote Control) peripheral**. `ports/espressif/common-hal/neopixel_write/__init__.c` reserves an RMT channel per write, translates each byte into WS2812 timing items, transmits, then frees the channel (≤4 RMT channels concurrently; a shared reservation system also used by PulseIn/Out).
- **ESP32 has no PIO** — PIO is RP2-silicon only. So "PIO" wording on an ESP32 board is always wrong.

**Why it matters (doc / teardown correctness).** Describe `neopixel` / `deinit` teardown *per silicon*: "PIO state machine + data pin" on RP2, "RMT peripheral + data pin" on ESP32. A docstring carried verbatim across a port silently goes stale — exp16 inherited Exp14's RP2040 "PIO" wording on its ESP32-S2 board (corrected 2026-09-12 across 5 sites; the divergence + do-not-back-port rule are in exp16 `Notes/exp14-divergence.md` §3). Forward rule: when a project returns to an RP2350 board this reverts to PIO — re-derive per silicon, do not treat either term as canonical.

**Sources (concordant, official CircuitPython).**
- ESP32 → RMT: PR `adafruit/circuitpython#3232` ("ESP32-S2: Add Neopixel support" — utilizes the RMT peripheral + a channel-reservation system, freed after each write); commit `9537b1d` "Improve neopixel on ESP" (RMT channel/memory, moves the RMT interrupt to the 2nd core); `ports/espressif/common-hal/neopixel_write/__init__.c`.
- RP2 → PIO: `ports/raspberrypi/common-hal/neopixel_write/__init__.c` (`rp2pio` state machine, 12.8 MHz `neopixel_program`, sideset data pin, "release it from the PIO").
- API: `shared-bindings/neopixel_write/__init__.c` + docs.circuitpython.org `neopixel_write` — raw, color-order-independent bytes; "typically not used by user code".

**Scope note.** Off-CircuitPython WS2812 driving (bit-bang, SPI-MOSI, ESP32 I2S/`led_strip`) exists but is not what CircuitPython's `neopixel_write` uses on these ports; this concept is about the CP `common-hal` implementations only.

### BananaPi 5×5 WS2812 sequential index is shared across bit generations; the data GPIO is not — `evidence-supported`

**Claim.** Original **bpi:bit** (ESP-WROOM-32) and **BPI-Bit-S2** (ESP32-S2) wire the onboard 5×5 WS2812 with the **same column-major, right-to-left strip index** (origin top-left → index `row + 20 - column * 5`):

```
20 15 10  5  0
21 16 11  6  1
22 17 12  7  2
23 18 13  8  3
24 19 14  9  4
```

The **data pin is not shared**: original bit matrix = **GPIO 4**; Bit-S2 = **GPIO 18** / `board.NEOPIXEL`. Original-bit GPIO 18 is the separate red status LED (`R_LED` / SPI_SCK). Copying original-bit pin tables or `MicroPython-Samples/01.leds/heartbeat.py` (`Pin(18)` as a GPIO toggle) onto Bit-S2 is wrong — that sample is **not** a matrix heartbeat.

**What may carry (algorithm, not pins):** 25-pixel icon/font buffers in sequential-index order (`microbit/display.py` `Image.seq` / `Image.HEART`); Webduino Blockly 25-bit LED strings (e.g. `webbit_i18n` `bit-s-02.json` heart pair). Re-bind the NeoPixel pin per board.

**Sources.** [BPI-BIT-Hardware `readme_en.md`](https://github.com/BPI-STEAM/BPI-BIT-Hardware/blob/master/readme_en.md) (GPIO 4 + sequential table); BananaPi Bit-S2 “5*5 LED Sequential List” (already in exp16 CONCLUSIONS); Exp09 `lib/display_v0.py`; CircuitPython `bpi_bit_s2` `pins.c` `NEOPIXEL`→GPIO18. Bit-S2 **electrical** schematic (this generation, not original bit): [BPI-BIT-Lite-Doc `sch/BPI-BIT-Lite-V0.2.pdf`](https://github.com/BPI-STEAM/BPI-BIT-Lite-Doc/blob/main/sch/BPI-BIT-Lite-V0.2.pdf) — 25× WS2812B sheet; local `ai-notes/BPI-Bit-S2_Hardware/` (CONTEXT *BPI-Bit-S2 schematic*). Vendor catalog: `crossref/BY_TOPIC.md` *BPI-STEAM predecessor*. **Local alternate for original-bit samples (may vanish):** exp16 `ai-notes/Elecfreaks-Repos/MicroPython-Samples/` pin `c03ed50` — GitHub is canonical; freshness procedure in exp16 CONTEXT *Local vendor snapshots*.
