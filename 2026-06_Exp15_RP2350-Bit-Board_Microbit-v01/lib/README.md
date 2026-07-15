CircuitPython libraries and project modules.

The blink sanity check (`code.py`) uses only built-in modules (`board`,
`digitalio`, `time`) -- no external libraries needed, so this folder is empty.

When a later milestone needs a library, install it here with circup
(no board required -- installs directly into this workspace `lib/`):

  /Users/alex/Development/PythonVEs/CircuitPython_3.13_VsCode/bin/circup \
    --path /Users/alex/Development/VsCode/CircuitPython/2026-06_Exp15_RP2350-Bit-Board_Microbit-v01 \
    --board-id raspberry_pi_pico2 --cpy-version 10.1.3 \
    install <library_name>
