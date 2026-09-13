# Student-facing API portability — BPI-Bit-S2 (5×5) → RP2350 (8×8)

**Status (2026-09-08):** committed experiment spec (stands alone without `ai-notes/`). Whole-goal claim remains `unverified` until a LightTower student sketch exists; individual guidelines tagged. Working revisit log (cadence extracts) stays in local `ai-notes/design/student-api-portability.md`.

**Student-facing** = APIs used to implement LightTower in CircuitPython. Library internals may change freely.

**How to check later:** (1) write a one-file LightTower *student sketch* against the PoC APIs; (2) at RP2350+8×8 switch, student **logic** (handlers, state machine, display call sequence) stays; **constructor arguments and config** may change in student code and in the library.

**Locked hardware (Alex, 2026-09-04):** display library drives **square WS2812 / NeoPixel** matrices only, N≤8. Supported sizes: **5×5** and **8×8**. Charlieplexed (row/column multiplexed) matrices are out of scope.

## Verdict

**Realistic for LightTower's student surface** if **names and call sequence** stay semantic. Do **not** build a full Hardware Abstraction Layer [HAL]. Motor/light: apply the same rule when those phases exist; do not invent their shapes now.

| Layer | First milestone | Full LightTower | Portable? |
|-------|-----------------|-----------------|-----------|
| Display (`show_icon` / `show_string` / `show_number` / `show_arrow`) | yes | yes | **yes** — 5×5 vs 8×8 is asset swap, not API change |
| Buttons A/B/C/D as press events | yes | yes | **yes** — handlers stay; pin args on the constructor/config may change |
| Mast motor / light sensor | no | Watch II / III | **conditional** — semantic `mast` / `is_dark`, not Nezha2 `M4` or a raw pin |

MCU change (ESP32-S2 → RP2350) is hidden by CircuitPython except wiring: student constructors/config may pass `board.*` pins.

## Design guidelines (hypotheses — revisit at checkpoints)

| Id | Guideline |
|----|-----------|
| G1 | Semantic names for operations, not hardware names in logic. Buttons A/B/C/D; icons YES/NO/DIAMOND; arrows by compass. GPIO as **constructor/config arguments** is allowed. |
| G2 | Constructors and config are the seam. Pins, LUT, font directory live in swap files and/or constructor args. |
| G3 | MakeCode-shaped display API is the student API (`show_icon`, `show_string`, `show_number`, `show_arrow`, `pause`). Tier 1 (`render_*`, `set_pixel`, patterns) may remain for tests; LightTower examples must not need them. |
| G4 | Same icon/arrow *names* on 5×5 and 8×8 for the LightTower set. Extra 8×8-only names may exist only on 8×8. |
| G5 | Library internals may be rewritten at the platform switch as long as student call sites still use the same operation names. Constructor signatures may gain/change wiring parameters. |
| G6 | Anticipate, don't over-build. Motor/light APIs are known-unknowns this milestone. |
| G7 | Student examples are the portability test. One LightTower sketch is the oracle. |

**Confirm** = student **logic** unchanged; constructor args / config may change. **Refute** = a required rewrite of handlers, state machine, or display sequence.

## Hazards (what would force sketch rewrites)

| Hazard | Mitigation |
|--------|------------|
| GPIO / `board.IO13` **inside handlers** | Pins on constructors/config, not in handler bodies |
| `WIDTH`/`HEIGHT` or 5-vs-8 in student **logic** | Examples use icons/strings/arrows only |
| Icon set mismatch (YES, NO, DIAMOND, 4-way arrows) | Keep those names on both geometries |
| Font path leaked to students | Students call `show_string` only |
| Sync `update()` loop in every sketch | Event/async API is the student path |
| Nezha2 `M4` as the motor API | Defer; later expose park/sweep/nudge in mast degrees |
| Brightness 20% cap as a student-set value | Keep cap inside the library |

Hardcoded 8×8 `#`/`.` pattern strings and `set_pixel(x,y)` with literal coords are **not** LightTower student logic.

## Load-bearing assumptions

| Id | Assumption | Status (2026-09-08) |
|----|------------|---------------------|
| A1 | LightTower CircuitPython PoC uses the LED matrix as the MakeCode feedback channel | keep |
| A2 | BPI-Bit-S2 CP 10.3.0 still has `keypad` + user-facing bundle `asyncio` on device | `unverified` (P8) |
| A3 | Square WS2812 only, N≤8; 5×5 and 8×8 | **locked** 2026-09-04 |
| A4 | PlanetX C/D remain two GPIOs, active-low, pull-up — only pin *identities* change | cable `unverified` (P8); firmware names known |

## Overnight P1–P6 (host, 2026-09-04)

G1–G4, G6 **confirm** (names + seam). G5 n/a (no platform switch). G7 stand-in only (Watch I sketch deferred). A2/A4 still P8.

## See also

- Exp16 `lib/display/README.md` — two-tier API
- LightTower `2026-05-15_lighthouse-keeper_requirements_v1.0.md` — Watch I–III operations
- Persona `CODING_PRINCIPLES.md` — student-facing API stability directive
