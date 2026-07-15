# Context — circuitpython-exp15-microbit

**Family**: `circuitpython` · **Status**: active (early — Milestone 1) · **Repo folder** (workspace-relative to `/Users/alex/Development/VsCode/CircuitPython/`): `2026-06_Exp15_RP2350-Bit-Board_Microbit-v01/`.

## Scope & goal

A Python-programmable **micro:bit alternative** on an **RP2350 bit board** with a de-soldered 5×5 LED matrix (wires on the pads). Hardware identical to exp11. End-goal of the build stream: a usable micro:bit-style learning device.

## Entry points (further reading — links into the repo, not copied)

- `2026-06_Exp15_RP2350-Bit-Board_Microbit-v01/README.md` — hardware + pin map + Milestone 1 wiring/run + serial-monitor + circup.
- `2026-06_Exp15_.../code.py` — Milestone 1 blink (external LED on `LED_Col1 == GP2`, active-high through on-board 1K).
- `2026-06_Exp15_.../docs/removed-LED-matrix-wiring.png` — pin-map source image.
- Pin map (`evidence-supported` via exp11): `LED_Col1`=GP2, `Col2`=GP3, `Col3`=GP4, `Col4`=GP5, `Col5`=GP25 (each through on-board 1K); rows GP7/8/9/21/22 (no resistor); GP0/GP1 = Button A/B (not free).
- Venv: `/Users/alex/Development/PythonVEs/CircuitPython_3.13_VsCode`.

## Domain knowledge

Shares `../../concepts/circuitpython-runtime.md`; LED-driving specifics will seed a `led-driving` concept domain when content accrues.

## Resumption point

On-device run of the Milestone-1 blink (LED + serial output) pending board connection (no `/Volumes/CIRCUITPY` / `/dev/tty.usbmodem*` at setup). Per-session detail in `SESSION_LOG.md` (session 9).
