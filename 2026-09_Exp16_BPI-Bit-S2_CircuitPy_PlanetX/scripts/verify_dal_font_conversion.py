"""Verify that the pinned Lancaster micro:bit Device Abstraction Layer [DAL] ``pendolino3`` source reconstructs ``spaced_glyphs.py``.

Host-only; never imported or deployed on-device. Fetches Lancaster
``MicroBitFont.cpp`` at a commit-SHA pin, packs the trimmed glyph table, and
diffs that source against the committed ``lib/display/font_makecode_5/spaced_glyphs.py``.
It does not write the file.

Usage (from this experiment's folder, any Python 3 with stdlib urllib):

    python3 scripts/verify_dal_font_conversion.py

Exit codes:
    0  packed source matches the committed module
    1  mismatch, fetch/hash/parse failure, or import error
"""

from __future__ import annotations

import sys
from pathlib import Path

# Same-directory helpers (scripts/ is not a package).
sys.path.insert(0, str(Path(__file__).resolve().parent))
import dal_pendolino3  # noqa: E402
import generate_spaced_font_table as spaced  # noqa: E402


def main() -> int:
    print(f"Fetching {dal_pendolino3.DAL_URL}")
    try:
        converted = dal_pendolino3.load_column_major()
        text = spaced.render_module(spaced.build_spaced_table(converted))
        stored = spaced.DEFAULT_OUTPUT.read_text()
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    if text == stored:
        print(
            f"OK: DAL pendolino3 @ {dal_pendolino3.DAL_COMMIT[:12]}… → spaced table "
            f"matches {spaced.DEFAULT_OUTPUT.name}"
        )
        return 0

    print(
        f"FAIL: regenerated {spaced.DEFAULT_OUTPUT.name} does not match the committed file",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
