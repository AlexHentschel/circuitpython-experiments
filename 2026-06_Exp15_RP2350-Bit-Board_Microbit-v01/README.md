# Experiment 15 -- RP2350 Bit Board as a micro:bit Alternative (v01)

First step of a multi-experiment stream whose end goal is a **micro:bit
alternative programmable in Python**. This experiment starts with bring-up:
verifying the toolchain and board with a single blinking LED, then growing
toward micro:bit-style features.

Hardware platform is **identical to Exp11**
(`2026-03_Exp11_Ws2812_with_CPy_RP2350-Bit-Board`), including the board
modifications (de-soldered LED matrix, wires soldered to the pads).

## Hardware


| Item        | Detail                                                                                                             |
| ----------- | ------------------------------------------------------------------------------------------------------------------ |
| MCU board   | **RP2350 bit board** (RP2350A + 4 MB flash, micro:bit V2 form factor)                                              |
| Firmware    | CircuitPython **10.1.3** for Raspberry Pi Pico 2 ([download](https://circuitpython.org/board/raspberry_pi_pico2/)) |
| Board ID    | `raspberry_pi_pico2` (no dedicated RP2350-bit-board image exists)                                                  |
| Power       | RP2350 powered via its own USB port                                                                                |
| IDE         | Cursor + CircuitPythonSync extension (`padgettholdings`) on macOS 26.3                                             |
| Python venv | `/Users/alex/Development/PythonVEs/CircuitPython_3.13_VsCode/bin/python`                                           |


### Board modifications (inherited from Exp11)

The original 5x5 **Charlieplexed LED matrix was de-soldered**.
Breadboard-friendly wires were soldered to the pads. The former column drivers
reach their GPIOs through **1K series resistors (R1-R5_LED)** still on the board.

## GPIO Pin Map (former LED matrix)

See `docs/removed-LED-matrix-wiring.png` for the full net map.


| Function                                       | GPIO pins                                                                 |
| ---------------------------------------------- | ------------------------------------------------------------------------- |
| Column drivers (R1-R5_LED, 1K series resistor) | **LED_Col1=GP2**, LED_Col2=GP3, LED_Col3=GP4, LED_Col4=GP5, LED_Col5=GP25 |
| Row drivers (no series resistor)               | GP7, GP8, GP9, GP21, GP22                                                 |


### On-board buttons (do NOT use as outputs)


| Button   | GPIO | micro:bit edge pad**Hardware setup (active-high, 1 external LED):** |
| -------- | ---- | ------------------------------------------------------------------- |
| Button A | GP0  | small pad 6                                                         |
| Button B | GP1  | small pad 12                                                        |


> GPIO numbers on this board do **not** match the micro:bit pad numbers.

## Milestone 1 -- Blink an external LED on LED_Col1 / GP2 (`code.py`)

Sanity check: confirm board, toolchain, and a soldered pad wire all work.

**Hardware setup (active-high, 1 external LED):**

```
LED_Col1 wire (GP2, via on-board 1K) ──► LED anode (+, long leg)
LED cathode (-, short leg) ───────────► RP2350 GND
```

- Connect the external LED across the soldered **LED_Col1** wire and any board **GND**.
- No external resistor -- the on-board 1K (R1_LED) limits current to ~1.5 mA at 3.3 V.
- `GP2` HIGH = LED on. The LED is **dim** by design (1K); that's expected for a sanity check.

**How to run:**

1. Plug in the RP2350 via USB. CircuitPythonSync uploads `code.py`.
2. Open a serial monitor (115200 baud) -- see below.
3. The LED blinks ~1 Hz; the console prints the pin state each toggle.

## Serial monitor

The Microsoft Serial Monitor extension is broken in Cursor. Use the bundled
task instead (`pyserial-miniterm` from the venv):

- **Connect:** `Cmd+Shift+P` -> `Tasks: Run Task` -> `Serial Monitor (miniterm)`
- **Exit miniterm:** `Ctrl+]`
- **REPL:** `Ctrl-C` (stop program) / `Ctrl-D` (restart program)
- **Kill stuck session:** `Tasks: Run Task` -> `Serial Monitor: disconnect`

## Project layout


| File                    | Purpose                                             | Synced to board?        |
| ----------------------- | --------------------------------------------------- | ----------------------- |
| `code.py`               | Active script (Milestone 1 blink)                   | Yes                     |
| `lib/`                  | CircuitPython libraries (empty -- blink needs none) | Yes (via "Copy Libs")   |
| `docs/`                 | RP2350 bit board schematics + wiring image          | No (`.circuitpyignore`) |
| `README.md`             | This file                                           | No (`.circuitpyignore`) |
| `.vscode/cpfiles.txt`   | CircuitPythonSync file-copy manifest                | N/A                     |
| `.vscode/tasks.json`    | Serial monitor task (miniterm)                      | N/A                     |
| `.vscode/settings.json` | Folder-level settings (Python venv)                 | N/A                     |
| `.circuitpyignore`      | CircuitPythonSync exclusions                        | N/A                     |


## Library installation via `circup`

Not needed for Milestone 1. For later milestones, libraries install directly
into the workspace `lib/` (no board required):

```bash
/Users/alex/Development/PythonVEs/CircuitPython_3.13_VsCode/bin/circup \
  --path /Users/alex/Development/VsCode/CircuitPython/2026-06_Exp15_RP2350-Bit-Board_Microbit-v01 \
  --board-id raspberry_pi_pico2 --cpy-version 10.1.3 \
  install <library_name>
```

CircuitPythonSync then syncs `lib/` to the board via "Copy Libs to Board".