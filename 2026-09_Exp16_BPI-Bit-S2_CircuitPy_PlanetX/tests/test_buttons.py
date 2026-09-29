"""
Async button dispatcher: fake EventQueue events fire handlers on Button / pairs.

Does not import ``board``, Blinka ``keypad``, or ``display.core``.
Event shape matches CircuitPython ``keypad.Event`` (``.key_number``, ``.pressed``).
"""

import asyncio
import warnings

import pytest

from buttons import Button, OnboardButtons, PushButtonBase, _LANE_MAX, _SwitchLane
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


async def _one_tick(runner, turns=3):
    """Let ``run()`` and its per-switch tasks drain queued events, then cancel.

    The first ``sleep(0)`` runs the pump until it parks on its 10 ms sleep.
    The switch tasks are scheduled during that turn, so they need a later
    turn before a synchronous handler has run.
    """
    task = asyncio.create_task(runner.run())
    for _ in range(turns):
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
async def test_async_handler_and_bound_method_run():
    """An ``async def`` and an async bound method both run their bodies.

    - Covers: a bare ``async def`` and ``Counter.on_press`` both execute when the switch is pressed.
    - How: register both; ``await _handle(True)``; the list and the counter each advance once.
    """
    button = PushButtonBase()

    async def on_bare():
        fired.append("bare")

    class Counter:
        def __init__(self):
            self.count = 0

        async def on_press(self):
            self.count += 1

    counter = Counter()
    fired = []
    button.on_pressed(on_bare)
    button.on_pressed(counter.on_press)
    await button._handle(True)
    assert fired == ["bare"]
    assert counter.count == 1


@pytest.mark.asyncio
async def test_async_handlers_run_in_registration_order():
    """The second handler starts after the first async handler returns.

    - Covers: handlers on one switch run in registration order, one finishing before the next starts.
    - How: the first handler sleeps, then appends; the second appends. Order is first-done, then second.
    """
    button = PushButtonBase()
    order = []

    async def first():
        order.append("first-start")
        await asyncio.sleep(0)
        order.append("first-done")

    async def second():
        order.append("second")

    button.on_pressed(first)
    button.on_pressed(second)
    await button._handle(True)
    assert order == ["first-start", "first-done", "second"]


@pytest.mark.asyncio
async def test_button_clear_drops_handler(queue):
    """``clear()`` removes previously registered handlers on that Button only.

    - Covers: ``clear`` as a no-op, or clearing a different button.
    - How: register, ``clear()``, ``_dispatch`` a FALL; ``fired`` stays empty.
    """
    button = Button(event_queue=queue)
    fired = []
    button.on_pressed(lambda: fired.append("p"))
    button.clear()
    await button._dispatch(FakeEvent(key_number=0, pressed=True))
    assert fired == []


@pytest.mark.asyncio
async def test_clear_pressed_leaves_released():
    """``clear_pressed()`` drops press handlers and leaves release handlers.

    - Covers: ``clear_pressed`` clearing both lists.
    - How: register both, ``clear_pressed()``, ``_handle`` True then False; only release fires.
    """
    button = PushButtonBase()
    fired = []
    button.on_pressed(lambda: fired.append("p"))
    button.on_released(lambda: fired.append("r"))
    button.clear_pressed()
    await button._handle(True)
    await button._handle(False)
    assert fired == ["r"]


@pytest.mark.asyncio
async def test_clear_released_leaves_pressed():
    """``clear_released()`` drops release handlers and leaves press handlers.

    - Covers: ``clear_released`` clearing both lists.
    - How: register both, ``clear_released()``, ``_handle`` True then False; only press fires.
    """
    button = PushButtonBase()
    fired = []
    button.on_pressed(lambda: fired.append("p"))
    button.on_released(lambda: fired.append("r"))
    button.clear_released()
    await button._handle(True)
    await button._handle(False)
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


@pytest.mark.asyncio
async def test_onboard_clear_drops_both(queue):
    """``OnboardButtons.clear()`` drops handlers on both A and B.

    - Covers: ``clear`` only wiping one side.
    - How: register both, ``clear()``, ``_dispatch`` 0 and 1; ``fired`` empty.
    """
    ab = OnboardButtons(event_queue=queue)
    fired = []
    ab.button_a.on_pressed(lambda: fired.append("a"))
    ab.button_b.on_pressed(lambda: fired.append("b"))
    ab.clear()
    await ab._dispatch(FakeEvent(key_number=0, pressed=True))
    await ab._dispatch(FakeEvent(key_number=1, pressed=True))
    assert fired == []


@pytest.mark.asyncio
async def test_onboard_rejects_out_of_range_index(queue):
    """Negative / too-large key_number does not wrap onto A or B.

    - Covers: bare IndexError wrap of ``-1`` onto the last element.
    - How: ``_dispatch`` key_number -1 and 2; ``fired`` stays empty.
    """
    ab = OnboardButtons(event_queue=queue)
    fired = []
    ab.button_a.on_pressed(lambda: fired.append("a"))
    ab.button_b.on_pressed(lambda: fired.append("b"))
    await ab._dispatch(FakeEvent(key_number=-1, pressed=True))
    await ab._dispatch(FakeEvent(key_number=2, pressed=True))
    assert fired == []


@pytest.mark.asyncio
async def test_planetx_clear_drops_both(queue):
    """``PlanetXButtonSensor.clear()`` drops handlers on both C and D.

    - Covers: ``clear`` only wiping one side.
    - How: register both, ``clear()``, ``_dispatch`` 0 and 1; ``fired`` empty.
    """
    px = PlanetXButtonSensor(event_queue=queue)
    fired = []
    px.button_c.on_pressed(lambda: fired.append("c"))
    px.button_d.on_pressed(lambda: fired.append("d"))
    px.clear()
    await px._dispatch(FakeEvent(key_number=0, pressed=True))
    await px._dispatch(FakeEvent(key_number=1, pressed=True))
    assert fired == []


@pytest.mark.asyncio
async def test_planetx_rejects_out_of_range_index(queue):
    """Negative / too-large key_number does not wrap onto C or D.

    - Covers: bare IndexError wrap of ``-1`` onto the last element.
    - How: ``_dispatch`` key_number -1 and 2; ``fired`` stays empty.
    """
    px = PlanetXButtonSensor(event_queue=queue)
    fired = []
    px.button_c.on_pressed(lambda: fired.append("c"))
    px.button_d.on_pressed(lambda: fired.append("d"))
    await px._dispatch(FakeEvent(key_number=-1, pressed=True))
    await px._dispatch(FakeEvent(key_number=2, pressed=True))
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


@pytest.mark.asyncio
async def test_two_planetx_instances_are_independent():
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
    await px2._dispatch(FakeEvent(key_number=0, pressed=True))
    assert fired1 == []
    assert fired2 == ["c"]


@pytest.mark.asyncio
async def test_planetx_clear_c_leaves_d(queue):
    """``button_c.clear()`` drops C handlers and leaves D.

    - Covers: ``clear`` on one switch clearing the whole pair.
    - How: register C and D, ``button_c.clear()``, dispatch both; only D fires.
    """
    px = PlanetXButtonSensor(event_queue=queue)
    fired = []
    px.button_c.on_pressed(lambda: fired.append("c"))
    px.button_d.on_pressed(lambda: fired.append("d"))
    px.button_c.clear()
    await px._dispatch(FakeEvent(key_number=0, pressed=True))
    await px._dispatch(FakeEvent(key_number=1, pressed=True))
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


@pytest.mark.asyncio
async def test_other_switch_runs_during_await(queue):
    """B's handler runs while A's async handler is suspended.

    - Covers: both switches sharing one task, so B waits until A returns.
    - How: A awaits ``sleep(0)``; B is a sync press already queued; B appears before ``a-end``.
    """
    ab = OnboardButtons(event_queue=queue)
    order = []

    async def on_a():
        order.append("a-start")
        await asyncio.sleep(0)
        order.append("a-end")

    ab.button_a.on_pressed(on_a)
    ab.button_b.on_pressed(lambda: order.append("b"))
    queue.send(FakeEvent(key_number=0, pressed=True))
    queue.send(FakeEvent(key_number=1, pressed=True))
    await _one_tick(ab, turns=6)
    assert order.index("a-start") < order.index("b") < order.index("a-end")


@pytest.mark.asyncio
async def test_same_switch_events_stay_sequential(queue):
    """A second press on A waits until the first press's handler returns.

    - Covers: two events on one switch overlapping because each has its own task.
    - How: one async handler, two queued presses; the log is start, end, start, end.
    """
    button = Button(event_queue=queue)
    order = []

    async def on_press():
        order.append("start")
        await asyncio.sleep(0)
        order.append("end")

    button.on_pressed(on_press)
    queue.send(FakeEvent(key_number=0, pressed=True))
    queue.send(FakeEvent(key_number=0, pressed=True))
    await _one_tick(button, turns=6)
    assert order == ["start", "end", "start", "end"]


@pytest.mark.asyncio
async def test_handler_error_leaves_the_other_switch_running(queue):
    """An exception on A is reported and B still runs. ``run()`` stays alive.

    - Covers: one handler error ending the whole module's ``run()``.
    - How: A raises; B is queued; after the drive, ``fired == ["b"]`` and cancel is ``CancelledError``.
    """
    ab = OnboardButtons(event_queue=queue)
    fired = []

    def boom():
        raise RuntimeError("boom")

    ab.button_a.on_pressed(boom)
    ab.button_b.on_pressed(lambda: fired.append("b"))
    queue.send(FakeEvent(key_number=0, pressed=True))
    queue.send(FakeEvent(key_number=1, pressed=True))
    await _one_tick(ab, turns=4)
    assert fired == ["b"]


@pytest.mark.asyncio
async def test_release_reaches_the_lane(queue):
    """A release event delivered by ``run()`` calls the release handler.

    - Covers: the lane forwarding only presses.
    - How: queue a release; one drive; ``fired == ["r"]``.
    """
    button = Button(event_queue=queue)
    fired = []
    button.on_released(lambda: fired.append("r"))
    queue.send(FakeEvent(key_number=0, pressed=False))
    await _one_tick(button)
    assert fired == ["r"]


@pytest.mark.asyncio
async def test_planetx_other_switch_runs_during_await(queue):
    """D runs while C's async handler is suspended.

    - Covers: PlanetX ``run()`` still awaiting both switches on one task.
    - How: C awaits ``sleep(0)``; D is already queued; D appears before ``c-end``.
    """
    px = PlanetXButtonSensor(event_queue=queue)
    order = []

    async def on_c():
        order.append("c-start")
        await asyncio.sleep(0)
        order.append("c-end")

    px.button_c.on_pressed(on_c)
    px.button_d.on_pressed(lambda: order.append("d"))
    queue.send(FakeEvent(key_number=0, pressed=True))
    queue.send(FakeEvent(key_number=1, pressed=True))
    await _one_tick(px, turns=6)
    assert order.index("c-start") < order.index("d") < order.index("c-end")


@pytest.mark.asyncio
async def test_error_skips_later_handlers_on_that_event(queue):
    """A raising handler skips the rest of that event. The next event still runs.

    - Covers: the lane dying, or continuing into the next handler of the failed event.
    - How: first handler raises, second is registered; one press then another; only the first handler of each press runs.
    """
    button = Button(event_queue=queue)
    order = []

    def boom():
        order.append("boom")
        raise RuntimeError("boom")

    def later():
        order.append("later")

    button.on_pressed(boom)
    button.on_pressed(later)
    queue.send(FakeEvent(key_number=0, pressed=True))
    queue.send(FakeEvent(key_number=0, pressed=True))
    await _one_tick(button, turns=4)
    assert order == ["boom", "boom"]


@pytest.mark.asyncio
async def test_sync_handler_returning_coroutine_is_awaited(queue):
    """A normal function's returned coroutine is awaited by the lane.

    - Covers: dropping a coroutine that the handler returned.
    - How: sync handler returns an async animation; the animation body runs.
    """
    button = Button(event_queue=queue)
    order = []

    async def anim():
        order.append("anim")

    def sync():
        return anim()

    button.on_pressed(sync)
    queue.send(FakeEvent(key_number=0, pressed=True))
    await _one_tick(button)
    assert order == ["anim"]


@pytest.mark.asyncio
async def test_async_handler_return_value_is_not_awaited(queue):
    """The coroutine returned by an async handler is not itself awaited.

    - Covers: awaiting both the handler and the object it returns.
    - How: async handler returns another coroutine; that body does not run.
    """
    button = Button(event_queue=queue)
    order = []

    async def anim():
        order.append("anim")

    async def handler():
        order.append("handler")
        return anim()

    button.on_pressed(handler)
    queue.send(FakeEvent(key_number=0, pressed=True))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        await _one_tick(button)
    assert order == ["handler"]


@pytest.mark.asyncio
async def test_clear_during_handle_still_runs_handlers_already_listed():
    """``clear()`` inside a handler does not drop the rest of this event.

    - Covers: ``clear`` replacing the list the ``for`` loop is already walking.
    - How: first handler calls ``clear()``; the second handler still appends.
    """
    button = PushButtonBase()
    seen = []

    def first():
        seen.append("1")
        button.clear()

    def second():
        seen.append("2")

    button.on_pressed(first)
    button.on_pressed(second)
    await button._handle(True)
    await button._handle(True)
    assert seen == ["1", "2"]


def test_lane_drops_events_past_the_cap():
    """A switch keeps at most ``_LANE_MAX`` events waiting.

    - Covers: an unbounded list while a handler awaits and that switch is pressed again.
    - How: ``offer`` ``_LANE_MAX + 5`` times with no ``run``; the list length is the cap.
    """
    lane = _SwitchLane(PushButtonBase())
    for _ in range(_LANE_MAX + 5):
        lane.offer(True)
    assert len(lane.pending) == _LANE_MAX


def test_no_update_on_public_classes():
    """Student API has no Exp09-style ``update()`` loop.

    - Covers: ``update`` sneaking onto Button or a pair class.
    - How: ``hasattr(..., "update")`` is false on the public button classes.
    """
    for cls in (PushButtonBase, Button, PlanetXButtonSensor, OnboardButtons):
        assert not hasattr(cls, "update")
