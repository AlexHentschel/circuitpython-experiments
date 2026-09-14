# Exp16 — BPI-Bit-S2 CircuitPython display + PlanetX buttons

Async MakeCode-style **5×5 LED** library and **per-module button** dispatchers (`OnboardButtons` A/B, `PlanetXButtonSensor` C/D) for the [BananaPi BPI-Bit-S2](https://docs.banana-pi.org/en/BPI-Bit-S2/BananaPi_BPI-Bit-S2).

Display architecture: [`lib/display/README.md`](lib/display/README.md).


## Hardware

![BPI-Bit-S2 hardware interface, front and back](Notes/bpi_bit_v2_interface_en.jpg)

<sub>BananaPi BPI-Bit-S2 hardware; unmodified source: [BananaPi docs](https://docs.banana-pi.org/en/BPI-Bit-S2/BananaPi_BPI-Bit-S2), available under Creative Commons Attribution-ShareAlike License, by BananaPi. (local [license file](Notes/bpi_bit_v2_interface_en.jpg.license))</sub>


| Piece | Detail |
|-------|--------|
| Board | [BPI-Bit-S2](https://circuitpython.org/board/bpi_bit_s2/) (ESP32-S2, micro:bit form factor) |
| Firmware | Stock CircuitPython **10.3.0**, board-id `bpi_bit_s2` |
| LEDs | Onboard 5×5 WS2812 (25 NeoPixels), `board.NEOPIXEL` (GPIO18), brightness cap 0.20 |
| Wiring | Column-major, right-to-left. Logical (0,0) = top-left. Strip index `row + 20 - column * 5` |
| Buttons A/B | Onboard, `board.BUTTON_A` / `board.BUTTON_B` (active-low) |
| Buttons C/D | [ElecFreaks PlanetX Push Button Module](https://wiki.elecfreaks.com/en/microbit/sensor/planet-x-sensors/Plant_X_EF05017/) connected to goldfinger P13/P14 = `board.IO13` / `board.IO14` |

## This experiment's setup

These libraries are not tied to macOS or a particular Python virtual environment. Host tests need a desktop CPython with `pytest` and `pytest-asyncio`. Do not treat Blinka `board`/`keypad` as CircuitPython.

So far, I used for development: Cursor on macOS 26, CPython 3.13 in a virtual environment at `<path-to-venv>`. Do not pip-install `neopixel` or `adafruit_bitmap_font` into that venv (host tests stay off `display.core`).

On a BPI-Bit-S2 this experiment uses CircuitPython 10.3.0 (`neopixel` frozen, `keypad.Keys` built in). User-facing `asyncio` is a **bundle** library: `circup install asyncio` (pulls `adafruit_ticks`). Host CPython `asyncio` is a different library.

## Tests

From this folder, using that host CPython (not CircuitPython on the board). The suite does not import `board` or `display.core`.

```bash
<path-to-venv>/bin/pytest
```

Needs `pytest` and `pytest-asyncio` on that interpreter. Concrete path for this machine: [`tests/README.md`](tests/README.md).

## Deploy

Human-run deploy scripts (host → mounted CIRCUITPY drive; the board is a deploy target, never the source of truth):

1. Flash CircuitPython 10.3.0 ([board page](https://circuitpython.org/board/bpi_bit_s2/); 4 MB Espressif needs TinyUF2 ≥ 0.33.0 if using UF2).
2. When the CIRCUITPY drive mounts, ship the libraries: `python3 scripts/sync_lib_to_board.py` — filtered copy of `lib/` (excludes `__pycache__/`, `.DS_Store`, `README.md`, `*.pyc`; skips unchanged files by size+mtime; never deletes board files). Also ships the vendored `asyncio/` + `adafruit_ticks.mpy`, so no `circup install` step is needed.
3. Ship the code: `python3 scripts/sync_files_to_board.py` — copies what `.vscode/cpfiles.txt` lists (currently `readme.txt` + a `code_stageN.py -> /code.py` replay line). **Switching which script is active**: edit `.vscode/cpfiles.txt` directly — comment out the currently-active `... -> /code.py` line, uncomment (or add) the one you want, then re-run the sync script. Exactly one `-> /code.py` line must be active at a time; the manifest's own header comment documents the full syntax and a real gotcha (a trailing inline comment on an active line silently corrupts the destination filename instead of erroring).
4. The board auto-reloads after each copy batch — batch changes into as few sync runs as possible.

The CircuitPythonSync extension's "CP Copy Files to Board" works here too (Exp16 currently sits at workspace folder index 0) and is fine for code-file updates; prefer the scripts for routine deploys. Its "CP Copy Libs to Board" is **not** used in this experiment — unfiltered whole-`lib/` copy (no exclude mechanism), and every extension copy triggers a full-volume `dot_clean` sweep on the live drive.

Clean-slate reset (destructive): `import storage; storage.erase_filesystem()` at the board REPL — the verified-clean path. Do **not** host-side-delete `lib/` on the live volume, and never cancel a copy mid-flight (if one stalls, eject cleanly and inspect before further writes).

**Exact bundle-library versions vendored in `lib/`** are recorded in [`requirements.txt`](requirements.txt) (`adafruit_ticks==1.1.7`, `asyncio==3.1.1`, via `circup freeze -r`). The `.mpy` files themselves are the pin — gitignored bundle copies, shipped as-is by the sync script; re-download from the Adafruit Community Bundle if lost.

## Status

**First milestone (async 5×5 display + async button events) confirmed on-device 2026-09-13** on UID `0740D10F1BE9` (Stages 0–3: Tier 1, Tier 2 display/K1, button pumps cancelling an in-flight animation/K3). **Button API (current):** one object per physical module — `OnboardButtons()` (A/B) and `PlanetXButtonSensor(c_pin=..., d_pin=...)` (C/D); extra PlanetX sensors are extra instances. Host `pytest` is green on that API (suite does not import `board` / `display.core`). `code_stage3.py` matches it; on-device re-run of that script is pending. Per-stage scripts stay as siblings; `.vscode/cpfiles.txt` switches which one deploys to `/code.py` (see `§ Deploy` step 3).

Separate, still-open thread: a font inter-glyph-spacing fix (design converged, implementation Phases 1-3 landed and host-green, Phase 4 `core.py` cutover gated on an explicit go-ahead) — not required for the first-milestone claim above.

Student-API stability target (5×5 → later 8×8): [`Notes/student-api-portability.md`](Notes/student-api-portability.md).

## Folder structure

```
lib/display/       5×5 display package (copy of Exp14; work here, not in Exp14)
lib/buttons.py      Async per-module dispatchers (`PushButton`, `Button`, `ButtonPair`, `OnboardButtons`, `PlanetXButtonSensor`)
code_stage0-3.py    Frozen, on-device-confirmed test-stage scripts (replay via cpfiles.txt)
scripts/            Human-run deploy + font-build scripts (see § Deploy)
.vscode/            Per-experiment CircuitPythonSync config + tasks.json + cpfiles.txt
tests/              Host pytest (no board / no display.core); see tests/README.md
Notes/              Human spec + BananaPi photos (CC BY-SA, unmodified)
```

A local `ai-notes/` folder may exist as a gitignored working store; this tree does not depend on it.

## Further reading

| What | Where |
|------|--------|
| Display package architecture | [`lib/display/README.md`](lib/display/README.md) |
| Host tests (local interpreter path) | [`tests/README.md`](tests/README.md) |
| Spec / working prefs | [`Notes/overall_goal.md`](Notes/overall_goal.md) |
| Student-API portability (5×5 → 8×8) | [`Notes/student-api-portability.md`](Notes/student-api-portability.md) |
| Exp14 vs. Exp16 `lib/display/` divergence (maintainer-facing) | [`Notes/exp14-divergence.md`](Notes/exp14-divergence.md) |
| Goldfinger pinout (CC BY-SA) | [`Notes/bpi_bit_v2_goldfinger.jpg`](Notes/bpi_bit_v2_goldfinger.jpg) |
| Board interface photo (CC BY-SA) | [`Notes/bpi_bit_v2_interface_en.jpg`](Notes/bpi_bit_v2_interface_en.jpg) |
| Firmware | [circuitpython.org/board/bpi_bit_s2](https://circuitpython.org/board/bpi_bit_s2/) |
