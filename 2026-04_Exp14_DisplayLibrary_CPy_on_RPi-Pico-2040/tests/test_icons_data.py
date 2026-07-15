"""
Shape, value-range, and name-alignment tests for ``display.icons``.

These checks pin the contract between ``ICON_NAMES`` / ``ARROW_NAMES``
(ordered string tuples) and the ``ICONS`` / ``ARROWS`` byte arrays.
``core.py`` consumes both at import time to build the user-facing
``Icons`` / ``Arrows`` wrapper classes, so a length mismatch here would
silently corrupt every ``Icons.<NAME>`` lookup downstream.
"""

from display._constants import WIDTH
from display.icons import ICONS, ARROWS, ICON_NAMES, ARROW_NAMES


EXPECTED_ICON_COUNT = 40
EXPECTED_ARROW_COUNT = 8


# ---------------------------------------------------------------------------
# Shape: array length must equal count * WIDTH bytes
# ---------------------------------------------------------------------------

def test_icons_length():
    assert len(ICONS) == EXPECTED_ICON_COUNT * WIDTH


def test_arrows_length():
    assert len(ARROWS) == EXPECTED_ARROW_COUNT * WIDTH


# ---------------------------------------------------------------------------
# Type: authoritative storage is immutable ``bytes``
# ---------------------------------------------------------------------------

def test_icons_is_bytes():
    assert isinstance(ICONS, bytes)


def test_arrows_is_bytes():
    assert isinstance(ARROWS, bytes)


# ---------------------------------------------------------------------------
# Byte range (tautology for ``bytes`` but kept as contract pin against a
# future type change to a signed or wider container).
# ---------------------------------------------------------------------------

def test_icons_byte_range():
    assert all(0 <= b <= 255 for b in ICONS)


def test_arrows_byte_range():
    assert all(0 <= b <= 255 for b in ARROWS)


# ---------------------------------------------------------------------------
# Name-list <-> data alignment
# ---------------------------------------------------------------------------

def test_icon_names_is_tuple_of_strings():
    assert isinstance(ICON_NAMES, tuple)
    assert all(isinstance(n, str) for n in ICON_NAMES)


def test_arrow_names_is_tuple_of_strings():
    assert isinstance(ARROW_NAMES, tuple)
    assert all(isinstance(n, str) for n in ARROW_NAMES)


def test_icon_names_length_matches_data():
    assert len(ICON_NAMES) == len(ICONS) // WIDTH == EXPECTED_ICON_COUNT


def test_arrow_names_length_matches_data():
    assert len(ARROW_NAMES) == len(ARROWS) // WIDTH == EXPECTED_ARROW_COUNT


def test_icon_names_unique():
    assert len(set(ICON_NAMES)) == len(ICON_NAMES)


def test_arrow_names_unique():
    assert len(set(ARROW_NAMES)) == len(ARROW_NAMES)


def test_icon_names_are_identifiers():
    """Names become ``Icons`` class attributes -- must be valid Python identifiers."""
    assert all(n.isidentifier() for n in ICON_NAMES)


def test_arrow_names_are_identifiers():
    assert all(n.isidentifier() for n in ARROW_NAMES)
