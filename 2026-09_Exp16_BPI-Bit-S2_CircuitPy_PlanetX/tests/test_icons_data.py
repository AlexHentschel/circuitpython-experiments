"""
Shape, value-range, LightTower name-alignment, and ASCII↔byte tests for ``display.icons``.

``test_pattern_codec.test_icons_round_trip`` only checks codec invertibility
(bytes → generated pattern → bytes). It cannot catch an icon whose *comments
and bytes agree with each other* but disagree with MakeCode. The tests below
split that: comments must encode to the stored bytes, and named MakeCode
fixtures must match independently of ``icons.py``.
"""

from pathlib import Path
import re

from display._constants import WIDTH, HEIGHT
from display.bitmap_codec import colmajor_to_pattern, pattern_to_colmajor
from display.icons import ICONS, ARROWS, ICON_NAMES, ARROW_NAMES


EXPECTED_ICON_COUNT = 40
EXPECTED_ARROW_COUNT = 8
LIGHTHOUSE_ICONS = ("YES", "NO", "DIAMOND")
LIGHTHOUSE_ARROWS = ("NORTH", "EAST", "SOUTH", "WEST")


def test_icons_length():
    """ICONS is 40 icons × one column-byte per column.

    - Covers: truncated/padded table, WIDTH drift after a 5×5 swap.
    - Approach: ``len(ICONS)`` vs ``EXPECTED_ICON_COUNT * WIDTH``.
    """
    assert len(ICONS) == EXPECTED_ICON_COUNT * WIDTH


def test_arrows_length():
    """ARROWS is 8 compass arrows × one column-byte per column.

    - Covers: truncated/padded arrow table, WIDTH drift.
    - Approach: ``len(ARROWS)`` vs ``EXPECTED_ARROW_COUNT * WIDTH``.
    """
    assert len(ARROWS) == EXPECTED_ARROW_COUNT * WIDTH


def test_icons_is_bytes():
    """ICONS must be immutable ``bytes`` (not ``bytearray`` / list).

    - Covers: accidental mutable backing that ``Image`` slices would share.
    - Approach: ``isinstance(ICONS, bytes)``.
    """
    assert isinstance(ICONS, bytes)


def test_arrows_is_bytes():
    """ARROWS must be immutable ``bytes`` (not ``bytearray`` / list).

    - Covers: same shared-mutation hazard as ICONS.
    - Approach: ``isinstance(ARROWS, bytes)``.
    """
    assert isinstance(ARROWS, bytes)


def test_icon_names_length_matches_data():
    """One ICON_NAMES entry per WIDTH-byte slot in ICONS.

    - Covers: name list vs bitmap table drifting (extra/missing names or slots).
    - Approach: ``len(ICON_NAMES) == len(ICONS) // WIDTH == EXPECTED_ICON_COUNT``.
    """
    assert len(ICON_NAMES) == len(ICONS) // WIDTH == EXPECTED_ICON_COUNT


def test_arrow_names_length_matches_data():
    """One ARROW_NAMES entry per WIDTH-byte slot in ARROWS.

    - Covers: name list vs arrow table drifting.
    - Approach: ``len(ARROW_NAMES) == len(ARROWS) // WIDTH == EXPECTED_ARROW_COUNT``.
    """
    assert len(ARROW_NAMES) == len(ARROWS) // WIDTH == EXPECTED_ARROW_COUNT


def test_icon_names_unique():
    """ICON_NAMES has no duplicate slot labels.

    - Covers: two names pointing at the same conceptual icon (silent overwrite on the wrapper class).
    - Approach: ``set`` cardinality vs list length.
    """
    assert len(set(ICON_NAMES)) == len(ICON_NAMES)


def test_arrow_names_unique():
    """ARROW_NAMES has no duplicate slot labels.

    - Covers: same silent-overwrite hazard as icon names.
    - Approach: ``set`` cardinality vs list length.
    """
    assert len(set(ARROW_NAMES)) == len(ARROW_NAMES)


def test_icon_names_are_identifiers():
    """Each ICON_NAMES string is a legal Python identifier (``Icons.HEART`` etc.).

    - Covers: names that cannot become attributes (spaces, leading digits, hyphens).
    - Approach: ``str.isidentifier`` on every name.
    """
    assert all(n.isidentifier() for n in ICON_NAMES)


def test_arrow_names_are_identifiers():
    """Each ARROW_NAMES string is a legal Python identifier (``Arrows.NORTH`` etc.).

    - Covers: names that cannot become attributes.
    - Approach: ``str.isidentifier`` on every name.
    """
    assert all(n.isidentifier() for n in ARROW_NAMES)


def test_lighthouse_icon_names_present():
    """LightTower student ops can name YES, NO, and DIAMOND.

    - Covers: 8×8-era names dropped or renamed during the 5×5 port.
    - Approach: membership of ``LIGHTHOUSE_ICONS`` in ``ICON_NAMES`` (presence only, not pixels).
    """
    for name in LIGHTHOUSE_ICONS:
        assert name in ICON_NAMES


def test_lighthouse_arrow_names_present():
    """LightTower student ops can name the four compass arrows.

    - Covers: NORTH/EAST/SOUTH/WEST missing or only as diagonals.
    - Approach: membership of ``LIGHTHOUSE_ARROWS`` in ``ARROW_NAMES``.
    """
    for name in LIGHTHOUSE_ARROWS:
        assert name in ARROW_NAMES


def _slice_named(names, data, name):
    """Return the WIDTH-byte column-major slice for ``name`` in ``data``."""
    i = names.index(name)
    return data[i * WIDTH : (i + 1) * WIDTH]


def test_yes_no_diamond_bitmaps_are_nonzero():
    """YES, NO, DIAMOND slices are not all-off.

    - Covers: name present but the slot is empty (wrong index, zeros pasted).
    - Approach: ``any(blob)`` on each LightTower icon slice. Does not check the picture.
    """
    for name in LIGHTHOUSE_ICONS:
        blob = _slice_named(ICON_NAMES, ICONS, name)
        assert any(blob), f"{name} bitmap is empty"


def test_compass_arrow_bitmaps_are_nonzero():
    """NORTH, EAST, SOUTH, WEST slices are not all-off and are WIDTH bytes.

    - Covers: empty compass slots; slice length ≠ WIDTH.
    - Approach: ``any(blob)`` and ``len(blob) == WIDTH``. Does not check the picture.
    """
    for name in LIGHTHOUSE_ARROWS:
        blob = _slice_named(ARROW_NAMES, ARROWS, name)
        assert any(blob), f"{name} bitmap is empty"
        assert len(blob) == WIDTH


_ICONS_PY = Path(__file__).resolve().parents[1] / "lib" / "display" / "icons.py"
_NAME_LINE = re.compile(r"^    # \d+: ([A-Z0-9_]+)\s*$")
_GRID_LINE = re.compile(r"^    #    ((?:[.#] ){4}[.#])\s*$")
_BYTES_LINE = re.compile(r"^    (0x[0-9A-Fa-f]{2}(?:, 0x[0-9A-Fa-f]{2}){4}),?\s*$")


def _parse_comment_blocks(source: str):
    """Yield ``(name, ascii_pattern, hex_bytes)`` from each ``icons.py`` comment+hex block.

    A block is ``# N: NAME``, then HEIGHT ``#    . # .`` rows, then one ``0x.., …`` line.
    Used by the comment↔byte tests; not a second encoder.
    """
    lines = source.splitlines()
    i = 0
    while i < len(lines):
        name_m = _NAME_LINE.match(lines[i])
        if not name_m:
            i += 1
            continue
        name = name_m.group(1)
        grid = []
        j = i + 1
        while j < len(lines):
            grid_m = _GRID_LINE.match(lines[j])
            if not grid_m:
                break
            grid.append(grid_m.group(1))
            j += 1
        if len(grid) != HEIGHT:
            raise AssertionError(f"{name}: expected {HEIGHT} ASCII rows in comments, got {len(grid)}")
        if j >= len(lines):
            raise AssertionError(f"{name}: missing hex line after ASCII comments")
        bytes_m = _BYTES_LINE.match(lines[j])
        if not bytes_m:
            raise AssertionError(f"{name}: expected hex bytes after comments, got {lines[j]!r}")
        blob = bytes(int(part, 16) for part in bytes_m.group(1).split(", "))
        yield name, "\n".join(grid), blob
        i = j + 1


def test_ascii_comments_encode_to_following_bytes():
    """Each ``# . #`` comment grid must encode to the hex on the following line, and back.

    - Covers: comment art drifting from the hex beside it (typo, missed row, bit-order slip).
    - Does not cover: both comment and hex copying a wrong upstream (see MakeCode fixtures).
    - Approach: parse every named block in ``icons.py``; names must be ICON_NAMES then ARROW_NAMES;
      ``pattern_to_colmajor(comments)`` equals the hex line; ``colmajor_to_pattern(hex)`` equals comments.
    """
    blocks = list(_parse_comment_blocks(_ICONS_PY.read_text()))
    assert [name for name, _, _ in blocks] == list(ICON_NAMES) + list(ARROW_NAMES)
    for name, pattern, hex_blob in blocks:
        encoded = pattern_to_colmajor(pattern, width=WIDTH, height=HEIGHT)
        assert encoded == hex_blob, f"{name}: comments encode to {encoded.hex()}, hex line is {hex_blob.hex()}"
        decoded = colmajor_to_pattern(hex_blob, width=WIDTH, height=HEIGHT)
        assert decoded == pattern, f"{name}: bytes decode to\n{decoded}\ncomments were\n{pattern}"


def test_stored_bytes_match_comment_encoded_bytes():
    """Imported ``ICONS`` / ``ARROWS`` slices must equal the hex line after each comment block.

    - Covers: table bytes edited without updating the comment hex (or vice versa).
    - Approach: parse comment-block hex; compare to ``_slice_named`` of the imported tables.
    """
    blocks = list(_parse_comment_blocks(_ICONS_PY.read_text()))
    for name, _, hex_blob in blocks:
        if name in ICON_NAMES:
            stored = _slice_named(ICON_NAMES, ICONS, name)
        else:
            stored = _slice_named(ARROW_NAMES, ARROWS, name)
        assert stored == hex_blob, f"{name}: table slice {stored.hex()} != comment hex {hex_blob.hex()}"


# Independent of icons.py — MakeCode grids from the 2026-09-04 attached screenshots.
# Catches the shared-derivation case where comments and bytes both copy a wrong Exp09 source.
MAKECODE_ICON_PATTERNS = {
    "GHOST": "\n".join(
        (
            ". # # # .",
            "# . # . #",
            "# # # # #",
            "# # # # #",
            "# . # . #",
        )
    ),
    "LEFT_TRIANGLE": "\n".join(
        (
            "# . . . .",
            "# # . . .",
            "# . # . .",
            "# . . # .",
            "# # # # #",
        )
    ),
}


def test_makecode_icon_fixtures_match_stored_bytes():
    """GHOST and LEFT_TRIANGLE match MakeCode grids that do not live in ``icons.py``.

    - Covers: comments + hex both copied from a wrong Exp09 source (shared-derivation).
    - Approach: encode each fixture with ``pattern_to_colmajor``; compare to the named ICONS slice;
      decode the slice and compare to the fixture string.
    """
    for name, pattern in MAKECODE_ICON_PATTERNS.items():
        stored = _slice_named(ICON_NAMES, ICONS, name)
        assert stored == pattern_to_colmajor(pattern, width=WIDTH, height=HEIGHT)
        assert colmajor_to_pattern(stored, width=WIDTH, height=HEIGHT) == pattern
