"""
Design-time conversion between ASCII-art patterns and column-major bytes.

Column-major format: one byte per column (column 0 = leftmost); within each byte, bit N has numeric value 2**N (bit 0 = least-significant
bit) and indicates row N is lit (row 0 = top). Each ``WIDTH``-column grid therefore serialises to ``WIDTH`` bytes. The format caps height
at ``_MAX_HEIGHT_PER_COLUMN_BYTE`` (8) bits per byte; see ``_constants`` for the encoding-vs-geometry distinction.

These helpers are authoring tools, not a runtime hot path: strict
validation surfaces typos in hard-coded icon definitions rather than
silently padding or truncating.
"""

from ._constants import WIDTH, HEIGHT, _MAX_HEIGHT_PER_COLUMN_BYTE


def pattern_to_colmajor(pattern, width=WIDTH, height=HEIGHT):
    """Convert monochrome ASCII art to column-major bytes.

    Input: multiline string of `#` (on) / `.` (off) cells. Each non-blank
    line is treated as one row. All whitespace within a line is collapsed,
    so `# # . .`, `##..`, and `#\t# . .` all parse identically. Blank
    lines (any amount of whitespace) are skipped.

    Output: `bytes` of length `width`. Bit N of byte `c` (value 2**N) = row N of column `c` (bit 0 = least-significant bit = row 0 = top).
    `height` is capped by the encoding format limit of `_MAX_HEIGHT_PER_COLUMN_BYTE` bits per column-byte.

    Validation is strict (design-time authoring tool): raises `ValueError`
    with row/column locators for short rows, long rows, wrong row counts,
    or unknown cell characters. This surfaces typos in hard-coded icon
    definitions rather than silently padding/truncating.

    Use case: author a new icon as ASCII art, convert once, paste the hex
    bytes into ICONS.

        >>> pattern_to_colmajor('''
        ... . # # . . # # .
        ... # # # # # # # #
        ... # # # # # # # #
        ... # # # # # # # #
        ... . # # # # # # .
        ... . . # # # # . .
        ... . . . # # . . .
        ... . . . . . . . .
        ... ''').hex()
        '0e1f3f7e7e3f1f0e'
    """
    if height > _MAX_HEIGHT_PER_COLUMN_BYTE:
        raise ValueError(f"height={height} exceeds column-major encoding limit of {_MAX_HEIGHT_PER_COLUMN_BYTE} (one byte per column)")

    # Single pass: normalize each line (collapse all whitespace via split()/join), skip blanks, validate, and encode into `cols`.
    # `"".join(raw.split())` handles spaces, tabs, carriage returns (\r from CRLF line endings), form feeds, etc. uniformly --
    # more robust than chained .replace() calls on specific characters. Join only adds negligible overhead.
    cols = bytearray(width)
    row_idx = 0
    for raw in pattern.split("\n"):
        row = "".join(raw.split())  # split treats any run of consecutive whitespace (spaces, tabs, newlines) as a single separator
        if not row:
            continue
        if row_idx >= height:
            raise ValueError(f"too many rows, expected {height}")
        if len(row) != width:
            raise ValueError(f'row {row_idx}: {len(row)} cells, expected {width}: "{row}"')
        # `|=` accumulates ON bits into `cols[col_idx]` without disturbing already-set rows. Overflow-safe because the upfront
        # `_MAX_HEIGHT_PER_COLUMN_BYTE` check enforces that `row_idx` ≤ 7, so `1 << row_idx` always fits in one bytearray element.
        # CAUTION: increasing the row count is a format redesign, not a parameter tweak.
        for col_idx, ch in enumerate(row):
            if ch == "#":
                # For encoding details, see the README.md file. In essence, the top row is represented by the least significant bit.
                # So all we need to do is shift 1 (representing "on" for the top row without shift) to the position of the row.
                cols[col_idx] |= 1 << row_idx
            elif ch != ".":
                raise ValueError(f"row {row_idx}, col {col_idx}: unknown cell '{ch}' (expected '#' or '.')")
        row_idx += 1

    if row_idx != height:
        raise ValueError(f"expected {height} rows, got {row_idx}")
    return bytes(cols)


def colmajor_to_pattern(data, width=None, height=HEIGHT):
    """Inverse of `pattern_to_colmajor`: render icon in column-major byte representation as to ASCII art (string).

    Input: `data` bytes in column-major layout, `width` columns (default `len(data)`), `height` rows.

    Output: multiline string, one line per row, cells separated by spaces (`# . . # ...`). Paste-ready for documentation comments.

    Use case: inspect existing ICONS / ARROWS bytes or verify a round trip.
    """
    if width is None:
        width = len(data)
    lines = []
    for row in range(height):
        # Inverse of the encode step: right-shift the column byte by `row` so row N's bit lands at position 0, then `& 1` isolates it.
        # CAUTION: widening the format past one byte per column invalidates this shift.
        # For encoding details (top row = least significant bit), see the README.md file.
        row_cells = ["#" if (data[col] >> row) & 1 else "." for col in range(width)]
        lines.append(" ".join(row_cells))
    return "\n".join(lines)
