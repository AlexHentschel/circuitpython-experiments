"""
Async button dispatcher: fake EventQueue FALL events fire C/D handlers.

Does not import ``board``, Blinka ``keypad``, or ``display.core``.
Event shape matches CircuitPython ``keypad.Event`` (``.key_number``, ``.pressed``).
"""

import asyncio

import pytest

from buttons import Buttons


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


@pytest.fixture
def queue_and_buttons():
    queue = FakeEventQueue()
    buttons = Buttons(event_queue=queue)
    return queue, buttons


def test_constructor_exposes_a_b_c_d_pressed_names(queue_and_buttons):
    """Student press-handler registration exists for A, B, C, and D.

    - Covers: overnight bar that A/B names exist even if C/D are the PlanetX pair.
    - How: ``getattr`` each ``on_*_pressed``; must be callable. Does not fire events.
    """
    _, buttons = queue_and_buttons
    for name in ("on_a_pressed", "on_b_pressed", "on_c_pressed", "on_d_pressed"):
        assert callable(getattr(buttons, name))


@pytest.mark.asyncio
async def test_c_pressed_fires_on_fake_fall(queue_and_buttons):
    """A FALL on key_number 2 runs the C pressed handler.

    - Covers: C not wired, or index 2 mapped to another letter.
    - How: inject ``FakeEvent(2, pressed=True)``; one ``run()`` tick; ``fired == ["c"]``.
    """
    queue, buttons = queue_and_buttons
    fired = []
    buttons.on_c_pressed(lambda: fired.append("c"))
    queue.send(FakeEvent(key_number=2, pressed=True))
    task = asyncio.create_task(buttons.run())
    await asyncio.sleep(0)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert fired == ["c"]


@pytest.mark.asyncio
async def test_d_pressed_fires_on_fake_fall(queue_and_buttons):
    """A FALL on key_number 3 runs the D pressed handler.

    - Covers: D not wired, or index 3 mapped to another letter.
    - How: inject ``FakeEvent(3, pressed=True)``; one ``run()`` tick; ``fired == ["d"]``.
    """
    queue, buttons = queue_and_buttons
    fired = []
    buttons.on_d_pressed(lambda: fired.append("d"))
    queue.send(FakeEvent(key_number=3, pressed=True))
    task = asyncio.create_task(buttons.run())
    await asyncio.sleep(0)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert fired == ["d"]


def test_clear_drops_c_handler(queue_and_buttons):
    """``clear()`` removes previously registered C handlers.

    - Covers: ``clear`` as a no-op, or only clearing A/B.
    - How: register C, ``clear()``, ``_dispatch`` a C FALL; ``fired`` stays empty.
    """
    queue, buttons = queue_and_buttons
    fired = []
    buttons.on_c_pressed(lambda: fired.append("c"))
    buttons.clear()
    buttons._dispatch(FakeEvent(key_number=2, pressed=True))
    assert fired == []


def test_a_and_b_pressed_exist_need_not_fire_overnight(queue_and_buttons):
    """A and B handler registration is callable (overnight does not require a FALL).

    - Covers: missing ``on_a_pressed`` / ``on_b_pressed`` after C/D were added.
    - How: call both with a no-op. Does not pump the queue.
    """
    _, buttons = queue_and_buttons
    buttons.on_a_pressed(lambda: None)
    buttons.on_b_pressed(lambda: None)
