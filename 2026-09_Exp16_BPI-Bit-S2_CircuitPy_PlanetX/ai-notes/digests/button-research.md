# Digest — Button research (public API vs backend)

**Status:** public-API shape `unverified` until first student sketch; backend choice for BPI-Bit-S2 = **provisional** (NOTES). ChatGPT micro:bit-v2 rec = **does not transfer**.
**Date:** 2026-09-04.
**Purpose:** distill two research dumps into what Exp16 should implement. Do not implement the button library this session.
**Sources:** `/Users/alex/Development/VsCode/CircuitPython/2026-09_Exp16_BPI-Bit-S2_CircuitPy_PlanetX/Notes/Button_chat.md` · `/Users/alex/Development/VsCode/CircuitPython/CodingTutor/mini-project-scatches/button-library.md` (near-duplicate of the v2 analysis; CodingTutor also has the RP2350 follow-up).

---

## Do not implement (wrong target)

ChatGPT’s **stock micro:bit v2** stack:

`digitalio` → `adafruit_debouncer.Button` → sync `buttons.update()` in `while True`

Reason it was recommended: stock micro:bit v2 firmware **omits** `keypad` and `_asyncio` (space). BPI-Bit-S2 CircuitPython **10.0.3 support matrix includes `_asyncio`, `keypad.Keys`, frozen `neopixel`**. Goal heading is **asynchronous**. A forced `update()` loop in every student sketch is a second programming model (portability hazard G, `student-api-portability.md`).

The RP2350 section of the same chat is the closer analogue: `keypad.Keys` + semantic dispatcher; asyncio pump as the student path.

---

## Public API (keep — matches LightTower + Alex lock)

Student names **A/B/C/D**. Overnight smoke **C/D only**; A/B on constructor/API.

Shape from the research (MakeCode-ish, not a consumer ABC unless it stays tiny):

```
buttons = ButtonSensor(a_pin=…, b_pin=…, c_pin=…, d_pin=…)   # pins = config seam
buttons.on_c_pressed(handler)
buttons.on_c_released(handler)   # have it; LightTower uses press = FALL
buttons.on_d_pressed(handler)
# … A/B same
buttons.clear_c() / clear()      # drop handlers
```

Handlers run from an **asyncio pump**, not from a sync `update()` the student must call. Optional power-user `update()` underneath is OK if undocumented in student examples.

Constructor pins may change at RP2350 switch (G2). Handler names and “press means falling/active-low” stay.

---

## Backend (provisional until on-device 10.3.0)

```
GPIOs (pull-up, LOW=pressed)
  → keypad.Keys(value_when_pressed=False, pull=True, …)
  → EventQueue (native debounce)
  → map key index → A/B/C/D
  → dispatch on_*_pressed / on_*_released
  → asyncio task that drains the queue (the pump)
```

Confirm at first device contact (log-only this session): `keypad` + `asyncio` present on **CP 10.3.0** `bpi_bit_s2`. Fallback if missing: escalate; do not silently revert to `update()` as the student API.

Exp09 `elecfreaks_planetx.Button` = electrical reference only (pull-up, LOW=pressed). Pin names `IO13`/`IO14` are **disputed** vs official goldfinger P13/P14 = GPIO36/GPIO37 (`Notes/bpi_bit_v2_goldfinger.jpg`).

---

## CodingTutor sketch vs Button_chat

Same prompt + v2 recommendation. CodingTutor file also contains the RP2350 `keypad` recommendation. Use **Button_chat.md** as the longer dump; treat them as one research thread, not two competing designs.

---

## See also

- `../NOTES.md` Recommended button backend
- `lighttower-student-ops.md` PIN_EVT_FALL
- `exp09-lut-icons.md` C/D hypothesis
