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
    _, buttons = queue_and_buttons
    for name in ("on_a_pressed", "on_b_pressed", "on_c_pressed", "on_d_pressed"):
        assert callable(getattr(buttons, name))


@pytest.mark.asyncio
async def test_c_pressed_fires_on_fake_fall(queue_and_buttons):
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
    queue, buttons = queue_and_buttons
    fired = []
    buttons.on_c_pressed(lambda: fired.append("c"))
    buttons.clear()
    buttons._dispatch(FakeEvent(key_number=2, pressed=True))
    assert fired == []


def test_a_and_b_pressed_exist_need_not_fire_overnight(queue_and_buttons):
    _, buttons = queue_and_buttons
    buttons.on_a_pressed(lambda: None)
    buttons.on_b_pressed(lambda: None)
