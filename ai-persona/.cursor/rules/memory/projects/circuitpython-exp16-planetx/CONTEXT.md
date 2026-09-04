# Context — circuitpython-exp16-planetx

**Family**: `circuitpython` · **Status:** P6 host-green (overnight 2026-09-04); P7/P8 not started · **Repo folder**: `/Users/alex/Development/VsCode/CircuitPython/2026-09_Exp16_BPI-Bit-S2_CircuitPy_PlanetX/` · **Goal note**: `Notes/overall_goal.md`.

## Scope & goal

Prove a CircuitPython stack on the **BPI-Bit-S2** (ESP32-S2, micro:bit form factor, onboard 5×5 WS2812) can run the **LightTower challenge** as a PoC. Stack to build; LightTower is the demonstration, not production firmware. Library-level code should be upgradable to production with moderate effort.

**First major milestone (interim):**
1. Async LED-matrix library — fork Exp14 `lib/display/` onto 5×5 (brightness cap 20%). **Hardware scope (locked):** square WS2812 / NeoPixel only, max 8 on a side; realistic sizes **5×5** and **8×8**. Charlieplexed matrices out of scope. **5×5 ↔ 8×8 via file replacement and/or localized edits**: geometry/LUT, icons, arrows, font. Not a second library. Exp14: arrows live in `icons.py` beside icons; font is `font_*/` + `_FONT_PATH` in `core.py`.
2. Async button library — PlanetX C/D (+ board A/B later for LightTower).

**Portability (design goal, not a Hardware Abstraction Layer [HAL]):** student-facing LightTower **operations** should survive a later RP2350+8×8 switch. Constructor parameters and config may change in student code and in the library. Analysis: exp16 `ai-notes/design/student-api-portability.md`. Realistic for display+buttons now; motor/light later as semantic APIs.

**End demonstration:** `/Users/alex/Development/Isana/LightTower-challenge` requirements (`2026-05-15_lighthouse-keeper_requirements_v1.0.md`). Needs more than LED+buttons (servo sweep, light sensor) — later.

## Constraints (Alex, 2026-09-03)

- Experiments human-conducted; agent writes software. Overnight independent iteration is the aim; physical reset of a stuck board is acceptable.
- Host Python: `/Users/alex/Development/PythonVEs/CircuitPython_3.13_VsCode` (Mac/Cursor; pytest).
- Focus: **asynchronous** programming.
- Do not change Alex's working setup without explicit permission. Workspace-level CircuitPythonSync currently still points at Exp14's YD-RP2040 / 10.1.3 — override per-experiment, do not rewrite the shared workspace settings without asking.
- **Destructive ops hard gate** (persona-wide, Exp16 reminder): never delete/overwrite/rewrite-history without a ledger grant. Banner: exp16 `ai-notes/NOTES.md` (top) + `ai-notes/INDEX.md`. Protocol: `/Users/alex/Git/rnd-ai-skills/generalized-agent-learnings/destructive-operations.md`. Ledger: `memory/PERMITTED_DESTRUCTIVE_ACTIONS.md` (empty). Always-on stub: `06-destructive-operations.mdc`.
- **Standing §4 park (confirmed 2026-09-04):** `…/2026-09_Exp16_…/ai-notes/_parked/` — move here instead of delete. Policy `_parked/README.md`; index `_parked/MANIFEST.md`. Deleting parked copies still gated. Exp16 only.
- Working notes: `ai-notes/` in the exp16 folder. Cold-AI plan on disk; chat stays high-level.
- Coarse git commits on working branches when a chunk is done or enters revision. History of *reasoning* → `ai-notes/`, not git messages alone.

## Entry points (links, not copies)

| What | Path |
|------|------|
| Goal / working prefs | `…/2026-09_Exp16_…/Notes/overall_goal.md` |
| Goldfinger pinout (CC BY-SA, unmodified) | `…/Notes/bpi_bit_v2_goldfinger.jpg` + `bpi_bit_v2_goldfinger.jpg.license` |
| Button brainstorm (ChatGPT, micro:bit v2 then RP2350) | `…/Notes/Button_chat.md` |
| Alternate button sketch | `…/CodingTutor/mini-project-scatches/button-library.md` |
| Display library to copy | `…/2026-04_Exp14_…/lib/display/` (`README.md`, `geometry.py`, `_constants.py`, `core.py`, `icons.py`) — **style + algorithm SoT**; Exp16 works on its copy |
| 5×5 LUT / orientation (formula `index = row + 20 - column * 5`) | `…/2026-02_Exp09_…/lib/display_v0.py`, `lib/microbit.py` |
| Micro:bit 5×5 pictograms (already in Exp09 `Image.*`) | `…/2026-02_Exp09_…/lib/microbit.py` (~line 245+) |
| LightTower requirements | `…/Isana/LightTower-challenge/2026-05-15_lighthouse-keeper_requirements_v1.0.md` |
| Portability analysis + reflection cadence | `…/2026-09_Exp16_…/ai-notes/design/student-api-portability.md`, `…/ai-notes/plan/reflection-cadence.md` |

## Domain knowledge (central)

- Runtime / allocation → `../../concepts/circuitpython-runtime.md`
- Fonts at small pixel sizes → `../../concepts/fonts.md` (outline fonts fail; 5×5 wants a hand-designed bitmap / MakeCode-style font)
- `led-driving` not yet seeded; Exp09 LUT is the first concrete 5×5 WS2812 mapping

## Resumption point

**2026-09-04 — overnight P1–P6 host-green.** 146 pytest passed (no `board` / `display.core`). Stopped at the overnight bar. Do **not** P7 `.vscode/` / shared CircuitPythonSync, do **not** P8 / USB-probe until Alex says so. Flash board to CP 10.3.0 at P8. Locks: `ai-notes/NOTES.md`. Learnings: `ai-notes/learnings/p1-p6-overnight.md`.
