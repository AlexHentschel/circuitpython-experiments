"""Guard: overnight host suite never imports ``board`` or ``display.core``."""

import sys

import display
import display.bitmap_codec  # noqa: F401
import display.font_makecode_5  # noqa: F401
import display.geometry  # noqa: F401
import display.icons  # noqa: F401
import buttons  # noqa: F401


def test_display_package_skips_core_on_cpython():
    """Importing ``display`` on host CPython must not load ``display.core``.

    - Covers: ``__init__`` pulling in ``core`` (and thus ``board``/``neopixel``) on CPython.
    - How: after package import, ``display.core`` absent from ``sys.modules``; ``_HAS_HARDWARE`` is False.
    """
    assert "display.core" not in sys.modules
    assert display._HAS_HARDWARE is False


def test_board_not_imported_by_pure_stack():
    """The overnight stack must not ``import board`` (Blinka in this venv is broken on purpose).

    - Covers: a pure submodule or ``buttons`` pulling ``board`` as a side effect.
    - How: after the module-level imports above, ``board`` absent from ``sys.modules``.
    """
    # Blinka ``board`` in this venv is broken on purpose; tests must not need it.
    assert "board" not in sys.modules
