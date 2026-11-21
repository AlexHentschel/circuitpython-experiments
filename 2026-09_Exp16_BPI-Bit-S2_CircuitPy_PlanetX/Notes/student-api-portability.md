# Student-facing API portability — BPI-Bit-S2 (5×5) → RP2350 (8×8)

**Status (2026-09-08):** committed experiment spec (stands alone without `ai-notes/`). Whole-goal claim remains `unverified` until a LightTower student sketch exists; individual guidelines tagged. Working revisit log (cadence extracts) stays in local `ai-notes/design/student-api-portability.md`.

**Student-facing** = APIs used to implement LightTower in CircuitPython. Library internals may change freely.

**How to check later:** (1) write a one-file LightTower *student sketch* against the PoC APIs; (2) at RP2350+8×8 switch, student **logic** (handlers, state machine, display call sequence) stays; **constructor arguments and config** may change in student code and in the library.

**Locked hardware (Alex, 2026-09-04):** display library drives **square WS2812 / NeoPixel** matrices only, N≤8. Supported sizes: **5×5** and **8×8**. Charlieplexed (row/column multiplexed) matrices are out of scope.

## Verdict

**Realistic for LightTower's student surface** if **names and call sequence** stay semantic. Do **not** build a full Hardware Abstraction Layer [HAL]. Motor/light: apply the same rule when those phases exist; do not invent their shapes now.

| Layer | First milestone | Full LightTower | Portable? |
|-------|-----------------|-----------------|-----------|
| Display (verb grid: `render_*` / `show_*` / `scroll_*`, plus `hold`, `clear`, `centered`, `start_col`) | yes | yes | **yes** — 5×5 vs 8×8 is asset swap, not API change |
| Buttons A/B/C/D as press events | yes | yes | **yes** — `button_a` … `button_d` then `.on_pressed` (one handler; a later call replaces it; `None` clears it); constructor seam is *which object* (`buttons.OnboardButtons` vs `planetx.PlanetXButtonSensor`) plus pin or `port=` args |
| Mast motor / light sensor | no | Watch II / III | **conditional** — semantic `mast` / `is_dark`, not Nezha2 `M4` or a raw pin |

MCU change (ESP32-S2 → RP2350) is hidden by CircuitPython except wiring: student constructors/config may pass `board.*` pins.

## Design guidelines (hypotheses — revisit at checkpoints)

| Id | Guideline |
|----|-----------|
| G1 | Semantic names for operations, not hardware names in logic. Press handlers are `button_a` / `button_b` on `OnboardButtons` and `button_c` / `button_d` on each `PlanetXButtonSensor`, then `.on_pressed`. One function per press; the student composes anything further inside that function. Icons YES/NO/DIAMOND; arrows by compass. GPIO as **constructor/config arguments** is allowed. |
| G2 | Constructors and config are the seam. Pins, LUT, font directory live in swap files and/or constructor args. Button wiring is two (or more) objects, not four pins on one dispatcher. Onboard A/B import from ``buttons``; PlanetX C/D from ``planetx`` (``port=J3`` or explicit pins). |
| G3 | The display API is a verb grid, and it is the student API. `render_*` draws and returns (stays lit). `show_*` draws, holds for `duration_ms`, then blanks. `scroll_*` moves content one column at a time, at `interval_ms` per column (`blank_edges` chooses marquee or pan). Tier 0 (`get_pixel`, `set_brightness`, `set_rotation`) never interrupts. Also `clear`, `hold`, and `repeat_until_cancelled`. Content is left-aligned by default. `start_col` places it. `centered(...)` centers text on request. Names follow MakeCode where a counterpart exists (`show_icon`, `show_string`, `show_number`, `show_arrow`). `hold` is this library's name for MakeCode's `pause`: it keeps the current frame and does not wipe. Contracts are the library's own, and MakeCode compatibility is no longer a goal (Alex, 2026-10-17). LightTower examples are ported by hand: a MakeCode `show icon` that persists is `render_icon`; one followed by MakeCode `pause(n)` is `show_icon(…, duration_ms=n)`; a long `show string` is `scroll_string`. The verb predicts `await` (render sync; show, scroll, and hold async). |
| G4 | Same icon/arrow *names* on 5×5 and 8×8 for the LightTower set. Extra 8×8-only names may exist only on 8×8. |
| G5 | Library internals may be rewritten at the platform switch as long as student call sites still use the same operation names. Constructor signatures may gain/change wiring parameters. |
| G6 | Anticipate, don't over-build. Motor/light APIs are known-unknowns this milestone. |
| G7 | Student examples are the portability test. One LightTower sketch is the oracle. |
| G8 | Display `Token` and motor `Token` are separate classes. Display (2026-11-20): read-only properties `was_completed` (sticky) and `is_expired` (live; a later display call can set it after completion). Not methods. One small int, bits 1 and 2. `hold` replaced `pause`. Motor `Token` is still the older `is_expired`-only class. `task.cancel()` is not this pair. |

**Confirm** = student **logic** unchanged; constructor args / config may change. **Refute** = a required rewrite of handlers, state machine, or display sequence.

## Hazards (what would force sketch rewrites)

| Hazard | Mitigation |
|--------|------------|
| GPIO / `board.IO13` **inside handlers** | Pins on constructors/config, not in handler bodies |
| `WIDTH`/`HEIGHT` or 5-vs-8 in student **logic** | Examples use icons/strings/arrows only |
| Icon set mismatch (YES, NO, DIAMOND, 4-way arrows) | Keep those names on both geometries |
| Font path leaked to students | Students call `show_string`, `render_string`, or `render_number`; they do not name the font path |
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

G1, G2, G4, and G6 **confirm** (names + seam) for the guidelines as they stood that night. G5 n/a (no platform switch). G7 stand-in only (Watch I sketch deferred). A2/A4 still P8. G3 was rewritten 2026-11-20 to the verb grid (`start_col`, `hold`, `was_completed`, `is_expired`, `scroll_*`). That rewrite is not part of the 2026-09-04 confirm. Plan: `ai-notes/2026-10-17_display-api-uniformity/05_execution_plan_v1.1.md` § 7, with the names in § Current code.

## See also

- Exp16 `lib/display/README.md` — two-tier API
- LightTower `2026-05-15_lighthouse-keeper_requirements_v1.0.md` — Watch I–III operations
- Persona `CODING_PRINCIPLES.md` — student-facing API stability directive
- Exp16 `README.md` § *ElecFreaks PlanetX / Nezha — protocol sources* — vendor MicroPython + MakeCode repos for pin maps / I2C command bytes when motor/light (or further sensors) land; not CircuitPython drivers
