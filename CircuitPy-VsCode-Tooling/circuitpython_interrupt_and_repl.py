#!/usr/bin/env python3
"""
Interrupt running CircuitPython code and open interactive REPL.

This script:
1. Connects to CircuitPython serial port
2. Sends Ctrl-C twice to interrupt running code
3. Launches miniterm for interactive REPL session

Usage:
    python circuitpython_interrupt_and_repl.py <port>
    python circuitpython_interrupt_and_repl.py /dev/cu.usbmodem0740D10F1BE91

Exit codes:
    0 - Success
    1 - Invalid arguments
    2 - Serial port error
    3 - Unexpected error
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time

import serial


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Interrupt CircuitPython and open REPL",
        epilog="Examples:\n"
        "  macOS:   %(prog)s /dev/cu.usbmodem0740D10F1BE91\n"
        "  Linux:   %(prog)s /dev/ttyACM0\n"
        "  Windows: %(prog)s COM3",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "port",
        help="Serial port device path (e.g., /dev/cu.usbmodem*, COM3)",
    )
    return parser.parse_args()


def interrupt_circuitpython(port: str, baudrate: int = 115200) -> None:
    """
    Send interrupt sequence to CircuitPython board.
    Uses hardware reset (DTR toggle) if software interrupt fails.
    
    Parameters
    ----------
    port : str
        Serial port path
    baudrate : int
        Baud rate (default: 115200)
    """
    print(f"Interrupting CircuitPython on '{port}'...")
    
    try:
        with serial.Serial(port, baudrate, timeout=1) as ser:
            # Strategy 1: Hardware reset (most reliable for tight loops)
            print("Attempting hardware reset (DTR toggle)...")
            ser.dtr = False
            time.sleep(0.1)
            ser.dtr = True
            time.sleep(0.5)  # Wait for boot
            
            # Drain boot messages
            ser.reset_input_buffer()
            
            # Strategy 2: Send interrupt signals during boot window
            print("Sending interrupt signals (Ctrl-C × 8)...")
            for i in range(4):
                ser.write(b"\x03\x03")  # Two Ctrl-C per iteration
                time.sleep(0.2)
            
            # Send newline to get clean prompt
            ser.write(b"\r\n")
            time.sleep(0.3)
            
            # Try to read response to verify REPL is active
            ser.timeout = 2
            response = ser.read(2000).decode('utf-8', errors='ignore')
            
            if '>>>' in response:
                print("✓ Hardware reset successful - REPL prompt detected")
            elif 'Auto-reload' in response or 'CircuitPython' in response:
                # Board rebooted, send one more interrupt
                print("Board rebooted, sending final interrupt...")
                ser.write(b"\x03\x03\r\n")
                time.sleep(0.5)
                response = ser.read(1000).decode('utf-8', errors='ignore')
                if '>>>' in response:
                    print("✓ REPL prompt detected")
                else:
                    print("⚠ Continuing (you may need to press Ctrl-C manually in miniterm)")
            else:
                print("⚠ Response unclear, continuing (press Ctrl-C in miniterm if needed)")
            
    except serial.SerialException as e:
        print(f"ERROR: Failed to access serial port '{port}'", file=sys.stderr)
        print(f"Reason: {e}", file=sys.stderr)
        print("\nTroubleshooting:", file=sys.stderr)
        print("  - Close all other serial monitor programs", file=sys.stderr)
        print("  - Verify board is connected", file=sys.stderr)
        print("  - Check port path is correct", file=sys.stderr)
        if sys.platform.startswith("linux"):
            print("  - Linux: Ensure user is in 'dialout' group", file=sys.stderr)
        raise


def launch_miniterm(port: str, baudrate: int = 115200) -> int:
    """
    Launch miniterm for interactive REPL session.
    
    Parameters
    ----------
    port : str
        Serial port path
    baudrate : int
        Baud rate (default: 115200)
        
    Returns
    -------
    int
        Miniterm exit code
    """
    print(f"\nLaunching miniterm on '{port}'...")
    print("Controls: Ctrl-] to exit, Ctrl-D to reload\n")
    
    # Launch miniterm using subprocess
    cmd = [sys.executable, "-m", "serial.tools.miniterm", port, str(baudrate)]
    
    try:
        # Use exec-style replacement to give user direct control
        os.execvp(sys.executable, cmd)
        # Note: This line never executes if exec succeeds
        return 0
    except Exception as e:
        print(f"ERROR: Failed to launch miniterm", file=sys.stderr)
        print(f"Reason: {e}", file=sys.stderr)
        return 3


def main() -> int:
    """Main entry point."""
    try:
        args = parse_args()
        
        # Step 1: Interrupt running code
        interrupt_circuitpython(args.port)
        
        # Step 2: Launch miniterm (this replaces current process)
        return launch_miniterm(args.port)
        
    except serial.SerialException:
        return 2
    except KeyboardInterrupt:
        print("\n✗ Interrupted by user", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 3


if __name__ == "__main__":
    sys.exit(main())
