# Context — circuitpython-exp16-planetx

**Family**: `circuitpython` · **Status:** P6 host-green (149 pytest); round-1 device window open — K2 (buttons) evidence-supported, K1 (bundle asyncio via this project's own Tier-2 API) unverified; local `lib/` staging **confirmed complete** (Session 17, fresh re-check); Stage-0 `code.py` (Tier 1 only) drafted locally, **not yet deployed** — waiting on Alex to mirror + run · **next = Alex mirrors lib/+code.py to board, run Stage 0, report back; then progress the 4-stage plan toward K1** · Session 18 (2026-09-11) ran a retrospective plan-refinement-loop on the Session 16→17 handoff prompt — no exp16-technical change, see `SESSION_LOG.md` Session 18 + `ai-persona/ai-notes/handoff-prompt-refinement-2026-09-11/RETROSPECTIVE_v1.0.md` · **Repo folder**: `/Users/alex/Development/VsCode/CircuitPython/2026-09_Exp16_BPI-Bit-S2_CircuitPy_PlanetX/` · **Goal note**: `Notes/overall_goal.md`.

## Scope & goal

Prove a CircuitPython stack on the **BPI-Bit-S2** (ESP32-S2, micro:bit form factor, onboard 5×5 WS2812) can run the **LightTower challenge** as a PoC. Stack to build; LightTower is the demonstration, not production firmware. Library-level code should be upgradable to production with moderate effort.

**First major milestone (interim):**
1. Async LED-matrix library — fork Exp14 `lib/display/` onto 5×5 (brightness cap 20%). **Hardware scope (locked):** square WS2812 / NeoPixel only, max 8 on a side; realistic sizes **5×5** and **8×8**. Charlieplexed matrices out of scope. **5×5 ↔ 8×8 via file replacement and/or localized edits**: geometry/LUT, icons, arrows, font. Not a second library. Exp14: arrows live in `icons.py` beside icons; font is `font_*/` + `_FONT_PATH` in `core.py`.
2. Async button library — PlanetX C/D (+ board A/B later for LightTower).

**Portability (design goal, not a Hardware Abstraction Layer [HAL]):** student-facing LightTower **operations** should survive a later RP2350+8×8 switch. Constructor parameters and config may change in student code and in the library. Spec: exp16 `Notes/student-api-portability.md`. Realistic for display+buttons now; motor/light later as semantic APIs.

**End demonstration:** `/Users/alex/Development/Isana/LightTower-challenge` requirements (`2026-05-15_lighthouse-keeper_requirements_v1.0.md`). Needs more than LED+buttons (servo sweep, light sensor) — later.

## Constraints (Alex, 2026-09-03)

- Experiments human-conducted; agent writes software. Overnight independent iteration is the aim; physical reset of a stuck board is acceptable.
- Host Python: `/Users/alex/Development/PythonVEs/CircuitPython_3.13_VsCode` (Mac/Cursor; pytest).
- Focus: **asynchronous** programming.
- Do not change Alex's working setup without explicit permission. Workspace-level CircuitPythonSync currently still points at Exp14's YD-RP2040 / 10.1.3 — override per-experiment, do not rewrite the shared workspace settings without asking.
- **Destructive ops hard gate** (persona-wide, Exp16 reminder): never delete/overwrite/rewrite-history without a ledger grant. Protocol: `/Users/alex/Git/rnd-ai-skills/generalized-agent-learnings/destructive-operations.md`. Ledger: `memory/PERMITTED_DESTRUCTIVE_ACTIONS.md`. Always-on stub: `06-destructive-operations.mdc`. Local reminder banners: exp16 `ai-notes/NOTES.md` + `INDEX.md` (gitignored working store).
- **Standing §4 park (confirmed 2026-09-04):** `…/2026-09_Exp16_…/ai-notes/_parked/` — move here instead of delete. Policy `_parked/README.md`; index `_parked/MANIFEST.md`. Deleting parked copies still gated. Exp16 only.
- Working notes: local gitignored `ai-notes/` in the exp16 folder (untracked 2026-09-08). Durable claims: `Notes/` + this persona folder. Chat stays high-level.
- Coarse git commits on working branches when a chunk is done or enters revision. History of *reasoning* → `ai-notes/`, not git messages alone.

## Entry points (links, not copies)

| What | Path |
|------|------|
| Project README (goal, hardware, tests, deploy) | `…/2026-09_Exp16_…/README.md` |
| Goal / working prefs | `…/2026-09_Exp16_…/Notes/overall_goal.md` |
| Goldfinger pinout (CC BY-SA, unmodified) | `…/Notes/bpi_bit_v2_goldfinger.jpg` + `bpi_bit_v2_goldfinger.jpg.license` |
| Board interface photo (CC BY-SA, unmodified; README eye-catcher) | `…/Notes/bpi_bit_v2_interface_en.jpg` + `bpi_bit_v2_interface_en.jpg.license` |
| Button brainstorm (ChatGPT, micro:bit v2 then RP2350) | `…/Notes/Button_chat.md` |
| Alternate button sketch | `…/CodingTutor/mini-project-scatches/button-library.md` |
| Display library to copy | `…/2026-04_Exp14_…/lib/display/` (`README.md`, `geometry.py`, `_constants.py`, `core.py`, `icons.py`) — **style + algorithm SoT**; Exp16 works on its copy |
| 5×5 LUT / orientation (formula `index = row + 20 - column * 5`) | `…/2026-02_Exp09_…/lib/display_v0.py`, `lib/microbit.py` |
| Micro:bit 5×5 pictograms (already in Exp09 `Image.*`) | `…/2026-02_Exp09_…/lib/microbit.py` (~line 245+) |
| LightTower requirements | `…/Isana/LightTower-challenge/2026-05-15_lighthouse-keeper_requirements_v1.0.md` |
| Portability spec (student operations across 5×5 → 8×8) | `…/2026-09_Exp16_…/Notes/student-api-portability.md` |
| Working notes (local, gitignored) | `…/2026-09_Exp16_…/ai-notes/` (`INDEX.md`, `NOTES.md`, cadence `plan/reflection-cadence.md`) |

## Domain knowledge (central)

- Runtime / allocation → `../../concepts/circuitpython-runtime.md`
- Fonts at small pixel sizes → `../../concepts/fonts.md` (outline fonts fail; 5×5 wants a hand-designed bitmap / MakeCode-style font)
- `led-driving` not yet seeded; Exp09 LUT is the first concrete 5×5 WS2812 mapping

## Resumption point

**2026-09-11 — Session 17: local lib stack re-verified complete; Stage-0 code.py drafted; test plan handed to Alex; no device write yet.**

- Board: **UID `0740D10F1BE9`, CP 10.3.0** (unchanged since Session 14). Still **wiped clean** (only `boot_out.txt`/`settings.toml`/`sd/`, no `lib/`, no `code.py`) as of Session 16 — this session did not touch it (no fresh mount check run; assume unchanged until Alex acts).
- **K2 (PlanetX C/D buttons) is evidence-supported** — do not re-run. **K1 (bundle `asyncio` via this project's own Tier-2 API) is still the load-bearing unknown** — nothing on-device has yet exercised `lib/display/core.py`'s `show_*` methods or `lib/buttons.py`'s `Buttons.run()`; the button-PoC used raw `keypad`+`neopixel` directly, not this project's async layer.
- **Local repo `lib/` — re-verified complete, fresh-eyes, Session 17:** `buttons.py` + `display/` (tracked) + `adafruit_ticks.mpy` + `asyncio/` (untracked, staged via `circup --path`). `circup --path . --board-id bpi_bit_s2 --cpy-version 10.3.0 freeze` shows exactly `adafruit_ticks==1.1.7` + `asyncio==3.1.1`; idempotent re-`install` confirmed no gap. Matches `README.md § Deploy` steps 1-3 exactly. Host pytest re-run fresh: **149 passed** (prior record said 146 — untracked minor drift, not a concern).
- **`code.py.backup` loose end: resolved by disappearance** — no longer exists anywhere in the tree. Separately, the git-tracked `code.py` (button-PoC, commit `b62bc6b`) is deleted from the working tree (`git status`: ` D code.py`) — history + the `ai-notes/` backup snapshot both retain it; not staged/unstaged by the agent, Alex's call if it needs resolving.
- **New Stage-0 `code.py` drafted directly in the local repo this session** (see `SESSION_LOG.md` Session 17 for exact content/rationale) — Tier 1 (sync) only, no `asyncio`, no buttons; isolates the display library's synchronous path before K1 enters. **Proposed, not deployed** — matches `.vscode/cpfiles.txt`'s manifest (`code.py`), so Alex's existing `CP Copy Files to Board` / `sync_files_to_board.py` workflow will pick it up once he reviews and syncs.
- **`.circuitpyignore` does not exist as a real mechanism — corrected, same session.** Verified against the extension's own source + docs (see `../../concepts/tooling.md`); "Copy Libs to Board" copies `lib/` whole-folder, unfiltered, always. Fixed the actual `__pycache__` concern at the source instead: `tests/conftest.py` now sets `sys.dont_write_bytecode = True` (verified: no new `.pyc` writes on a fresh pytest run). Open question for Alex: does he still want a *documentation-only* file (different name) listing dev-only top-level folders, given no tool reads it either way?
- **`readme.txt`** (Alex's empty placeholder) drafted — goal + CP 10.3.0 + bundle libs + public repo URL, small on purpose. Added to `.vscode/cpfiles.txt` so it deploys alongside `code.py`.
- **Standing policy (`../../universal/WORKING_STYLE.md § Domain-Specific`):** local-first, then mirror — no direct-to-board writes by the agent, ever.
- **Next:** Alex reviews the Stage-0 `code.py` + the 4-stage test plan (given in-chat, Session 17), mirrors `lib/` + `code.py` to the board himself, runs Stage 0, reports back what the matrix did — collaborative interpretation, not solo agent analysis. Stages 1-3 (broader Tier 1, then Tier 2 minimal = first real K1 test, then Tier 2 + buttons combined) follow once Stage 0 is confirmed.

**Session 11/15 coverage-discussion reconciliation (older, now moot):** resolved in Session 16 — `0740D10F1BE9` confirmed as the round-1 target.
