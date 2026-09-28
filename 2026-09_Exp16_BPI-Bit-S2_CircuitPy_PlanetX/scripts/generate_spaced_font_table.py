"""Generate the interleaved trimmed-glyph table from the pinned Lancaster micro:bit Device Abstraction Layer [DAL] ``pendolino3`` font.

Host-only; never imported or deployed on-device. Reuses ``dal_pendolino3``'s
proven row-bytes → column-major conversion (same pin, same hash check), then
computes each glyph's authored occupied span and writes

    lib/display/font_makecode_5/spaced_glyphs.py

from ``scripts/templates/spaced_glyphs.py.in`` (stdlib ``string.Template``).

Record layout, ``WIDTH + 1`` bytes/glyph: ``[length, ink_0, ..., ink_{length-1}, unused...]``.
The feeder always inserts a spacer between characters (not stored in the table).

Ink-bearing glyphs: span is the columns that contain ink (leading/trailing
blank columns dropped). Space (the only all-zero printable glyph): authored
width 3; a following inter-glyph spacer, if any, supplies the fourth column.
Unknown/out-of-range characters are not in this table; the accessor draws
tofu (``ink._TOFU_INK``).

Source is the pinned DAL fetch (``dal_pendolino3.load_column_major``), not
``glyphs._COLUMN_MAJOR``. While that saved table is still live, agreement with
it is ``verify_dal_font_conversion.py``'s job.

Usage (from this experiment's folder):

    python3 scripts/generate_spaced_font_table.py
"""

from __future__ import annotations

import string
import sys
from pathlib import Path

EXPERIMENT_ROOT = Path(__file__).resolve().parent.parent
LIB_ROOT = EXPERIMENT_ROOT / "lib"
DEFAULT_OUTPUT = LIB_ROOT / "display" / "font_makecode_5" / "spaced_glyphs.py"
TEMPLATE_PATH = Path(__file__).resolve().parent / "templates" / "spaced_glyphs.py.in"

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dal_pendolino3  # noqa: E402

# Per-font authored width for space, not counting the inter-glyph spacer.
# Interior ``"A B"`` is then 3 blanks plus spacers around the space (five
# columns of gap, same as the former 4-column space with a spacer only after A).
# Do not treat this as ``FONT_WIDTH - 1``.
SPACE_AUTHORED_WIDTH = 3
SPACE_ORD = 32
ASCII_START = 32
ASCII_END = 126  # inclusive
HEX_LINE_BYTES = 34  # matches glyphs.py's wrap (~68 hex chars)


def authored_ink(col_bytes: bytes, code: int) -> bytes:
    """Return the occupied column bytes to store for one native-width glyph.

    ``col_bytes`` is one glyph at the font's native width (five column-bytes for
    pendolino3). Typical case: the glyph has ink, so leading and trailing all-zero
    columns are dropped and the remaining slice is the authored span.

    Space (``code == 32``) is all-zero but not empty: it is a 3-column blank span.
    A following inter-glyph spacer, if any, supplies the fourth column. Any other
    all-zero glyph would pass through at full native width; this font has none
    besides space.

    ``code`` is the ASCII code point (32..126), used only to recognise space.
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
    """Pack one interleaved glyph record: ``[length, ink..., unused...]``.

    ``ink`` is the authored occupied columns from ``authored_ink``. The record is
    always ``width + 1`` bytes: one length byte (the value ``n``, not ``n`` zeros),
    then the ``n`` ink bytes, then ``width - n`` trailing 0x00 so the ink/pad field
    is a fixed ``width`` slots.

    Raises ``ValueError`` if ``len(ink) > width``.
    """
    if len(ink) > width:
        raise ValueError(f"ink length {len(ink)} exceeds native width {width}")
    length_prefix = bytes((len(ink),))  # 1-byte header whose value is n; comma → 1-tuple (litteral), specifies values not lenghts (of zero-filled array)
    occupied = ink  # n column-bytes of authored ink, packed as-is after the length
    padding = bytes(width - len(ink))  # width-n trailing 0x00; unused slots, fixed ink/pad field of `width`
    return length_prefix + occupied + padding  # [length, ink..., pad...]; always width+1 bytes


def build_spaced_table(column_major: bytes, width: int = dal_pendolino3.FONT_WIDTH) -> bytes:
    """Build the concatenated table of 95 packed records from column-major glyphs.

    ``column_major`` is the whole font blob (``GLYPH_COUNT * width`` bytes), ASCII
    32..126 in order, each glyph native-width. Each glyph is trimmed then packed
    via ``authored_ink`` and ``pack_record``.

    Ink-bearing glyphs are checked against an independent occupied-slice of the
    native bytes; space must be a 3-column blank.

    Raises ``ValueError`` if the blob length is not ``95 * width``.
    Raises ``RuntimeError`` if a glyph's packed ink disagrees with that slice.
    """
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
                raise RuntimeError(f"glyph {ASCII_START + i} ink does not match native glyph slice")
        elif ASCII_START + i == SPACE_ORD:
            if ink != bytes(SPACE_AUTHORED_WIDTH) or any(raw):
                raise RuntimeError("space record is not a 3-column blank")
        out.extend(rec)
    return bytes(out)


def _hex_literal(data: bytes) -> str:
    """Format ``data`` as concatenated quoted hex strings, one per source line.

    Wrap width is ``HEX_LINE_BYTES`` payload bytes (~68 hex chars per line, matching
    ``glyphs.py``). The result is the argument body of ``bytes.fromhex(...)`` in the
    generated module.
    """
    hex_str = data.hex()
    chunk = HEX_LINE_BYTES * 2
    lines = [f'    "{hex_str[i : i + chunk]}"' for i in range(0, len(hex_str), chunk)]
    return "\n".join(lines)


def render_module(table: bytes, width: int = dal_pendolino3.FONT_WIDTH) -> str:
    """Return the full source of ``spaced_glyphs.py`` for a packed ``table``.

    Fills ``scripts/templates/spaced_glyphs.py.in`` (stdlib ``string.Template``) with
    the DAL commit, glyph count, and hex-literal body. ``table`` must be
    ``GLYPH_COUNT * (width + 1)`` bytes.

    Raises ``ValueError`` if the table length does not match that size.
    """
    stride = width + 1
    n = dal_pendolino3.GLYPH_COUNT
    if len(table) != n * stride:
        raise ValueError(f"table length {len(table)} != {n}×{stride}")
    commit = dal_pendolino3.DAL_COMMIT
    template = string.Template(TEMPLATE_PATH.read_text())
    return template.substitute(
        commit=commit,
        commit_short=commit[:12],
        glyph_count=n,
        hex_literal=_hex_literal(table),
    )


def _spot_check(table: bytes, width: int = dal_pendolino3.FONT_WIDTH) -> None:
    """Raise if packed-table survey cases (space, ``.``, ``7``) do not hold.

    These pin the three record shapes: 3-column blank space, 1-column ink-bearing
    punctuation, and a full-width ink glyph. Prints a one-line summary on success.
    """
    stride = width + 1

    def rec(ch: str) -> tuple[int, bytes, bool]:
        """Unpack one record as ``(length, ink_bytes, has_ink)``."""
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

    print(f"spot-checks: space length={SPACE_AUTHORED_WIDTH} blank; '.' length=1 has_ink; '7' length={width} has_ink")


def main() -> int:
    """Fetch the pinned DAL font, pack the table, spot-check, and write the module.

    Happy path: ``load_column_major``, ``build_spaced_table``, ``_spot_check``,
    ``render_module``, write ``DEFAULT_OUTPUT``. Returns 0 on success, 1 on
    fetch/pack/write failure (message on stderr).
    """
    print(f"Fetching {dal_pendolino3.DAL_URL}")
    try:
        converted = dal_pendolino3.load_column_major()
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
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
