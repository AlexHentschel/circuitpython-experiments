# Digest — Local MCU emulation on macOS (pre-P8 smoke options)

**Status:** research 2026-09-07, **post-loop** (not one of the four P0 digests; the plan-refinement loop was already closed). **Not a plan change** — P8 stays the on-device gate; any sim smoke is optional and needs Alex's go.
**Load only if** the pre-P8 / current-board emulation question is live this session. Sibling (hypothetical RP2350 switch): [`../design/rp2350-emulation-macos.md`](../design/rp2350-emulation-macos.md).
**Question:** can the Exp16 target — stock CircuitPython **10.3.0**, board build `bpi_bit_s2` (ESP32-S2) — run emulated on the dev machine (macOS 26.x) before the P8 human window?
**One-line answer:** **no tool discharges K1/K2.** Wokwi is the only plausible pre-P8 smoke, and CircuitPython-for-S2 booting inside Wokwi is **unverified**. espressif QEMU and Renode have **no usable ESP32-S2 story**; the CP `unix` port is interpreter-only. Web-docs scan dated 2026-09-07 — versions move, re-check before spending real time.

## Verdict table

| Tool | macOS | ESP32-S2 | Runs CP 10.3.0 `bpi_bit_s2`? | NeoPixel path | Discharges K1/K2 |
|------|-------|----------|------------------------------|---------------|------------------|
| **Wokwi** (browser free; VS Code ext; `wokwi-cli`; offline = Pro) | yes | yes — S2 boards exist (ESP32-S2-DevKitM-1, Franzininho WiFi, Wemos S2 mini); S2 is tracked via `wokwi/esp32-test-binaries`, not the headline matrix | **unverified** — custom-firmware upload exists (merged `.bin` or `flasher_args.json`); official CP-on-Wokwi template is **Pico only** | plausible — RMT emulated **transmit-only**, documented for WS2812 strips; GPIO interrupts supported (buttons) | **no** |
| **espressif QEMU fork** (macOS aarch64/x86_64 prebuilts) | yes | **no** — official targets are ESP32 / S3 / C3 only; S2 absent from the support matrix | no | RMT not emulated even on supported chips — NeoPixel path dead | no |
| **Renode** (Antmicro) | yes | **no S2 SoC model** — Xtensa ISA support exists (SOF project) but no ESP32-S2 platform/peripherals | no — CP's Renode port is `renode_cortex_m0plus`, a minimal core-debug port (PR #9199) | no | no |
| **CircuitPython `unix` port** | yes (clang build) | n/a (host binary, not emulation) | interpreter only; module set is port-config — **no** `board` / `keypad` / `neopixel_write` by default | n/a | no |
| **Ebiroll `qemu-xtensa-esp32s2`** (community) | source build | partial; stale (2021): "S2 emulation has regressed", SHA-256 patched to 0, ROM dumps + patching required | no realistic path | no | no |

## Wokwi — only candidate; unverifieds, not blockers

What checks out (per Wokwi docs, 2026-09-07):

- ESP32-S2 chips are simulated (board list above); custom application firmware = merged single `.bin` (esptool `merge_bin`) or `flasher_args.json`, where hand-authored `flash_files` at offsets is an accepted trick for preloading extra flash regions.
- S2 "USB" support = **UART over USB (CDC)** — enough in principle for CP's native-USB CDC REPL; **not** a host-attached MSC device, so expect **no CIRCUITPY drive** in the sim. File delivery would be REPL paste (`Ctrl+E`) or a pre-baked flash image (unverified).
- RMT transmit-only is exactly the WS2812 direction; GPIO interrupts cover `keypad.Keys` plausibility.

What is unverified (do not assume before a 30-min spike): CP 10.3.0 `bpi_bit_s2` image actually booting; bundle-`asyncio` import on the sim; `keypad` event flow; NeoPixel rendering on GPIO18.

If Alex green-lights a smoke (optional, **not a new plan phase**): merged bin → `diagram.json` with an S2 board + 25-px WS2812 on GPIO18 + four buttons on GPIO36/37/38/33 → REPL `help("modules")` → paste `lib/` + a `code.py` → stop at "LUT renders, C/D fire" and log-only results.

## CP `unix` port — why it adds ~nothing

Builds natively on macOS and runs the CP interpreter, but the hardware modules our P8 cares about are port-config extras. Host pytest already covers the pure-Python layers better (checkpoint in [`../NOTES.md`](../NOTES.md); suite stays off `board`/`display.core`). Treat as a curiosity, not a bar.

## Load-bearing evidence rules

- A sim run never discharges **K1** (bundle `asyncio` on the real CIRCUITPY drive) or **K2** (real PlanetX cable on goldfinger P13/P14) — both stay P8 (`../plan/plan_v1.0.md` known-unknowns table).
- A different S2 board build (e.g. `espressif_esp32s2_saola_1_wrover`) is **not** `bpi_bit_s2` evidence — `pins.c` differs (plan § Pins).
- Sim NeoPixel output is not the LUT source of truth; the hand-authored visual fixture in `tests/test_geometry.py` is.
- Host pytest stays the quality bar; a sim smoke, if approved, is additive and ends at "interesting", never at "P8 green".

## Sources

- Wokwi ESP32 guide (chips, peripheral matrix, USB CDC, custom firmware): <https://docs.wokwi.com/guides/esp32>
- Wokwi CircuitPython guide (Pico-only template): <https://docs.wokwi.com/guides/circuitpython>
- Wokwi project config (firmware types, `flasher_args.json`): <https://docs.wokwi.com/vscode/project-config>
- Wokwi offline mode (Pro): <https://docs.wokwi.com/vscode/offline-mode>
- espressif QEMU support matrix (targets ESP32/S3/C3; RMT ❌): <https://github.com/espressif/esp-toolchain-docs/tree/main/qemu> · releases (macOS prebuilts): <https://github.com/espressif/qemu/releases>
- Community S2 QEMU fork: <https://github.com/Ebiroll/qemu-xtensa-esp32s2>
- Renode + Xtensa ISA (SOF): <https://antmicro.com/blog/2022/01/xtensa-isa-in-renode-for-sof-project/> · CP Renode port: <https://docs.circuitpython.org/en/latest/ports/renode/README.html>
- CP `unix` port: <https://docs.circuitpython.org/en/latest/ports/unix/README.html>
- CP espressif port (ESP32-S2 = stable; REPL over native USB CDC): <https://docs.circuitpython.org/en/latest/ports/espressif/README.html>

## See also

- `../NOTES.md` — K1/K2 reminder, firmware cache path, P8 block
- `../plan/plan_v1.0.md` — P8 row, Pins table, known unknowns K1/K2
- `../design/rp2350-emulation-macos.md` — sibling (hypothetical RP2350 switch); **load only if** that question is live. Different chip, same shape of answer.
- `INDEX.md` — this folder's router
