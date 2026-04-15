"""
Auto-detect CircuitPython REPL serial port

Purpose
-------
Scans available serial ports and identifies the most likely CircuitPython device
using heuristic scoring. Outputs the port path to stdout for shell script consumption.
This is a pure auto-detection tool, which always attempts to figure out the serial port location,
regardless of user settings (`vscode/settings.json`) or environment variables.


Exit codes
----------
0 : Success - CircuitPython port detected and printed to stdout
1 : No serial ports found
2 : Multiple equally-scored candidates (ambiguous)
3 : Unexpected error

Output format
-------------
Success: Single line with port device path (e.g., "/dev/cu.usbmodem0740D10F1BE91")
Error: Error message to stderr

Usage examples
--------------
Basic usage (captures port in shell variable):
    PORT=$(python detect_circuitpy_port.py) && echo "Found: $PORT"

With error handling:
    if PORT=$(python detect_circuitpy_port.py); then
        echo "Using port: $PORT"
    else
        echo "Port detection failed (see error above)" >&2
        exit 1
    fi

In VSCode task (requires pyserial in selected Python environment):
    PORT=$(python .vscode/detect_circuitpy_port.py) && \
    python .vscode/circuitpython_soft_reload.py "$PORT"

Detection strategy
------------------
Ports are scored by:
- VID/PID match (configurable preference): +1000 points
- Device name patterns:
  * usbmodem (macOS): +200
  * ttyACM (Linux CDC): +180
  * ttyUSB (Linux UART): +120
  * COMx (Windows): +150
- Description keywords (CircuitPython, CDC, Adafruit, Espressif, etc.): +20-120
- USB presence: +10

Configuration
-------------
Set PREFERRED_VID/PREFERRED_PID below to strongly prefer specific hardware.
For ESP32-S2 BPI-Bit-S2: VID=0x303A, PID=0x80E6

Platform support
----------------
macOS:
  - Ports: /dev/cu.usbmodem*, /dev/tty.usbmodem*
  - Prefer cu.* for outbound connections
  - No special permissions needed

Linux:
  - Ports: /dev/ttyACM* (CDC), /dev/ttyUSB* (UART bridges)
  - Permissions: User must be in 'dialout' group or have udev rules
    Fix: sudo usermod -a -G dialout $USER (logout/login required)

Windows:
  - Ports: COM3, COM4, COM5, etc.
  - Check Device Manager → Ports (COM & LPT)
  - No special permissions typically needed

Prerequisites
-------------
- pyserial package installed in Python environment:
    pip install pyserial
- Find installed ports manually:
    python -m serial.tools.list_ports
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Optional

from serial.tools import list_ports


# ====== CONFIGURATION ======

# Preferred VID/PID for your CircuitPython board (set to None to disable)
# ESP32-S2 BPI-Bit-S2 defaults:
PREFERRED_VID: Optional[int] = 0x303A
PREFERRED_PID: Optional[int] = 0x80E6

# Verbosity: if True, print scoring details to stderr for debugging
DEBUG_SCORING: bool = False

# ====== END CONFIGURATION ======


@dataclass(frozen=True)
class PortCandidate:
    """Represents a discovered serial port with metadata."""
    device: str                # Port path (e.g., /dev/cu.usbmodem123)
    description: str           # Human-readable description
    manufacturer: str          # Manufacturer string (if available)
    vid: Optional[int]         # USB Vendor ID (hex)
    pid: Optional[int]         # USB Product ID (hex)
    hwid: str                  # Hardware ID string


def normalize(s: Optional[str]) -> str:
    """Safely normalize optional string to lowercase stripped string."""
    return (s or "").strip().lower()


def list_candidates() -> list[PortCandidate]:
    """
    Enumerate all available serial ports.
    
    Returns
    -------
    List of PortCandidate objects with normalized metadata.
    """
    candidates: list[PortCandidate] = []
    for p in list_ports.comports():
        candidates.append(
            PortCandidate(
                device=p.device,
                description=normalize(getattr(p, "description", "")),
                manufacturer=normalize(getattr(p, "manufacturer", "")),
                vid=getattr(p, "vid", None),
                pid=getattr(p, "pid", None),
                hwid=normalize(getattr(p, "hwid", "")),
            )
        )
    return candidates


def score_candidate(c: PortCandidate) -> int:
    """
    Compute heuristic score for a port candidate.
    
    Higher scores indicate higher likelihood of being the CircuitPython device.
    
    Parameters
    ----------
    c : PortCandidate
        Port to score
    
    Returns
    -------
    int
        Score (higher is better)
    """
    score = 0
    dev = c.device.lower()
    
    # Combined search text from all metadata fields
    desc_full = f"{c.description} {c.manufacturer} {c.hwid}"
    
    # Strong preference: exact VID/PID match
    if PREFERRED_VID is not None and PREFERRED_PID is not None:
        if c.vid == PREFERRED_VID and c.pid == PREFERRED_PID:
            score += 1000
            if DEBUG_SCORING:
                print(f"  [{c.device}] VID/PID match: +1000", file=sys.stderr)
    
    # Device name patterns (platform-specific)
    if "usbmodem" in dev:
        score += 200
        if DEBUG_SCORING:
            print(f"  [{c.device}] usbmodem: +200", file=sys.stderr)
    if "ttyacm" in dev:
        score += 180
        if DEBUG_SCORING:
            print(f"  [{c.device}] ttyacm: +180", file=sys.stderr)
    if "ttyusb" in dev:
        score += 120
        if DEBUG_SCORING:
            print(f"  [{c.device}] ttyusb: +120", file=sys.stderr)
    if dev.startswith("com") and dev[3:].isdigit():
        score += 150  # Windows COM ports
        if DEBUG_SCORING:
            print(f"  [{c.device}] COM port: +150", file=sys.stderr)
    
    # Description/manufacturer keyword scoring
    keywords = [
        ("circuitpython", 120),
        ("cdc", 60),
        ("usb serial", 60),
        ("adafruit", 60),
        ("espressif", 50),
        ("esp32", 50),
        ("cp210", 20),    # Common USB-UART bridges
        ("ch340", 20),
        ("ftdi", 20),
    ]
    for keyword, points in keywords:
        if keyword in desc_full:
            score += points
            if DEBUG_SCORING:
                print(f"  [{c.device}] keyword '{keyword}': +{points}", file=sys.stderr)
    
    # Mild preference for anything USB
    if "usb" in desc_full:
        score += 10
        if DEBUG_SCORING:
            print(f"  [{c.device}] USB: +10", file=sys.stderr)
    
    return score


def find_best_port(candidates: list[PortCandidate]) -> tuple[Optional[PortCandidate], int]:
    """
    Select the highest-scoring port candidate.
    
    Parameters
    ----------
    candidates : list[PortCandidate]
        Available ports
    
    Returns
    -------
    tuple[Optional[PortCandidate], int]
        (best_candidate, tied_count) where tied_count indicates how many
        candidates share the top score (1 = unique winner, >1 = ambiguous)
    """
    if not candidates:
        return None, 0
    
    scored = [(score_candidate(c), c) for c in candidates]
    scored.sort(key=lambda x: x[0], reverse=True)
    
    best_score = scored[0][0]
    best_candidate = scored[0][1]
    
    # Count how many candidates have the same top score
    tied_count = sum(1 for s, _ in scored if s == best_score)
    
    return best_candidate, tied_count


def main() -> int:
    """
    Main entry point.
    
    Returns
    -------
    int
        Exit code (0=success, 1=no ports, 2=ambiguous, 3=error)
    """
    try:
        candidates = list_candidates()
        
        if not candidates:
            print("ERROR: No serial ports found", file=sys.stderr)
            print("Check:", file=sys.stderr)
            print("  - Board is connected via USB", file=sys.stderr)
            print("  - Driver installed (if required)", file=sys.stderr)
            print("  - Permissions (Linux: dialout group)", file=sys.stderr)
            return 1
        
        best, tied_count = find_best_port(candidates)
        assert best is not None
        
        if DEBUG_SCORING or tied_count > 1:
            # Print all candidates with scores to stderr for debugging
            scored = [(score_candidate(c), c) for c in candidates]
            scored.sort(key=lambda x: x[0], reverse=True)
            
            print("Port candidates (ranked):", file=sys.stderr)
            for i, (s, c) in enumerate(scored, start=1):
                vidpid = f"{c.vid:#06x}/{c.pid:#06x}" if c.vid and c.pid else "n/a"
                mark = "→ " if c == best else "  "
                print(f"{mark}{i}. score={s:4d}  dev={c.device}  vid/pid={vidpid}", file=sys.stderr)
                print(f"      desc={c.description or '—'}", file=sys.stderr)
                print(f"      mfg={c.manufacturer or '—'}", file=sys.stderr)
        
        if tied_count > 1:
            print(f"WARNING: {tied_count} ports tied with same score", file=sys.stderr)
            print(f"Selecting first: {best.device}", file=sys.stderr)
            print("Consider setting PREFERRED_VID/PREFERRED_PID for disambiguation", file=sys.stderr)
            # Not an error, but flag it with exit code 2 if desired
            # For now, we'll proceed with code 0 since we made a choice
        
        # Success: print port path to stdout for shell consumption
        print(best.device)
        return 0
    
    except ImportError:
        print("ERROR: pyserial not installed", file=sys.stderr)
        print("Fix: pip install pyserial", file=sys.stderr)
        return 3
    except Exception as e:
        print(f"ERROR: Unexpected failure: {e}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
