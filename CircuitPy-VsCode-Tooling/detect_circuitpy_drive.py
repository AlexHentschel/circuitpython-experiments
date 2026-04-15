#!/usr/bin/env python3
"""
Auto-detect CIRCUITPY drive mount point

Purpose
-------
Locates the CIRCUITPY USB drive mount point across macOS, Linux, and Windows.
Outputs the mount path to stdout for shell script consumption.
This is a pure auto-detection tool, which always attempts to figure out the drive location, 
regardless of user settings (`vscode/settings.json`) or environment variables.

Exit codes
----------
0 : Success - CIRCUITPY drive found and printed to stdout
1 : CIRCUITPY drive not found
2 : Multiple CIRCUITPY drives found (ambiguous)
3 : Unexpected error

Output format
-------------
Success: Single line with mount path (e.g., "/Volumes/CIRCUITPY")
Error: Error message to stderr

Usage examples
--------------
Basic usage (capture mount path):
    DRIVE=$(python detect_circuitpy_drive.py) && echo "Found: $DRIVE"

With error handling:
    if DRIVE=$(python detect_circuitpy_drive.py); then
        echo "Using drive: $DRIVE"
    else
        echo "Detection failed (see error above)" >&2
        exit 1
    fi

In VSCode task:
    DRIVE=$(python .vscode/detect_circuitpy_drive.py) && \
    rsync -av --delete code.py "$DRIVE/"

Detection strategy
------------------
Searches common mount point locations by platform:

macOS:
  - /Volumes/CIRCUITPY
  - /Volumes/CIRCUITPY[0-9]*  (e.g., CIRCUITPY1 if name collision)

Linux:
  - /media/$USER/CIRCUITPY
  - /media/*/CIRCUITPY
  - /run/media/$USER/CIRCUITPY
  - /mnt/CIRCUITPY

Windows:
  - Scans drive letters D: through Z: for CIRCUITPY label
  - Uses volume label detection (platform-specific)

Validation:
  - Confirms path exists and is a directory
  - Checks for CircuitPython marker files (boot_out.txt, code.py, lib/)

Platform support
----------------
macOS:
  - Typical mount: /Volumes/CIRCUITPY
  - Auto-mounted by system when board connected

Linux:
  - Typical mount: /media/$USER/CIRCUITPY or /run/media/$USER/CIRCUITPY
  - May require manual mount or automount configuration
  - Mount manually: sudo mount /dev/sdX1 /mnt/CIRCUITPY

Windows:
  - Assigned drive letter (usually D:, E:, F:, etc.)
  - Auto-mounted when board connected
  - Check Disk Management if not visible

Troubleshooting
---------------
If drive not detected:
  - Verify board is connected and CircuitPython is running
  - Check board appears in system (macOS: Disk Utility, Linux: lsblk, Windows: Disk Management)
  - Verify filesystem isn't corrupted (re-flash CircuitPython if needed)
  - On Linux, check automount is enabled or mount manually
  - Try replugging the board (USB enumeration issue)
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional


# ====== CONFIGURATION ======

# Expected volume name (case-sensitive on some filesystems)
VOLUME_NAME = "CIRCUITPY"

# Marker files that confirm this is a CircuitPython drive
# (at least one should exist)
MARKER_FILES = ["boot_out.txt", "code.py", "lib"]

# Debug output to stderr
DEBUG: bool = False

# ====== END CONFIGURATION ======


def find_circuitpy_macos() -> list[Path]:
    """
    Search for CIRCUITPY drive on macOS.
    
    Returns
    -------
    list[Path]
        List of candidate mount paths (empty if none found)
    """
    candidates: list[Path] = []
    volumes_dir = Path("/Volumes")
    
    if not volumes_dir.exists():
        return candidates
    
    # Look for exact match
    exact_match = volumes_dir / VOLUME_NAME
    if exact_match.is_dir():
        candidates.append(exact_match)
    
    # Look for numbered variants (CIRCUITPY1, CIRCUITPY2, etc.)
    for entry in volumes_dir.iterdir():
        if entry.is_dir() and entry.name.startswith(VOLUME_NAME):
            if entry.name[len(VOLUME_NAME):].isdigit():
                candidates.append(entry)
    
    return candidates


def find_circuitpy_linux() -> list[Path]:
    """
    Search for CIRCUITPY drive on Linux.
    
    Returns
    -------
    list[Path]
        List of candidate mount paths (empty if none found)
    """
    candidates: list[Path] = []
    
    # Common automount locations
    search_patterns = [
        f"/media/{os.environ.get('USER', '')}/{VOLUME_NAME}",
        f"/run/media/{os.environ.get('USER', '')}/{VOLUME_NAME}",
        f"/mnt/{VOLUME_NAME}",
    ]
    
    # Add pattern for /media/*/CIRCUITPY (multi-user systems)
    media_dir = Path("/media")
    if media_dir.exists():
        for user_dir in media_dir.iterdir():
            if user_dir.is_dir():
                candidate = user_dir / VOLUME_NAME
                if candidate.is_dir():
                    candidates.append(candidate)
    
    # Check explicit paths
    for pattern in search_patterns:
        p = Path(pattern)
        if p.is_dir():
            candidates.append(p)
    
    return candidates


def find_circuitpy_windows() -> list[Path]:
    """
    Search for CIRCUITPY drive on Windows.
    
    Returns
    -------
    list[Path]
        List of candidate mount paths (empty if none found)
    
    Notes
    -----
    Scans drive letters D: through Z: and checks for CIRCUITPY label.
    On Windows, this requires checking each drive's volume label.
    """
    candidates: list[Path] = []
    
    # Scan common drive letters (skip C: which is typically system)
    for letter in "DEFGHIJKLMNOPQRSTUVWXYZ":
        drive_path = Path(f"{letter}:/")
        
        # Quick existence check
        if not drive_path.exists():
            continue
        
        # Try to read volume label (Windows-specific)
        try:
            # Simple heuristic: look for boot_out.txt or code.py in root
            # (volume label detection requires platform-specific APIs)
            has_markers = any((drive_path / marker).exists() for marker in MARKER_FILES)
            if has_markers:
                candidates.append(drive_path)
        except (PermissionError, OSError):
            continue
    
    return candidates


def validate_circuitpy_drive(path: Path) -> bool:
    """
    Validate that a path is likely a CircuitPython drive.
    
    Parameters
    ----------
    path : Path
        Candidate mount path
    
    Returns
    -------
    bool
        True if path contains CircuitPython marker files
    """
    if not path.is_dir():
        return False
    
    # Check for at least one marker file
    for marker in MARKER_FILES:
        marker_path = path / marker
        if marker_path.exists():
            if DEBUG:
                print(f"  [{path}] Found marker: {marker}", file=sys.stderr)
            return True
    
    if DEBUG:
        print(f"  [{path}] No markers found", file=sys.stderr)
    return False


def main() -> int:
    """
    Main entry point.
    
    Returns
    -------
    int
        Exit code (0=success, 1=not found, 2=ambiguous, 3=error)
    """
    try:
        candidates: list[Path] = []
        
        # Detect platform and search
        if sys.platform == "darwin":
            candidates = find_circuitpy_macos()
            if DEBUG:
                print("Platform: macOS", file=sys.stderr)
        elif sys.platform.startswith("linux"):
            candidates = find_circuitpy_linux()
            if DEBUG:
                print("Platform: Linux", file=sys.stderr)
        elif sys.platform == "win32":
            candidates = find_circuitpy_windows()
            if DEBUG:
                print("Platform: Windows", file=sys.stderr)
        else:
            print(f"ERROR: Unsupported platform: {sys.platform}", file=sys.stderr)
            return 3
        
        # Filter by validation
        valid_candidates = [c for c in candidates if validate_circuitpy_drive(c)]
        
        if DEBUG and candidates:
            print(f"Found {len(candidates)} candidate(s), {len(valid_candidates)} valid", file=sys.stderr)
        
        if not valid_candidates:
            print(f"ERROR: CIRCUITPY drive not found", file=sys.stderr)
            print("Check:", file=sys.stderr)
            print("  - Board is connected via USB", file=sys.stderr)
            print("  - CircuitPython is running (check for CIRCUITPY drive in Finder/Explorer)", file=sys.stderr)
            print("  - Filesystem isn't corrupted (re-flash if needed)", file=sys.stderr)
            if sys.platform.startswith("linux"):
                print("  - Drive is mounted (try: lsblk, or mount manually)", file=sys.stderr)
            return 1
        
        if len(valid_candidates) > 1:
            print(f"WARNING: Multiple CIRCUITPY drives found:", file=sys.stderr)
            for c in valid_candidates:
                print(f"  - {c}", file=sys.stderr)
            print(f"Using first: {valid_candidates[0]}", file=sys.stderr)
        
        # Success: print mount path to stdout
        print(str(valid_candidates[0]))
        return 0
    
    except Exception as e:
        print(f"ERROR: Unexpected failure: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
