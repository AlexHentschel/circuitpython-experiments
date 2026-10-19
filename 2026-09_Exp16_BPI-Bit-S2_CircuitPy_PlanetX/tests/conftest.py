"""
Host-test setup: prepend ``lib/`` so ``import display.<submodule>``,
``import buttons``, and ``import planetx`` resolve without an editable install.

Most tests exercise pure sub-modules (``_constants``, ``bitmap_codec``,
``geometry``, ``icons``, ``font_makecode_5``) plus the button dispatcher
with a fake EventQueue. ``display.__init__`` guards the core import with a
``board`` presence check, so package initialisation succeeds on CPython.
``test_display_core_host.py`` is the exception: it installs stubs for the
duration of each test and removes them again, so ``board`` and
``display.core`` are not left in ``sys.modules``.
"""

import asyncio
import pathlib
import sys

import pytest

# Board deploy ("CP Copy Libs to Board") copies the whole lib/ folder verbatim
# -- there is no ignore-file mechanism in the sync extension (verified against
# its own source + docs, 2026-09-11; a folder-level ignore convention does not
# exist for it). Stop pytest's import machinery from littering lib/ with
# __pycache__/*.pyc that would otherwise ride along onto the ~960 KiB CIRCUITPY
# volume. Must be set before the lib/* imports below (and before test
# collection imports lib.* modules).
sys.dont_write_bytecode = True

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "lib"))


@pytest.fixture
def sleep_ms_shim():
    """Install ``asyncio.sleep_ms`` for one test, then remove it.

    Host CPython has no ``asyncio.sleep_ms``. The stand-in awaits
    ``asyncio.sleep(ms / 1000)``, so a pump waiting ``_POLL_MS`` parks and
    can be cancelled. Opt-in: a test requests this fixture.
    ``test_display_core_host.py`` saves and restores ``asyncio.sleep_ms``
    itself; an autouse shim would be the object that file saves.
    """

    async def sleep_ms(ms):
        await asyncio.sleep(ms / 1000)

    had_sleep_ms = hasattr(asyncio, "sleep_ms")
    previous = getattr(asyncio, "sleep_ms", None)
    asyncio.sleep_ms = sleep_ms
    try:
        yield sleep_ms
    finally:
        if had_sleep_ms:
            asyncio.sleep_ms = previous
        else:
            del asyncio.sleep_ms
