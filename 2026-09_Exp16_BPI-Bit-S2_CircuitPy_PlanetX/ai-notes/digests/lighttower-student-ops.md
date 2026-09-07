# Digest — LightTower student operations (first-milestone surface)

**Status:** `evidence-supported` for Watch I display/button ops (tutorial v1.0). Motor/light = later; not this milestone.
**Date:** 2026-09-04.
**Purpose:** the CircuitPython PoC must offer **these operations**, not a pin-level clone of MakeCode. First milestone = libraries that make Watch I traces possible; not implementing the lighthouse tonight.
**Sources (read-only):** `/Users/alex/Development/Isana/LightTower-challenge/2026-05-15_lighthouse-keeper_requirements_v1.0.md` · `2026-05-15_lighthouse-keeper_v1.0.md` (tutorial).

---

## What the tower must do (requirements — later full PoC)

Buttons: **Blue C** = go on duty; **Red D** = come home / maintenance; **A/B** = nudge park (maintenance only). Startup in park + maintenance. Motor sweep / light sensor = Watch II–III.

First milestone does **not** implement this state machine. It must make the **student-facing calls** below available so a later sketch can.

---

## Watch I student ops (the overnight API bar)

Tutorial self-test I.2–I.5. Trace shape: `letter → (icon) → LighthouseMode`.

| MakeCode | When | CircuitPython equivalent (G3) |
|----------|------|-------------------------------|
| `show string "A"` / `"B"` / `"C"` / `"D"` | handler entry | `await display.show_string("C")` (single char, centered) |
| `pause 1000` | between flashes | `await display.pause(1000)` |
| `show icon YES` (✓) | accepted | `await display.show_icon(Icons.YES)` |
| `show icon NO` (X) | ignored | `await display.show_icon(Icons.NO)` |
| `show icon DIAMOND` (◆) | wait / transitioning | `await display.show_icon(Icons.DIAMOND)` |
| `show number LighthouseMode` | handler tail | `await display.show_number(n)` |
| `on event … PIN_EVT_FALL` A/B/C/D | press = falling edge | `buttons.on_a_pressed(handler)` … `on_d_pressed` (names locked A/B/C/D) |
| `set pin Pxx emit edge events` | wiring | **constructor/config only** — must not appear in handler bodies (G1/G2) |

Watch II (not this milestone, names must exist when arrows land): `show arrow` N/S/E/W for A/B nudges.

**Out of student logic:** `set_pixel`, `#`/`.` pattern strings, `WIDTH`/`HEIGHT`, GPIO ids inside handlers.

---

## Pins (tutorial vs this board)

Stock micro:bit tutorial:

| Button | Tutorial pin |
|--------|----------------|
| A | P5 |
| B | P11 |
| C blue | P13 |
| D red | P14 |

BPI-Bit-S2: C/D pin identity **disputed** (`exp09-lut-icons.md`) — Exp09 `board.IO13`/`IO14` vs official P13/P14 = GPIO36/GPIO37. A/B = onboard (official GPIO38/GPIO33); identities left to constructor. **Press = active-low fall** — same electrical story; `keypad.Keys(..., value_when_pressed=False)`.

---

## Modes (context for later sketch, not library code)

`LighthouseMode`: 0 maintenance · 1 operational · 2 transitioning home. Library must not encode this table. Handlers + a student variable do.

---

## Milestone cut

| In first-milestone libraries | Later (full LightTower) |
|------------------------------|-------------------------|
| Display Tier 2: string / number / icon / pause (+ arrow names) | mast park/sweep/nudge |
| Buttons A/B/C/D press (+ release OK to have) | light `is_dark` |
| Host tests of LUT, icons YES/NO/DIAMOND, glyph A–D and digits | on-device Watch I walkthrough |

---

## See also

- `../design/student-api-portability.md` G1–G7
- `exp14-display-lib.md` Tier 2 names already exist
- `button-research.md` handler registration shape
