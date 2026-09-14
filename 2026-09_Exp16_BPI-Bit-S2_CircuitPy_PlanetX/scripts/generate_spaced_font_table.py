"""Generate the interleaved trimmed-glyph table from the pinned Lancaster micro:bit Device Abstraction Layer [DAL] ``pendolino3`` font.

Host-only; never imported or deployed on-device. Reuses ``dal_pendolino3``'s
proven row-bytes → column-major conversion (same pin, same hash check), then
computes each glyph's authored occupied span and writes

    lib/display/font_makecode_5/spaced_glyphs.py

Record layout, ``WIDTH + 1`` bytes/glyph: ``[length, ink_0, ..., ink_{length-1}, unused...]``.
``needs_spacer`` is not stored; it is ``any(ink_bytes)`` at access time.

Ink-bearing glyphs: span is the columns that contain ink (leading/trailing
blank columns dropped). Space (the only all-zero printable glyph): authored
width 4, a per-font heuristic matching this font's common narrow-letter width
— not a ``WIDTH - 1`` formula. Unknown/out-of-range characters are not in this
table; the accessor handles them as a full-``WIDTH`` blank pass-through.

If the DAL-derived column-major bytes ever disagree with ``glyphs._COLUMN_MAJOR``,
this script refuses to write: the on-device-confirmed table wins, and the
divergence is a finding, not something to ship silently.

Usage (from this experiment's folder):

    python3 scripts/generate_spaced_font_table.py
"""

from __future__ import annotations

import sys
from pathlib import Path

EXPERIMENT_ROOT = Path(__file__).resolve().parent.parent
LIB_ROOT = EXPERIMENT_ROOT / "lib"
DEFAULT_OUTPUT = LIB_ROOT / "display" / "font_makecode_5" / "spaced_glyphs.py"

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dal_pendolino3  # noqa: E402

# Per-font authored width for space. Heuristic: match this font's common
# narrow-letter occupied width (49 of 94 ink-bearing glyphs are 4 columns).
# Re-derive for a future font from that font's own width distribution; do not
# treat this as ``FONT_WIDTH - 1``.
SPACE_AUTHORED_WIDTH = 4
SPACE_ORD = 32
ASCII_START = 32
ASCII_END = 126  # inclusive
HEX_LINE_BYTES = 34  # matches glyphs.py's wrap (~68 hex chars)


def _load_stored_column_major() -> bytes:
    sys.path.insert(0, str(LIB_ROOT))
    from display.font_makecode_5.glyphs import _COLUMN_MAJOR  # type: ignore[import-not-found]

    return _COLUMN_MAJOR


def authored_ink(col_bytes: bytes, code: int) -> bytes:
    """Return the authored occupied columns for one native-width glyph.

    Ink-bearing: uniquely determined by ink (drop blank lead/trail).
    Space: authored 4-column blank span. Any other all-zero glyph would be a
    full-width pass-through; this font has none besides space.
    """
    if any(col_bytes):
        skip_lead = 0
        while col_bytes[skip_lead] == 0:
            skip_lead += 1
        skip_trail = 0
        while col_bytes[-(skip_trail + 1)] == 0:
            skip_trail += 1
        return col_bytes[skip_lead : len(col_bytes) - skip_trail]
    if code == SPACE_ORD:
        return bytes(SPACE_AUTHORED_WIDTH)
    return col_bytes  # full native width, all-zero


def pack_record(ink: bytes, width: int = dal_pendolino3.FONT_WIDTH) -> bytes:
    """``[length, ink..., unused padding to width]`` — ``width + 1`` bytes."""
    if len(ink) > width:
        raise ValueError(f"ink length {len(ink)} exceeds native width {width}")
    length_prefix = bytes((len(ink),))  # 1-byte header whose value is n; comma → 1-tuple (litteral), specifies values not lenghts (of zero-filled array)
    occupied = ink  # n column-bytes of authored ink, packed as-is after the length
    padding = bytes(width - len(ink))  # width-n trailing 0x00; unused slots, fixed ink/pad field of `width`
    return length_prefix + occupied + padding  # [length, ink..., pad...]; always width+1 bytes


def build_spaced_table(column_major: bytes, width: int = dal_pendolino3.FONT_WIDTH) -> bytes:
    """Pack 95 interleaved records from native-width column-major glyphs."""
    n = dal_pendolino3.GLYPH_COUNT
    if len(column_major) != n * width:
        raise ValueError(f"column-major length {len(column_major)} != {n}×{width}")
    out = bytearray()
    for i in range(n):
        raw = column_major[i * width : (i + 1) * width]
        ink = authored_ink(raw, ASCII_START + i)
        rec = pack_record(ink, width)
        # Insurance: ink bytes equal the native glyph's occupied slice
        # (space: the leading SPACE_AUTHORED_WIDTH zeros of a blank glyph).
        if any(raw):
            start = next(idx for idx, b in enumerate(raw) if b)
            end = len(raw) - next(idx for idx, b in enumerate(reversed(raw)) if b)
            if raw[start:end] != ink:
                raise RuntimeError(f"glyph {ASCII_START + i} ink does not match _COLUMN_MAJOR slice")
        elif ASCII_START + i == SPACE_ORD:
            if ink != bytes(SPACE_AUTHORED_WIDTH) or any(raw):
                raise RuntimeError("space record is not a 4-column blank")
        out.extend(rec)
    return bytes(out)


def _hex_literal(data: bytes) -> str:
    hex_str = data.hex()
    chunk = HEX_LINE_BYTES * 2
    lines = [f'    "{hex_str[i : i + chunk]}"' for i in range(0, len(hex_str), chunk)]
    return "\n".join(lines)


def render_module(table: bytes, width: int = dal_pendolino3.FONT_WIDTH) -> str:
    stride = width + 1
    n = dal_pendolino3.GLYPH_COUNT
    if len(table) != n * stride:
        raise ValueError(f"table length {len(table)} != {n}×{stride}")
    commit = dal_pendolino3.DAL_COMMIT
    return f'''"""Trimmed MakeCode 5×5 glyph records for inter-glyph spacing.

GENERATED by ``scripts/generate_spaced_font_table.py``. Do not hand-edit.
Re-run that script to regenerate from the pinned Lancaster micro:bit Device Abstraction Layer [DAL] ``pendolino3`` source
(commit ``{commit}``).

Each glyph is a fixed ``WIDTH + 1``-byte record::

    [length, ink_0, ..., ink_{{length-1}}, unused...]

``length`` is the authored occupied span (ink-bearing glyphs: columns that
contain ink; space: 4 blank columns). ``needs_spacer`` is not stored; it is
``any(ink)`` at access time. Unknown/out-of-range characters are not in this
table.

MIT notice: ``LICENSE`` in this directory (Copyright 2016 BBC; Lancaster
University by arrangement with the BBC).
"""

from .._constants import WIDTH

_ASCII_START = 32
_ASCII_END = 126  # inclusive
_RECORD_STRIDE = WIDTH + 1

# Packed from DAL pendolino3 @ {commit[:12]}… . {n} glyphs × (WIDTH+1) bytes.
_SPACED_GLYPHS = bytes.fromhex(
{_hex_literal(table)}
)

if len(_SPACED_GLYPHS) != (_ASCII_END - _ASCII_START + 1) * _RECORD_STRIDE:
    raise RuntimeError("spaced glyph table length does not match ASCII range × stride")
'''


def _spot_check(table: bytes, width: int = dal_pendolino3.FONT_WIDTH) -> None:
    """Fail loudly if survey cases from the design/plan do not hold."""
    stride = width + 1

    def rec(ch: str) -> tuple[int, bytes, bool]:
        i = (ord(ch) - ASCII_START) * stride
        row = table[i : i + stride]
        length = row[0]
        ink = row[1 : 1 + length]
        return length, ink, any(ink)

    length, ink, needs = rec(" ")
    if not (length == SPACE_AUTHORED_WIDTH and ink == bytes(SPACE_AUTHORED_WIDTH) and not needs):
        raise RuntimeError(f"spot-check space failed: length={length} ink={ink.hex()} needs={needs}")

    length, ink, needs = rec(".")
    if not (length == 1 and needs and ink != b"\x00"):
        raise RuntimeError(f"spot-check '.' failed: length={length} ink={ink.hex()} needs={needs}")

    length, ink, needs = rec("7")
    if not (length == width and needs):
        raise RuntimeError(f"spot-check '7' failed: length={length} ink={ink.hex()} needs={needs}")

    print(f"spot-checks: space length={SPACE_AUTHORED_WIDTH} needs_spacer=False; '.' length=1 needs_spacer=True; '7' length={width} needs_spacer=True")


def main() -> int:
    print(f"Fetching {dal_pendolino3.DAL_URL}")
    try:
        converted = dal_pendolino3.load_column_major()
        stored = _load_stored_column_major()
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    if converted != stored:
        print(
            "FAIL: DAL-derived column-major disagrees with glyphs._COLUMN_MAJOR. Not writing a new table; the on-device-confirmed bytes win. Treat this as a standalone finding.",
            file=sys.stderr,
        )
        return 1

    try:
        table = build_spaced_table(converted)
        _spot_check(table)
        text = render_module(table)
        DEFAULT_OUTPUT.write_text(text)
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    print(f"wrote {DEFAULT_OUTPUT.relative_to(EXPERIMENT_ROOT)} ({len(table)} bytes, {dal_pendolino3.GLYPH_COUNT} records)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
