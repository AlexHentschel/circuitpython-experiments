"""Read-only USB-serial log tap for the BPI-Bit-S2 (or any CircuitPython board enumerating as
a USB CDC modem on macOS).

Purpose: let an AI agent (or a human, from a plain shell) capture a bounded window of the
board's serial console output -- CircuitPython's REPL banner, print() output, tracebacks --
without an interactive terminal session. This is the non-interactive sibling of the
"Serial Monitor (miniterm)" VS Code task in this experiment's `.vscode/tasks.json`: that task
is for a human watching an open, blocking terminal panel; this script is for a one-shot,
bounded capture that returns.

Read-only guarantee: this script never calls `Serial.write()` / never sends bytes to the
board. It only opens the port and reads. Safe to run at any time while the board is attached
without risking an accidental keypress/command reaching the REPL.

Dependency: `pyserial` (the same package that provides `pyserial-miniterm`). Not stdlib --
install into your own scratch/tooling venv, e.g. the one already used for this experiment's
tooling. This script does not hardcode which Python/venv runs it; any interpreter with
`pyserial` importable works.

Usage:
    python3 read_serial_log.py [--port PORT] [--baud BAUD] [--duration SECONDS] [--max-lines N]

    --port          Serial device path. Default: auto-detect the first port whose USB
                     VID matches Espressif (0x303A) or Adafruit (0x239A), falling back to
                     the first /dev/tty.usbmodem* / /dev/cu.usbmodem* match.
    --baud          Default 115200 (CircuitPython's standard console baud rate).
    --duration      Capture window in seconds. Default 5.0. Use 0 for "read until
                     --max-lines is hit or EOF", but note a live board's console rarely EOFs.
    --max-lines     Optional cap on lines captured, independent of --duration.

Exit codes:
    0  ran and captured >=0 lines (an empty capture is not an error -- the board may be idle)
    1  no matching serial port found
    2  pyserial not importable
"""

from __future__ import annotations

import argparse
import glob
import sys
import time

try:
    import serial  # type: ignore[import-untyped]
    from serial.tools import list_ports  # type: ignore[import-untyped]
except ImportError:
    print(
        "ERROR: pyserial not importable in this interpreter. Install it into your tooling "
        "venv, e.g.: <venv>/bin/pip install pyserial",
        file=sys.stderr,
    )
    sys.exit(2)

# USB VIDs seen on CircuitPython boards in this workspace (Espressif ESP32-S2/S3 boards,
# Adafruit SAMD/RP2040 boards). Extend if a new vendor board shows up.
_KNOWN_VIDS = {0x303A, 0x239A}


def _autodetect_port() -> str | None:
    """Return the most likely CircuitPython serial port, or None if none is found.

    Preference order: (1) a USB CDC device whose VID matches a known CircuitPython vendor,
    (2) the first /dev/tty.usbmodem* or /dev/cu.usbmodem* glob match (macOS-specific; this
    mirrors the same glob the "Serial Monitor (miniterm)" VS Code task uses).
    """
    for port_info in list_ports.comports():
        if port_info.vid in _KNOWN_VIDS:
            return port_info.device
    for pattern in ("/dev/tty.usbmodem*", "/dev/cu.usbmodem*"):
        matches = sorted(glob.glob(pattern))
        if matches:
            return matches[0]
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--port", default=None, help="Serial device path (default: auto-detect)")
    parser.add_argument("--baud", type=int, default=115200, help="Baud rate (default: 115200)")
    parser.add_argument(
        "--duration", type=float, default=5.0, help="Capture window in seconds (default: 5.0)"
    )
    parser.add_argument(
        "--max-lines", type=int, default=None, help="Optional cap on captured lines"
    )
    args = parser.parse_args()

    port = args.port or _autodetect_port()
    if port is None:
        print(
            "ERROR: no usbmodem serial device found. Is the board plugged in and enumerated? "
            "(check `ls /Volumes/` for CIRCUITPY and `ls /dev/cu.usbmodem*`)",
            file=sys.stderr,
        )
        return 1

    print(f"# reading {port} at {args.baud} baud for {args.duration:.1f}s (read-only, no writes)")
    line_count = 0
    deadline = time.monotonic() + args.duration if args.duration > 0 else None
    with serial.Serial(port, args.baud, timeout=0.5) as ser:
        while True:
            if deadline is not None and time.monotonic() >= deadline:
                break
            if args.max_lines is not None and line_count >= args.max_lines:
                break
            raw = ser.readline()  # read-only; this script never calls ser.write()
            if not raw:
                continue  # timeout with no data -- keep polling until the deadline
            timestamp = time.strftime("%H:%M:%S")
            text = raw.decode("utf-8", errors="replace").rstrip("\r\n")
            print(f"[{timestamp}] {text}")
            line_count += 1

    print(f"# captured {line_count} line(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
