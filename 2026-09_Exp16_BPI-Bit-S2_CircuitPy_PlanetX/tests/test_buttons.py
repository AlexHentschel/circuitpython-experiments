"""
Async button dispatcher: fake EventQueue events fire handlers on Button / pairs.

Does not import ``board``, Blinka ``keypad``, or ``display.core``.
Event shape matches CircuitPython ``keypad.Event`` (``.key_number``, ``.pressed``).
"""

import asyncio

import pytest

from buttons import Button, ButtonPair, OnboardButtons, PlanetXButtonSensor, PushButton


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


@pytest.mark.asyncio
async def test_button_ignores_nonzero_key_number(queue):
    """Standalone Button only dispatches key_number 0.

    - Covers: a pair-style index 1 leaking into a 1-pin scanner.
    - How: inject ``FakeEvent(1, pressed=True)``; ``fired`` stays empty.
    """
    button = Button(event_queue=queue)
    fired = []
    button.on_pressed(lambda: fired.append("p"))
    queue.send(FakeEvent(key_number=1, pressed=True))
    await _one_tick(button)
    assert fired == []


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


def test_button_requires_pin_or_event_queue():
    """Public ``Button()`` with neither pin nor queue raises at construct time.

    - Covers: a silent handler-bag that only fails later at ``run()``.
    - How: ``Button()`` raises ``ValueError``.
    """
    with pytest.raises(ValueError, match="pin is required"):
        Button()


def test_pushbutton_has_no_run():
    """``PushButton`` is handlers only; ``run()`` lives on ``Button`` / ``ButtonPair``.

    - Covers: pair children exposing ``run`` (student ``await pair.left.run()``).
    - How: ``PushButton`` and ``pair.left`` have no ``run`` attribute.
    """
    pair = ButtonPair(event_queue=FakeEventQueue())
    assert not hasattr(PushButton, "run")
    assert not hasattr(pair.left, "run")
    assert type(pair.left) is PushButton
    assert not isinstance(pair.left, Button)


@pytest.mark.asyncio
async def test_pair_left_and_right_fire(queue):
    """key_number 0/1 run left/right handlers on a generic pair.

    - Covers: swapped indices, or both events hitting the same Button.
    - How: register both sides; inject 0 then 1; ``fired == ["L", "R"]``.
    """
    pair = ButtonPair(event_queue=queue)
    fired = []
    pair.left.on_pressed(lambda: fired.append("L"))
    pair.right.on_pressed(lambda: fired.append("R"))
    queue.send(FakeEvent(key_number=0, pressed=True))
    queue.send(FakeEvent(key_number=1, pressed=True))
    await _one_tick(pair)
    assert fired == ["L", "R"]


def test_pair_clear_drops_both(queue):
    """``ButtonPair.clear()`` drops handlers on left and right.

    - Covers: ``clear`` only wiping one side.
    - How: register both, ``clear()``, ``_dispatch`` 0 and 1; ``fired`` empty.
    """
    pair = ButtonPair(event_queue=queue)
    fired = []
    pair.left.on_pressed(lambda: fired.append("L"))
    pair.right.on_pressed(lambda: fired.append("R"))
    pair.clear()
    pair._dispatch(FakeEvent(key_number=0, pressed=True))
    pair._dispatch(FakeEvent(key_number=1, pressed=True))
    assert fired == []


def test_pair_rejects_out_of_range_index(queue):
    """Negative / too-large key_number does not wrap onto left or right.

    - Covers: bare IndexError wrap of ``-1`` onto the last element.
    - How: ``_dispatch`` key_number -1 and 2; ``fired`` stays empty.
    """
    pair = ButtonPair(event_queue=queue)
    fired = []
    pair.left.on_pressed(lambda: fired.append("L"))
    pair.right.on_pressed(lambda: fired.append("R"))
    pair._dispatch(FakeEvent(key_number=-1, pressed=True))
    pair._dispatch(FakeEvent(key_number=2, pressed=True))
    assert fired == []


@pytest.mark.asyncio
async def test_planetx_c_and_d_pressed(queue):
    """PlanetX C is left (key 0), D is right (key 1).

    - Covers: C/D swapped, or letters bound to a different instance.
    - How: ``on_c_pressed`` / ``on_d_pressed``; inject 0 then 1; ``fired == ["c", "d"]``.
    """
    px = PlanetXButtonSensor(event_queue=queue)
    fired = []
    px.on_c_pressed(lambda: fired.append("c"))
    px.on_d_pressed(lambda: fired.append("d"))
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
    px1.on_c_pressed(lambda: fired1.append("c"))
    px2.on_c_pressed(lambda: fired2.append("c"))
    px2._dispatch(FakeEvent(key_number=0, pressed=True))
    assert fired1 == []
    assert fired2 == ["c"]


def test_planetx_clear_c_leaves_d(queue):
    """``clear_c()`` drops C handlers and leaves D.

    - Covers: ``clear_c`` clearing the whole pair.
    - How: register C and D, ``clear_c()``, dispatch both; only D fires.
    """
    px = PlanetXButtonSensor(event_queue=queue)
    fired = []
    px.on_c_pressed(lambda: fired.append("c"))
    px.on_d_pressed(lambda: fired.append("d"))
    px.clear_c()
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
    ab.on_a_pressed(lambda: fired.append("a"))
    ab.on_b_pressed(lambda: fired.append("b"))
    queue.send(FakeEvent(key_number=0, pressed=True))
    queue.send(FakeEvent(key_number=1, pressed=True))
    await _one_tick(ab)
    assert fired == ["a", "b"]


def test_no_update_on_public_classes():
    """Student API has no Exp09-style ``update()`` loop.

    - Covers: ``update`` sneaking onto Button or a pair class.
    - How: ``hasattr(..., "update")`` is false on the public button classes.
    """
    for cls in (PushButton, Button, ButtonPair, PlanetXButtonSensor, OnboardButtons):
        assert not hasattr(cls, "update")
