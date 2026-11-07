# Host tests

Run from the experiment root, on any desktop CPython with `pytest` and `pytest-asyncio`:

```bash
<path-to-venv>/bin/pytest
```

The suite does not import `board` or `display.core`. Do not pip-install `neopixel` or `adafruit_bitmap_font` into that venv.

In `lib/buttons.py` and `lib/planetx/`, the CircuitPython-only modules (`board`, `keypad`, `busio`, `analogio`, `neopixel`) are module-level names that are `None` outside CircuitPython. A test that needs one replaces it with a fake: `monkeypatch.setattr(buttons, "keypad", fake)` or `monkeypatch.setattr("planetx.light.analogio", fake)`. Forgetting the fake fails with an `AssertionError` that names the missing replacement; `planetx.ports` instead builds pin-less `J1`–`J4` / `I2C` objects (wiring data only).

## `<path-to-venv>` is machine-specific

Each **experiment checkout** chooses its own CPython virtual environment. Experiments under this workspace are reasonably self-contained; a clone of Exp16 need not share another experiment’s interpreter.

The path below is **only an example** from one development machine, to make `<path-to-venv>` tangible. It is not a requirement of this experiment. Another checkout may use a different location, OS, or Python minor version.

Example (this machine): Cursor on macOS 26, CPython 3.13 Miniconda at

`/Users/alex/Development/PythonVEs/CircuitPython_3.13_VsCode`

(The folder name is not the language. Blinka `board`/`keypad` in that venv is not CircuitPython.)

```bash
/Users/alex/Development/PythonVEs/CircuitPython_3.13_VsCode/bin/pytest
```
