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
