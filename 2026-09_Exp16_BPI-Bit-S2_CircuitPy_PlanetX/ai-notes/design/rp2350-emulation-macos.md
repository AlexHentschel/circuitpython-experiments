# RP2350 local emulation on macOS — research (possible stack switch)

**Status:** research snapshot, **live 2026-09-07**. Not a lock, not a plan change, not a decision to switch hardware. **Load only if** the RP2350-switch / RP2350-emulation question is live this session. Answers Alex's 2026-09-07 question: *assuming we switch the hardware stack to an RP2350 MCU, is there a way to emulate the MCU locally on the dev machine (macOS 26.6)?*
**Purpose:** one-hop reference so a cold AI (or Alex) can re-check the emulator landscape without re-searching; feeds the RP2350-switch seam already analyzed in [`student-api-portability.md`](student-api-portability.md) (A3: RP2350 target = 8×8 WS2812).
**Method:** web research 2026-09-07 (sources listed at the bottom; all accessed that day) + local host checks (tagged `[local]`). Web claims about third-party projects are the projects' own statements, not things we ran. Re-verify anything load-bearing before relying on it.
**How to check:** every landscape row names its source. Host inventory is commands in the host-machine section — re-run on the trigger day, do not treat a prior snapshot as current.

---

## Headline answers

1. **Stock CircuitPython `raspberry_pi_pico2` firmware does not boot in any local emulator today** (2026-09-07). Every candidate below either lacks the RP2350 machine entirely, models cores but stubs the peripherals CP needs (USB MSC/REPL, flash filesystem, timers), or is RISC-V-only. CP's own emulator story is the Renode port, which is a **cortex-m0plus** build (RP2040-class, not RP2350).
2. **The project's existing host-test strategy already is the local emulation strategy.** The suite stays off `board`/`display.core` (`../../tests/conftest.py`), buttons take an injected `event_queue=`, and display swap units are files (G2 seam). Silicon emulation would add little for student-API work; it would matter only for firmware-level debugging.
3. **If a real `.uf2` must run locally**, try `rp2350js` first (if `which node` succeeds) then `picoem` (needs `rustup`); both are hobby-grade with no CP-on-RP2350 boot demonstrated. Track upstream QEMU instead of investing now.

## What a stack switch would mean on the firmware side

A switch is a **constructor/config + swap-file** change (pins, LUT, 8×8 assets) under G1–G5 in [`student-api-portability.md`](student-api-portability.md), not an API redesign. Emulation only affects *how much can be tested without hardware*.

Do not copy pin maps or firmware facts here:
- Locks / CP version / firmware cache: [`../NOTES.md`](../NOTES.md)
- RP2350 bit-board prior art (Pico 2 image, pin map): Exp15 [`README.md`](../../../2026-06_Exp15_RP2350-Bit-Board_Microbit-v01/README.md)

## Host machine (re-check on the trigger day)

Snapshot `[local]` 2026-09-07 is **inventory, not a lock**. Re-run before investing:

| Check | Why it matters |
|-------|----------------|
| `sw_vers`; `uname -m` | macOS / arch |
| `which node npm` | if present, `rp2350js` needs no new toolchain |
| `which qemu-system-arm`; `brew info qemu` | QEMU still has no Pico 2 machine today (work item #3125), even if the binary exists |
| `which cargo` | `picoem` needs `rustup` first |
| `which dotnet` | Lemur needs .NET 10 SDK |
| `ls /Users/alex/Development/PythonVEs/circuitpython-firmware/` | cache layout (a switch would add `raspberry_pi_pico2/` beside `bpi_bit_s2/`) |

## Emulator landscape (2026-09-07)

"CP boot?" = does the project demonstrate the **stock CircuitPython `raspberry_pi_pico2` image** booting. "mac arm64" = runs on Apple-silicon macOS.

| Option | RP2350 coverage | CP boot? | mac arm64 | Verdict for this project |
|--------|-----------------|----------|------------|--------------------------|
| **QEMU** (`qemu-system-arm`) | `cortex-m33` CPU model exists, but **no RP2350 / Pico 2 machine** upstream; [work item #3125](https://gitlab.com/qemu-project/qemu/-/work_items/3125) (opened 2025-09-21) still open | No | Yes (brew) | No today. Revisit when #3125 lands. |
| **CircuitPython Renode port** (official) | Minimal CP built from source for `renode_cortex_m0plus` **only**; UART↔PTY REPL ([docs](https://docs.circuitpython.org/en/stable/ports/renode/README.html)) | Yes, but M0+ = RP2040-class, minimal build, no `board` fidelity to any real board | Yes | CP-on-host playground only; **not RP2350**. |
| **Renode** (standalone) | Cortex-M33 CPU supported in general `.repl` platforms; no canonical RP2350 board platform tied to CP | No | Yes | Same upstream gap as QEMU. |
| **Wokwi** (hosted simulator) | [Supported-hardware doc](https://github.com/wokwi/wokwi-docs/blob/main/docs/getting-started/supported-hardware.md) lists **RP2040 only**; no RP2350 / Pico 2 part | No | n/a (cloud) | Not available; the "Pico 2" starter project renders the RP2040 Pico part. |
| **`picoem` / `rp2350-emu`** (0x4D44, Rust, [repo](https://github.com/0x4D44/picoem), [crate 0.2.6, 2026-06-27](https://crates.io/crates/rp2350-emu)) | Cycle-accurate **dual Cortex-M33**, boots the real A2 bootrom (BSD-3-Clause), differential-tested vs QEMU M33 **and real silicon**; **Arm-mode only** (no Hazard3); UART/SPI/I2C/DMA/timers = **stubs**; GDB RSP stub; macOS OK (serial backend; threaded backend x86_64-only); self-described "personal research project — no maintenance commitments" | No (MicroPython-class firmware is the demonstrated ceiling) | Yes (needs `rustup`) | Best silicon-accuracy sandbox for firmware-level work; not a CP target. |
| **`rp2350js`** (c1570, TypeScript fork of wokwi/rp2040js, [repo](https://github.com/c1570/rp2350js)) | **Both personalities**: Hazard3 RV32 machine-mode + **basic** Cortex-M33 (no TrustZone/secure mode); runs from bootrom, flash + no-flash UF2; runs MicroPython (both variants); GDB; **MCP server + agent skill**; ~70 M cycles/s, C-transpile option; MIT | No (MicroPython demonstrated, not CP) | Yes (Node) | Cheapest local `.uf2` experiment if `which node` succeeds; expect partial boot, USB unmodeled. |
| **`rp2350js_emulator`** (GhostRoboticsLab, [repo](https://github.com/GhostRoboticsLab/rp2350js_emulator)) | **RISC-V only** (rejects Arm UF2s loudly); dual Hazard3 cores; WS2812 bit-accurate; 409 tests | No (Arm images rejected — CP RP2350 is an Arm build) | Yes (node) | RISC-V-side only; out for CP. |
| **Lemur** (lukaspirkl, C#/.NET 10, [repo](https://github.com/lukaspirkl/lemur)) | **Hazard3 core 0 only**; GDB drop-in for OpenOCD; Avalonia UI | No | Yes if `dotnet` present | RISC-V only; out for CP. |
| **Bramble** (Night-Traders-Dev, C, [repo](https://github.com/Night-Traders-Dev/Bramble)) | Tri-arch `-arch m0+/m33/rv32`, UF2 family-ID auto-detect, 319 tests; **boots CircuitPython on RP2040** (their claim); RP2350 M33 mode runs firmware with UART output | **CP on RP2040 only**; RP2350 CP not claimed | Likely (plain C) | The closest "CP boots in an emulator" evidence anywhere — but on RP2040, not RP2350. |

## Key negative result, precisely stated

As of 2026-09-07, no project searched demonstrates the **stock CircuitPython `raspberry_pi_pico2` image** booting under emulation. Why it is hard: CP boot needs USB CDC/MSC, a flash filesystem, and timer/RTC behavior — exactly the peripherals that are stubs (picoem) or untested (rp2350js "basic" M33). The only official CP-under-emulator path is the **Renode port**, which targets `renode_cortex_m0plus` and is a *minimal* CP without real-board fidelity. Treat any future "CP runs in emulator X" claim as unverified until we run it.

## Implications for Exp16 / a future Exp (RP2350 switch)

- **Primary:** keep the host-pytest pattern as the portability oracle (G7: the student sketch is the test, not a compatibility matrix). The constructor/`event_queue=` seams already give hardware-free coverage of everything student-facing.
- **Secondary, optional:** if firmware-level local debugging is ever wanted, order of attempt on this machine: (1) `rp2350js` — zero new toolchain; (2) `picoem` — `rustup` + `brew install qemu` (its QEMU differential harness needs `qemu-system-arm`); (3) re-check QEMU/Renode upstream. Budget expectation: instruction-level bring-up, not a CIRCUITPY drive.
- **Do not** block any plan phase on emulation; P8-style human device windows remain the on-device oracle.
- **Firmware cache convention:** a switch would add `circuitpython-firmware/raspberry_pi_pico2/` alongside `bpi_bit_s2/` (same 10.3.0).

## Revisit triggers (re-scan this page when any fires)

| Trigger | Action |
|---------|--------|
| Alex decides the RP2350 switch | Re-verify landscape same day; this page is the starting point, not the answer |
| QEMU #3125 merged | `brew install qemu` → try `-machine` Pico 2 with the stock `.uf2`/`.bin` |
| CircuitPython Renode port gains a non-M0+ / RP2350 board | Rebuild `ports/renode`; reconsider as CI device-approximation |
| Any emulator demonstrates CP-on-RP2350 boot | Promote to a candidate; test with our `lib/` before believing |
| Wokwi adds an RP2350 part | Free hosted option for student demos; re-evaluate |

## Sources (accessed 2026-09-07)

- QEMU RP2350 work item: <https://gitlab.com/qemu-project/qemu/-/work_items/3125>
- CircuitPython Renode port: <https://docs.circuitpython.org/en/stable/ports/renode/README.html>
- CircuitPython Pico 2 board page (CP 10.3.0 stable): <https://circuitpython.org/board/raspberry_pi_pico2/>
- picoem: <https://github.com/0x4D44/picoem> · <https://crates.io/crates/rp2350-emu> · <https://docs.rs/crate/rp2350-emu/latest>
- rp2350js: <https://github.com/c1570/rp2350js>
- rp2350js_emulator (RISC-V fork): <https://github.com/GhostRoboticsLab/rp2350js_emulator>
- Lemur: <https://github.com/lukaspirkl/lemur>
- Bramble: <https://github.com/Night-Traders-Dev/Bramble>
- Wokwi supported hardware: <https://github.com/wokwi/wokwi-docs/blob/main/docs/getting-started/supported-hardware.md>

## See also

- [`student-api-portability.md`](student-api-portability.md) — the switch seam this research serves (G1–G7, A1–A4)
- [`../digests/local-mcu-emulation.md`](../digests/local-mcu-emulation.md) — **current** board (ESP32-S2 / `bpi_bit_s2`) pre-P8 question; **load only if** that is the task. Different chip, same shape of answer
- [`../NOTES.md`](../NOTES.md) — locks (this page adds none)
- [`../plan/plan_v1.0.md`](../plan/plan_v1.0.md) — P8 human device window stays the on-device oracle
- [`../../tests/README.md`](../../tests/README.md) — host-test strategy that makes silicon emulation optional
- Exp15 [`README.md`](../../../2026-06_Exp15_RP2350-Bit-Board_Microbit-v01/README.md) — RP2350 bit board pin map + CP 10.1.3 prior art
