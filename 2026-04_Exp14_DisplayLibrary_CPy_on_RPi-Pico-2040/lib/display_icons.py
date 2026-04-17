"""
Icon and arrow bitmap data for the 8x8 WS2812b display library.

Storage format: column-major bytes -- one byte per column, where bit N of
each byte indicates row N is lit (bit 0 = top row). This layout enables
efficient horizontal scrolling by iterating contiguous column bytes.
Each icon/arrow is WIDTH bytes (one per column of the WIDTH x HEIGHT grid,
with WIDTH = HEIGHT = 8 for this hardware). Designed as row-major ASCII
art (# = on, . = off), then transposed to column-major at design time.

Encoding-vs-geometry note: the single-byte-per-column format caps height
at 8 (8 bits per byte). This is independent of display geometry -- a taller
display would need a different storage format, not just a parameter change.
See `_MAX_HEIGHT_PER_COLUMN_BYTE` below.

Lookup: ICONS[icon_id * WIDTH : (icon_id + 1) * WIDTH] gives the WIDTH
column bytes.

Design-time helpers `pattern_to_colmajor` / `colmajor_to_pattern` convert
between ASCII art and the byte encoding, useful for authoring new icons
or verifying existing ones.
"""


# ---------------------------------------------------------------------------
# Design-time conversion helpers (not used at runtime by the display library)
# ---------------------------------------------------------------------------

# Display grid defaults for the helpers -- match the hardware described in
# display.py. Duplicated locally (not imported from display) because display
# imports ICONS/ARROWS from this module; the reverse import would be circular.
# Keeping these named rather than using bare literals preserves parameter
# intent at every use site.
_DEFAULT_WIDTH = 8
_DEFAULT_HEIGHT = 8

# Encoding-imposed hard limit: each column is stored as a single byte, so at
# most 8 rows can be encoded. This is a property of the column-major byte
# format, NOT of the display geometry. Error messages must distinguish the
# two: exceeding this is a storage-format redesign, not a simple resize.
_MAX_HEIGHT_PER_COLUMN_BYTE = 8


def pattern_to_colmajor(pattern, width=_DEFAULT_WIDTH, height=_DEFAULT_HEIGHT):
    """Convert monochrome ASCII art to column-major bytes.

    Input: multiline string of `#` (on) / `.` (off) cells. Each non-blank
    line is treated as one row. Inter-cell spaces are stripped, so both
    `# # . .` and `##..` work. Blank lines are skipped.

    Output: `bytes` of length `width`. Bit N of byte `c` = row N of column `c`
    (bit 0 = top row). `height` is capped by the encoding format limit of
    {_MAX_HEIGHT_PER_COLUMN_BYTE} bits per column-byte.

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


def colmajor_to_pattern(data, width=None, height=_DEFAULT_HEIGHT):
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


# fmt: off

# ---------------------------------------------------------------------------
# 40 Icons -- 8 bytes each, column-major
# Index matches IconNames enum values in display.py
# ---------------------------------------------------------------------------

ICONS = bytes([
    # 0: HEART
    #	 . # # . . # # .
    #	 # # # # # # # #
    #	 # # # # # # # #
    #	 # # # # # # # #
    #	 . # # # # # # .
    #	 . . # # # # . .
    #	 . . . # # . . .
    #	 . . . . . . . .
    0x0E, 0x1F, 0x3F, 0x7E, 0x7E, 0x3F, 0x1F, 0x0E,

    # 1: SMALL_HEART
    #	 . . . . . . . .
    #	 . . # . . # . .
    #	 . # # # # # # .
    #	 . # # # # # # .
    #	 . . # # # # . .
    #	 . . . # # . . .
    #	 . . . . . . . .
    #	 . . . . . . . .
    0x00, 0x0C, 0x1E, 0x3C, 0x3C, 0x1E, 0x0C, 0x00,

    # 2: YES (checkmark)
    #	 . . . . . . . .
    #	 . . . . . . . #
    #	 . . . . . . # .
    #	 . . . . . # . .
    #	 # . . . # . . .
    #	 . # . # . . . .
    #	 . . # . . . . .
    #	 . . . . . . . .
    0x10, 0x20, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02,

    # 3: NO (X)
    #	 # . . . . . # .
    #	 . # . . . # . .
    #	 . . # . # . . .
    #	 . . . # . . . .
    #	 . . # . # . . .
    #	 . # . . . # . .
    #	 # . . . . . # .
    #	 . . . . . . . .
    0x41, 0x22, 0x14, 0x08, 0x14, 0x22, 0x41, 0x00,

    # 4: HAPPY
    #	 . . . . . . . .
    #	 . # # . . # # .
    #	 . # # . . # # .
    #	 . . . . . . . .
    #	 . . . . . . . .
    #	 . # . . . . # .
    #	 . . # # # # . .
    #	 . . . . . . . .
    0x00, 0x26, 0x46, 0x40, 0x40, 0x46, 0x26, 0x00,

    # 5: SAD
    #	 . . . . . . . .
    #	 . # # . . # # .
    #	 . # # . . # # .
    #	 . . . . . . . .
    #	 . . . . . . . .
    #	 . . # # # # . .
    #	 . # . . . . # .
    #	 . . . . . . . .
    0x00, 0x46, 0x26, 0x20, 0x20, 0x26, 0x46, 0x00,

    # 6: CONFUSED
    #	 . . . . . . . .
    #	 . # # . . # # .
    #	 . # # . . # # .
    #	 . . . . . . . .
    #	 . . . . . . . .
    #	 . # . # . # . .
    #	 . . . . . . . .
    #	 . . . . . . . .
    0x00, 0x26, 0x06, 0x20, 0x00, 0x26, 0x06, 0x00,

    # 7: ANGRY
    #	 # . . . . . . #
    #	 . # . . . . # .
    #	 . . . . . . . .
    #	 . # # . . # # .
    #	 . # # . . # # .
    #	 . . . . . . . .
    #	 . . # # # # . .
    #	 . # # # # # # .
    0x01, 0x9A, 0xD8, 0xC0, 0xC0, 0xD8, 0x9A, 0x01,

    # 8: ASLEEP
    #	 . . . . . . . .
    #	 . # . # . # . #
    #	 . . . . . . . .
    #	 . . . . . . . .
    #	 . . . . . . . .
    #	 . . . # # . . .
    #	 . . # . . # . .
    #	 . . . # # . . .
    0x00, 0x02, 0x40, 0xA2, 0xA0, 0x42, 0x00, 0x02,

    # 9: SURPRISED
    #	 . . . . . . . .
    #	 . # # . . # # .
    #	 . # # . . # # .
    #	 . . . . . . . .
    #	 . . . # # . . .
    #	 . . # . . # . .
    #	 . . # . . # . .
    #	 . . . # # . . .
    0x00, 0x06, 0x66, 0x90, 0x90, 0x66, 0x06, 0x00,

    # 10: SILLY
    #	 . . . . . . . .
    #	 . # # . . . . .
    #	 . # # . . # # .
    #	 . . . . . . . .
    #	 . . . . . . . .
    #	 # # # # # # # #
    #	 . . . . . . . .
    #	 . . . . . . . .
    0x20, 0x26, 0x26, 0x20, 0x20, 0x24, 0x24, 0x20,

    # 11: FABULOUS
    #	 . . . . . . . .
    #	 # # . . . # # #
    #	 . . . . . . . .
    #	 . . . . . . . .
    #	 . # . . . . # .
    #	 . . # . . # . .
    #	 . . . # # . . .
    #	 . . . . . . . .
    0x02, 0x12, 0x20, 0x40, 0x40, 0x22, 0x12, 0x02,

    # 12: MEH
    #	 . . . . . . . .
    #	 . # # . . # # .
    #	 . # # . . # # .
    #	 . . . . . . . .
    #	 . . . . . . . .
    #	 . . . . . . . .
    #	 . # # # # # # .
    #	 . . . . . . . .
    0x00, 0x46, 0x46, 0x40, 0x40, 0x46, 0x46, 0x00,

    # 13: TSHIRT
    #	 # # . . . # # #
    #	 . # # # # # . .
    #	 . . # # # . . .
    #	 . . # # # . . .
    #	 . . # # # . . .
    #	 . . # # # . . .
    #	 . . # # # . . .
    #	 . . . # . . . .
    0x01, 0x03, 0x7E, 0xFE, 0x7E, 0x03, 0x01, 0x01,

    # 14: ROLLERSKATE
    #	 . . . # # . . .
    #	 . . . # . . . .
    #	 . . . # . . . .
    #	 # # # # . . . .
    #	 # . . . . . . .
    #	 # # # # # # # #
    #	 . . . . . . . .
    #	 . # . . . # . .
    0x38, 0xA8, 0x28, 0x2F, 0x21, 0xA0, 0x20, 0x20,

    # 15: DUCK
    #	 . . # # . . . .
    #	 . # # # # . . .
    #	 # # # # # . . .
    #	 . # # # # # # .
    #	 . . # # # # # #
    #	 . . # # # # # .
    #	 . . . # # # . .
    #	 . . . . . . . .
    0x04, 0x0E, 0x3F, 0x7F, 0x7E, 0x78, 0x38, 0x10,

    # 16: HOUSE
    #	 . . . # . . . .
    #	 . . # # # . . .
    #	 . # # # # # . .
    #	 # # # # # # # .
    #	 # # . . . # # .
    #	 # # . . . # # .
    #	 # # . . . # # .
    #	 . # # # # # . .
    0x78, 0xFC, 0x8E, 0x8F, 0x8E, 0xFC, 0x78, 0x00,

    # 17: TORTOISE
    #	 . . . # # . . .
    #	 . . # # # # . .
    #	 # # # # # # # #
    #	 # . # . # . # .
    #	 . . . . . . . .
    #	 . . . . . . . .
    #	 . . . . . . . .
    #	 . . . . . . . .
    0x0C, 0x04, 0x0E, 0x07, 0x0F, 0x06, 0x0C, 0x04,

    # 18: BUTTERFLY
    #	 # # . # # . # #
    #	 . # # # # # # .
    #	 # # # # # # # #
    #	 . # # # # # # .
    #	 # # # # # # # #
    #	 . # # # # # # .
    #	 # # . # # . # #
    #	 . . . . . . . .
    0x55, 0x7F, 0x3E, 0x7F, 0x7F, 0x3E, 0x7F, 0x55,

    # 19: STICK_FIGURE
    #	 . . . # . . . .
    #	 . . # # # . . .
    #	 . . . # . . . .
    #	 . # # # # # . .
    #	 # . . # . . # .
    #	 . . . # . . . .
    #	 . . # . # . . .
    #	 . # . . . # . .
    0x10, 0x88, 0x4A, 0x3F, 0x4A, 0x88, 0x10, 0x00,

    # 20: GHOST
    #	 . . # # # # . .
    #	 . # # # # # # .
    #	 # . # # . # # #
    #	 # # # # # # # #
    #	 # # # # # # # #
    #	 # . # # . # # #
    #	 # . # # # . # .
    #	 . . . . . . . .
    0x7C, 0x1A, 0x7F, 0x7F, 0x5B, 0x3F, 0x7E, 0x3C,

    # 21: SWORD
    #	 . . . # . . . .
    #	 . . . # . . . .
    #	 . . . # . . . .
    #	 . . . # . . . .
    #	 . . . # . . . .
    #	 . . # # # . . .
    #	 . . . # . . . .
    #	 . . . . . . . .
    0x00, 0x00, 0x20, 0x7F, 0x20, 0x00, 0x00, 0x00,

    # 22: GIRAFFE
    #	 . # # . . . . .
    #	 . # . . . . . .
    #	 . # . . . . . .
    #	 . # # . . . . .
    #	 . . # . . . . .
    #	 . . # . . . . .
    #	 . . # # . . . .
    #	 . . # . # . . .
    0x00, 0x0F, 0xF9, 0x40, 0x80, 0x00, 0x00, 0x00,

    # 23: SKULL
    #	 . # # # # # . .
    #	 # # # # # # # .
    #	 # . # # . # # .
    #	 # # # # # # # .
    #	 . # # # # # . .
    #	 . # . # . # . .
    #	 . . # # # . . .
    #	 . . . . . . . .
    0x0E, 0x3B, 0x5F, 0x7F, 0x5B, 0x3F, 0x0E, 0x00,

    # 24: UMBRELLA
    #	 . . # # # . . .
    #	 . # # # # # . .
    #	 # # # # # # # .
    #	 . . . # . . . .
    #	 . . . # . . . .
    #	 . . . # . . . .
    #	 # . . # . . . .
    #	 . # # . . . . .
    0x44, 0x86, 0x87, 0x7F, 0x07, 0x06, 0x04, 0x00,

    # 25: SNAKE
    #	 . # . . . . . .
    #	 # # . . . # . .
    #	 . # # # # # . .
    #	 . . . . . # # #
    #	 . . . . . . . .
    #	 . . . . . . . .
    #	 . . . . . . . .
    #	 . . . . . . . .
    0x02, 0x07, 0x04, 0x04, 0x04, 0x0E, 0x08, 0x08,

    # 26: RABBIT
    #	 . # . . # . . .
    #	 . # . . # . . .
    #	 . # # # # . . .
    #	 . # . # . # . .
    #	 . # # # # # . .
    #	 . # # # # # . .
    #	 . . # # # . . .
    #	 . . . # . . . .
    0x00, 0x3F, 0x74, 0xFC, 0x77, 0x38, 0x00, 0x00,

    # 27: COW
    #	 # . . . . . # .
    #	 # # . . . # # .
    #	 . # # # # # . .
    #	 . # . # . # . .
    #	 . # # # # # . .
    #	 . . # # # . . .
    #	 . . . . . . . .
    #	 . . . . . . . .
    0x03, 0x1E, 0x34, 0x3C, 0x34, 0x1E, 0x03, 0x00,

    # 28: QUARTER_NOTE
    #	 . . # . . . . .
    #	 . . # . . . . .
    #	 . . # . . . . .
    #	 . . # . . . . .
    #	 . . # . . . . .
    #	 . # # . . . . .
    #	 # # # . . . . .
    #	 . # . . . . . .
    0x40, 0xE0, 0x7F, 0x00, 0x00, 0x00, 0x00, 0x00,

    # 29: EIGHTH_NOTE
    #	 . . # . # . . .
    #	 . . # . . # . .
    #	 . . # . . . # .
    #	 . . # . . # . .
    #	 . . # . # . . .
    #	 . # # # # . . .
    #	 # # # # # . . .
    #	 . # . # . . . .
    0x40, 0xE0, 0x7F, 0xE0, 0x71, 0x0A, 0x04, 0x00,

    # 30: PITCHFORK
    #	 # . # . # . . .
    #	 # . # . # . . .
    #	 # . # . # . . .
    #	 # # # # # . . .
    #	 . . # . . . . .
    #	 . . # . . . . .
    #	 . . # . . . . .
    #	 . . # . . . . .
    0x0F, 0x08, 0xFF, 0x08, 0x0F, 0x00, 0x00, 0x00,

    # 31: TARGET
    #	 . . # # # . . .
    #	 . # # # # # . .
    #	 # # . . . # # .
    #	 # # . . . # # .
    #	 # # . . . # # .
    #	 . # # # # # . .
    #	 . . # # # . . .
    #	 . . . . . . . .
    0x1C, 0x3E, 0x63, 0x63, 0x63, 0x3E, 0x1C, 0x00,

    # 32: TRIANGLE
    #	 . . . . . . . .
    #	 . . . # . . . .
    #	 . . # . # . . .
    #	 . . # . # . . .
    #	 . # . . . # . .
    #	 . # . . . # . .
    #	 # # # # # # # .
    #	 . . . . . . . .
    0x40, 0x70, 0x4C, 0x42, 0x4C, 0x70, 0x40, 0x00,

    # 33: LEFT_TRIANGLE
    #	 # . . . . . . .
    #	 # # . . . . . .
    #	 # # # . . . . .
    #	 # # # # . . . .
    #	 # # # . . . . .
    #	 # # . . . . . .
    #	 # . . . . . . .
    #	 . . . . . . . .
    0x7F, 0x3E, 0x1C, 0x08, 0x00, 0x00, 0x00, 0x00,

    # 34: CHESSBOARD
    #	 # . # . # . # .
    #	 . # . # . # . #
    #	 # . # . # . # .
    #	 . # . # . # . #
    #	 # . # . # . # .
    #	 . # . # . # . #
    #	 # . # . # . # .
    #	 . # . # . # . #
    0x55, 0xAA, 0x55, 0xAA, 0x55, 0xAA, 0x55, 0xAA,

    # 35: DIAMOND
    #	 . . . # . . . .
    #	 . . # # # . . .
    #	 . # # # # # . .
    #	 # # # # # # # .
    #	 . # # # # # . .
    #	 . . # # # . . .
    #	 . . . # . . . .
    #	 . . . . . . . .
    0x08, 0x1C, 0x3E, 0x7F, 0x3E, 0x1C, 0x08, 0x00,

    # 36: SMALL_DIAMOND
    #	 . . . . . . . .
    #	 . . . # . . . .
    #	 . . # # # . . .
    #	 . # # # # # . .
    #	 . . # # # . . .
    #	 . . . # . . . .
    #	 . . . . . . . .
    #	 . . . . . . . .
    0x00, 0x08, 0x1C, 0x3E, 0x1C, 0x08, 0x00, 0x00,

    # 37: SQUARE
    #	 # # # # # # # #
    #	 # . . . . . . #
    #	 # . . . . . . #
    #	 # . . . . . . #
    #	 # . . . . . . #
    #	 # . . . . . . #
    #	 # . . . . . . #
    #	 # # # # # # # #
    0xFF, 0x81, 0x81, 0x81, 0x81, 0x81, 0x81, 0xFF,

    # 38: SMALL_SQUARE
    #	 . . . . . . . .
    #	 . . . . . . . .
    #	 . . # # # # . .
    #	 . . # . . # . .
    #	 . . # . . # . .
    #	 . . # # # # . .
    #	 . . . . . . . .
    #	 . . . . . . . .
    0x00, 0x00, 0x3C, 0x24, 0x24, 0x3C, 0x00, 0x00,

    # 39: SCISSORS
    #	 . . # . . . . .
    #	 . # . # . . . .
    #	 . . # . . . . .
    #	 . . . # # . . .
    #	 . . # . . # . .
    #	 . . . # # . . .
    #	 . . # . . . . .
    #	 . # . # . . . .
    0x00, 0x82, 0x55, 0xAA, 0x28, 0x10, 0x00, 0x00,
])

# ---------------------------------------------------------------------------
# 8 Arrows -- 8 bytes each, column-major
# Index matches ArrowNames enum values in display.py
# ---------------------------------------------------------------------------

ARROWS = bytes([
    # 0: NORTH (up arrow)
    #	 . . . # # . . .
    #	 . . # # # # . .
    #	 . # . # # . # .
    #	 # . . # # . . #
    #	 . . . # # . . .
    #	 . . . # # . . .
    #	 . . . # # . . .
    #	 . . . # # . . .
    0x08, 0x04, 0x02, 0xFF, 0xFF, 0x02, 0x04, 0x08,

    # 1: NORTH_EAST
    #	 . . # # # # # .
    #	 . . . . # # # .
    #	 . . . # . # # .
    #	 . . # . . . # .
    #	 . # . . . . . .
    #	 # . . . . . . .
    #	 . . . . . . . .
    #	 . . . . . . . .
    0x20, 0x10, 0x09, 0x05, 0x03, 0x07, 0x0F, 0x00,

    # 2: EAST (right arrow)
    #	 . . . # . . . .
    #	 . . . . # . . .
    #	 . . . . . # . .
    #	 # # # # # # # #
    #	 # # # # # # # #
    #	 . . . . . # . .
    #	 . . . . # . . .
    #	 . . . # . . . .
    0x18, 0x18, 0x18, 0x99, 0x5A, 0x3C, 0x18, 0x18,

    # 3: SOUTH_EAST
    #	 . . . . . . . .
    #	 . . . . . . . .
    #	 # . . . . . . .
    #	 . # . . . . . .
    #	 . . # . . . # .
    #	 . . . # . # # .
    #	 . . . . # # # .
    #	 . . # # # # # .
    0x04, 0x08, 0x90, 0xA0, 0xC0, 0xE0, 0xF0, 0x00,

    # 4: SOUTH (down arrow)
    #	 . . . # # . . .
    #	 . . . # # . . .
    #	 . . . # # . . .
    #	 . . . # # . . .
    #	 # . . # # . . #
    #	 . # . # # . # .
    #	 . . # # # # . .
    #	 . . . # # . . .
    0x10, 0x20, 0x40, 0xFF, 0xFF, 0x40, 0x20, 0x10,

    # 5: SOUTH_WEST
    #	 . . . . . . . .
    #	 . . . . . . . .
    #	 . . . . . . . #
    #	 . . . . . . # .
    #	 . # . . . # . .
    #	 . # # . # . . .
    #	 . # # # . . . .
    #	 . # # # # # . .
    0x00, 0xF0, 0xE0, 0xC0, 0xA0, 0x90, 0x08, 0x04,

    # 6: WEST (left arrow)
    #	 . . . . # . . .
    #	 . . . # . . . .
    #	 . . # . . . . .
    #	 . # # # # # # #
    #	 . # # # # # # #
    #	 . . # . . . . .
    #	 . . . # . . . .
    #	 . . . . # . . .
    0x00, 0x18, 0x3C, 0x5A, 0x99, 0x18, 0x18, 0x18,

    # 7: NORTH_WEST
    #	 . # # # # # . .
    #	 . # # # . . . .
    #	 . # # . # . . .
    #	 . # . . . # . .
    #	 . . . . . . # .
    #	 . . . . . . . #
    #	 . . . . . . . .
    #	 . . . . . . . .
    0x00, 0x0F, 0x07, 0x03, 0x05, 0x09, 0x10, 0x20,
])

# fmt: on
