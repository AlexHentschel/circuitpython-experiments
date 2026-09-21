# Context — circuitpython-exp16-planetx

**Family**: `circuitpython` · **Repo**: `/Users/alex/Development/VsCode/CircuitPython/2026-09_Exp16_BPI-Bit-S2_CircuitPy_PlanetX/` · **Goal note**: `Notes/overall_goal.md`

**Status digest** — current state is § Resumption point. Completed-session narrative is compacted in `SESSION_LOG.md` (2026-09-21).

- **Headline**: first milestone (async 5×5 display + async buttons) is **confirmed on-device** for the 2026-09-13 code (K1/K2/K3). Code since then (`4a337f4`, 2026-09-20) is host-green (pytest 178) and **not re-run** on the board: spaced `show_string`, and `button_a` / `button_c` registration (`ButtonPair` removed).
- **Open threads**: (a) font Phase 5 — Alex re-confirms `"STAGE2"` / `"42"` / `"!!"`. (b) `code_stage2.py` steps 11/12 not run; step 11's duration formula still assumes `WIDTH` columns/glyph. (c) re-run `code_stage3.py` on the current button API.
- **Board**: UID `0740D10F1BE9`, CircuitPython **10.3.0**. **Brightness floor (authoritative, Alex)**: 0.01 off, 0.02 lowest lit; library default `core.py BRIGHTNESS = 0.20`.

## Scope & goal

Prove a CircuitPython stack on the **BPI-Bit-S2** (ESP32-S2, micro:bit form factor, onboard 5×5 WS2812) can run the **LightTower challenge** as a PoC. Stack to build; LightTower is the demonstration, not production firmware. Library-level code should be upgradable to production with moderate effort.

**First major milestone (interim):**
1. Async LED-matrix library — fork Exp14 `lib/display/` onto 5×5 (brightness cap 20%). **Hardware scope (locked):** square WS2812 / NeoPixel only, max 8 on a side; realistic sizes **5×5** and **8×8**. Charlieplexed matrices out of scope. **5×5 ↔ 8×8 via file replacement and/or localized edits**: geometry/LUT, icons, arrows, font. Not a second library. Exp14: arrows live in `icons.py` beside icons; font is `font_*/` + `_FONT_PATH` in `core.py`.
2. Async button library — onboard A/B (`buttons.OnboardButtons`) and PlanetX C/D (`planetx.PlanetXButtonSensor`).

**Portability (design goal, not a Hardware Abstraction Layer [HAL]):** student-facing LightTower **operations** should survive a later RP2350+8×8 switch. Constructor parameters and config may change in student code and in the library. Spec: exp16 `Notes/student-api-portability.md`. Realistic for display+buttons now; motor/light later as semantic APIs.

**End demonstration:** `/Users/alex/Development/Isana/LightTower-challenge` requirements (`2026-05-15_lighthouse-keeper_requirements_v1.0.md`). Needs more than LED+buttons (servo sweep, light sensor) — later.

## Constraints (Alex, 2026-09-03)

- Experiments human-conducted; agent writes software. Overnight independent iteration is the aim; physical reset of a stuck board is acceptable.
- Host Python: `/Users/alex/Development/PythonVEs/CircuitPython_3.13_VsCode` (Mac/Cursor; pytest).
- Focus: **asynchronous** programming.
- Do not change Alex's working setup without explicit permission. Workspace-level CircuitPythonSync currently still points at Exp14's YD-RP2040 / 10.1.3 — override per-experiment, do not rewrite the shared workspace settings without asking. **Which file is "the shared workspace settings" — corrected 2026-09-13**: the actually-active multi-root workspace for this Cursor session is `~/Development/Cursor Workspaces/circuitpython.code-workspace`, **not** the in-repo `CircuitPy_VSCode.code-workspace` (a separate, similarly-populated-but-not-identical file) — verified via `workspaceStorage`, not assumed by location. See `../../concepts/tooling.md` § *Determining which `.code-workspace` file actually backs a Cursor session*. Re-verify per session if this matters again.
- **Destructive ops hard gate** (persona-wide, Exp16 reminder): never delete/overwrite/rewrite-history without a ledger grant. Protocol: `/Users/alex/Git/rnd-ai-skills/generalized-agent-learnings/destructive-operations.md`. Ledger: `memory/PERMITTED_DESTRUCTIVE_ACTIONS.md`. Always-on stub: `06-destructive-operations.mdc`. Local reminder banners: exp16 `ai-notes/NOTES.md` + `INDEX.md` (gitignored working store).
- **Standing §4 park (confirmed 2026-09-04):** `…/2026-09_Exp16_…/ai-notes/_parked/` — move here instead of delete. Policy `_parked/README.md`; index `_parked/MANIFEST.md`. Deleting parked copies still gated. Exp16 only.
- Working notes: local gitignored `ai-notes/` in the exp16 folder (untracked 2026-09-08). Durable claims: `Notes/` + this persona folder. Chat stays high-level.
- Coarse git commits on working branches when a chunk is done or enters revision. History of *reasoning* → `ai-notes/`, not git messages alone.

## Entry points (links, not copies)

| What | Path |
|------|------|
| Project README (goal, hardware, tests, deploy) | `…/2026-09_Exp16_…/README.md` |
| Goal / working prefs | `…/2026-09_Exp16_…/Notes/overall_goal.md` |
| Goldfinger pinout (CC BY-SA, unmodified) | `…/Notes/bpi_bit_v2_goldfinger.jpg` + `bpi_bit_v2_goldfinger.jpg.license` — silk / marketing; electrical schematic is the next row |
| BPI-Bit-S2 schematic (vendor names **BIT-Lite** / **BIT-V2** / wiki **Bit_Lite**) | Official BananaPi Bit-S2 docs link [BPI-BIT-Lite-Doc `sch/BPI-BIT-Lite-V0.2.pdf`](https://github.com/BPI-STEAM/BPI-BIT-Lite-Doc/blob/main/sch/BPI-BIT-Lite-V0.2.pdf) (repo MIT; README is one line). **This generation (ESP32-S2FN4R2), not** original-bit `BPI-BIT-Hardware`. Title block: `ESP32-S2-BIT Lite` / `BPi-Webduino-Bit`; KiCad `BPI-BIT-Lite-ESP32-S2.sch` + `Sensor.sch`; 25× WS2812B, BTN-A/B, LUM, buzzer, USB-C, goldfinger `BIT-P0`…`P20`. File renamed from `BPI-BIT-V2-V0.2.pdf` (commit `775cf99`, 2022-08-02). Pin-level SoT remains CP `pins.c` + goldfinger JPEG until a schematic net is independently decoded. **Local alternate (may vanish, no `source.txt`):** exp16 `ai-notes/BPI-Bit-S2_Hardware/BPI-BIT-Lite-V0.2.pdf` — blob `ea1335e` size **183103** bytes; last checked **2026-09-14** matches `main`. How-to-check: `GET /repos/BPI-STEAM/BPI-BIT-Lite-Doc/contents/sch/BPI-BIT-Lite-V0.2.pdf` size/sha vs local file; if different, notify Alex (do not silently replace). |
| Board interface photo (CC BY-SA, unmodified; README eye-catcher) | `…/Notes/bpi_bit_v2_interface_en.jpg` + `bpi_bit_v2_interface_en.jpg.license` |
| Button brainstorm (ChatGPT, micro:bit v2 then RP2350) | `…/Notes/Button_chat.md` |
| Alternate button sketch | `…/CodingTutor/mini-project-scatches/button-library.md` |
| Display library to copy | `…/2026-04_Exp14_…/lib/display/` (`README.md`, `geometry.py`, `_constants.py`, `core.py`, `icons.py`) — **style + algorithm SoT**; Exp16 works on its copy |
| 5×5 LUT / orientation (formula `index = row + 20 - column * 5`) | `…/2026-02_Exp09_…/lib/display_v0.py`, `lib/microbit.py` |
| Micro:bit 5×5 pictograms (already in Exp09 `Image.*`) | `…/2026-02_Exp09_…/lib/microbit.py` (~line 245+) |
| LightTower requirements | `…/Isana/LightTower-challenge/2026-05-15_lighthouse-keeper_requirements_v1.0.md` |
| Portability spec (student operations across 5×5 → 8×8) | `…/2026-09_Exp16_…/Notes/student-api-portability.md` |
| ElecFreaks PlanetX / Nezha protocol sources (MicroPython + MakeCode; not CPy) | exp16 `README.md` § *ElecFreaks PlanetX / Nezha — protocol sources* — `PlanetX_MicroPython`, `EF_Produce_MicroPython`, `pxt-PlanetX`, `pxt-nezha2`. **Local snapshot (gitignored, may vanish):** next row. |
| BPI-STEAM predecessor (original **bpi:bit** ESP32 / Webduino) — not CPy, not Bit-S2 pin-compatible | **`../../concepts/led-driving.md`** (shared 5×5 index vs GPIO trap); `../../crossref/BY_TOPIC.md` row *BPI-STEAM predecessor*. Repos: [BPI-BIT-Hardware](https://github.com/BPI-STEAM/BPI-BIT-Hardware), [MicroPython-Samples](https://github.com/BPI-STEAM/MicroPython-Samples) (`microbit/display.py`; do not treat `01.leds/heartbeat.py` as matrix), [BPI-BIT-Webduino](https://github.com/BPI-STEAM/BPI-BIT-Webduino) (firmware hub), [webbit_i18n](https://github.com/BPI-STEAM/webbit_i18n) (`blockly/samples/en/bit-s-02.jpg` = 5×5 heartbeat Blockly demo). **Local `MicroPython-Samples`:** next row. |
| Local vendor snapshots (`source.txt`-pinned) | exp16 `ai-notes/Elecfreaks-Repos/<folder>/` — **GitHub remains canonical**; local is an offline alternate. Folder name is a misnomer: one of three trees is BPI-STEAM, not ElecFreaks. **Not present locally:** `pxt-PlanetX`, `pxt-nezha2`, `BPI-BIT-Hardware`, `BPI-BIT-Webduino`, `webbit_i18n`. **Freshness:** before using a local tree, compare `source.txt` SHA to GitHub default-branch HEAD; if they differ, **notify Alex** (do not silently refresh). Expected stale window: months. Last checked **2026-09-14** — all three matched `master`. Pins: `PlanetX_MicroPython` `268740c` (elecfreaks, 2025-06-07); `EF_Produce_MicroPython` `c0b3a53` (elecfreaks, 2026-03-13); `MicroPython-Samples` `c03ed50` (BPI-STEAM, 2019-09-03). How-to-check: `GET /repos/{owner}/{repo}/commits/master` vs the SHA in that folder's `source.txt`. |
| Vendor-vs-Exp16 unpack (display.py, PlanetX modules) | exp16 `ai-notes/vendor-sources/` (gitignored, may vanish) — start `INDEX.md`. Durable one-liners: `concepts/fonts.md` (BananaPi `CharData` ≠ DAL); CONCLUSIONS light-sensor jack constraint. Not a `lib/` port. |
| Nezha V2 motor I2C (durable) | **`../../concepts/nezha.md`** — opcode table + MP-vs-MakeCode disputes. Unpack (gitignored): `ai-notes/digests/nezha-v2-motor-protocol.md` |
| Working notes (local, gitignored) | `…/2026-09_Exp16_…/ai-notes/` (`INDEX.md`, `NOTES.md`, cadence `plan/reflection-cadence.md`) |
| Cursor syntax completion (firmware / bundle / own `lib/`; `Icons` pattern) | Durable: `../../concepts/tooling.md` concept *Cursor syntax completion*. Unpack (may vanish): `ai-persona/ai-notes/circuitpython-syntax-completion/NOTES.md` |
| Frozen on-device test milestones (not copied to board) | `…/2026-09_Exp16_…/code_stage0.py` (Stage 0, `b99152b`); live program is `code.py` |
| Stage 3 test script (current `button_a` / `button_c` API; 2026-09-13 on-device confirm was the earlier `Buttons` / `on_*_pressed` shape — re-run pending) | `…/2026-09_Exp16_…/code_stage3.py` — `from buttons import OnboardButtons` + `from planetx import PlanetXButtonSensor` + `gather` of three tasks |
| Deploy-to-board scripts (human-run; agent never writes to the board) | `…/2026-09_Exp16_…/scripts/sync_files_to_board.py` (manifest files: `.vscode/cpfiles.txt` → board `code.py` etc.) + `…/2026-09_Exp16_…/scripts/sync_lib_to_board.py` (filtered `lib/` sync — excludes `__pycache__`/`.DS_Store`/`README.md`/`*.pyc`, mtime-aware; replaces the extension's unfiltered "CP Copy Libs to Board", see `../../concepts/tooling.md`). Lib script **validated on-device 2026-09-13** (bracketed-repro S1: 19/19 files byte-identical, excludes proven) and committed (`7ae8157`, together with the `README.md § Deploy` script-first recipe). Usage lines live in each script's own docstring. **Runnable via Cursor's Run Task UI, not just a manual terminal** (Session 31, 2026-09-13): `.vscode/tasks.json` has 4 tasks (`Sync Files/Lib to Board` × dry-run/real), all pinned to `${config:python.defaultInterpreterPath}` (not ambient `python3`) — **confirmed working** by Alex. `cpfiles.txt` — never put a comment on the same line as an active `source -> dest` mapping (own line above instead); a trailing inline comment silently corrupts the destination filename, see `../../concepts/tooling.md`. |

**Recorded convention (asked Session 19; re-ask only if policy changes):** park confirmed on-device `code.py` stages as sibling `code_stageN.py`. Replay on the board (optional): comment out the `code.py` manifest line, uncomment `code_stageN.py -> /code.py`, then Copy Files to Board — that overwrites **board** `code.py` only; local `code.py` stays as-is.

## Domain knowledge (central)

- Runtime / allocation → `../../concepts/circuitpython-runtime.md`
- Fonts at small pixel sizes → `../../concepts/fonts.md` (outline fonts fail; 5×5 wants a hand-designed bitmap / MakeCode-style font)
- LED driving (WS2812/NeoPixel output peripheral: RP2→PIO, ESP32→RMT; BananaPi 5×5 index shared, GPIO not) → `../../concepts/led-driving.md`
- Nezha V2 smart motors (I2C `0x10`, 8-byte `FF F9` frame) → `../../concepts/nezha.md` (seeded 2026-09-14; decode evidence-supported, on-device unverified). Unpack: `ai-notes/digests/nezha-v2-motor-protocol.md` (may vanish)

## Resumption point

**2026-09-21 — notes aligned with code `4a337f4` (2026-09-20).** Host pytest **178 passed**.

**Confirmed on UID `0740D10F1BE9` (CP 10.3.0):** Stages 0–2 steps 1–10 and the original Stage 3. Brightness floor 0.01 off / 0.02 lit; library `BRIGHTNESS = 0.20`.

**On the host since that confirmation, not re-run on the board:**

- `show_string` uses `SpacedGlyphColumnFeeder` / `glyph_ink`: one spacer between characters, unknown glyphs draw tofu (`_TOFU_INK`), space is 3 blank columns.
- Buttons: `OnboardButtons().button_a.on_pressed(...)` and `PlanetXButtonSensor(port=J3).button_c.on_pressed(...)`. `ButtonPair` is gone. `code_stage3.py` matches this.
- `code_stage2.py` steps 11/12 (rotate during an in-flight animation) are drafted only. Step 11's elapsed-time formula still assumes `WIDTH` columns per glyph.

**Next hardware:** analog light on Nezha2 J1/J2, then Nezha V2 motor (`concepts/nezha.md`; no driver). Color-constant tuning and `show_number` formatting stay deferred.

Detail, including 2026-09-20 chat coverage: `SESSION_LOG.md`. Blow-by-blow before the 2026-09-21 compaction is in git at `4a337f4`.
