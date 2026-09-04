# Student-facing API portability — BPI-Bit-S2 (5×5) → RP2350 (8×8)

**Status:** analysis + design guidelines. `unverified` as a whole-goal claim until a LightTower student sketch exists; individual rows tagged. **Date:** 2026-09-03.
**Purpose:** decide whether a mostly-stable student API across the later hardware switch is realistic, and record guidelines to *revisit / test / adjust* during plan execution (not to freeze a Hardware Abstraction Layer [HAL] now — a catch-all board-hiding stack).
**Student-facing** = APIs used to implement LightTower in CircuitPython. Library internals may change freely.
**How to check later:** (1) write a one-file LightTower *student sketch* against the PoC APIs; (2) at RP2350+8×8 switch, student **logic** (handlers, state machine, display call sequence) stays; **constructor arguments and config** may change in student code and in the library. Target: no redesign of the sketch.

**Revisit this file at every phase checkpoint** (`../plan/reflection-cadence.md`). Guidelines below are **hypotheses**. Confirm / refute / refine with dated notes; do not silently absorb.

**Locked hardware (Alex, 2026-09-04 — not a hypothesis):** display library drives **square WS2812 / NeoPixel** matrices only, N≤8. Supported sizes: **5×5** and **8×8**. Charlieplexed (row/column multiplexed) matrices are out of scope.

**Sources:** LightTower `2026-05-15_lighthouse-keeper_v1.0.md` + requirements v1.0; Exp14 `lib/display/`; Exp09 `lib/microbit.py` + `lib/elecfreaks_planetx/button.py`; Exp15 pin map; CircuitPython 10.0.3 support matrix (BPI-Bit-S2: `_asyncio`, `keypad.Keys`).

---

## Verdict

**Realistic for LightTower's student surface**, if **names and call sequence** stay semantic. Constructor parameters and config may change in student code and in the library at the platform switch.

| Layer | Now (first milestone) | Later (full LightTower) | Portable? |
|-------|----------------------|-------------------------|-----------|
| Display (`show_icon` / `show_string` / `show_number` / `show_arrow`) | yes | yes (feedback channel in Watch I–III) | **yes** — Exp14 already is MakeCode-shaped; 5×5 vs 8×8 is asset swap, not API change |
| Buttons A/B/C/D as press events | yes | yes (Watch I core) | **yes** — handlers stay; pin args on the constructor/config may change |
| Mast motor (park, sweep 240°, nudge 10°) | no | Watch II | **conditional** — need a semantic `mast` API, not Nezha2 `M4` |
| Light sensor (dark / not) | no | Watch III | **conditional** — `is_dark` / `light_level`, not a pin |

MCU change (ESP32-S2 → RP2350) is hidden by CircuitPython for everything except wiring: student constructors/config may pass `board.*` pins. Both boards' stock firmware include `keypad` + `_asyncio` (S2: matrix 10.0.3; RP2350: full build). **On-device 10.3.0 still to confirm.**

Pragmatic PoC: do **not** build a full Hardware Abstraction Layer [HAL]. Build display + buttons so a LightTower sketch would survive an 8×8/RP2350 swap by editing constructors/config, not handlers. Motor/light: design later against the same rule; do not invent their shapes now.

Language switch MakeCode-blocks → CircuitPython is a *separate* cost. Hardware switch must not pile a second redesign on top.

---

## What LightTower students actually call

From the MakeCode tutorial (the CircuitPython PoC should offer equivalents, not pin-level clones):

| MakeCode | Role in LightTower | Exp14 / planned CP equivalent |
|----------|--------------------|-------------------------------|
| `show string "C"` | letter flash | `await display.show_string("C", …)` |
| `show number LighthouseMode` | mode tail | `await display.show_number(n, …)` |
| `show icon YES` / `NO` / `DIAMOND` | accept / ignore / wait | `await display.show_icon(Icons.YES)` — names exist in Exp14 `ICON_NAMES` |
| `arrow image` N/S/E/W | nudge direction | `await display.show_arrow(Arrows.NORTH)` — `ARROW_NAMES` |
| `on event … PIN_EVT_FALL` for A/B/C/D | press handlers | `buttons.on_a_pressed(handler)` (shape provisional) |
| `set pin Pxx emit edge events` | wiring, not logic | **must not appear in student code** |
| Nezha2 M4 absolute angle / rotate | Watch II | later: `mast` — not this milestone |
| `Light sensor > 100` | Watch III | later: `light` — not this milestone |

Hardcoded 8×8 `#`/`.` pattern strings are **not** in LightTower. `set_pixel(x,y)` with literal coords is **not** in LightTower. Those APIs may exist for power users; student **logic** must not depend on `WIDTH`/`HEIGHT`. GPIO ids as **constructor / config arguments** are an allowed seam (Alex, 2026-09-04).

---

## Hazards (what would force sketch rewrites)

| Hazard | Why it breaks the switch | Mitigation (hypothesis) | Revisit when |
|--------|--------------------------|-------------------------|--------------|
| GPIO / `board.IO13` / `P13` **inside handlers** | Pin identities differ (Exp09 `IO13/IO14`; Exp15 A/B = GP0/GP1, not micro:bit P5/P11) | Pins belong on constructors/config, not in event-handler bodies | First button API sketch; again at RP2350 pin map |
| `WIDTH`/`HEIGHT` or 5-vs-8 in student code | 5×5 → 8×8 changes the grid | Student examples use icons/strings/arrows only | Any demo that draws pixels or pattern strings |
| Icon set mismatch | LightTower needs YES, NO, DIAMOND, 4-way arrows. 8×8-only icons (GIRAFFE, …) must remain optional | Keep the LightTower names on both geometries | Icon port from Exp09; 8×8 swap test |
| Font path / glyph metrics leaked | `_FONT_PATH` is a library hook; students call `show_string` | Never document font files in student API | Font integration |
| Sync `update()` loop vs asyncio | Goal is async; a forced `while True: buttons.update()` in every sketch is a second programming model | Event/async API is the student path; sync poll may exist underneath | Button-lib spike |
| `asyncio.run` / `async def main` vs MakeCode forever | Language cost, same on both boards | Accept; do not paper over with a fake MakeCode runtime | First end-to-end sketch |
| Nezha2 `M4` / encoder degrees as the motor API | RP2350 bit board has no Nezha2 | Defer; when built, expose park/sweep/nudge in *degrees of mast*, not port names | Watch II phase (not now) |
| Brightness 20% cap as a student-set value | Different LED counts / current | Keep cap inside the library | 8×8 current check |
| Column-major height > 8 | Would need a different bitmap encoding | **Out of scope** — library is square WS2812, N≤8, only 5×5 and 8×8 | do not reopen unless Alex expands scope |

**Allowed at platform switch (student code and library):** constructor parameters and config (pins, `board.*` aliases, which pixel pin). **Not OK:** rewriting handlers, state machine, or display call sequence.

---

## Design guidelines (hypotheses — revisit)

G1. **Semantic names for operations, not hardware names in logic.** Buttons A/B/C/D; icons YES/NO/DIAMOND; arrows by compass. No `M4` / `J3` in student-facing *operation* signatures. GPIO as **constructor/config arguments** is allowed.
G2. **Constructors and config are the seam.** Board-specific pins, `PIXEL_PIN`, LUT, font directory live in swap files and/or constructor args. Student **logic** imports the stack; wiring may be passed in.
G3. **MakeCode-shaped display API is the student API.** Exp14 Tier 2 (`show_icon`, `show_string`, `show_number`, `show_arrow`, `pause`) is the target. Tier 1 (`render_*`, `set_pixel`, patterns) may remain for tests/power users; LightTower examples must not need them.
G4. **Same icon/arrow *names* on 5×5 and 8×8.** Bitmaps swap; attributes do not disappear for names LightTower uses. Extra 8×8-only names may exist only on 8×8 (document as optional).
G5. **Library internals may be rewritten** at the platform switch (LUT, PIO vs `neopixel`, keypad vs not) as long as student call sites still type-check against the same operation names. "Don't invalidate the entire design" = keep G1–G4, not freeze `core.py`. Constructor signatures may gain/change wiring parameters.
G6. **Anticipate, don't over-build.** Motor/light APIs are known-unknowns. Do not invent them this milestone. When they arrive, apply G1–G2.
G7. **Student examples are the portability test**, not a compatibility matrix. One LightTower sketch is the oracle.

Each Gi: **signals** — confirm = student **logic** unchanged; constructor args / config may change. Refute = a required rewrite of handlers, state machine, or display sequence. **Act on refute:** adjust the guideline (narrow/drop) or the API; escalate if it would change the *target* (stable student operations).

---

## Load-bearing assumptions (tag; revisit first)

A1. LightTower CircuitPython PoC uses the LED matrix as the MakeCode feedback channel (letter → icon → number). If we drop display from LightTower, display-API stability still matters for the stack but is no longer on the student critical path.
A2. BPI-Bit-S2 CP 10.3.0 still has `keypad` + asyncio (inferred from 10.0.3 matrix).
A3. **Locked 2026-09-04 (no longer an assumption):** display lib = square WS2812 only, N≤8; supported sizes 5×5 and 8×8. Charlieplexed matrices out of scope. RP2350 target therefore an 8×8 WS2812, not Exp15's de-soldered Charlieplexed 5×5.
A4. PlanetX C/D remain two GPIOs, active-low, pull-up — only the pin *identities* change.

---

## See also

- `../plan/reflection-cadence.md` — when to re-open this file
- `../NOTES.md` — locked product decisions
- Exp14 `lib/display/README.md` — two-tier API
- LightTower tutorial Watch I.2–I.5 — actual student operations
- Corpus: `/Users/alex/Git/rnd-ai-skills/generalized-agent-learnings/Flexible Plans for AI Execution.md` (layered commitment); `plan-refinement-loop.md` (checkpoints); `09-RECURSIVE-LEARNING.md` (extraction gets crowded out unless scheduled)
