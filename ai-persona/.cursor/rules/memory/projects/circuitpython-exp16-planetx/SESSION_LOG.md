# Session Log — circuitpython-exp16-planetx

Per-project session memory for **exp16** (BPI-Bit-S2 CircuitPython + PlanetX, LightTower PoC). Behavioral/process: `../../universal/`. Domain: `../../concepts/`. Roster: `../_INDEX.md`.

## Current state (2026-09-21)

Code at `4a337f4` (2026-09-20, "library cleanup"), plus a 2026-09-21 docstring edit on `code_stage3.py` (behavior only; run status stays in this file, `CONTEXT.md`, `CONCLUSIONS.md`, and the experiment `README.md`). Host pytest **178 passed** (2026-09-21, from `tests/`). Board anchor: UID `0740D10F1BE9`, CircuitPython 10.3.0.

| Work item | End state | Still open |
|-----------|-----------|------------|
| Stages 0–2 steps 1–10, original Stage 3 | Confirmed on-device 2026-09-11…13. K1/K2/K3 for that code. | — |
| Font spacing | Live `show_string` uses `SpacedGlyphColumnFeeder`. Always one spacer between characters; unknown → tofu; space = 3 columns. | Phase 5: Alex looks at `"STAGE2"` / `"42"` / `"!!"` on the matrix. `code_stage2.py` step 11's duration formula still assumes `WIDTH` columns/glyph. |
| Button API | `OnboardButtons().button_a.on_pressed(...)`; `PlanetXButtonSensor(port=J3).button_c.on_pressed(...)`. `ButtonPair` removed. | Re-run `code_stage3.py`. The 2026-09-13 confirm used `Buttons` / `on_*_pressed`. |
| Rotation during scroll | Steps 11/12 drafted in `code_stage2.py`. | Not run on-device. |
| LightTower extras | Nezha V2 I2C decoded (`concepts/nezha.md`). J1–J4 + shared I2C in `planetx.ports`. | No light-sensor driver, no motor driver. |

## 2026-09-21 — Icons catalog: generate the class body

Follow-up on the completion research the same day. Preferred fix, not coded: a host generator writes `class Icons` / `class Arrows` assignments into `core.py` (slices of `ICONS` / `ARROWS`), replacing `_build_image_namespace`. Checker and board then share one class. A `TYPE_CHECKING`-only twin is the fallback if generation is rejected; generating that twin is not. AST test against `ICON_NAMES` / `ARROW_NAMES`; do not import `core.py` on the host. Detail: `ai-persona/ai-notes/circuitpython-syntax-completion/04-experimental-guidelines.md` § Recommended shape.

## 2026-09-21 — Cursor syntax completion (research only; library unchanged)

Student member-completion is Cursor Pyright, not Tab and not Pylance. Exp16 `Icons` / `Arrows` are `type()` + `setattr` (`core.py`), so `HEART` is not a static member (40 icons, 8 arrows). `Display` methods and `button_a` are class-body and should list once `lib/` is on `cursorpyright.analysis.extraPaths` — it is not, in the open workspace. Editor stubs are **10.1.3**; board is **10.3.0**. Popup not looked at. Checks: `concepts/tooling.md` *Cursor syntax completion*; protocol in `ai-persona/ai-notes/circuitpython-syntax-completion/04-experimental-guidelines.md` (may vanish). Do not edit the workspace unless asked.

## 2026-09-20 chats reviewed 2026-09-21

Left without a closing note: [PlanetX ports + button call shape](1523f597-a613-4af8-95a8-110ab722fd63). Its result is the Button API row above (student docs on `ports.py` / `button.py` / `buttons.py`; `ButtonPair` dropped; handlers are `button_a` / `button_c`, not `on_a_pressed`).

Already reflected before this pass: [font cutover](c84a0971-ed6a-4eac-8b20-5f7cc17cfa72), [text_layout template](16d2d15b-bc9b-41da-842e-c1798c9377a8), [week-break resumption](fb52651f-626f-4197-bc94-ea557131643d). [Vendor-repo chat](f35cd208-fda8-46d5-b1d7-379393e4660f) closed 2026-09-14 (vendor block below); its last turn only explained the filename `planetx-vs-lib.md`. [Button-split chat](908cb757-dd37-4617-93da-f030849dea74) is the 2026-09-13…14 arc below; [shorter parallel](939c0867-beb0-40bf-a906-64c962757171) added no later result. Skill-catalog chat is `projects/ai-tooling/SESSION_LOG.md` (2026-09-20), not Exp16.

## Completed work — compacted 2026-09-21

Procedural session notes for finished items are collapsed to start, end, result, and the challenges that still matter. Full prose before this compaction is git-recoverable at `4a337f4`. Sessions 1–9 were already thinned 2026-09-15 (block below).

### On-device stages 0–3 (started 2026-09-11, confirmed 2026-09-13)

- **Start:** local `lib/` ready; board wiped of this project's code; K1 (bundle `asyncio` through this display API) and the async button pump unproven on hardware. K2 (PlanetX C/D via raw `keypad`) already held.
- **End:** Alex confirmed Stages 0, 1, 2 (10 steps), and 3 on UID `0740D10F1BE9`. Frozen siblings `code_stage0.py` … `code_stage2.py`. Per-stage scripts stay; `.vscode/cpfiles.txt` switches which one deploys. No unified all-stages script.
- **Result:** LUT origin top-left; Tier-1 sync path; Tier-2 `show_*` + cancellation; `Buttons.run()` concurrent with an animation, including onboard A/B. Findings in `CONCLUSIONS.md`.
- **Challenges:** a one-shot `code.py` had already fallen through to the REPL before serial capture started — scripts loop. Brightness floor measured 0.01 off / 0.02 lit (`BRIGHTNESS` default stays 0.20). `YELLOW` looks warm-orange and `ORANGE` looks red (still open). `asyncio.sleep(0)` in the button pump busy-spins when it is the only ready task — poll is 10 ms (`concepts/circuitpython-runtime.md`). `__slots__` is inert on CircuitPython. Host pytest must be run from `tests/` (`code.py` shadows stdlib `code`).

### Font spacing (started 2026-09-11, host cutover 2026-09-20)

- **Start:** `"STAGE2"` and `"42"` merged on the matrix. Every glyph was a fixed 5 columns; only some glyphs had a blank right column. Lancaster DAL inserts one spacer column; this port did not.
- **End:** Phases 1–3 (2026-09-13) built a parallel path from pinned DAL commit `b60953b…` (475/475 match to `_COLUMN_MAJOR`). Phase 4 (2026-09-20) switched live `show_string` to `SpacedGlyphColumnFeeder` and removed `_GlyphColumnFeeder`. Generator template: `scripts/templates/spaced_glyphs.py.in`.
- **Result:** always one spacer between characters; unknown glyphs draw tofu (stripped `icons.SMALL_SQUARE`, `0e 0a 0e`); space is 3 authored blank columns; `glyph_ink` returns `bytes` only. `☐` is not in ASCII 32–126. Interior `"A B"` stays a 5-column gap.
- **Challenges:** the converged design (`ai-notes/design/font-inter-glyph-spacing.md` §14: conditional spacer, `needs_spacer`, space width 4) was **not** what shipped. Alex replaced it on 2026-09-20 with tofu + an always-on spacer + space width 3. An interned `_INK` tuple built to avoid a slice was rejected (GC-managed; see `MONITORING.md`). `code_stage2.py` step 11 still times a scroll as if each glyph were `WIDTH` columns.

### Button library (started 2026-09-13, call shape closed 2026-09-20)

- **Start:** one `Buttons` class, handlers `on_a_pressed` … `on_d_pressed`, PlanetX assumed present.
- **End:** `PushButtonBase` holds handlers and has no `run()`. `Button` is one pin. `OnboardButtons` and `PlanetXButtonSensor` each own their two switches (`button_a`/`button_b`, `button_c`/`button_d`). `ButtonPair` was removed on 2026-09-20 — duplicated pair code, fewer types. PlanetX construction is `port=J3` or `c_pin`+`d_pin`. Student wording for ports: Nezha2 sockets, micro:bit edge-connector P-numbers, BananaPi "goldfinger" for this board's connector. J1–J4 are not on the BPI-Bit-S2 itself.
- **Result:** host tests cover the property API. `code_stage3.py` registers `ab.button_a.on_pressed` / `px.button_c.on_pressed`.
- **Challenges:** `keypad.Keys` must be kept alive by the owner; `EventQueue` does not (`concepts/circuitpython-runtime.md`). A no-arg `Button()` used to look constructed and fail only at `run()` — it now raises. The on-device K3 confirm predates this call shape.

### Deploy tooling (2026-09-12 … 2026-09-13) — done

- **Start:** extension "Copy Libs" copies `lib/` unfiltered; "Copy Files" only works for workspace folder 0.
- **End:** `scripts/sync_lib_to_board.py` + `scripts/sync_files_to_board.py`, Cursor tasks pinned to `python.defaultInterpreterPath`. Active workspace file is `~/Development/Cursor Workspaces/circuitpython.code-workspace`.
- **Result:** bracketed repro exonerated the toolchain after a lib-wipe (`CONCLUSIONS.md`; cause of the wipe still unproven).
- **Challenge:** a trailing `# comment` on a `cpfiles.txt` mapping became part of the board filename. Comments sit on their own line. `concepts/tooling.md`.

### Vendor sources (2026-09-14) — notes, not a port

- **Start:** ElecFreaks and BananaPi repos might carry display/button/motor logic onto this board.
- **End:** local `source.txt`-pinned trees under `ai-notes/Elecfreaks-Repos/`; schematic is BPI-STEAM `BPI-BIT-Lite-V0.2.pdf`. Durable facts in `concepts/led-driving.md`, `concepts/fonts.md`, `concepts/nezha.md`, `CONCLUSIONS.md`.
- **Result:** 5×5 strip **index** matches the original bpi:bit; GPIO does not. BananaPi `CharData` is not DAL `pendolino3`. PlanetX light is analog J1/J2 only. Do not import those trees.
- **Challenge:** the notes folder is named Elecfreaks but one tree is BPI-STEAM. Compare pinned SHA to GitHub before treating a local tree as current (`WORKING_STYLE.md`).

## Pre-execution planning + early setup — Sessions 1–9 (2026-09-03 … 2026-09-07) — thinned 2026-09-15

> **Compacted to an index.** These pre-PoC planning / handoff / early-setup sessions' durable outcomes all live in `CONTEXT.md` (§ Scope & goal / Constraints / Resumption point), `CONCLUSIONS.md`, and the `concepts/*` files; only the superseded blow-by-blow narrative was removed. Full original prose is recoverable from git history (before the 2026-09-15 lifecycle-iter4 commit).

- **Session 9 (2026-09-07) — persona-less emulation research** persisted to `ai-notes/`: no stock-CP emulator discharges on-device K1/K2; host-pytest stays the oracle. Payload `ai-notes/design/rp2350-emulation-macos.md` + `ai-notes/digests/local-mcu-emulation.md` (different chips, same answer shape). Durable: `CONCLUSIONS.md` Unverified (emulation rows). Commit `aaf38ea` / PR #2.
- **Session 8 (2026-09-04) — README interface JPEG:** added `Notes/bpi_bit_v2_interface_en.jpg` (CC BY-SA, unmodified) + `.license` sidecar; README caption uses `<sub>` fine print. Durable: `CONCLUSIONS.md` CC BY-SA row.
- **Session 7 (2026-09-04) — MakeCode icon corrections:** `GHOST` → `0x1E,0x0D,0x1F,0x0D,0x1E`, `LEFT_TRIANGLE` → `0x1F,0x12,0x14,0x18,0x10` (`TRIANGLE` left as Exp09; not in the attachments). Comment↔byte + MakeCode fixtures, 149 pytest green; grep-confirmed no absolute host paths in `lib/`/`tests`. Durable: `CONCLUSIONS.md` (Exp09 GHOST/TRIANGLE_LEFT ≠ MakeCode).
- **Session 6 (2026-09-04) — overnight P1–P6 executed, host-green (146 pytest):** `WIDTH=HEIGHT=5`; BPI-Bit-S2 LUT `py+20-px*5`; Exp09 icons → 5 column bytes; DAL `pendolino3` MIT vendored (table storage, Exp14 PCF algorithm untouched); `PIXEL_PIN=board.NEOPIXEL`, `BRIGHTNESS=0.20`; `lib/buttons.py` fake-EventQueue C/D; mpy-cross 10.3.0 → mpy v6.3. Durable: `CONTEXT.md` (P6 host-green) + `CONCLUSIONS.md`.
- **Sessions 5b–5i (2026-09-04) — plan-lock + setup increments:** font-license bar = *no copyleft combined into `lib/`* (case-by-case; DAL `pendolino3` MIT chosen; pitchfork-5x5 GPLv3 a candidate pending a written combination case); goldfinger JPEG CC BY-SA collection-item OK (sidecar); C/D-pin dispute recorded (Exp09 `IO13`/`IO14` vs official GPIO36/37) — *no silent winner*; host venv = CPython 3.13 Miniconda (Blinka `keypad` ≠ K1 evidence); mpy-cross = Adafruit CP binary, **not** the PyPI MicroPython wheel; overnight P1–P6 kickoff authorized on `alex/display-mvp_5x5`. Durable: `CONCLUSIONS.md` (K1/K2, font/pin rows), `concepts/circuitpython-runtime.md` (asyncio split, mpy-cross), `CODING_PRINCIPLES.md` (cross-runtime lift), `WORKING_STYLE.md` § Domain-Specific.
- **Session 5 (2026-09-04) — digests + plan_v1.0:** `ai-notes/digests/` (4 files) + Exp14 `lib/display/` copied in; plan-refinement converged → `ai-notes/plan/plan_v1.0.md` (+ `risk-register.md`); hard stop, PoC not started.
- **Sessions 1–4 (2026-09-03/04) — kickoff / alignment / handoff:** goal = CircuitPython stack on BPI-Bit-S2 for LightTower; first milestone = async 5×5 display (from Exp14) + async buttons, PoC with library-upgrade path; template + library source = **Exp14**, 5×5 LUT/orientation/pictograms from **Exp09**; **async** (not sync) buttons via `keypad` → dispatch → asyncio pump; hardware scope locked (square WS2812 N≤8; only 5×5/8×8; charlieplex out); 8×8 switch-back also touches font + arrows; portability target = student *operations*, not a pin-free student file; standing §4 park = `ai-notes/_parked/`; destructive-ops banners installed (Session 1 "not named" flag invalidated by Session 2). Durable: `CONTEXT.md` (§ Scope & goal / Constraints), central `SESSION_LOG.md` 2026-09-04.

## Open Questions

- **Phase 5:** on-device re-confirm of spaced text (`"STAGE2"` / `"42"` / `"!!"`). Step 11's elapsed-time check is stale against the new column counts.
- **Re-run `code_stage3.py`** on the `button_a` / `button_c` API. K3's 2026-09-13 confirm does not cover this call shape.
- **`code_stage2.py` steps 11/12** (rotate while a Tier-2 animation is in flight) — drafted, not run.
- LightTower extras (servo, light sensor) — out of first milestone. Next hardware: analog light on J1/J2, then Nezha V2 motor (`concepts/nezha.md`; no driver).
- **Color constants** in `lib/display/_constants.py`: `YELLOW` has an orange tinge; `ORANGE` renders as red. Iterative visual pass, not blocking.
- `show_number` formatting (`decimals` / `scientific`; reject `bool`) — decided 2026-09-12, not implemented. `ai-notes/design/show-number-numeric-types.md`.
- Pitchfork-5x5 into `lib/` — not used (DAL MIT taken). Written GPLv3 combination case only if that path is chosen later.
- ~~Flash to CircuitPython 10.3.0; P7 `.vscode/`; P8 on-device; K2 cable; unified end-to-end script; PlanetX vendor inventory.~~ **Done** 2026-09-11…14. See the completed-work blocks and `CONCLUSIONS.md`.
