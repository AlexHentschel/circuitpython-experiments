"""
Async button dispatcher: fake EventQueue events fire the one handler on a Button.

Does not import ``board``, Blinka ``keypad``, or ``display.core``.
Event shape matches CircuitPython ``keypad.Event`` (``.key_number``, ``.pressed``).
``key_number`` is ignored: each ``Button`` has its own queue.
"""

import asyncio
import sys
import types
import warnings

import pytest

from buttons import Button, OnboardButtons, _OVERFLOW_WARNING
from planetx import PlanetXButtonSensor, PlanetXCrashSensor

pytestmark = pytest.mark.usefixtures("sleep_ms_shim")


class FakeEvent:
    def __init__(self, key_number, pressed):
        self.key_number = key_number
        self.pressed = pressed


class FakeEventQueue:
    def __init__(self):
        self._pending = []
        self.overflowed = False

    def send(self, event):
        self._pending.append(event)

    def get(self):
        if not self._pending:
            return None
        return self._pending.pop(0)

    def clear(self):
        self._pending.clear()
        self.overflowed = False


def _onboard():
    qa, qb = FakeEventQueue(), FakeEventQueue()
    pair = OnboardButtons._from_buttons(Button._from_queue(qa), Button._from_queue(qb))
    return pair, qa, qb


def _planetx():
    qc, qd = FakeEventQueue(), FakeEventQueue()
    pair = PlanetXButtonSensor._from_buttons(Button._from_queue(qc), Button._from_queue(qd))
    return pair, qc, qd


async def _one_tick(runner, turns=3):
    """Run ``runner.run()`` for ``turns`` yields, then cancel.

    One yield lets a pump drain its queue and park on ``sleep_ms``. An async
    handler that awaits ``sleep(0)`` needs a later yield to finish.
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
    """A queued press runs the standalone Button pressed handler.

    - Covers: press handler never registered.
    - How: inject one press; one ``run()`` tick; ``fired == ["p"]``.
    """
    button = Button._from_queue(queue)
    fired = []
    button.on_pressed(lambda: fired.append("p"))
    queue.send(FakeEvent(key_number=0, pressed=True))
    await _one_tick(button)
    assert fired == ["p"]


@pytest.mark.asyncio
async def test_async_handler_and_bound_method_run():
    """An ``async def`` and an async bound method each run when they are the one slot.

    - Covers: a bare ``async def`` or ``Counter.on_press`` never executing.
    - How: deliver with the ``async def``; replace with the bound method; deliver again.
    """
    button = Button._from_queue(FakeEventQueue())

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
    await button._on_event(True)
    button.on_pressed(counter.on_press)
    await button._on_event(True)
    assert fired == ["bare"]
    assert counter.count == 1


@pytest.mark.asyncio
async def test_second_on_pressed_replaces(queue):
    """The second ``on_pressed`` is the only press handler that runs.

    - Covers: both handlers running, as a list would.
    - How: register two press handlers; one press; ``fired == ["new"]``.
    """
    button = Button._from_queue(queue)
    fired = []
    button.on_pressed(lambda: fired.append("old"))
    button.on_pressed(lambda: fired.append("new"))
    queue.send(FakeEvent(key_number=0, pressed=True))
    await _one_tick(button)
    assert fired == ["new"]


@pytest.mark.asyncio
async def test_on_pressed_none_leaves_released():
    """``on_pressed(None)`` clears the press slot and leaves the release handler.

    - Covers: clearing both events, or clearing another button.
    - How: register both; clear press; deliver press then release; only release fires.
    """
    button = Button._from_queue(FakeEventQueue())
    fired = []
    button.on_pressed(lambda: fired.append("p"))
    button.on_released(lambda: fired.append("r"))
    button.on_pressed(None)
    await button._on_event(True)
    await button._on_event(False)
    assert fired == ["r"]


@pytest.mark.asyncio
async def test_on_released_none_leaves_pressed():
    """``on_released(None)`` clears the release slot and leaves the press handler.

    - Covers: clearing both events.
    - How: register both; clear release; deliver press then release; only press fires.
    """
    button = Button._from_queue(FakeEventQueue())
    fired = []
    button.on_pressed(lambda: fired.append("p"))
    button.on_released(lambda: fired.append("r"))
    button.on_released(None)
    await button._on_event(True)
    await button._on_event(False)
    assert fired == ["p"]


def test_button_requires_pin():
    """Public ``Button()`` without a pin raises at construct time; the queue seam is not a keyword.

    - Covers: a silent handler-bag that only fails later at ``run()``, or ``event_queue=`` back on the signature.
    - How: ``Button()`` and ``Button(event_queue=...)`` raise ``TypeError``.
    """
    with pytest.raises(TypeError):
        Button()
    with pytest.raises(TypeError):
        Button(event_queue=FakeEventQueue())


@pytest.mark.asyncio
async def test_onboard_none_leaves_the_other_button():
    """Clearing A's press leaves A's release and B's press.

    - Covers: one ``on_pressed(None)`` clearing the whole pair.
    - How: ``_on_event`` A press, A release, and B press; only the last two fire.
    """
    ab, _qa, _qb = _onboard()
    fired = []
    ab.button_a.on_pressed(lambda: fired.append("a"))
    ab.button_a.on_released(lambda: fired.append("ar"))
    ab.button_b.on_pressed(lambda: fired.append("b"))
    ab.button_a.on_pressed(None)
    await ab.button_a._on_event(True)
    await ab.button_a._on_event(False)
    await ab.button_b._on_event(True)
    assert fired == ["ar", "b"]


@pytest.mark.asyncio
async def test_planetx_none_leaves_the_other_switch():
    """Clearing C's press leaves D's press.

    - Covers: one ``on_pressed(None)`` clearing the whole module.
    - How: ``_on_event`` C and D; only D fires.
    """
    px, _qc, _qd = _planetx()
    fired = []
    px.button_c.on_pressed(lambda: fired.append("c"))
    px.button_d.on_pressed(lambda: fired.append("d"))
    px.button_c.on_pressed(None)
    await px.button_c._on_event(True)
    await px.button_d._on_event(True)
    assert fired == ["d"]


@pytest.mark.asyncio
async def test_planetx_c_and_d_pressed():
    """PlanetX C and D each receive the press sent on their own queue.

    - Covers: C/D swapped, or letters bound to a different instance.
    - How: ``_from_buttons``; one press on each queue; both letters appear.
    """
    px, qc, qd = _planetx()
    fired = []
    px.button_c.on_pressed(lambda: fired.append("c"))
    px.button_d.on_pressed(lambda: fired.append("d"))
    qc.send(FakeEvent(key_number=0, pressed=True))
    qd.send(FakeEvent(key_number=0, pressed=True))
    await _one_tick(px)
    assert fired == ["c", "d"]


@pytest.mark.asyncio
async def test_two_planetx_instances_are_independent():
    """Two PlanetX sensors both have C locally; handlers do not cross.

    - Covers: a global C table so the second instance overwrites the first.
    - How: two pairs; deliver only the second C; the first list stays empty.
    """
    px1, _qc1, _qd1 = _planetx()
    px2, _qc2, _qd2 = _planetx()
    fired1, fired2 = [], []
    px1.button_c.on_pressed(lambda: fired1.append("c"))
    px2.button_c.on_pressed(lambda: fired2.append("c"))
    await px2.button_c._on_event(True)
    assert fired1 == []
    assert fired2 == ["c"]


@pytest.mark.asyncio
async def test_onboard_a_and_b_pressed():
    """Onboard A and B each receive the press sent on their own queue.

    - Covers: missing A/B names after the pair split, or importing ``board`` on the host.
    - How: ``_from_buttons``; one press on each queue; both letters appear.
    """
    ab, qa, qb = _onboard()
    fired = []
    ab.button_a.on_pressed(lambda: fired.append("a"))
    ab.button_b.on_pressed(lambda: fired.append("b"))
    qa.send(FakeEvent(key_number=0, pressed=True))
    qb.send(FakeEvent(key_number=0, pressed=True))
    await _one_tick(ab)
    assert fired == ["a", "b"]


@pytest.mark.asyncio
async def test_other_switch_runs_during_await():
    """B's handler runs while A's async handler is suspended.

    - Covers: both switches sharing one task, so B waits until A returns.
    - How: A awaits ``sleep(0)``; B is a sync press already queued; B appears before ``a-end``.
    """
    ab, qa, qb = _onboard()
    order = []

    async def on_a():
        order.append("a-start")
        await asyncio.sleep(0)
        order.append("a-end")

    ab.button_a.on_pressed(on_a)
    ab.button_b.on_pressed(lambda: order.append("b"))
    qa.send(FakeEvent(key_number=0, pressed=True))
    qb.send(FakeEvent(key_number=0, pressed=True))
    await _one_tick(ab, turns=6)
    assert order.index("a-start") < order.index("b") < order.index("a-end")


@pytest.mark.asyncio
async def test_same_switch_events_stay_sequential(queue):
    """A second press on A waits until the first press's handler returns.

    - Covers: two events on one button overlapping.
    - How: one async handler, two queued presses; the log is start, end, start, end.
    """
    button = Button._from_queue(queue)
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
async def test_mixed_events_finish_one_at_a_time(queue):
    """Press, press, release run in that order, each finishing before the next starts.

    - Covers: a release overtaking a press, or two presses overlapping.
    - How: async press handler and sync release handler; log is two full presses, then release.
    """
    button = Button._from_queue(queue)
    order = []

    async def on_press():
        order.append("p-start")
        await asyncio.sleep(0)
        order.append("p-end")

    button.on_pressed(on_press)
    button.on_released(lambda: order.append("r"))
    queue.send(FakeEvent(key_number=0, pressed=True))
    queue.send(FakeEvent(key_number=0, pressed=True))
    queue.send(FakeEvent(key_number=0, pressed=False))
    await _one_tick(button, turns=8)
    assert order == ["p-start", "p-end", "p-start", "p-end", "r"]


@pytest.mark.asyncio
async def test_handler_error_leaves_the_other_switch_running(queue):
    """An exception on A is reported and B still runs. ``run()`` stays alive.

    - Covers: one handler error ending the whole module's ``run()``.
    - How: A raises; B is queued; after the drive, ``fired == ["b"]`` and cancel is ``CancelledError``.
    """
    ab, qa, qb = _onboard()
    fired = []

    def boom():
        raise RuntimeError("boom")

    ab.button_a.on_pressed(boom)
    ab.button_b.on_pressed(lambda: fired.append("b"))
    qa.send(FakeEvent(key_number=0, pressed=True))
    qb.send(FakeEvent(key_number=0, pressed=True))
    await _one_tick(ab, turns=4)
    assert fired == ["b"]


@pytest.mark.asyncio
async def test_release_reaches_the_handler(queue):
    """A release event delivered by ``run()`` calls the release handler.

    - Covers: the pump forwarding only presses.
    - How: queue a release; one drive; ``fired == ["r"]``.
    """
    button = Button._from_queue(queue)
    fired = []
    button.on_released(lambda: fired.append("r"))
    queue.send(FakeEvent(key_number=0, pressed=False))
    await _one_tick(button)
    assert fired == ["r"]


@pytest.mark.asyncio
async def test_planetx_other_switch_runs_during_await():
    """D runs while C's async handler is suspended.

    - Covers: PlanetX ``run()`` still awaiting both switches on one task.
    - How: C awaits ``sleep(0)``; D is already queued; D appears before ``c-end``.
    """
    px, qc, qd = _planetx()
    order = []

    async def on_c():
        order.append("c-start")
        await asyncio.sleep(0)
        order.append("c-end")

    px.button_c.on_pressed(on_c)
    px.button_d.on_pressed(lambda: order.append("d"))
    qc.send(FakeEvent(key_number=0, pressed=True))
    qd.send(FakeEvent(key_number=0, pressed=True))
    await _one_tick(px, turns=6)
    assert order.index("c-start") < order.index("d") < order.index("c-end")


@pytest.mark.asyncio
async def test_error_on_one_event_leaves_the_next_event_running(queue, capsys):
    """A raising handler is reported, and the next event on that button still runs.

    - Covers: the pump dying after the first exception.
    - How: the handler raises on both presses; the log is two calls; stderr names the error.
    """
    button = Button._from_queue(queue)
    order = []

    def boom():
        order.append("boom")
        raise RuntimeError("boom")

    button.on_pressed(boom)
    queue.send(FakeEvent(key_number=0, pressed=True))
    queue.send(FakeEvent(key_number=0, pressed=True))
    await _one_tick(button, turns=4)
    assert order == ["boom", "boom"]
    assert "boom" in capsys.readouterr().err


@pytest.mark.asyncio
async def test_sync_handler_returning_coroutine_is_awaited(queue):
    """A normal function's returned coroutine is awaited by the pump.

    - Covers: dropping a coroutine that the handler returned.
    - How: sync handler returns an async animation; the animation body runs.
    """
    button = Button._from_queue(queue)
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
    button = Button._from_queue(queue)
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
async def test_long_await_on_a_does_not_block_b():
    """B is handled while A's handler is inside a long sleep.

    - Covers: A's await holding the other button.
    - How: A awaits 50 ms; B is queued; B appears before ``a-end``.
    """
    ab, qa, qb = _onboard()
    order = []

    async def on_a():
        order.append("a-start")
        await asyncio.sleep(0.05)
        order.append("a-end")

    ab.button_a.on_pressed(on_a)
    ab.button_b.on_pressed(lambda: order.append("b"))
    qa.send(FakeEvent(key_number=0, pressed=True))
    qb.send(FakeEvent(key_number=0, pressed=True))
    task = asyncio.create_task(ab.run())
    for _ in range(6):
        await asyncio.sleep(0)
        if "b" in order:
            break
    assert "a-start" in order and "b" in order and "a-end" not in order
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task


@pytest.mark.asyncio
async def test_double_run_raises_and_the_first_keeps_working(queue):
    """A second ``run()`` raises ``RuntimeError``. The first ``run()`` still delivers.

    - Covers: two pumps splitting one queue, or the first pump stopping when the second raises.
    - How: start ``run()``; ``await run()`` again; then one press still appends ``"p"``.
    """
    button = Button._from_queue(queue)
    fired = []
    button.on_pressed(lambda: fired.append("p"))
    task = asyncio.create_task(button.run())
    await asyncio.sleep(0)
    with pytest.raises(RuntimeError, match="already running"):
        await button.run()
    queue.send(FakeEvent(key_number=0, pressed=True))
    await asyncio.sleep(0.05)
    assert fired == ["p"]
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task


def test_partial_pair_deinits_the_first_scanner(monkeypatch):
    """If the second ``Button`` fails to bind, the first scanner is deinited.

    - Covers: a failed pair leaving the first pin in use.
    - How: fake ``keypad.Keys``; the second construct raises; the first records ``deinit``.
    """
    created = []

    class Keys:
        def __init__(self, pins, value_when_pressed=False, pull=True):
            self.pins = pins
            self.events = FakeEventQueue()
            self.deinited = False
            created.append(self)
            if len(created) == 2:
                raise RuntimeError("pin in use")

        def deinit(self):
            self.deinited = True

    keypad = types.ModuleType("keypad")
    keypad.Keys = Keys
    monkeypatch.setitem(sys.modules, "keypad", keypad)
    with pytest.raises(RuntimeError, match="pin in use"):
        OnboardButtons(a_pin=object(), b_pin=object())
    assert len(created) == 2
    assert created[0].deinited is True


def _install_fake_keypad(monkeypatch):
    created = []

    class Keys:
        def __init__(self, pins, value_when_pressed=False, pull=True):
            self.pins = pins
            self.events = FakeEventQueue()
            self.deinit_calls = 0
            created.append(self)

        def deinit(self):
            self.deinit_calls += 1

    keypad = types.ModuleType("keypad")
    keypad.Keys = Keys
    monkeypatch.setitem(sys.modules, "keypad", keypad)
    return created


def test_deinit_releases_the_gpio_pin(monkeypatch):
    """``deinit()`` calls ``Keys.deinit`` once. A queue-built button has no pin.

    - Covers: a second ``deinit`` calling ``Keys.deinit`` again, or a ``_from_queue`` button raising.
    - How: one fake scanner; ``deinit`` twice; then a queue-built button.
    """
    created = _install_fake_keypad(monkeypatch)
    button = Button(object())
    button.deinit()
    button.deinit()
    assert created[0].deinit_calls == 1
    Button._from_queue(FakeEventQueue()).deinit()


def test_onboard_deinit_releases_both_pins(monkeypatch):
    """``OnboardButtons.deinit()`` releases A and B.

    - Covers: only one of the two scanners being deinited.
    - How: two fake scanners; both record one ``deinit``.
    """
    created = _install_fake_keypad(monkeypatch)
    OnboardButtons(a_pin=object(), b_pin=object()).deinit()
    assert [keys.deinit_calls for keys in created] == [1, 1]
    assert not hasattr(OnboardButtons(a_pin=object(), b_pin=object()).button_a, "deinit")


@pytest.mark.asyncio
async def test_deinit_while_running_stops_run(queue):
    """``deinit()`` while ``run()`` is active releases the pin. ``run()`` then raises.

    - Covers: ``deinit`` refusing while ``run()`` is active, so the student must cancel the task.
    - How: start ``run()``; ``deinit`` returns; awaiting the task raises ``RuntimeError``.
      A later ``run()`` raises immediately.
    """
    button = Button._from_queue(queue)
    task = asyncio.create_task(button.run())
    await asyncio.sleep(0)
    button.deinit()
    with pytest.raises(RuntimeError, match="deinitialized"):
        await task
    with pytest.raises(RuntimeError, match="deinitialized"):
        await button.run()


@pytest.mark.asyncio
async def test_cancelled_run_releases_the_pin_and_cannot_start_again(monkeypatch):
    """A cancelled ``run()`` leaves the button done: the pin is released and ``run()`` raises.

    - Covers: a cancelled button holding its pin, or a second ``run()`` starting on it.
    - How: fake scanners; cancel a ``Button`` and an ``OnboardButtons`` task; every scanner records one ``deinit``.
    """
    created = _install_fake_keypad(monkeypatch)
    button = Button(object())
    pair = OnboardButtons(a_pin=object(), b_pin=object())
    await _one_tick(button)
    await _one_tick(pair)
    assert [keys.deinit_calls for keys in created] == [1, 1, 1]
    with pytest.raises(RuntimeError, match="deinitialized"):
        await button.run()
    with pytest.raises(RuntimeError, match="deinitialized"):
        await pair.run()



@pytest.mark.asyncio
async def test_pump_polls_with_sleep_ms_10(queue, sleep_ms_shim):
    """The pump waits with ``sleep_ms(10)``.

    - Covers: a float ``asyncio.sleep``, or a different interval.
    - How: one ``run()`` tick; the shim recorded ``10``.
    """
    button = Button._from_queue(queue)
    await _one_tick(button)
    assert sleep_ms_shim == [10]


@pytest.mark.asyncio
async def test_replace_during_await_keeps_the_running_call(queue):
    """Replacing a handler mid-await lets that call finish. The next event uses the new one.

    - Covers: the in-flight call switching to the new handler, or the next event keeping the old one.
    - How: the running handler replaces itself, then awaits; the second press appends ``"new"``.
    """
    button = Button._from_queue(queue)
    order = []

    async def old():
        order.append("old-start")
        button.on_pressed(lambda: order.append("new"))
        await asyncio.sleep(0)
        order.append("old-end")

    button.on_pressed(old)
    queue.send(FakeEvent(key_number=0, pressed=True))
    queue.send(FakeEvent(key_number=0, pressed=True))
    await _one_tick(button, turns=6)
    assert order == ["old-start", "old-end", "new"]


@pytest.mark.asyncio
async def test_same_button_wait_stalls_that_button_only():
    """A handler that waits for a later event of the same button stalls that button.

    - Covers: the release slipping in and ending the wait, or B stalling with A.
    - How: A's press waits for an event only A's release would set; B still appends.
      The test stops without waiting for A to finish.
    """
    ab, qa, qb = _onboard()
    release = asyncio.Event()
    order = []

    async def on_a():
        order.append("a-press")
        await release.wait()
        order.append("a-done")

    def on_a_release():
        release.set()
        order.append("a-release")

    ab.button_a.on_pressed(on_a)
    ab.button_a.on_released(on_a_release)
    ab.button_b.on_pressed(lambda: order.append("b"))
    qa.send(FakeEvent(key_number=0, pressed=True))
    qa.send(FakeEvent(key_number=0, pressed=False))
    qb.send(FakeEvent(key_number=0, pressed=True))
    task = asyncio.create_task(ab.run())
    for _ in range(8):
        await asyncio.sleep(0)
        if "b" in order:
            break
    assert "a-press" in order
    assert "b" in order
    assert "a-release" not in order
    assert "a-done" not in order
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task


@pytest.mark.asyncio
async def test_overflow_warns_each_time_the_marker_is_set(queue, capsys):
    """Each overflow prints a warning, then the marker is cleared.

    - Covers: one warning for the whole run, or a warning on every poll while the marker stays set.
    - How: set ``overflowed``; it is cleared after one warning. Set it again; a second warning.
    """
    queue.overflowed = True
    fired = []

    async def fast(ms):
        await asyncio.sleep(0)

    asyncio.sleep_ms = fast
    button = Button._from_queue(queue)
    button.on_pressed(lambda: fired.append("p"))
    queue.send(FakeEvent(key_number=0, pressed=True))
    task = asyncio.create_task(button.run())
    for _ in range(8):
        await asyncio.sleep(0)
        if not queue.overflowed:
            break
    assert fired == ["p"]
    assert queue.overflowed is False
    queue.overflowed = True
    for _ in range(8):
        await asyncio.sleep(0)
        if not queue.overflowed:
            break
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert capsys.readouterr().out.count(_OVERFLOW_WARNING) == 2
    assert queue.overflowed is False


@pytest.mark.asyncio
async def test_overflow_warns_before_queued_events_and_keeps_them(queue, monkeypatch):
    """An overflow seen with events still queued warns once, before their handlers, and delivers them all.

    - Covers: a warning only after the drain, one warning per queued event, or ``clear()`` dropping the queued events.
    - How: three presses queued with ``overflowed`` set; ``print`` and the handler append to one list.
    """
    import buttons

    order = []
    monkeypatch.setattr(buttons, "print", lambda *args: order.append(args[0]), raising=False)
    queue.overflowed = True
    button = Button._from_queue(queue)
    button.on_pressed(lambda: order.append("p"))
    for _ in range(3):
        queue.send(FakeEvent(key_number=0, pressed=True))
    await _one_tick(button, turns=8)
    assert order == [_OVERFLOW_WARNING, "p", "p", "p"]
    assert queue.overflowed is False


def test_crash_sensor_port_maps_to_the_second_wire(monkeypatch):
    """``PlanetXCrashSensor(port=)`` binds ``port.pins[1]`` and is a ``Button``.

    - Covers: the first wire, or a missing ``port=`` constructing a scanner.
    - How: fake ``keypad``; a port whose pins are ``("wire0", "wire1")``; ``Keys`` saw ``("wire1",)``.
      ``PlanetXCrashSensor()`` raises ``TypeError``.
    """
    seen = []

    class Keys:
        def __init__(self, pins, value_when_pressed=False, pull=True):
            seen.append(pins)
            self.events = FakeEventQueue()

        def deinit(self):
            pass

    keypad = types.ModuleType("keypad")
    keypad.Keys = Keys
    monkeypatch.setitem(sys.modules, "keypad", keypad)

    class _Port:
        pins = ("wire0", "wire1")

    crash = PlanetXCrashSensor(port=_Port())
    assert isinstance(crash, Button)
    assert seen == [("wire1",)]
    with pytest.raises(TypeError):
        PlanetXCrashSensor()


def test_no_update_on_public_classes():
    """Student API has no Exp09-style ``update()`` loop.

    - Covers: ``update`` sneaking onto Button, a pair, or the crash sensor.
    - How: ``hasattr(..., "update")`` is false on the public button classes.
    """
    for cls in (Button, OnboardButtons, PlanetXButtonSensor, PlanetXCrashSensor):
        assert not hasattr(cls, "update")
