"""
Async button dispatcher: fake EventQueue events fire handlers on Button / pairs.

Does not import ``board``, Blinka ``keypad``, or ``display.core``.
Event shape matches CircuitPython ``keypad.Event`` (``.key_number``, ``.pressed``).
"""

import asyncio

import pytest

from buttons import Button, OnboardButtons, PushButtonBase
from planetx import PlanetXButtonSensor


class FakeEvent:
    def __init__(self, key_number, pressed):
        self.key_number = key_number
        self.pressed = pressed


class FakeEventQueue:
    def __init__(self):
        self._pending = []

    def send(self, event):
        self._pending.append(event)

    def get(self):
        if not self._pending:
            return None
        return self._pending.pop(0)


async def _one_tick(runner):
    """Pump ``run()`` through one ``asyncio.sleep`` then cancel."""
    task = asyncio.create_task(runner.run())
    await asyncio.sleep(0)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task


@pytest.fixture
def queue():
    return FakeEventQueue()


@pytest.mark.asyncio
async def test_button_press_fires(queue):
    """A FALL on key_number 0 runs the standalone Button pressed handler.

    - Covers: press handler never registered, or key_number 0 mapped elsewhere.
    - How: inject ``FakeEvent(0, pressed=True)``; one ``run()`` tick; ``fired == ["p"]``.
    """
    button = Button(event_queue=queue)
    fired = []
    button.on_pressed(lambda: fired.append("p"))
    queue.send(FakeEvent(key_number=0, pressed=True))
    await _one_tick(button)
    assert fired == ["p"]


def test_button_clear_drops_handler(queue):
    """``clear()`` removes previously registered handlers on that Button only.

    - Covers: ``clear`` as a no-op, or clearing a different button.
    - How: register, ``clear()``, ``_dispatch`` a FALL; ``fired`` stays empty.
    """
    button = Button(event_queue=queue)
    fired = []
    button.on_pressed(lambda: fired.append("p"))
    button.clear()
    button._dispatch(FakeEvent(key_number=0, pressed=True))
    assert fired == []


def test_clear_pressed_leaves_released():
    """``clear_pressed()`` drops press handlers and leaves release handlers.

    - Covers: ``clear_pressed`` clearing both lists.
    - How: register both, ``clear_pressed()``, ``_handle`` True then False; only release fires.
    """
    button = PushButtonBase()
    fired = []
    button.on_pressed(lambda: fired.append("p"))
    button.on_released(lambda: fired.append("r"))
    button.clear_pressed()
    button._handle(True)
    button._handle(False)
    assert fired == ["r"]


def test_clear_released_leaves_pressed():
    """``clear_released()`` drops release handlers and leaves press handlers.

    - Covers: ``clear_released`` clearing both lists.
    - How: register both, ``clear_released()``, ``_handle`` True then False; only press fires.
    """
    button = PushButtonBase()
    fired = []
    button.on_pressed(lambda: fired.append("p"))
    button.on_released(lambda: fired.append("r"))
    button.clear_released()
    button._handle(True)
    button._handle(False)
    assert fired == ["p"]


def test_button_requires_pin_or_event_queue():
    """Public ``Button()`` with neither pin nor queue raises at construct time.

    - Covers: a silent handler-bag that only fails later at ``run()``.
    - How: ``Button()`` raises ``ValueError``.
    """
    with pytest.raises(ValueError, match="pin is required"):
        Button()


def test_pushbutton_has_no_run():
    """``PushButtonBase`` is handlers only; ``run()`` lives on the owning button object.

    - Covers: a lettered button property exposing ``run`` (student ``await ab.button_a.run()``).
    - How: ``PushButtonBase``, ``OnboardButtons.button_a``, and ``PlanetXButtonSensor.button_c``
      all have no ``run`` attribute.
    """
    ab = OnboardButtons(event_queue=FakeEventQueue())
    px = PlanetXButtonSensor(event_queue=FakeEventQueue())
    assert not hasattr(PushButtonBase, "run")
    assert not hasattr(ab.button_a, "run")
    assert not hasattr(px.button_c, "run")
    assert type(ab.button_a) is PushButtonBase
    assert not isinstance(ab.button_a, Button)


# The following pair-mechanics checks (clear-drops-both, out-of-range index) are
# deliberately duplicated across OnboardButtons and PlanetXButtonSensor: since
# 2026-09-20 each owns its own copy of the dispatch/clear logic (no shared
# ButtonPair base — see buttons.py's module docstring), so each needs its own
# direct coverage instead of one shared test exercising a common base class.


def test_onboard_clear_drops_both(queue):
    """``OnboardButtons.clear()`` drops handlers on both A and B.

    - Covers: ``clear`` only wiping one side.
    - How: register both, ``clear()``, ``_dispatch`` 0 and 1; ``fired`` empty.
    """
    ab = OnboardButtons(event_queue=queue)
    fired = []
    ab.button_a.on_pressed(lambda: fired.append("a"))
    ab.button_b.on_pressed(lambda: fired.append("b"))
    ab.clear()
    ab._dispatch(FakeEvent(key_number=0, pressed=True))
    ab._dispatch(FakeEvent(key_number=1, pressed=True))
    assert fired == []


def test_onboard_rejects_out_of_range_index(queue):
    """Negative / too-large key_number does not wrap onto A or B.

    - Covers: bare IndexError wrap of ``-1`` onto the last element.
    - How: ``_dispatch`` key_number -1 and 2; ``fired`` stays empty.
    """
    ab = OnboardButtons(event_queue=queue)
    fired = []
    ab.button_a.on_pressed(lambda: fired.append("a"))
    ab.button_b.on_pressed(lambda: fired.append("b"))
    ab._dispatch(FakeEvent(key_number=-1, pressed=True))
    ab._dispatch(FakeEvent(key_number=2, pressed=True))
    assert fired == []


def test_planetx_clear_drops_both(queue):
    """``PlanetXButtonSensor.clear()`` drops handlers on both C and D.

    - Covers: ``clear`` only wiping one side.
    - How: register both, ``clear()``, ``_dispatch`` 0 and 1; ``fired`` empty.
    """
    px = PlanetXButtonSensor(event_queue=queue)
    fired = []
    px.button_c.on_pressed(lambda: fired.append("c"))
    px.button_d.on_pressed(lambda: fired.append("d"))
    px.clear()
    px._dispatch(FakeEvent(key_number=0, pressed=True))
    px._dispatch(FakeEvent(key_number=1, pressed=True))
    assert fired == []


def test_planetx_rejects_out_of_range_index(queue):
    """Negative / too-large key_number does not wrap onto C or D.

    - Covers: bare IndexError wrap of ``-1`` onto the last element.
    - How: ``_dispatch`` key_number -1 and 2; ``fired`` stays empty.
    """
    px = PlanetXButtonSensor(event_queue=queue)
    fired = []
    px.button_c.on_pressed(lambda: fired.append("c"))
    px.button_d.on_pressed(lambda: fired.append("d"))
    px._dispatch(FakeEvent(key_number=-1, pressed=True))
    px._dispatch(FakeEvent(key_number=2, pressed=True))
    assert fired == []


@pytest.mark.asyncio
async def test_planetx_c_and_d_pressed(queue):
    """PlanetX C is left (key 0), D is right (key 1).

    - Covers: C/D swapped, or letters bound to a different instance.
    - How: ``button_c.on_pressed`` / ``button_d.on_pressed``; inject 0 then 1; ``fired == ["c", "d"]``.
    """
    px = PlanetXButtonSensor(event_queue=queue)
    fired = []
    px.button_c.on_pressed(lambda: fired.append("c"))
    px.button_d.on_pressed(lambda: fired.append("d"))
    queue.send(FakeEvent(key_number=0, pressed=True))
    queue.send(FakeEvent(key_number=1, pressed=True))
    await _one_tick(px)
    assert fired == ["c", "d"]


def test_two_planetx_instances_are_independent():
    """Two PlanetX sensors both have C/D locally; handlers do not cross.

    - Covers: a global C/D table so the second instance overwrites the first.
    - How: two queues; C on each; dispatch only the second; first ``fired`` empty.
    """
    q1, q2 = FakeEventQueue(), FakeEventQueue()
    px1 = PlanetXButtonSensor(event_queue=q1)
    px2 = PlanetXButtonSensor(event_queue=q2)
    fired1, fired2 = [], []
    px1.button_c.on_pressed(lambda: fired1.append("c"))
    px2.button_c.on_pressed(lambda: fired2.append("c"))
    px2._dispatch(FakeEvent(key_number=0, pressed=True))
    assert fired1 == []
    assert fired2 == ["c"]


def test_planetx_clear_c_leaves_d(queue):
    """``button_c.clear()`` drops C handlers and leaves D.

    - Covers: ``clear`` on one switch clearing the whole pair.
    - How: register C and D, ``button_c.clear()``, dispatch both; only D fires.
    """
    px = PlanetXButtonSensor(event_queue=queue)
    fired = []
    px.button_c.on_pressed(lambda: fired.append("c"))
    px.button_d.on_pressed(lambda: fired.append("d"))
    px.button_c.clear()
    px._dispatch(FakeEvent(key_number=0, pressed=True))
    px._dispatch(FakeEvent(key_number=1, pressed=True))
    assert fired == ["d"]


@pytest.mark.asyncio
async def test_onboard_a_and_b_pressed(queue):
    """Onboard A is left (key 0), B is right (key 1), via ``event_queue`` (no ``board``).

    - Covers: missing A/B names after the pair split, or importing ``board`` on host.
    - How: ``OnboardButtons(event_queue=)``; inject 0 then 1; ``fired == ["a", "b"]``.
    """
    ab = OnboardButtons(event_queue=queue)
    fired = []
    ab.button_a.on_pressed(lambda: fired.append("a"))
    ab.button_b.on_pressed(lambda: fired.append("b"))
    queue.send(FakeEvent(key_number=0, pressed=True))
    queue.send(FakeEvent(key_number=1, pressed=True))
    await _one_tick(ab)
    assert fired == ["a", "b"]


def test_no_update_on_public_classes():
    """Student API has no Exp09-style ``update()`` loop.

    - Covers: ``update`` sneaking onto Button or a pair class.
    - How: ``hasattr(..., "update")`` is false on the public button classes.
    """
    for cls in (PushButtonBase, Button, PlanetXButtonSensor, OnboardButtons):
        assert not hasattr(cls, "update")
