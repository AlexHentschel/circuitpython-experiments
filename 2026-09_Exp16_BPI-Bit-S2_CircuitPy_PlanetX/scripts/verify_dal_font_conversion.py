"""Verify that the pinned DAL ``pendolino3`` source reconstructs ``_COLUMN_MAJOR``.

Host-only; never imported or deployed on-device. Fetches Lancaster
``MicroBitFont.cpp`` at a commit-SHA pin, integrity-checks the file hash,
converts DAL row-bytes to column-major, and diffs the result against
``lib/display/font_makecode_5/glyphs.py``'s existing ``_COLUMN_MAJOR``.

This script is verify-only: it does not rewrite ``glyphs.py``.

Usage (from this experiment's folder, any Python 3 with stdlib urllib):

    python3 scripts/verify_dal_font_conversion.py

Exit codes:
    0  converted bytes match ``_COLUMN_MAJOR`` (475/475)
    1  mismatch, fetch/hash/parse failure, or import error
"""

from __future__ import annotations

import sys
from pathlib import Path

EXPERIMENT_ROOT = Path(__file__).resolve().parent.parent
LIB_ROOT = EXPERIMENT_ROOT / "lib"

# Same-directory helper (scripts/ is not a package).
sys.path.insert(0, str(Path(__file__).resolve().parent))
import dal_pendolino3  # noqa: E402


def _load_stored_column_major() -> bytes:
    sys.path.insert(0, str(LIB_ROOT))
    from display.font_makecode_5.glyphs import _COLUMN_MAJOR  # type: ignore[import-not-found]

    return _COLUMN_MAJOR


def main() -> int:
    print(f"Fetching {dal_pendolino3.DAL_URL}")
    try:
        converted = dal_pendolino3.load_column_major()
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    try:
        stored = _load_stored_column_major()
    except Exception as exc:
        print(f"FAIL: could not import glyphs._COLUMN_MAJOR: {exc}", file=sys.stderr)
        return 1

    if converted == stored:
        print(
            f"OK: DAL pendolino3 @ {dal_pendolino3.DAL_COMMIT[:12]}… → column-major "
            f"matches glyphs._COLUMN_MAJOR ({len(converted)}/{len(stored)} bytes)"
        )
        return 0

    first = next(
        (i for i, (a, b) in enumerate(zip(converted, stored)) if a != b),
        min(len(converted), len(stored)),
    )
    print(
        f"FAIL: converted {len(converted)} bytes vs stored {len(stored)} bytes; "
        f"first mismatch at index {first} "
        f"(converted=0x{converted[first]:02x}, stored=0x{stored[first]:02x})",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
