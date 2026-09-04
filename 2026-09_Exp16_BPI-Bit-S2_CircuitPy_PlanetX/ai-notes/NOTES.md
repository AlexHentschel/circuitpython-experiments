# NOTES — Exp16 kickoff lock (2026-09-03)

> **HARD GATE — Destructive operations (cannot miss).**
>
> An agent with a shell never deletes or non-trivially-reverses anything unless Alex has given an **explicit, specific grant covering those exact files**. There is **no a-priori permission**. Silence, skipping a question, "continue", "go ahead on the plan", an unobjected default, or approval of an adjacent non-destructive plan is **not** a grant. Partial grant ≠ blanket. When unsure, treat as destructive.
>
> **What is gated:** untracked/gitignored delete, `rm`/`rm -rf`, overwrite without a verified cheap restore, git history rewrite / `push --force`, deleting backups. Git-tracked **committed** edits are trivially reversible (`git restore`) and are not this gate. **If blocked:** MOVE to the standing park (do not delete). **If requesting:** dedicated message, unmissable header, exhaustive list, **fresh trigger word** for this case. Record the grant in persona `memory/PERMITTED_DESTRUCTIVE_ACTIONS.md` (fail-closed: no matching active entry = no permission). Active grants today: **none**.
>
> **Standing §4 park (confirmed 2026-09-04, Exp16 only):** `/Users/alex/Development/VsCode/CircuitPython/2026-09_Exp16_BPI-Bit-S2_CircuitPy_PlanetX/ai-notes/_parked/`. Each move: dated subfolder + `MOVE.md` + `MANIFEST.md` row, then tell Alex. Policy: `_parked/README.md`. Deleting a parked copy is still §5-gated. This is **not** a delete grant.
>
> **Further reading (corpus is source of truth):** `/Users/alex/Git/rnd-ai-skills/generalized-agent-learnings/destructive-operations.md` — §0 one-line purpose, §2 what counts, §3 hard gate, §4 move never delete, §5 confirmation protocol, §6 ledger, §7 per-action self-check (+ inbound-ref sweep), §8 backups are gated, §9 directive table. Persona durable copy: `ai-persona/.cursor/rules/reference/destructive-operations.md`. Always-on stub: `ai-persona/.cursor/rules/06-destructive-operations.mdc`. Working-style banner: `memory/universal/WORKING_STYLE.md` (opens with this gate). Facet split: corpus `host-portability.md` §7. Router: corpus `README.md` ("Stop the AI deleting files…").

Checkpoint: **2026-09-04** — overnight **P1–P6 host-green** (146 pytest; no `board`/`core`). P7/P8 not started. Board **unplugged** until Alex instructs otherwise. Host venv: pytest, Adafruit `mpy-cross` 10.3.0, `circuitpython-stubs` 10.3.0. Overnight git: coarse commits on `alex/display-mvp_5x5`.

**REMINDER — flash the board to CircuitPython 10.3.0** (Alex, 2026-09-04). Host tools are on 10.3.0; the BPI-Bit-S2 is believed still on older firmware. Do this before/at P8.

- **Blocked 2026-09-04:** board not connected (Alex confirmed). **Overnight P1–P6 does not need it.** Flash + REPL confirm = P8 / first human device window.
- Images (local cache, 2026-09-04, **not** on the board): `/Users/alex/Development/PythonVEs/circuitpython-firmware/bpi_bit_s2/adafruit-circuitpython-bpi_bit_s2-en_US-10.3.0.uf2` (+ `.bin`). Official: [board page](https://circuitpython.org/board/bpi_bit_s2/). After flash: REPL version + `help("modules")`. CP 10 on 4MB Espressif needs TinyUF2 ≥ 0.33.0 if using UF2.

## Locked (Alex, 2026-09-03)

- Overnight PoC = **full first milestone**: async 5×5 display (icons + MakeCode-style font) **and** async PlanetX buttons.
- Library + project template = Exp14. Copy `lib/display/` Exp14 → Exp16; work on the copy. Exp09 supplies 5×5 LUT, orientation, pictogram bitmaps only.
- Button library is **asynchronous** (goal heading corrected). Do not implement the micro:bit-v2 ChatGPT backend (`digitalio` + `adafruit_debouncer` + sync `update()`).
- 5×5 ↔ 8×8 switch-back = **file replacement and/or localized edits**, not a second library and not a `core.py` rewrite. Swap units: **geometry/LUT, icons, arrows, font**. Exp14 today: `geometry.py` + `_constants.py` (WIDTH/HEIGHT), `icons.py` (ICONS **and** ARROWS in one file — arrows are a distinct named set, `ARROW_NAMES` / `ARROWS`), `font_free_mono_8/` plus `_FONT_PATH` in `core.py`. Keep `core.py` / `bitmap_codec.py` geometry-agnostic except those thin hooks. Whether arrows get their own file is shape — leave open; they must remain independently replaceable.
- **Display library hardware scope (locked 2026-09-04):** WS2812 / NeoPixel matrices only; **square**; max 8 LEDs on a side. Realistic sizes: **5×5** (BPI-Bit-S2 onboard) and **8×8** (later RP2350). Charlieplexed matrices (row/column multiplexed grids — stock micro:bit, Exp15 remnant) are **out of scope**. Column-major byte encoding (`_MAX_HEIGHT_PER_COLUMN_BYTE = 8`) matches this cap; do not design for 4×4/6×6/7×7 as first-class targets even if `WIDTH==HEIGHT` parameterization would allow them.
- Scaffolding = per-experiment `.vscode/`. Do **not** rewrite shared workspace CircuitPythonSync (still YD-RP2040 / CP 10.1.3).
- **Student-facing APIs** (the ones a LightTower CircuitPython sketch would call) should stay mostly stable across a later switch to an RP2350 + 8×8 matrix. Library internals may change; **constructor parameters and config** may change in student code and in the library. Handler / state-machine / display-sequence rewrites are the thing to avoid. Analysis + guidelines: `design/student-api-portability.md` (revisit, do not freeze). **Verdict: realistic** for display+buttons; motor/light deferred to a semantic API when those phases exist. PoC stays pragmatic — anticipate, don't over-build a Hardware Abstraction Layer [HAL] (a generic hide-the-board interface covering every peripheral).
- **Reflection + learning extraction is a standing constraint** at every planning and execution stage: `plan/reflection-cadence.md`. Silence at a checkpoint is the failure mode.
- **Plan-refinement loop (locked 2026-09-04, not started):** cap **8** iterations (`v0.8` max → `plan_v1.0.md`); agent may start the loop on own judgement after digests; sub-agents authorized. Location/naming: `plan/loop-setup.md`. Corpus digest (lean-context + pointers) goes *inside* the plan when drafted — not this turn.

## Approach locks (Alex, 2026-09-04 question round)

- **Overnight success bar:** host tests + libraries on disk. On-device is a later human window (physical reset OK then). Do not block overnight on a missing/wedged board.
- **Buttons:** student API names **A/B/C/D**. Overnight smoke: PlanetX **C/D only**. Onboard A/B exist on the constructor/API; not required for overnight. **C/D names:** CP 10.3.0 `pins.c` maps `board.IO13`/`IO14` → GPIO36/37 = goldfinger P13/P14 (photoresistors are `LUM1`/`LUM2`). Overnight still fake FALL. Physical PlanetX cable unverified until P8.
- **Font:** research during digests; recommendation in the plan. **Do not lock a glyph source.** **License (2026-09-04, restated same day):** hobby + vendor-with-notice in this public repo. Copyleft **combined into `lib/`** needs a written case on that candidate — not a coarse “GPLv3 files are banned.” Collection items outside `lib/` are a separate analysis. DAL `pendolino3` (MIT) is the low-friction default; pitchfork-5x5 (GPLv3) stays a candidate until the combination analysis is written.
- **Exp14 `lib/display/` copy:** during digest collection, so the later plan points at the real Exp16 tree. New files in Exp16 (not a delete).
- **Exp14 algorithms (2026-09-04):** keep reviewed/optimized designs (`_write_pattern_on_the_fly` and siblings); localized edits only; do not strip comments. Style SoT = Exp14 `lib/display/`. Plan § Exp14 engine.

## Recommended button backend (provisional until on-device)

BPI-Bit-S2 CP **10.3.0** support matrix includes `_asyncio`, `keypad.Keys`, frozen `neopixel`. User-facing `asyncio` is a **bundle** library (`circup install asyncio` + `adafruit_ticks`), not the host CPython stdlib and not frozen. Public API can follow `Notes/Button_chat.md`. Internals: `keypad.Keys` → dispatcher → asyncio pump. On-device `help("modules")` still P8.

## Constraints

- PoC, not production; library-level code upgradable with moderate effort. TODOs in code for future work; git for history; `ai-notes/` for reasoning.
- Stock CircuitPython **10.3.0** `bpi_bit_s2` on the **board**. **Host (Mac/Cursor) interpreter:** `/Users/alex/Development/PythonVEs/CircuitPython_3.13_VsCode` = **CPython 3.13 Miniconda** (folder name is not the language). Pytest and host scripts only. Blinka imports in that venv are not CircuitPython. MicroPython docs/APIs are not CircuitPython until the CircuitPython tree says so (K1 = P8).
- **Host `mpy-cross` (2026-09-04):** Adafruit CircuitPython binary `…/bin/mpy-cross` → `mpy-cross-macos-10.3.0-arm64` (S3 `bin/mpy-cross/macos/`, **not** PyPI `mpy-cross` which is MicroPython). Reports `CircuitPython 10.3.0 … emitting mpy v6.3`. Uninstall: remove those two names under `bin/`.
- **Host `circuitpython-stubs` (2026-09-04):** 10.0.3 → **10.3.0** (PEP 561 `.pyi` only; Blinka `keypad.py` unchanged). Types for the IDE, not MCU proof.
- No working-setup mutation without explicit yes. Max 5 agent scripts, spec + uninstall in this folder.
- **Destructive ops** (delete / overwrite / history rewrite / force-push / drop backups): Core Principle *Destructive-action hard gate* — see the banner at the top of this file. Corpus: `/Users/alex/Git/rnd-ai-skills/generalized-agent-learnings/destructive-operations.md`. Silence is not consent. Ledger empty as of 2026-09-04.
- Human testing is rare and strategic. Board stuck → physical reset is OK.

## Third-party in-tree (public-repo)

- `Notes/bpi_bit_v2_goldfinger.jpg` — BananaPi docs goldfinger pinout, **unmodified**. License: CC BY-SA as declared on https://docs.banana-pi.org/en/BPI-Bit-S2/BananaPi_BPI-Bit-S2 (footer does not print a version). Sidecar: `Notes/bpi_bit_v2_goldfinger.jpg.license`. Allowed in a public repo as a collection item; ShareAlike does **not** infect the rest of the tree. Do not treat any repo-root LICENSE as covering this file.

## LUT (from Exp09, not yet on-device in this project)

Logical (column, row), origin top-left, micro:bit convention → strip index `row + 20 - column * 5`. Brightness cap 0.20 (Exp09 used 0.10).

## Pictograms

Exp09 `lib/microbit.py` already has the standard micro:bit `Image.*` set (HEART, HAPPY, SAD, clocks, arrows, animals, …). Port/adapt into Exp14 `icons.py` column-major format at 5×5, not the 8×8 Exp14 set.

## Font

Target: MakeCode 5×5 compromise (legible at 5 rows). Exp14 FreeMono-at-8px is known-illegible (`concepts/fonts.md`). Glyph **source** not locked. **License (restated 2026-09-04):** hobby + vendor-with-notice; copyleft into `lib/` only after a written case. Recommended default: DAL `pendolino3` (**MIT**). Pitchfork-5x5 is promising but GPLv3-combination must be analyzed, not auto-rejected.
