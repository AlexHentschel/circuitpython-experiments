# Execution plan v0.1 — Exp16 first milestone (overnight PoC)

**Status:** refinement 1 (substance). **Date:** 2026-09-04. **Loop:** cap 8 (`loop-setup.md`); sign-off candidate is `plan_v1.0.md`.
**Purpose:** a cold AI can execute the overnight PoC without re-deriving locks. **Planning chat stops at v1.0** — do not implement from this file.
**How to check later:** host pytest green on LUT + LightTower icons + button dispatcher (no `board` required); `lib/display/` is 5×5; `lib/` has an async button module. On-device is a later human window.

Cadence (import, do not copy): [`reflection-cadence.md`](reflection-cadence.md). Portability rubric: [`../design/student-api-portability.md`](../design/student-api-portability.md). Locks: [`../NOTES.md`](../NOTES.md). Digests: [`../digests/INDEX.md`](../digests/INDEX.md). Notes for this version: [`notes_v0.1.md`](notes_v0.1.md).

---

## Corpus digest (lean context — pointers, not dumps)

| Discipline | One line | Open |
|------------|----------|------|
| Chat = cache; detail on disk; resume = INDEX + NOTES | working-notes-lean-context.md | `/Users/alex/Git/rnd-ai-skills/generalized-agent-learnings/working-notes-lean-context.md` |
| Layered commitment + audible checkpoints | Flexible Plans for AI Execution.md | same corpus folder |
| Destructive-ops hard gate; Exp16 park is not a delete grant | ledger empty; **move** to `ai-notes/_parked/` | corpus `destructive-operations.md`; `../_parked/README.md` |
| Reflect **and** extract at every gate | this folder’s `reflection-cadence.md`; corpus 09-RECURSIVE-LEARNING.md | import cadence file |
| Anything else | corpus README / 00-OVERVIEW.md | corpus root |

Persona durable copies: `ai-persona/.cursor/rules/reference/`.

---

## Layered commitment

### Fix (escalate to Alex if these change)

- **Outcome:** first milestone = async 5×5 display (icons + MakeCode-style font) **and** async PlanetX buttons.
- **Overnight bar:** host tests + libraries on disk. On-device = later human window (physical reset OK then).
- **Firmware:** stock CircuitPython **10.3.0** for `bpi_bit_s2`. Host venv: `/Users/alex/Development/PythonVEs/CircuitPython_3.13_VsCode`.
- **Quality:** PoC, not production; library-level code upgradable with moderate effort; TODOs in code; reasoning in `ai-notes/`.
- **Display hardware:** square WS2812 / NeoPixel only, N≤8; sizes **5×5** now, **8×8** later. Charlieplexed matrices out of scope.
- **5×5 ↔ 8×8:** file replacement and/or localized edits of **geometry/LUT, icons, arrows, font**. Not a second library. Not a `core.py` rewrite.
- **Work on the Exp16 copy** at `/Users/alex/Development/VsCode/CircuitPython/2026-09_Exp16_BPI-Bit-S2_CircuitPy_PlanetX/lib/display/` (copied 2026-09-04 from Exp14). Do not edit Exp14 for this milestone.
- **Student operations** stay stable across a later RP2350+8×8 switch; **constructors/config may change**. Revisit G1–G7; do not freeze a Hardware Abstraction Layer [HAL].
- **Buttons:** names **A/B/C/D**; overnight C/D (host-fake now, device later); A/B on constructor/API. Backend: `keypad.Keys` → semantic dispatcher → asyncio pump. Do **not** ship micro:bit-v2 sync `update()` as the student path.
- **Brightness cap** 0.20 hardcoded in the library (not a student-set value).
- **No working-setup mutation** of shared CircuitPythonSync (still Exp14 YD-RP2040 / 10.1.3). Per-experiment `.vscode/` = later execution chat only.
- **Destructive ops:** ledger empty. Move-don’t-delete to `_parked/`. No git commit unless Alex asks.
- **Cadence:** every checkpoint Observe→Evaluate→Revise-or-no-change **and** extract/record.

### Provisional (expected to evolve)

- Phase list and order below.
- Font **source** (§ Font recommendation; not locked in NOTES).
- Host-test layout (copy Exp14 `tests/` vs thin 5×5 suite).
- Button package path / class name.
- Whether arrows stay in `icons.py`.

### Open (shape at execution)

- Helper names, file splits, glyph storage (PCF vs raw 5-byte table), pytest filenames, optional `code.py` demo.

---

## Font recommendation (do not lock a source)

**Target look:** MakeCode 5×5 (LightTower students already know it). Exp14 `font_free_mono_8` (FreeType auto-raster of FreeMono at 8 px) is structurally illegible — `concepts/fonts.md`.

**Recommend (provisional):** Lancaster DAL `MicroBitFont` / MakeCode `pendolino3`. **P3 first action:** read the DAL file’s license header before copying any glyphs (Apache-2.0 is a hypothesis until then). Convert to Exp14 column-major **or** a 5-byte-per-glyph table. Overnight minimum: `A`–`D` and digits `0`–`9`. Full ASCII if conversion is cheap.

**Do not silently ship:** Exp09 `pitchfork-5x5` / `lib/microbit.py` `_FONT` — **GPLv3**. Escalate to Alex before copying.

**Leave open:** Portable Compiled Font [PCF] for `_glyph_columns` vs a 5×5-native table that isolates the font the same way (`font_*/` or one module).

---

## Pins (hypothesis — confirm at wiring / P-device)

| Role | Hypothesis | Overnight |
|------|------------|-----------|
| Matrix DIN | `board.NEOPIXEL` (= IO18) | host tests do not need the pin |
| C (blue) | `board.IO13` | fake FALL events in pytest |
| D (red) | `board.IO14` | same |
| A/B onboard | constructor args; likely `board.BUTTON_A` / `BUTTON_B` | API present; not required to fire overnight |

Electrical: internal pull-up, LOW = pressed = falling edge.

---

## Phases (provisional; **execution** chat)

Each P1–P6 close: cadence **P-phase** + re-open G1–G7. First student-facing name: **P-api**. **P-device** / **P-human** are not overnight.

### Overnight (success bar)

| ID | Target | First atomic action | Exit / escalate |
|----|--------|---------------------|-----------------|
| P0 | Knowledge in tree | **Done** — `ai-notes/digests/` + Exp16 `lib/display/` copy | — |
| P1 | 5×5 geometry + LUT | `WIDTH=HEIGHT=5`; replace `build_lut` stage-2 with Exp09 `idx = row + 20 - column * 5`; test with a **visual fixture** (independent of that formula) | Formula vs Exp09 docstring grid disagree → stop and compare |
| P2 | Icons/arrows 5×5 | Hypothesis: Exp09 `Image.*` is 25-byte row-major brightness 0–9 → Exp14 column-major (5 bytes). Keep names YES, NO, DIAMOND, compass arrows | G4: those names must exist |
| P3 | Font | Read DAL license header, then recommended path **or** alternative; letters+digits | GPLv3 → escalate. Legibility = P-human |
| P4 | Hardware hooks | `PIXEL_PIN=board.NEOPIXEL`, `BRIGHTNESS=0.20`; keep `__init__.py` hardware import guard | — |
| P5 | Async buttons | `keypad.Keys` + A/B/C/D dispatch + asyncio pump; pytest with a fake EventQueue | Student `update()` loop → escalate (target conflict) |
| P6 | Host suite green | Pytest via the designated venv. Cover **pure** modules (`geometry`, `bitmap_codec`, `icons`) + button dispatcher. Do **not** require importing `Display`/`core` on a host without `board` | Overnight success bar |

### Out of overnight (do not treat as P6 exit)

| ID | Target | When |
|----|--------|------|
| P7 | Per-experiment `.vscode/` CircuitPythonSync override | Later execution chat; **escalate** before any **shared** workspace CircuitPythonSync edit |
| P8 | On-device: CP 10.3.0 `keypad`+asyncio; C/D + LUT smoke | Human window; log-only until then |

This planning chat does **not** run P1–P8.

---

## Success criteria (initial — revision gate at each phase close)

Overnight API bar = Watch I **operations**, not the lighthouse state machine:

1. Exp16 `lib/display/` is 5×5; Exp14 tree untouched.
2. Host tests (no `board`): LUT corners + interior; icons YES, NO, DIAMOND (+ one arrow); codec still rejects height>8; button `on_c_pressed` / `on_d_pressed` fire on fake FALL; `clear` drops handlers; A/B exist on the constructor.
3. Glyph helpers (or equivalent) can produce column bytes for `A`–`D` and `0`–`9` without FreeMono.
4. No student-facing path requires `buttons.update()` or GPIO ids inside handlers. Constructors take pins.
5. TODOs in code for future work; extracts in `ai-notes/learnings/`.

**G7 overnight stand-in:** a host test that the **names** for `show_string` / `pause` / `show_icon` / `show_number` / `on_*_pressed` exist on the public surface (import or documented re-export). A full Watch I student sketch is **not** overnight.

**Criteria-revision:** if a phase shows a criterion is the wrong one, revise audibly (this happened v0.0→v0.1: dropped “mocked Display `show_*` on host” as required).

---

## Known unknowns

| ID | Unknown | When it discharges | If it blows up |
|----|---------|--------------------|----------------|
| K1 | CP 10.3.0 exposes `keypad` + asyncio on this board | P8 | Escalate; do not silently make `update()` the student API |
| K2 | IO13/IO14 really C/D on this wiring | P8 | Constructor pins change (allowed) |
| K3 | DAL/MakeCode conversion cheap + license OK | P3 | Hand-author A–D + digits; still not FreeMono; GPLv3 still escalate |
| K4 | Exp14 pytest suite vs thin 5×5 suite | P1–P6 | Thin suite is an acceptable provisional choice |
| K5 | Onboard A/B CircuitPython names | P7/P8 | Stubs on the constructor |

---

## Authority-handoff

| Change | Who |
|--------|-----|
| Target-preserving implementation (LUT, icon bytes, font conversion, test layout, button module path) | Agent |
| Student-API **stability target**, cadence rules, hardware scope, overnight bar, GPLv3 ingest, shared CircuitPythonSync, destructive ops, git commit | **Alex** |
| Criteria additions, Watch II motor / light / HAL | Escalate **before** expanding |

Park: `../_parked/`. Ledger: `ai-persona/.cursor/rules/memory/PERMITTED_DESTRUCTIVE_ACTIONS.md` (empty = nothing permitted).

---

## Checkpoints

P-plan (this loop) · P-phase (P1–P6) · P-api (first student-facing name) · P-device · P-human (font/button feel) · P-surprise · P-done.

Silence at a checkpoint is the failure mode.

---

## See also

- Digests: `../digests/exp14-display-lib.md`, `exp09-lut-icons.md`, `lighttower-student-ops.md`, `button-research.md`
- Copy architecture: `../../lib/display/README.md`
- Exp09 LUT: `/Users/alex/Development/VsCode/CircuitPython/2026-02_Exp09_BPI-Bit-S2-LED-Matrix/lib/display_v0.py`
