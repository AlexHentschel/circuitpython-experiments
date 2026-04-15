"""
CircuitPython soft reload via serial port

Purpose
-------
Sends soft reload command to CircuitPython REPL over serial connection.
Stops running code and executes supervisor.reload() to restart with fresh code.

Exit codes
----------
0 : Success - reload command sent
1 : Invalid arguments
2 : Serial port error (busy, nonexistent, permission denied)
3 : Unexpected error

Usage
-----
Command-line:
    python circuitpython_soft_reload.py <port_path>

Examples:
    macOS:   python circuitpython_soft_reload.py /dev/cu.usbmodem0740D10F1BE91
    Linux:   python circuitpython_soft_reload.py /dev/ttyACM0
    Windows: python circuitpython_soft_reload.py COM3

With auto-detection (typical VSCode task usage):
    PORT=$(python detect_circuitpy_port.py) && \
    python circuitpython_soft_reload.py "$PORT"

In VSCode task (complete workflow):
    DRIVE=$(python .vscode/detect_circuitpy_drive.py) && \
    rsync -av --delete code.py "$DRIVE/" && \
    PORT=$(python .vscode/detect_circuitpy_port.py) && \
    python .vscode/circuitpython_soft_reload.py "$PORT"

Reload mechanism
----------------
1. Opens serial port (115200 baud, standard CircuitPython REPL speed)
2. Sends Ctrl-C twice (0x03 0x03) to interrupt running program and return to REPL
3. Sends: import supervisor; supervisor.reload()
4. supervisor.reload() is more reliable than Ctrl-D on some USB stacks

Why supervisor.reload() instead of Ctrl-D?
- Ctrl-D (0x04) soft-reboots but can be flaky on certain boards/USB implementations
- supervisor.reload() explicitly triggers code reload via CircuitPython API
- Both achieve the same goal; reload() is more deterministic

Prerequisites
-------------
- pyserial package installed:
    pip install pyserial
- No other program holding serial port open (close miniterm, serial monitors, etc.)

Platform notes
--------------
macOS:
  - Ports: /dev/cu.usbmodem*, /dev/tty.usbmodem*
  - Prefer cu.* for outbound connections
  - No special permissions needed

Linux:
  - Ports: /dev/ttyACM* (CDC), /dev/ttyUSB* (UART bridges)
  - Permissions: user must be in dialout group
    Fix: sudo usermod -a -G dialout $USER (logout/login required)

Windows:
  - Ports: COM3, COM4, COM5, etc.
  - Check Device Manager → Ports (COM & LPT)

Timing parameters
-----------------
Delays ensure REPL readiness and byte transmission completion.
Increase if reload fails intermittently (rare, typically indicates USB issues).

Troubleshooting
---------------
Port busy:
  - Close all serial terminals (miniterm, VSCode Serial Monitor, etc.)
  - Check: lsof <port_path> (macOS/Linux) or Resource Monitor (Windows)

Permission denied (Linux):
  - Add user to dialout: sudo usermod -a -G dialout $USER
  - Logout and login
  - Or use udev rules for specific device

Reload doesn't execute:
  - Verify correct port (run detect_circuitpy_port.py)
  - Check USB cable (try different cable/port)
  - Increase OPEN_DELAY_S or AFTER_BREAK_DELAY_S
  - Try manual REPL: screen <port> 115200, then Ctrl-C, Ctrl-D

Board not responding:
  - Hard reset board (power cycle or reset button)
  - Re-flash CircuitPython if filesystem corrupted
"""

from __future__ import annotations

import argparse
import sys
import time
import serial


# ====== CONFIGURATION ======

# CircuitPython REPL standard baud rate
BAUDRATE = 115200

# Timing delays (seconds): small delays help ensure the REPL is ready and receives the bytes.
# Adjust if experiencing intermittent reload failures
OPEN_DELAY_S = 0.2          # Wait after opening port (USB settling)
AFTER_BREAK_DELAY_S = 0.2   # Wait after Ctrl-C (REPL prompt ready)
AFTER_COMMAND_DELAY_S = 0.2 # Wait after reload command (transmission complete)

# ====== END CONFIGURATION ======


def soft_reload(port: str, baud: int = BAUDRATE) -> None:
    """
    Execute soft reload on CircuitPython device.
    
    Parameters
    ----------
    port : str
        Serial port device path (e.g., /dev/cu.usbmodem123, COM3)
    baud : int
        Baud rate (default: 115200 for CircuitPython)
    
    Raises
    ------
    serial.SerialException
        Port access error (busy, nonexistent, permission denied)
    """
    # timeout: keep short since we only write (don't block on reads)
    with serial.Serial(port, baud, timeout=1) as ser:
        time.sleep(OPEN_DELAY_S)
        
        # Interrupt running program and return to REPL
        # Sending Ctrl-C twice is CircuitPython convention for clean interrupt
        ser.write(b"\x03\x03")
        time.sleep(AFTER_BREAK_DELAY_S)
        
        # Execute supervisor reload (more reliable than Ctrl-D)
        ser.write(b"import supervisor; supervisor.reload()\r\n")
        time.sleep(AFTER_COMMAND_DELAY_S)


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns
    -------
    argparse.Namespace
        Parsed arguments with 'port' attribute
    """
    parser = argparse.ArgumentParser(
        description="Send soft reload command to CircuitPython REPL over serial",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  macOS:   %(prog)s /dev/cu.usbmodem0740D10F1BE91
  Linux:   %(prog)s /dev/ttyACM0
  Windows: %(prog)s COM3

With auto-detection:
  PORT=$(python detect_circuitpy_port.py) && %(prog)s "$PORT"
        """
    )
    parser.add_argument(
        "port",
        help="Serial port device path (e.g., /dev/cu.usbmodem*, /dev/ttyACM*, COM3)"
    )
    return parser.parse_args()


def main() -> int:
    """
    Main entry point.
    
    Returns
    -------
    int
        Exit code (0=success, 1=invalid args, 2=serial error, 3=unexpected error)
    """
    try:
        args = parse_args()
        soft_reload(args.port)
        print(f"Soft reload sent to {args.port}", file=sys.stderr)
        return 0
    
    except serial.SerialException as e:
        print(f"ERROR: Cannot access serial port: {args.port if 'args' in locals() else 'unknown'}", file=sys.stderr)
        print("Common causes:", file=sys.stderr)
        print("  - Port doesn't exist (check device path)", file=sys.stderr)
        print("  - Port is busy (close miniterm/serial monitors)", file=sys.stderr)
        print("  - Permission denied (Linux: add user to dialout group)", file=sys.stderr)
        print(f"Details: {e}", file=sys.stderr)
        return 2
    
    except SystemExit as e:
        # argparse exits with code 2 for invalid arguments
        return e.code if isinstance(e.code, int) else 1
    
    except Exception as e:
        print(f"ERROR: Unexpected failure: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
