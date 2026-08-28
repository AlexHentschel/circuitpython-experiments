# Micro:bit

**Question:** 

I am looking for a Circuit Python library for illustrating event-based programming in a lessor / tutorial format. Please do not confuse with Micro Python, even though both have the same origin - investigate the source code if in doubt. 

Let's consider CircuitPython (e.g. 10.2.1) for the **BBC micro\:bit v2**. I assume we can read out the 
As a first example, lets consider programming a button library, that exposes button-specific wrappers, e.g. for the ELECFREAKS PlanetX Button Sensor (see https://wiki.elecfreaks.com/en/microbit/sensor/planet-x-sensors/Plant_X_EF05017/ ). Electrically, these buttons just connect to Microbit pins via a breakout board. In our Example, we assume the following electrical of the PlanetX Button Sensor:

- button C (blue) connected to pin P13
- button D (red) connected to pin P14

As a tutorial, we want to program our own "PlanetX Button Sensor library" for CircuitPython in an event-driven manner:
* import something like `OutOwnPlanetX` library
* Constructor: `buttons = OutOwnPlanetX.Button_Sensor(pins)`
* the user of the library can register consumers, e.g `buttons.on_C_pressed( consumer() )` and equivalent events (maybe just press and release as state transitions? does that make sense for a physical button like the PlanetX Button Sensor)
* we could even have a `buttons.C_clear` dropping all registered consumers
* we would provide a base class for the consumer as part of the library, with all methods providing full type hints, and but raising NotImplementedError 


Ideally, I would like to build on top of lower level system primitives exposed by CircuitPython, or a low-level library for event-driven logic in circuit python. 

Please do extensive internet research, keeping internal ephemeral notes, and then present a human-readable, contextually complete, concise overview, selection of most promising approaches, risks, and recommendation. 



**ChatGPT Analysis**
I checked this specifically against **CircuitPython 10.2.1 for the BBC micro:bit v2**, including the CircuitPython build configuration and `keypad` implementation, rather than extrapolating from MicroPython. There is a fairly clean answer, but one important limitation of the micro:bit build changes which approach I would use.


## Bottom line

For a tutorial running on the **stock CircuitPython 10.2.1 micro:bit v2 firmware**, I would build your `PlanetXButtonSensor` on:

`digitalio` **→** `adafruit_debouncer.Button` **→ your own small event/callback dispatcher.**

That gives you a proper event-oriented *public* API such as:

```python
buttons = PlanetXButtonSensor(
    c_pin=board.P13,
    d_pin=board.P14,
)

buttons.on_c_pressed(c_pressed)
buttons.on_c_released(c_released)
buttons.on_d_pressed(d_pressed)

while True:
    buttons.update()
```

where the application is reacting to semantic events, rather than testing `if button.value` everywhere.

There actually is an even nicer native CircuitPython primitive, `keypad.Keys`, which does background scanning, debouncing, and produces press/release events. Unfortunately, `keypad` **is deliberately omitted from the stock micro:bit v2 build because of firmware-space constraints**. ([CircuitPython](https://circuitpython.org/board/microbit_v2/))

The interesting pedagogical point is that native `keypad.Keys` is itself **not GPIO-interrupt-driven**. I inspected its CircuitPython 10.2.1 C implementation: CircuitPython registers the scanner with the supervisor and periodically calls it from `keypad_tick()`. In other words, the native implementation also follows roughly:

**scan → debounce → detect transition → enqueue event → application consumes event**. 

So implementing the same architecture in Python on the micro:bit is not a second-rate imitation. It is quite close conceptually to CircuitPython's own event machinery.

---



## What the hardware and CircuitPython actually give you

Your assumed PlanetX wiring is correct for the J3 connection used by ELECFREAKS. Their current MakeCode source maps:

```text
C -> P13
D -> P14
```

and enables pull-ups on both pins. It considers a pin value of **0 to mean pressed**. 

CircuitPython 10.2.1 exposes both pins directly as `board.P13` and `board.P14`; internally they are nRF52833 GPIO P0.17 and P0.01 respectively. 

Consequently the electrical transitions are:

```text
released: 1
press:    1 -> 0    falling edge
release:  0 -> 1    rising edge
```

So **PRESSED and RELEASED are exactly the two primitive events I would expose**. They are more fundamental than "click", "double-click", "long press", etc., which can subsequently be derived from those state transitions.

Incidentally, I found an interesting inconsistency in ELECFREAKS' current MakeCode source. Their polling function explicitly says `0 == pressed`, but their `buttonEvent()` function registers `MICROBIT_PIN_EVT_RISE` as the event for C and D.  That appears inverted: with a pull-up, RISE corresponds to release. **The FALL event shown in your screenshot is consistent with the actual electrical behavior.**

---



## The promising implementation choices


| Approach                                                            | Stock micro:bit 10.2.1          | Mechanism                                                           | My assessment                                                |
| ------------------------------------------------------------------- | ------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------ |
| `digitalio` **+** `adafruit_debouncer.Button` **+ your dispatcher** | **Yes**                         | Python polls; Debouncer identifies stable press/release transitions | **Recommended**                                              |
| `digitalio` + your own debounce implementation                      | **Yes**                         | Same architecture, entirely written by students                     | Excellent if teaching debounce/event-source internals        |
| Native `keypad.Keys`                                                | **No, not in stock firmware**   | Native background scan + debounce + `EventQueue`                    | Best backend if you accept custom firmware                   |
| `asyncio` / `async_button`                                          | **No on stock micro:bit build** | Cooperative async polling                                           | Interesting elsewhere, poor choice for this target           |
| `pulseio.PulseIn`                                                   | Yes                             | Hardware-oriented pulse-duration capture                            | Wrong abstraction for buttons                                |
| `alarm.pin.PinAlarm`                                                | Yes                             | Pin-triggered wake from sleep                                       | Designed for sleeping/wakeup, not a general event dispatcher |
| `countio`                                                           | Not in stock build              | Hardware edge counting                                              | Doesn't solve callback/state-transition problem anyway       |


`digitalio` gives the normal CircuitPython input primitive and internal pull-up support. ([CircuitPython Docs](https://docs.circuitpython.org/en/latest/shared-bindings/digitalio/?utm_source=chatgpt.com)) The official Adafruit Debouncer library then gives you almost exactly the low-level semantics required: its `Button` class reports `pressed` and `released`, handles active-low buttons with `value_when_pressed=False`, and explicitly expects `update()` to be called frequently. ([CircuitPython Docs](https://docs.circuitpython.org/projects/debouncer/en/latest/api.html?utm_source=chatgpt.com))

That is a very good division of responsibility for a lesson:

```text
CircuitPython digitalio
        ↓
Adafruit Debouncer
  "has the stable state changed?"
        ↓
OurOwnPlanetX
  "C was pressed"
  "D was released"
        ↓
registered consumers
        ↓
application behavior
```

Students therefore write the interesting event abstraction themselves without having to reinvent mechanical-switch debounce immediately.

---



# Why not GPIO interrupts?

This is one of the important differences between **CircuitPython and MicroPython**.

CircuitPython explicitly says that Python-level interrupts and threading are disabled; only some boards provide `async`/`await` for cooperative multitasking, with some additional concurrency implemented inside native modules. ([GitHub](https://github.com/adafruit/circuitpython?utm_source=chatgpt.com))

So a MicroPython solution based on something like:

```python
pin.irq(...)
```

is **not a CircuitPython solution**.

There is also no general Python-accessible nRF52833 GPIOTE callback primitive hiding underneath `digitalio`.

This makes a useful lesson in itself:

> **Event-driven programming does not require hardware interrupts.**

"Event driven" describes the programming interface and control flow. Your consumer says *what should happen when C is pressed*; it does not repeatedly ask whether C is pressed. The fact that the event source internally samples the hardware every few milliseconds is an implementation detail.

That is also precisely how CircuitPython's native `keypad` architecture is structured. The documented `keypad.Keys` API scans buttons, debounces them, and places **pressed/released transition objects** into an `EventQueue`; the default scan interval is 20 ms. ([CircuitPython Docs](https://docs.circuitpython.org/en/latest/shared-bindings/keypad/?utm_source=chatgpt.com))

---



# I would use `adafruit_debouncer` as your lower layer

For your particular lesson, this is probably the sweet spot.

The private implementation can essentially be:

```python
c_pin = digitalio.DigitalInOut(board.P13)
c_pin.switch_to_input(pull=digitalio.Pull.UP)

c = Button(c_pin, value_when_pressed=False)

# event-loop iteration:
c.update()

if c.pressed:
    emit_c_pressed()

if c.released:
    emit_c_released()
```

Adafruit's implementation uses its `adafruit_ticks` helper and a default **10 ms debounce interval**. It only declares a transition once the new electrical state has remained stable long enough. ([GitHub](https://raw.githubusercontent.com/adafruit/Adafruit_CircuitPython_Debouncer/main/adafruit_debouncer.py))

Then your students' library adds the genuinely event-oriented part:

```python
def on_c_pressed(self, handler):
    self._c_pressed_handlers.append(handler)
```

and:

```python
def _emit_c_pressed(self, event):
    for handler in self._c_pressed_handlers:
        handler(event)
```

That is conceptually very clean.

## One syntax correction to your proposed API

You probably do **not** want:

```python
buttons.on_C_pressed(consumer())
```

because `consumer()` invokes the function immediately and passes its return value to `on_C_pressed`.

For a callback function, it should be:

```python
buttons.on_c_pressed(consumer)
```

or:

```python
buttons.on_c_pressed(my_consumer.on_c_pressed)
```

The absence of `()` is itself a nice lesson about functions being objects that can be passed around.

---



# I would separate events from consumers

I would make the basic event something like:

```python
ButtonEvent(
    button="C",
    pressed=True,
    timestamp_ms=...
)
```

and have the sensor emit exactly four basic kinds of transition:

```text
C pressed
C released
D pressed
D released
```

Then add derived behavior later:

```text
C clicked
C long-pressed
C double-clicked
C+D chord pressed
C+D chord released
```

That separation is particularly valuable for `C+D`. Electrically there is **no third CD button**. "CD pressed" means that two separately debounced states are simultaneously `pressed`. I would emit the chord event once when the system transitions from "not both down" to "both down".

That is cleaner than ELECFREAKS' current implementation, which checks C+D every 50 ms and raises the event repeatedly while both remain down. 

---



# Callback API versus a Consumer base class

For the first event-programming lesson, I would make callbacks the primary interface:

```python
buttons.on_c_pressed(on_blue_button)
buttons.on_c_released(on_blue_button_released)
buttons.on_d_pressed(on_red_button)
```

and support:

```python
buttons.clear_c_pressed()
buttons.clear_c_released()
buttons.clear_c()
buttons.clear_all()
```

That maps very directly onto the MakeCode mental model in your screenshot.

You can then introduce the OO Consumer pattern as a second lesson:

```python
class ButtonConsumer:
    def on_c_pressed(self, event: ButtonEvent) -> None:
        raise NotImplementedError

    def on_c_released(self, event: ButtonEvent) -> None:
        raise NotImplementedError

    def on_d_pressed(self, event: ButtonEvent) -> None:
        raise NotImplementedError

    def on_d_released(self, event: ButtonEvent) -> None:
        raise NotImplementedError
```

followed by:

```python
buttons.add_consumer(MyButtonConsumer())
```

There is one design issue with `NotImplementedError`: it says that **every Consumer is required to implement every event method**. If consumers are allowed to care only about C-pressed, I would instead make the unused base methods no-ops. Alternatively, require one method:

```python
def on_button_event(self, event: ButtonEvent) -> None:
    raise NotImplementedError
```

and let the consumer select the events it cares about.

For elementary event programming, I prefer the callback version first. It exposes the central concept without adding inheritance at the same time.

---



# What about full type hints?

This requires a little care on this board.

The stock micro:bit v2 firmware has a deliberately small module set and does **not** include `typing`. ([CircuitPython](https://circuitpython.org/board/microbit_v2/)) Adafruit's own CircuitPython libraries commonly protect their type-only imports with `try/except ImportError`, and Adafruit explicitly says that `circuitpython_typing` is **not needed at runtime**. ([CircuitPython Docs](https://docs.circuitpython.org/projects/adafruit-circuitpython-typing/en/latest/?utm_source=chatgpt.com))

For your library I would therefore either use lightweight runtime annotations:

```python
def on_c_pressed(self, handler) -> None:
    ...
```

with richer static information in a `.pyi` stub, or follow Adafruit's guarded-import convention for `Callable`, etc.

A `.pyi` file is actually attractive if "full type hints" are important but the teaching runtime should remain tiny. VS Code/Pylance sees rich signatures; the micro:bit does not need to load the typing machinery.

I would **not** pull in `abc.ABC` merely to get an abstract base class. Plain methods raising `NotImplementedError` accomplish the tutorial goal with much less machinery.

---



# Why I would not base this lesson on `asyncio`

This was worth checking because on many modern CircuitPython boards it would be an appealing answer.

Adafruit does have a proper CircuitPython `asyncio` library, and a community `async_button` library can asynchronously wait for presses/releases. ([CircuitPython Docs](https://docs.circuitpython.org/projects/asyncio/en/latest/))

But the **stock micro:bit v2 build is a special reduced build**. For the nRF52833 with its internal filesystem, CircuitPython explicitly sets:

```make
CIRCUITPY_FULL_BUILD ?= 0
```

with the comment `"Need the space"`. 

And CircuitPython 10.2.1 makes its `async`/`await` language support default to:

```make
MICROPY_PY_ASYNC_AWAIT ?= $(CIRCUITPY_FULL_BUILD)
```

so it is disabled as part of this reduced configuration. 

Therefore **simply copying the CircuitPython** `asyncio` **library onto a stock micro:bit v2 is not the solution**. This is exactly the sort of CircuitPython-versus-MicroPython/board-specific detail that generic search results easily miss.

---



# The interesting custom-firmware alternative: `keypad.Keys`

If at some point you are willing to distribute your own CircuitPython 10.2.1 build, this becomes my preferred backend.

Conceptually your driver would be backed by:

```python
keys = keypad.Keys(
    (board.P13, board.P14),
    value_when_pressed=False,
    pull=True,
    interval=0.020,
    max_events=8,
)
```

and then translate:

```python
event.key_number == 0   -> C
event.key_number == 1   -> D

event.pressed           -> pressed
event.released          -> released
```

`keypad.Event` already has almost exactly the model I would invent for your library: **key number, pressed/released transition, and timestamp**. ([CircuitPython Docs](https://docs.circuitpython.org/en/latest/shared-bindings/keypad/?utm_source=chatgpt.com))

Why isn't it available? The source makes the relationship explicit: `keypad` defaults to `CIRCUITPY_FULL_BUILD`, while the micro:bit's nRF52833 internal-flash configuration turns the full build off to save space. 

A custom build could selectively enable only the pieces needed for `keypad.Keys`, while leaving KeyMatrix/ShiftRegister support disabled. I would, however, **compile and verify flash size before promising that configuration**, because the nRF52833 configuration explicitly says it is space constrained. The board also has only a 60 KiB CircuitPython filesystem. 

For a classroom/tutorial deployment, that firmware-management cost probably outweighs the modest architectural improvement.

---



# My recommended tutorial architecture

I would structure it as three deliberately visible layers:

```text
┌──────────────────────────────────────┐
│ Student application                  │
│                                      │
│ buttons.on_c_pressed(turn_light_on)  │
└───────────────────▲──────────────────┘
                    │ callback
             semantic event
                    │
┌───────────────────┴──────────────────┐
│ OurOwnPlanetX.PlanetXButtonSensor    │
│                                      │
│ registration                         │
│ event dispatch                       │
│ C/D naming                           │
└───────────────────▲──────────────────┘
                    │
          stable state transition
                    │
┌───────────────────┴──────────────────┐
│ adafruit_debouncer.Button            │
│                                      │
│ debounce                             │
│ pressed / released                   │
└───────────────────▲──────────────────┘
                    │
                 0 / 1
                    │
┌───────────────────┴──────────────────┐
│ CircuitPython digitalio              │
│ P13 / P14, Pull.UP                   │
└──────────────────────────────────────┘
```

Then, in a subsequent lesson, you can peel away `adafruit_debouncer` and implement that box yourselves. And if you later move to a board whose CircuitPython firmware includes `keypad`, you can replace the bottom two boxes with `keypad.Keys` **without changing the public** `PlanetXButtonSensor` **API at all**.

That backend interchangeability is another useful software-design lesson.

### A few implementation rules I would establish

- **PRESSED/RELEASED are the primitive events.**
- Poll/debounce internally; don't expose raw pin edges to consumers.
- Call handlers synchronously outside any interrupt context.
- Handlers should be short. A handler that sleeps for two seconds prevents your event loop from servicing other inputs for two seconds.
- Either copy the handler list before dispatch or explicitly forbid modifying registrations from inside a handler.
- For a first tutorial, let callback exceptions propagate so programming mistakes are visible instead of silently swallowed.
- Give each event a timestamp, even if you don't initially use it. That makes long-press, double-click and chord lessons easy later.

The most important conclusion from the source-code investigation is therefore:

> **Do not chase a hidden CircuitPython interrupt API for this. On the stock micro:bit v2 there isn't an appropriate one.** `digitalio` **+** `adafruit_debouncer` **+ a tiny Observer/event-dispatch layer is the cleanest solution, and its internal architecture is remarkably similar to CircuitPython's own native** `keypad` **implementation.**

If you want, the natural next step would be to design the actual **minimal** `OurOwnPlanetX` **API and implementation**, perhaps ~100–150 lines, with `ButtonEvent`, callback registration/clearing, a typed `ButtonConsumer`, C/D chord semantics, and a very small `code.py` lesson demonstrating it.


# Micro:bit compatible MCU based on RP2350

**Question:** 
Let's now consider a Microbit-compatible physical form factor but a board running an RP2350 with 4MB of flash (RP pico 2 compatible). Provide recommendations for this stack please.

**ChatGPT Analysis**

Yes. On an **RP2350 + 4 MB flash** board, my recommendation changes substantially from the micro:bit v2 case.

For CircuitPython 10.2.1, I would make **native `keypad.Keys` the foundation of the button library**, and then put your own semantic event/consumer layer on top. I would make `asyncio` available as an optional second layer, but I would **not** make `asyncio` a requirement for the first event-driven-programming lesson.

The RP2350 port is a full CircuitPython build by default, and the stock Pico 2 10.2.1 image contains `keypad`, `keypad.Keys`, `keypad.EventQueue`, `countio`, `digitalio`, `rp2pio`, and the internal `_asyncio` support. CircuitPython's RP2 port explicitly sets `CIRCUITPY_FULL_BUILD=1`; `keypad` and async/await are enabled by the full-build configuration. ([CircuitPython][1])

## Recommended stack

I would use:

```text
PlanetX physical buttons
        │
        │ active-low GPIO
        ▼
CircuitPython keypad.Keys
        │
        │ native background scanning
        │ debounce
        │ timestamped press/release events
        │ bounded EventQueue
        ▼
OurOwnPlanetX.ButtonSensor
        │
        │ map key 0 → C
        │ map key 1 → D
        │ semantic event dispatch
        ▼
on_c_pressed(...)
on_c_released(...)
on_d_pressed(...)
on_d_released(...)
        │
        ▼
application / student code
```

Then, as a later lesson:

```text
                   ┌── callback API
keypad.EventQueue ─┤
                   └── asyncio event-pump adapter
```

That is a considerably nicer platform for this tutorial than the nRF52833 micro:bit v2 build.

---

## 1. Use `keypad.Keys` instead of `adafruit_debouncer`

For C and D, conceptually:

```python
import keypad

keys = keypad.Keys(
    (pin_c, pin_d),
    value_when_pressed=False,
    pull=True,
    interval=0.010,
    debounce_threshold=2,
    max_events=16,
)
```

The important part is that **you no longer have to call `update()` to sample the GPIO and perform debounce**.

CircuitPython's native `keypad` machinery registers the scanner with the supervisor's periodic tick mechanism. CircuitPython calls the scanner in the background and places state transitions in an event queue. The C source explicitly describes scanners as being "scanned in the background". 

Internally the flow really is:

```text
supervisor tick
      ↓
keypad.Keys scans GPIO
      ↓
native debounce
      ↓
transition detected
      ↓
keypad.Event
      ↓
EventQueue
```

The RP2350 implementation ultimately reads the pins through CircuitPython's native `digitalio` implementation and records a queue entry when the debounce state changes. 

This makes `keypad` an unusually good teaching primitive because the lower layer already behaves like a genuine event source.

---

## 2. `keypad.Event` already has almost exactly the event model we want

CircuitPython gives each transition:

```python
event.key_number
event.pressed
event.released
event.timestamp
```

The timestamp is in milliseconds using the `supervisor.ticks_ms` time base. ([CircuitPython Documentation][2])

For your sensor:

```text
key_number 0  → C
key_number 1  → D
```

and:

```text
pressed == True   → C_PRESSED / D_PRESSED
released == True  → C_RELEASED / D_RELEASED
```

So I would **not introduce "click" as the primitive event**.

The fundamental physical events should remain:

```text
C pressed
C released

D pressed
D released
```

Later lessons can derive:

```text
C clicked
C long-pressed
C double-clicked
C+D pressed
C+D released
```

from those primitives.

That creates a very nice progression from physical state transitions to higher-level semantic events.

---

## 3. The event queue is an important improvement

Suppose the student's application temporarily does something else:

```python
show_animation()
```

With a traditional:

```python
button.update()
```

polling design, a short press could occur entirely while the student's code is elsewhere and be lost.

With `keypad.Keys`, the underlying scanner continues operating and records:

```text
C pressed
C released
```

in its native queue.

The application can consume them later:

```python
event = keys.events.get()
```

or:

```python
while keys.events:
    event = keys.events.get()
    ...
```

The queue is bounded. In CircuitPython 10.2.1, if it is full, the **new event is discarded** and `overflowed` is set. The native implementation checks the ring buffer and returns without recording when no space remains. 

So your wrapper should probably notice:

```python
if self._keys.events.overflowed:
    ...
```

In a two-button educational project, `max_events=16` is already generous.

---

# 4. Debouncing: I would use the native `keypad` integrator

The CircuitPython implementation is a little more sophisticated than simply:

> has the pin stayed unchanged for 20 ms?

It maintains a saturating debounce counter for each key. Measurements in one direction increment it and measurements in the other direction decrement it; a transition occurs when the counter crosses the decision point. 

For these ordinary mechanical buttons, I would start with:

```python
interval=0.010
debounce_threshold=2
```

so roughly a **10–20 ms transition latency** depending on where the physical transition occurs relative to the sampling times, with two measurements needed to move from a stable opposite state to the transition.

Another completely reasonable starting point is:

```python
interval=0.005
debounce_threshold=3
```

for somewhat finer temporal resolution.

The CircuitPython default is:

```python
interval=0.020
debounce_threshold=1
```

which is probably adequate for many buttons, but for a tutorial I prefer explicitly demonstrating that **sampling interval and debounce strength are separate concepts**. ([CircuitPython Documentation][2])

---

## 5. Your PlanetX wiring is particularly appropriate for RP2350

For these PlanetX buttons we established:

```text
released → HIGH
pressed  → LOW
```

so:

```python
value_when_pressed=False
pull=True
```

means `keypad.Keys` uses an internal **pull-up**.

That is exactly what I would want on an RP2350.

CircuitPython documents a hardware issue on some RP2350 silicon, particularly A2 stepping, involving internal **pull-downs** and input leakage. `keypad.Keys` specifically warns against the combination:

```python
value_when_pressed=True
pull=True
```

on affected RP2350s. Active-low switches using a pull-up avoid this particular issue. ([CircuitPython Documentation][2])

So don't invert the PlanetX wiring merely to make "pressed = 1". Active-low is preferable here.

---

# 6. I would make your library's public API callback-oriented

For the first lesson I would expose something approximately like:

```python
buttons = PlanetXButtonSensor(
    c_pin=board.P13,
    d_pin=board.P14,
)

buttons.on_c_pressed(show_blue)
buttons.on_c_released(hide_blue)

buttons.on_d_pressed(show_red)
buttons.on_d_released(hide_red)

while True:
    buttons.dispatch()
```

where `dispatch()` **does not scan the buttons**. It merely drains events that CircuitPython has already detected:

```text
keypad does:
    scan
    debounce
    detect event
    queue event

our library does:
    dequeue
    translate C/D
    notify consumers
```

That distinction is pedagogically valuable.

The student's main loop isn't asking:

> "Is C down now?"

It is essentially saying:

> "Deliver anything that has happened."

And their application itself is saying:

```python
buttons.on_c_pressed(...)
```

rather than repeatedly checking physical state.

That's a strong example of event-oriented design even though CircuitPython itself ultimately obtains those events through periodic native sampling rather than GPIO ISR callbacks.

---

# 7. I would retain `dispatch()` even though `keypad` runs in the background

This is important.

I would **not** have the native scanner somehow call arbitrary Python callbacks asynchronously.

Instead:

```text
background native code
        ↓
     queue
        ↓
normal Python execution
        ↓
 callbacks
```

This gives you clean execution semantics:

* student callback code always runs in normal Python context;
* callbacks can allocate memory;
* exceptions behave normally;
* no ISR restrictions;
* callback registration can remain ordinary Python;
* application control flow remains understandable.

That is essentially what an event loop does in desktop/server programming as well.

I'd probably call the method:

```python
buttons.dispatch()
```

rather than:

```python
buttons.update()
```

because `update()` sounds as though it is polling the hardware.

Perhaps:

```python
buttons.dispatch_pending()
```

for the fully explicit name.

---

# 8. Then add `asyncio` as lesson 2

Unlike the stock micro:bit-v2 build we discussed, **RP2350 has async/await support**. CircuitPython's RP2 port defaults to a full build, and its generic configuration enables async/await and `_asyncio` for a full build. 

One nuance: the user-facing CircuitPython `asyncio` Python library is not the same thing as `_asyncio`. `_asyncio` is a built-in helper; Adafruit instructs users to install the `asyncio` library from the CircuitPython bundle, for example with:

```text
circup install asyncio
```

which also installs its `adafruit_ticks` dependency. ([CircuitPython Documentation][3])

Then your library could optionally provide:

```python
async def run(self) -> None:
    while True:
        self.dispatch_pending()
        await asyncio.sleep(0.005)
```

and an application becomes:

```python
async def main():
    buttons.on_c_pressed(c_pressed)
    buttons.on_d_pressed(d_pressed)

    asyncio.create_task(buttons.run())

    # other concurrent activities
    ...
```

There's an important architectural detail here:

**`keypad.EventQueue` itself is not awaitable.**

Its public API is essentially:

```python
get()
get_into()
clear()
len(...)
overflowed
```

not:

```python
await events.get()
```

([CircuitPython Documentation][2])

So the async adapter would periodically drain the native queue. That's fine because the **hardware scanning itself is not being polled by Python**. Only delivery of already-recorded events is being serviced periodically.

---

# 9. I would not make `asyncio` the first tutorial API

Even though it is now available, I don't think this:

```python
async def watch_buttons():
    ...
```

is the best first exposure to event-driven programming.

It introduces several independent concepts at once:

```text
events
callbacks
coroutines
tasks
await
cooperative scheduling
```

whereas:

```python
buttons.on_c_pressed(turn_led_on)
```

isolates the main lesson beautifully:

> A program can register behavior that should happen when an event occurs.

Your screenshot's MakeCode:

```text
on event from P5 with FALL
    call button_A_pressed
```

maps conceptually almost perfectly to:

```python
buttons.on_c_pressed(button_c_pressed)
```

That's exactly the bridge I'd want students to see.

Then later:

> But what if two long-running activities should progress concurrently?

becomes the motivation for `asyncio`.

---

# 10. Suggested implementation layers

For this board, I'd actually make the library internally modular:

```text
                 Public API
        PlanetXButtonSensor
                 │
       ┌─────────┴─────────┐
       │                   │
 callback registry    semantic state
       │               C+D chords etc.
       └─────────┬─────────┘
                 │
             dispatcher
                 │
        keypad.EventQueue
                 │
            keypad.Keys
                 │
              GPIO
```

And optionally:

```text
PlanetXButtonSensor
       │
       ├── dispatch_pending()
       │
       └── async run()
```

The important thing is that **both use exactly the same event source and exactly the same callback registry**.

You aren't maintaining an asyncio implementation and a non-async implementation of the sensor.

---

## 11. I would still offer the `Consumer` abstraction, but secondarily

You could have:

```python
class ButtonConsumer:
    def on_c_pressed(self, event: ButtonEvent) -> None:
        pass

    def on_c_released(self, event: ButtonEvent) -> None:
        pass

    def on_d_pressed(self, event: ButtonEvent) -> None:
        pass

    def on_d_released(self, event: ButtonEvent) -> None:
        pass
```

and:

```python
buttons.add_consumer(my_consumer)
```

But I would make this **lesson 2 or 3**, after callbacks.

I'd also change my recommendation slightly from your original `NotImplementedError` idea. For a multi-method consumer interface, I would make default event methods **no-ops**.

Otherwise a consumer that only wants C presses must unnecessarily implement:

```python
on_c_released()
on_d_pressed()
on_d_released()
```

If you specifically want to teach abstract interfaces and contracts, then I'd instead have one mandatory method:

```python
class ButtonConsumer:
    def on_button_event(self, event: ButtonEvent) -> None:
        raise NotImplementedError
```

and have the consumer inspect the event.

---

# 12. Keep your own `ButtonEvent`, despite `keypad.Event`

Although `keypad.Event` is an excellent low-level primitive, I would **not leak `keypad.Event` through `OurOwnPlanetX`'s public API**.

I'd make something conceptually like:

```python
class ButtonEvent:
    button: str
    pressed: bool
    timestamp: int
```

because otherwise the application has to know:

```text
key_number 0 means PlanetX C
```

which defeats the abstraction.

Your API should talk in terms of:

```python
event.button == "C"
event.pressed
```

while the hardware backend knows about:

```python
key_number == 0
```

It also means that if you later change from:

```python
keypad.Keys
```

to an I²C GPIO expander or some other sensor, the user-facing API doesn't change.

---

# 13. For typing, I'd use `.pyi` files

The RP2350 gives you lots more firmware space, but the Pico 2 CircuitPython 10.2.1 module list still does not expose CPython's full `typing` module as a built-in module. ([CircuitPython][1])

For educational code I'd therefore keep runtime Python straightforward:

```python
def on_c_pressed(self, handler):
    ...
```

while supplying:

```text
our_own_planetx/
    __init__.py
    button_sensor.py
    button_sensor.pyi
```

with the richer editor-facing declaration:

```python
def on_c_pressed(
    self,
    handler: Callable[[ButtonEvent], None]
) -> None: ...
```

This gives students autocomplete/type checking without making the embedded runtime execute typing machinery.

Normal concrete annotations are of course still perfectly useful in `.py`:

```python
def dispatch_pending(self) -> None:
    ...
```

---

# 14. One board-design recommendation: preserve `P13` and `P14` as aliases

Because this board has a **micro:bit-compatible physical edge connector**, I would strongly consider defining:

```python
board.P13
board.P14
```

in its CircuitPython board definition, irrespective of which RP2350 GPIO numbers they physically map to.

For example, don't let your educational software assume:

```text
micro:bit P13 == RP2350 GP13
```

unless that happens to be true electrically.

Instead the board definition should establish:

```text
physical micro:bit edge P13 → board.P13 → actual RP2350 GPIO xx
physical micro:bit edge P14 → board.P14 → actual RP2350 GPIO yy
```

Then examples remain beautifully hardware-oriented:

```python
buttons = PlanetXButtonSensor(
    c_pin=board.P13,
    d_pin=board.P14,
)
```

and students don't need to know the internal RP2350 routing.

If the custom board is sufficiently Pico-2-compatible electrically, CircuitPython's Pico 2 configuration shows the reference build uses an RP2350A and a 4 MB W25Q32 flash device. A custom board definition is nevertheless preferable if you want correct pin aliases and board identity. 

---

## What I would choose

For **this RP2350 board**, my ranking would be:

| Layer/problem             | Choice                                    |
| ------------------------- | ----------------------------------------- |
| Physical GPIO input       | **`keypad.Keys`**                         |
| Pull configuration        | **active-low + pull-up**                  |
| Debouncing                | **native `keypad` debounce**              |
| Recording events          | **native `keypad.EventQueue`**            |
| Hardware event names      | private mapping `0 → C`, `1 → D`          |
| Public primitive events   | **pressed / released**                    |
| Public introductory API   | **callbacks**                             |
| Event delivery            | **`dispatch_pending()`**                  |
| Consumer OO API           | optional second interface                 |
| Concurrency               | **CircuitPython `asyncio`**, later lesson |
| Long/double/chord presses | derive in your semantic layer             |
| Typing                    | runtime basic annotations + **`.pyi`**    |
| GPIO interrupts           | **don't use / don't need**                |
| `adafruit_debouncer`      | unnecessary on this target                |
| PIO (`rp2pio`)            | unnecessary for buttons                   |

So the conceptual progression of the course could become particularly nice:

```text
Lesson 1
physical state
    ↓
press/release events
    ↓
callbacks

Lesson 2
multiple event consumers
    ↓
Observer / Consumer pattern

Lesson 3
events carry data
    ↓
ButtonEvent
timestamp
button identity

Lesson 4
events can create semantic events
    ↓
click
long press
C+D

Lesson 5
event-driven ≠ necessarily concurrent
    ↓
asyncio tasks
cooperative scheduling
```

And the rather elegant part is that **Lesson 1 already rests on a real native, background-running CircuitPython event queue**, rather than us constructing the illusion of an event system entirely through Python polling.

For this hardware, I think that is the strongest stack for the tutorial.

[1]: https://circuitpython.org/board/raspberry_pi_pico2/?utm_source=chatgpt.com "Pico 2 Download"
[2]: https://docs.circuitpython.org/en/10.2.x/shared-bindings/keypad/index.html?utm_source=chatgpt.com "keypad – Support for scanning keys and key matrices — Adafruit CircuitPython 1 documentation"
[3]: https://docs.circuitpython.org/projects/asyncio/en/latest/?utm_source=chatgpt.com "Introduction — Adafruit CircuitPython asyncio Library 1.0 documentation"
