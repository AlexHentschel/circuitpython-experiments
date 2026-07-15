# Session Log — circuitpython-exp15-microbit

Per-project session memory for **exp15** (RP2350 bit-board micro:bit alternative, CircuitPython; hardware shared with exp11). Behavioral/process directives: `../../universal/`. Domain knowledge: `../../concepts/`. Roster + routing: `../_INDEX.md`. Technical artifacts live in the exp15 repo folder, linked from `CONTEXT.md`.

## Sessions
## 2026-06-07: Session 9 — [exp15] (project bootstrap: blink sanity check)

- Context: new experiment `2026-06_Exp15_RP2350-Bit-Board_Microbit-v01` — end-goal of the stream is a Python-programmable micro:bit alternative. Hardware identical to Exp11 (RP2350 bit board, de-soldered 5x5 LED matrix, wires on the pads). Venv `/Users/alex/Development/PythonVEs/CircuitPython_3.13_VsCode`.
- Artifacts created (folder bootstrapped from the Exp11 template):
  - `code.py` — Milestone 1 blink of an external LED on `LED_Col1 == GP2` (active-high through the on-board 1K R1_LED resistor; built-in modules only, no `lib/` needed). Pin map confirmed from `docs/removed-LED-matrix-wiring.png`.
  - `.vscode/{settings.json,tasks.json,cpfiles.txt}` — mirror of Exp11: venv interpreter path; `pyserial-miniterm` serial-monitor tasks (MS Serial Monitor ext broken in Cursor); CircuitPythonSync copy manifest.
  - `.circuitpyignore`, `lib/README.md` (empty-lib placeholder), `README.md` (hardware + pin map + Milestone 1 wiring/run + serial-monitor + circup instructions).
  - `CircuitPy_VSCode.code-workspace`: added Exp15 folder entry (top, name "Exp15: micro:bit alternative (RP2350)").
- Technical notes `[exp15]`:
  - `LED_Col1`=GP2, `LED_Col2`=GP3, `LED_Col3`=GP4, `LED_Col4`=GP5, `LED_Col5`=GP25 (each through on-board 1K). Rows GP7/8/9/21/22 (no resistor). GP0/GP1 = Button A/B (not free). Same as Exp11 — `evidence-supported` via Exp11 CONTEXT_HANDOFF + the wiring image.
  - Board not plugged in at setup time (no `/Volumes/CIRCUITPY`, no `/dev/tty.usbmodem*`) — setup only, not yet on-device verified.
- Open: on-device run of the blink (LED + serial output) pending board connection.
