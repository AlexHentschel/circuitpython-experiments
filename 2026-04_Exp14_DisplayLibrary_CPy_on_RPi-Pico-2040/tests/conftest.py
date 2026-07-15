"""
Tier 1 test setup: prepend ``lib/`` so ``import display.<submodule>``
resolves without an editable install. No stubs -- Tier 1 exercises only
the pure sub-modules (``_constants``, ``bitmap_codec``, ``geometry``,
``icons``) which have no hardware dependencies. ``display.__init__``
guards the core import with a ``board`` presence check, so package
initialisation succeeds on CPython; pure sub-module imports therefore
never trigger ``core.py``.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "lib"))
