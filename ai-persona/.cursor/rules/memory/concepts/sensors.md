# Concept domain: sensors (environmental / physical)

`[domain:sensors]` `[cross-experiment]` — **seeded 2026-09-28**. First concept: PlanetX light-sensor lux curve. Power-measurement devices stay in `power`. GPIO buttons stay in exp16 `lib/planetx/button.py` (not a sensing curve). Retrieval: `_INDEX.md` → here.

## Concepts

### PlanetX light sensor lux curve (one AnalogIn sample) — formula `evidence-supported`; on-device `unverified`

**Claim.** ELECFREAKS PlanetX light sensor EF05001 is analog on Nezha2 J1 (P1) or J2 (P2) only. MakeCode `lightSensor` (`pxt-PlanetX` `basic.ts`) maps a 0–1023 analog reading to integer lux: below 200 counts, `counts * 8` (0..200 → 0..1600); otherwise `1600 + (counts - 200) * 12400 / 823` (200..1023 → 1600..14000). The LightTower tutorial’s “dark” check is `< 100` on that lux number.

CircuitPython 10.3.0 `AnalogIn.value` is 0..65535 and, on ESP32, constructs and destroys an ADC unit on every read (`NO_OF_SAMPLES` 2). Exp16 `PlanetXLightSensor.lux()` converts with `(raw * 1023) // 65535` and the integer curve above, **one** read, synchronous. It does not repeat MakeCode’s 100-read average.

**Why one read.** A 100-iteration Python loop would repeat that allocate-and-free path. The student workaround for chatter near 100 is two thresholds in the caller (`lib/planetx/light.py` `lux` docstring), not a longer block inside the driver.

**Not this curve.** MicroPython `PlanetX_MicroPython/light.py` (`268740c`) subtracts a dark floor of 45 counts before the same split. Exp16 follows MakeCode so 100 means the tutorial’s 100.

**Driver.** exp16 `lib/planetx/light.py`. Notes: exp16 `ai-notes/planetx-drivers/sources.md`. On-device timing is `code_stage4.py` (not deployed).
