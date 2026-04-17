"""
Design-time conversion between ASCII-art patterns and column-major bytes.

Column-major format: one byte per column, where bit N of each byte
indicates row N is lit (bit 0 = top row). Each ``WIDTH``-column grid
therefore serialises to ``WIDTH`` bytes. The format caps height at
``_MAX_HEIGHT_PER_COLUMN_BYTE`` (8) bits per byte; see ``_constants``
for the encoding-vs-geometry distinction.

These helpers are authoring tools, not a runtime hot path: strict
validation surfaces typos in hard-coded icon definitions rather than
silently padding or truncating.
"""

from ._constants import WIDTH, HEIGHT, _MAX_HEIGHT_PER_COLUMN_BYTE


def pattern_to_colmajor(pattern, width=WIDTH, height=HEIGHT):
    """Convert monochrome ASCII art to column-major bytes.

    Input: multiline string of `#` (on) / `.` (off) cells. Each non-blank
    line is treated as one row. Inter-cell spaces are stripped, so both
    `# # . .` and `##..` work. Blank lines are skipped.

    Output: `bytes` of length `width`. Bit N of byte `c` = row N of column `c`
    (bit 0 = top row). `height` is capped by the encoding format limit of
    `_MAX_HEIGHT_PER_COLUMN_BYTE` bits per column-byte.

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
        raise ValueError("height={} exceeds column-major encoding limit of {} (one byte per column)".format(height, _MAX_HEIGHT_PER_COLUMN_BYTE))

    # Normalize each input line: strip surrounding whitespace, remove inter-
    # cell spaces and tabs, drop blanks. Order is preserved; each surviving
    # line becomes one row.
    rows = []
    for raw in pattern.split("\n"):
        stripped = raw.strip().replace(" ", "").replace("\t", "")
        if stripped:
            rows.append(stripped)

    if len(rows) < height:
        raise ValueError("expected {} rows, got {}".format(height, len(rows)))
    if len(rows) > height:
        raise ValueError("expected {} rows, got {} (extra rows: {})".format(height, len(rows), rows[height:]))

    cols = bytearray(width)
    for row_idx, row in enumerate(rows):
        if len(row) != width:
            raise ValueError('row {}: {} cells, expected {}: "{}"'.format(row_idx, len(row), width, row))
        for col_idx, ch in enumerate(row):
            if ch == "#":
                cols[col_idx] |= 1 << row_idx
            elif ch != ".":
                raise ValueError("row {}, col {}: unknown cell '{}' (expected '#' or '.')".format(row_idx, col_idx, ch))
    return bytes(cols)


def colmajor_to_pattern(data, width=None, height=HEIGHT):
    """Inverse of `pattern_to_colmajor`: render bytes back to ASCII art.

    Input: `data` bytes in column-major layout, `width` columns (default
    `len(data)`), `height` rows.

    Output: multiline string, one line per row, cells separated by spaces
    (`# . . # ...`). Paste-ready for documentation comments.

    Use case: inspect existing ICONS / ARROWS bytes or verify a round trip.
    """
    if width is None:
        width = len(data)
    lines = []
    for row in range(height):
        row_cells = ["#" if (data[col] >> row) & 1 else "." for col in range(width)]
        lines.append(" ".join(row_cells))
    return "\n".join(lines)
