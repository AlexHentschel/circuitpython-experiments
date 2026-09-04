"""
Shape, value-range, and LightTower name-alignment tests for ``display.icons``.
"""

from display._constants import WIDTH
from display.icons import ICONS, ARROWS, ICON_NAMES, ARROW_NAMES


EXPECTED_ICON_COUNT = 40
EXPECTED_ARROW_COUNT = 8
LIGHTHOUSE_ICONS = ("YES", "NO", "DIAMOND")
LIGHTHOUSE_ARROWS = ("NORTH", "EAST", "SOUTH", "WEST")


def test_icons_length():
    assert len(ICONS) == EXPECTED_ICON_COUNT * WIDTH


def test_arrows_length():
    assert len(ARROWS) == EXPECTED_ARROW_COUNT * WIDTH


def test_icons_is_bytes():
    assert isinstance(ICONS, bytes)


def test_arrows_is_bytes():
    assert isinstance(ARROWS, bytes)


def test_icon_names_length_matches_data():
    assert len(ICON_NAMES) == len(ICONS) // WIDTH == EXPECTED_ICON_COUNT


def test_arrow_names_length_matches_data():
    assert len(ARROW_NAMES) == len(ARROWS) // WIDTH == EXPECTED_ARROW_COUNT


def test_icon_names_unique():
    assert len(set(ICON_NAMES)) == len(ICON_NAMES)


def test_arrow_names_unique():
    assert len(set(ARROW_NAMES)) == len(ARROW_NAMES)


def test_icon_names_are_identifiers():
    assert all(n.isidentifier() for n in ICON_NAMES)


def test_arrow_names_are_identifiers():
    assert all(n.isidentifier() for n in ARROW_NAMES)


def test_lighthouse_icon_names_present():
    for name in LIGHTHOUSE_ICONS:
        assert name in ICON_NAMES


def test_lighthouse_arrow_names_present():
    for name in LIGHTHOUSE_ARROWS:
        assert name in ARROW_NAMES


def _slice_named(names, data, name):
    i = names.index(name)
    return data[i * WIDTH : (i + 1) * WIDTH]


def test_yes_no_diamond_bitmaps_are_nonzero():
    for name in LIGHTHOUSE_ICONS:
        blob = _slice_named(ICON_NAMES, ICONS, name)
        assert any(blob), f"{name} bitmap is empty"


def test_compass_arrow_bitmaps_are_nonzero():
    for name in LIGHTHOUSE_ARROWS:
        blob = _slice_named(ARROW_NAMES, ARROWS, name)
        assert any(blob), f"{name} bitmap is empty"
        assert len(blob) == WIDTH
