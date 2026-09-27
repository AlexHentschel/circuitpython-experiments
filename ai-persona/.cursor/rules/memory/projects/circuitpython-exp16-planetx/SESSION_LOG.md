# Session Log — circuitpython-exp16-planetx

Per-project session memory for **exp16** (BPI-Bit-S2 CircuitPython + PlanetX, LightTower PoC). Behavioral/process: `../../universal/`. Domain: `../../concepts/`. Roster: `../_INDEX.md`.

## Current state (2026-09-26)

Code post-`4a337f4`, plus 2026-09-25/26 work: `Icon`/`Emojis` rename, `show_leds`→`show_pattern`, `Token`-based Tier 2 cancellation, and `Display` instance-ownership (see 2026-09-26 entry below) — none yet committed/tagged, none yet re-run on-device. Host pytest **178 passed** throughout (run from `tests/`, not repo root). Board anchor: UID `0740D10F1BE9`, CircuitPython 10.3.0.

| Work item | End state | Still open |
|-----------|-----------|------------|
| Stages 0–2 steps 1–10, original Stage 3 | Confirmed on-device 2026-09-11…13. K1/K2/K3 for that code. | — |
| Font spacing | Live `show_string` uses `SpacedGlyphColumnFeeder`. Always one spacer between characters; unknown → tofu; space = 3 columns. | Phase 5: Alex looks at `"STAGE2"` / `"42"` / `"!!"` on the matrix. `code_stage2.py` step 11's duration formula still assumes `WIDTH` columns/glyph. |
| Button API | `OnboardButtons().button_a.on_pressed(...)`; `PlanetXButtonSensor(port=J3).button_c.on_pressed(...)`. `ButtonPair` removed. | Re-run `code_stage3.py`. The 2026-09-13 confirm used `Buttons` / `on_*_pressed`. |
| Rotation during scroll | Steps 11/12 drafted in `code_stage2.py`. | Not run on-device. |
| LightTower extras | Nezha V2 I2C decoded (`concepts/nezha.md`). J1–J4 + shared I2C in `planetx.ports`. | No light-sensor driver, no motor driver. |

## 2026-09-26 — typos in `lib/display/core.py`

Spelling only: `benefical` → `beneficial`, `compltes` → `completes`, `ouside` → `outside`, `tailing newline` → `trailing` (both pattern-parser comments), and "is alias of" → "is an alias of". `show_image` / `scroll_image` docstrings still say ``img`` after the parameter rename to `image`.

## 2026-09-25 — `render_icon` / `show_icon` gained `offset` before `color`

`offset` is the source column passed to `_render_colmajor`, which indexes `data[offset + x]` for `x` in `0..WIDTH-1` with no clip. Catalog icons are `WIDTH` bytes, so only `0` is in range; a wider mono image can start later. Callers that passed a color as the second positional (`code.py`, `code_stage0.py`, `code_stage1.py`, `code_stage2.py` `show_icon`) now pass `color=`. `render_arrow` / `show_arrow` stay at source column 0. README signatures updated.

## 2026-09-25 — `scroll_image` tail frame renders the overshot `pos`

The post-loop `if pos != max_start + step` matches case (ii) (exit `pos` is `max_start + step - (max_start % step)`). It renders that `pos`, not `max_start`. For `1 <= step <= WIDTH` the last column does appear, with `step - (max_start % step)` blank columns on the right. For `step > WIDTH` the extra frame can start at `offset >= width` (all OFF) and the tail can stay unseen. No cancel check before that render, so a cancel during the preceding sleep still paints it. Flush end would be `_render_window(max_start)`.

## 2026-09-25 — `scroll_image` end bound

`while pos <= max(width - WIDTH, 0)` with `pos += step` is the right end for `step=1`: the last start is `width - WIDTH`, so the last column is in that window. Stage 2's frame count `(max_start // step) + 1` matches, including one `interval_ms` hold after the last paint. When `step` does not divide `width - WIDTH`, starts stay on multiples of `step` and the rightmost columns never enter a window. No host test calls `scroll_image`.

## 2026-09-25 — no test for `from_pattern` empty string

`Image.from_pattern` line `max(..., default=WIDTH)` is the zero-kept-rows path (`""` and whitespace-only). No test calls `from_pattern`. Host suite must not import `display.core` (`tests/test_no_board_core.py`). `glyph_columns("")` / `glyph_ink("")` are the font, not this line.

## 2026-09-25 — deinit acquire cancels the old `Display`'s coroutines

Correction to the re-init note below. `Display.show_*` checks `self._is_cancelled` on the instance that started them. `deinit`'s `self._acquire()` bumps that same `_seq`, and the check sits before the next render after each `await` (`show_string` at the `sleep` resume). A later `Display()` is a different object; the old coroutines do not need its `_seq`. A missed check that then touches `self._pixels is None` raising is acceptable. `Image.scroll_image` looks up the global name `display` on each check. Rebinding that name during its `await asyncio.sleep` points the check at the new object. `_is_cancelled` is `_seq != token`, so the old scroll resumes iff the new object's `_seq` equals the old token (exactly N `_acquire` calls, not ≥ N). Both coroutines then share one generation. `show_image` does not render again after its sleep. `Display.show_*` stays on `self` and is immune. The "first wake sees `_seq == 0`" claim is invalidated.

## 2026-09-25 — `_pixels` as a `Display` field vs re-init

Chat only (code unchanged). Re-init does not require an instance field: `NeoPixel.deinit()` releases the pin, and a later `NeoPixel(...)` can claim it again, if every render reads the current buffer at entry (they already alias `_pixels` per call). A field's cost is one attribute load per frame once cached into a local, plus a guard so a second `Display()` does not double-claim the pin. Multi-display (Image holding its own buffer, `__slots__` growth) is a larger change than same-instance `init()` after `deinit()`. README § Singleton design bundles those two. A new `NeoPixel` starts at `BRIGHTNESS` 0.20.

## 2026-09-25 — `@staticmethod` on `Display.set_brightness` / `set_rotation`

Explained in chat (code unchanged). `Display`'s only instance field is `_seq`. Those two methods write module globals (`_pixels.brightness`, in-place `_LUT`) and skip `_acquire()`, so they do not cancel a Tier 2 animation. The decorator is that fact, not a hot-path optimization — `show()` dominates, and direct `display.method()` calls do not allocate a bound method on CircuitPython's `LOAD_METHOD` path. `get_pixel` also ignores `self` and is left as a normal method. Same pattern in Exp14 `lib/display/core.py`.

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
- ~~**Tier 2 cancellation redesign (Q1–Q5, opened 2026-09-25):** should `Display` Tier 1/Tier 2 methods return status (token / completed-vs-superseded bool) so calling code can chain display operations that cancel together?~~ **Resolved 2026-09-26** — `Token` class implemented, Tier 2 only. See 2026-09-26 entry below + `ai-notes/design/tier2-cancellation-semantics.md` §8/§8.5. New open item from that same work: on-device re-run of any Tier 2 cancellation path (never run on hardware under the `Token` design).
- **New (2026-09-26):** `Display` instance-ownership + `Image`/renderer decoupling from the module-level `display` singleton — implemented, host-verified only. Needs an on-device pass exercising a real second `Display()` after `deinit()`.

## 2026-09-25 — Cancellation semantics re-opened (design only, no code changed)

- Alex reviewed the 2026-09-25 cancellation-fix recommendation (`ai-notes/code-review-2026-09-21/02-cancellation-and-validation.md`) and asked to revisit before implementing, with two specific questions: why does `interval_ms` exist on Tier 2 holds at all, and why would early-return polling need shorter-than-`interval_ms` checks.
- **Resolution, worked through in `ai-notes/design/tier2-cancellation-semantics.md`:** Tier 2 methods split into "hold" (single render then wait — no pixel-correctness need to poll) and "animate" (repeated render — polling is load-bearing, already correct). `interval_ms` on holds is pixel-identical to Tier 1 + a bare `await asyncio.sleep(...)` today (Tier 1 already calls `_acquire()`); its value is API convenience + MakeCode parity, not cancellation. The actual gap is that nothing returns status, so chained Tier 2 calls can't cancel together regardless of polling speed.
- **Self-correction:** the earlier same-day polling recommendation, applied alone, would make the Stage 3 arrow-wipe finding worse (a chained hold would hand off to the next draw sooner, with no way for that next draw to know to skip itself). That section is now marked superseded, pointing to the new design note.
- **Also corrected:** the Stage 3 arrow's visible window was overstated as "one scheduler turn" in `ai-notes/code-review-2026-09-21/04-buttons-and-stage-scripts.md`; `asyncio.sleep` doesn't watch the cancellation token, so the real window is up to one animation frame period (~300 ms in that script). Fixed in that file.
- **Decisions pending (Q1–Q5, not yet answered):** Tier 2 returns bool; Tier 1 returns token; poll-based early return on holds (only after the bool convention lands); fix `code_stage3.py`'s `_display_loop` to use it; naming for a public cancellation-check accessor. No code changed. README gets a brief note only once these are settled (Alex's explicit instruction — ephemeral notes only for now).
- LightTower extras (servo, light sensor) — out of first milestone. Next hardware: analog light on J1/J2, then Nezha V2 motor (`concepts/nezha.md`; no driver).
- **Color constants** in `lib/display/_constants.py`: `YELLOW` has an orange tinge; `ORANGE` renders as red. Iterative visual pass, not blocking.
- `show_number` formatting (`decimals` / `scientific`; reject `bool`) — decided 2026-09-12, not implemented. `ai-notes/design/show-number-numeric-types.md`.
- Pitchfork-5x5 into `lib/` — not used (DAL MIT taken). Written GPLv3 combination case only if that path is chosen later.
- ~~Flash to CircuitPython 10.3.0; P7 `.vscode/`; P8 on-device; K2 cable; unified end-to-end script; PlanetX vendor inventory.~~ **Done** 2026-09-11…14. See the completed-work blocks and `CONCLUSIONS.md`.

## 2026-09-21 — Code review (lib/ + stage scripts; no code changes)

- **Task:** exhaustive bug / edge / performance pass over Exp16 `lib/` and stage scripts. No code changes.
- **Notes** (gitignored, may vanish): experiment `ai-notes/code-review-2026-09-21/NOTES.md`.
- **Highest finding** (cold session can act without the notes): `lib/display/core.py` `_render_ring_window` calls `pixels.show()` inside the column loop (read at line 279 on tree `4a337f4`). Scroll steps latch the strip `WIDTH` times and tear left-to-right. Fit-on-screen text uses `_render_colmajor` and is unaffected.
- **Other claims worth not losing:** ragged `create_image` (max row length, short rows pad); `scroll_image` skips the final window when `step` does not land on `max_start`; `pause` is not token-cancellable; `set_pixel` out of range and `show_string("")` cancel then draw nothing; async button handlers are dropped; Stage 2 step 11's `ROTATE` estimate is 7.2 s vs feeder 7.6 s and still passes the 0.5 s slack; Stage 3 arrow is wiped if the press hits `scroll_image`.
- **How to check:** `git rev-parse HEAD` versus `4a337f4`; re-read line 279 before editing.

## 2026-09-25 — Dedent `_render_ring_window` `show()`

- **Change:** `lib/display/core.py` `_render_ring_window`: `pixels.show()` moved from inside the column loop to after it, same shape as `_render_colmajor`. Alex asked to un-indent that line.
- **Effect:** one scroll step latches the 25-LED strip once, after all five columns are in the RAM buffer. Pre-fix behavior and the 4 ms estimate stay in `CONCLUSIONS.md` § 2026-09-21 and in experiment `ai-notes/code-review-2026-09-21/01-display-hot-path.md`.
- **Not done:** on-device look at `show_string("STAGE2")`. Other 2026-09-21 findings are unchanged.

## 2026-09-26 — Out-of-range `set_pixel` and empty `show_string` no longer cancel

- **Change:** `lib/display/core.py`. `set_pixel` returns before `_acquire()` when `(x, y)` is outside the matrix. `show_string` does `str(text)` and, if that is empty, returns `self._token` before `_acquire()`.
- **Effect:** neither call expires a running scroll's token, so the scroll keeps painting. Empty `show_string` does not clear. `show_pattern("")` still blanks, because the pattern writer fills a full OFF frame.
- **Holds already polled** (not part of this edit): `pause`, `show_pattern` / `show_icon` / `show_arrow` / `show_image`, and `show_string`'s centered hold go through `_sleep_pollable` / `_sleep_until_cancelled` (~50 ms chunks). Scroll frames still use one `asyncio.sleep(interval)` per column, checked on both sides.
- **Re-read later 2026-09-25** (question: is the per-column flush addressed?): yes in source. Line 279 `pixels.show()` is at function-body indent, after `for x`. `show_string` calls `_render_ring_window` once per step (line 935) and then sleeps. `interval_ms=0` still sleeps 0 once per column; each step is one latch of a finished frame.

## 2026-09-26 — Out-of-range `set_pixel` and empty `show_string` cancel again

- **Change:** Alex rejected the no-cancel edit above. Both calls `_acquire()` first, then write nothing when the coordinate is off the matrix or `str(text)` is empty. The previous frame stays on the LEDs. The running animation's token expires.
- **Why:** consistency — a mutating call cancels even when it does not push new pixels. `show_pattern("")` still blanks, because the pattern writer fills OFF.

## 2026-09-26 — `set_pixel` and empty `show_string` each follow one path

- **`set_pixel`:** already acquired first. On-matrix: change that pixel of the current frame and flush. Off-matrix: no write; the most recent frame stays. Tier 2 has stopped in both cases. Docstring and module policy now say that.
- **`show_string("")`:** the early return after `_acquire()` is gone. Zero columns take the fit-on-screen path, so the matrix is replaced by a blank frame and held like any other short string (`interval_ms * WIDTH`, or until cancel when `loop=True`).

## 2026-09-26 — `Image.create` whitespace sentence for a student

- Replaced "a string that `render_pattern` treats as a cell can be a gap here" with: spaces and other invisible characters are skipped, so `#` marks close up; `render_pattern` skips only space, tab, and carriage return, and anything else stays a pixel, off when it is not `#`. Surrounding lines left as Alex had them.

## 2026-09-26 — pattern and `show_number` docs applied

- `Image` class, `Image.create`, and `height`: dropped the `.height != HEIGHT` check. Pad is the contract. `Image.create` / `Icon.create`: every whitespace character is ignored; `Image.create` notes a `render_pattern` cell can be a gap here. `render_pattern`: space, tab, and CR are gaps; other characters are cells. `show_pattern`: same rules as `render_pattern`. `show_number`: `True` and `False` show as those words.

## 2026-09-26 — document parser and `show_number` conventions (recommended, not applied)

- Alex accepts different rendering conventions when the public docstrings say so. Recommend: leave `Image.create` pad-short-rows and the `scroll_image` student text; drop the `.height != HEIGHT` example (height is always `HEIGHT`). Add one sentence on `render_pattern` / `show_pattern` (gaps are space, tab, CR; other characters are cells) and on `Image.create` (every whitespace character is ignored). `show_number` already says `str(n)`; add that `True`/`False` show as those words.

## 2026-09-26 — public `scroll_image` docstring fixed on Alex's edit

- On `Display.scroll_image`: ``img`` → ``image``; ``disp`` paragraph removed (that parameter is only on `Image._scroll_image`); "returns immediately" → returns after the current frame's `interval_ms` sleep. Same sleep sentence on `Image._scroll_image`. Step sentences and the one-line `Raises` left as Alex had them.

## 2026-09-26 — public `scroll_image` docstring: `disp` and "immediately"

- Alex's editor selection of `Display.scroll_image` (~1026) included `Image._scroll_image`'s ``disp`` paragraph and "returns immediately". Not edited this turn. ``disp`` is not a parameter of the public method. A cancel is noticed when the current frame's `asyncio.sleep(interval_ms)` ends. Saved file still has the older "Cancellable:" paragraph at that spot.

## 2026-09-26 — rename `end` in `_scroll_image` (recommended, not applied)

- Alex proposed `image_columns_scrolling_in` for `end = max(0, width - WIDTH)`. Applied `image_columns_to_scroll_in`: the count of image columns that start off the right edge. Comment above the binding says that. The two comment lines below it were left as they were. Same loop: `pos` renamed `columns_scrolled`. Stop when `columns_scrolled >= image_columns_to_scroll_in`.

## 2026-09-26 — keep Alex's "pad with empty columns" sentence

- Alex revised `Image._scroll_image` to "might need to padd with empthy columns after the last image column." A later edit had put the public docstring back to "scroll empty columns in." Spelling fixed in place (`pad`, `empty`). That sentence is now also on `Display.scroll_image` and the last line of the `end` comment. The two sentences above it were left as he had them.

## 2026-09-26 — scroll wording is "image columns scroll in"

- Applied on `Display.scroll_image`, `Image._scroll_image`, and the `end` comment in `lib/display/core.py`. Each frame, `step` image columns scroll in from the right, until the last image column has appeared. A `step` above 1 might also scroll empty columns in after that last column. The lattice formula is off the public docstring.

## 2026-09-26 — `scroll_image` public docstring is for a teenage learner

- Alex rejected the lattice formula in `Display.scroll_image` (lines ~1034–1041) as too intricate. Preferred shape: start at 0; every `interval_ms`, move `step` columns left until every column has been shown; negative `step` unsupported. One extra sentence allowed: `step` above 1 might scroll empty columns in from the right so the last image column still appears.
- That "every column" sentence matches the code when `step` is at most `WIDTH`. A larger `step` skips columns between windows. Proposed text not yet applied. The same lattice paragraph is still on `Image._scroll_image`.

## 2026-09-26 — `scroll_image` stays on the step lattice

- **Change:** `Image._scroll_image` in `lib/display/core.py`. The flush snap (draw `max_start` when `step` missed it) is gone. Offsets are `0, step, 2*step, …` through the first multiple of `step` that is `>= max(0, width - WIDTH)`. Past the image, `_render_window` pads OFF. Token is checked before each paint, including the last.
- **Why:** Alex rejected offsets 0, 2, 4, then 5 as an edge that is not in the common sequence. Width 10, `step` 2 is now 0, 2, 4, 6. `step > WIDTH` still leaves gaps, the same gap a large step leaves mid-image. Directive: `CODING_PRINCIPLES.md` *An edge follows the same formula as the common case*.
- **Also this read:** strict `create_image` is gone. `Image.create` documents the pad. `Image.height` is always `HEIGHT`.

## 2026-09-26 — `scroll_image` snaps to the flush end

- **Change:** `Image._scroll_image` in `lib/display/core.py`. The per-frame loop is untouched. After it, if `pos != max_start + step`, and the token is still current, draw `max_start` (not the stepped-past `pos`) and hold one interval.
- **Effect:** a step that misses the last aligned window still ends with the image's last column on the right edge. A cancel during the previous sleep is not painted over. `step` that already lands on `max_start` pays one compare and no extra frame.

## 2026-09-26 — Re-read of the original half-implemented cancellation claim

- **Verdict:** addressed in current `lib/display/core.py`. Holds (`pause`, `show_pattern` / `show_icon` / `show_arrow` / `show_image`, centered `show_string`) use `_sleep_pollable` or `_sleep_until_cancelled` and return within ~50 ms of a later `_acquire()`. `show_string("")` draws a blank fit-on-screen frame. `set_pixel` off the matrix cancels and leaves the last frame, which is the stated policy, not an accidental freeze.
- **Still true:** a scroll frame uses one `asyncio.sleep(interval_ms)` and notices a cancel at the end of that sleep, not mid-sleep.

## 2026-09-25 — `Icon` class replaces `Image` for the catalog; `ICONS`→`EMOJIS` clean rename (implemented)

Separate design thread from the cancellation-chaining brainstorm above (both touch `core.py`, different classes, no interaction). Alex: "I am slowly tending towards a more self-contained API that is clearer in itself rather than partially mirroring existing APIs," proposed three changes, evaluated in chat, then confirmed and applied same session:

- New `Icon` class (`__slots__ = ("_data",)` — WIDTH×HEIGHT monochrome, no width/multi/color fields at all; not an `Image` subclass). New `create_icon(pattern_str) -> Icon` (mono only, no `color` param; reuses `Image.from_pattern`'s parse path).
- `ICONS`/`ICON_NAMES` → `EMOJIS`/`EMOJI_NAMES` (`icons.py`); `Icons` → `Emojis` (`core.py`); clean rename, no back-compat aliases (Alex: "please apply clean rename" — no external consumers).
- `Emojis`/`Arrows` namespace classes now built as `Icon` instances (`_build_icon_namespace`, was `_build_image_namespace`).
- `render_icon`/`show_icon` lose the `offset` parameter (checked every call site across `code.py`/`code_stage0-3.py`: never passed, always `0`; `Icon`'s fixed `WIDTH` makes any nonzero value an immediate `IndexError` regardless).
- `render_arrow`/`show_arrow` kept as separate public names (not merged into `render_icon`/`show_icon` — `Notes/student-api-portability.md` § G3 locks both as distinct MakeCode-parity operations) but now one-line delegates to `render_icon`/`show_icon`.
- Confirmed multi-color WIDTH×HEIGHT patterns stay `Image` forever (Alex: "yes") — `Icon` never grows a multi-color mode.
- Bonus finding surfaced during evaluation: `.recolor()` on a catalog `Image` was already dead for every real call path (`render_icon`/`show_icon`/`render_arrow`/`show_arrow` always pass `color=` and never read the instance's stored color) — confirmed via grep that `.recolor()` is only ever called on `_big_image` (a `create_big_image` scrollable `Image`), never on a catalog entry. `Icon` having no color field makes that former footgun structurally impossible instead of merely documented (README's old "Sharing hazard" note).

**Files touched:** `lib/display/{icons.py, core.py, __init__.py, bitmap_codec.py, README.md}`, `{code.py, code_stage0-2}.py` (call sites + `code_stage1.py`'s `_ring_image`→`_ring_icon` via `create_icon`), `tests/{test_icons_data.py (~20 refs + 7 test-name renames), test_font_spacing.py, test_pattern_codec.py}`. `code_stage3.py` untouched (only uses `Arrows`, name unchanged). Verified: host `tests/` 178 passed (venv `/Users/alex/Development/PythonVEs/CircuitPython_3.13_VsCode`), `py_compile` clean on every touched file. **Not yet done:** on-device run — `code_stage1.py` step 5 (`create_icon`) has no prior host-test coverage of that specific new function (thin wrapper over the already-tested `Image.from_pattern` mono path, but still first-run-on-hardware).

Supersedes the naming used in the 2026-09-21 "Icons catalog: generate the class body" entry below (`class Icons`/`ICON_NAMES` → would now be `class Emojis`/`EMOJI_NAMES`) — that entry's core recommendation (generate the namespace class body for completion, replacing `type()`+`setattr`) is otherwise unaffected and still open.

Full reasoning + before/after table: `ai-notes/design/icon-class-and-emoji-rename.md`.

## 2026-09-25 — Cancellation-fix recommendation (not applied)

- Alex asked to see the half-implemented cancellation rule and a recommended fix. No code change.
- **Fix, two parts:** (1) `Display._sleep_unless_cancelled(token, total_s, poll_s=0.05)` because `asyncio.sleep` does not watch `_seq`; use it for `pause`, `show_leds` / `show_icon` / `show_arrow` / `show_image` holds, and the non-loop centered `show_string` hold. Capture the token after `render_*`, which already `_acquire()`. (2) `set_pixel` returns before `_acquire` when `(x, y)` is off-matrix; `show_string` does `str(text)` and the empty return before `_acquire`.
- Detail: experiment `ai-notes/code-review-2026-09-21/02-cancellation-and-validation.md` § Recommended fix.

## 2026-09-26 — `Token` cancellation implemented; `Display` instance-ownership; `show_leds`→`show_pattern`

Resolves the Q1–Q5 cancellation-chaining design thread opened 2026-09-25 above, and the separately-tracked "Second `Display()`" review finding.

- **`show_leds` renamed `show_pattern`** (symmetry with `render_pattern`), across `core.py`/README/`code_stage2.py`.
- **`Token` class** (`__slots__ = ("_is_expired",)`, private `_is_expired` + read-only `is_expired` property). `Display._acquire()` expires the previous token in place, mints+stores+returns a new one; `_is_cancelled`/`_seq` removed entirely. Alex's design, chosen over a threaded-continuation alternative (explicit "bare check-after-the-fact" pick) — decision table in `ai-notes/design/tier2-cancellation-semantics.md` §8. Two follow-up refinements same session, both Alex-directed: `is_expired` made externally read-only (property over a public bool), and Tier 1 methods (+ `deinit`) reverted to returning `None` — only Tier 2 methods return `Token`. `show_pattern`/`show_icon` recover the token their internal Tier-1 call's `_acquire()` minted by reading `self._token` immediately after.
- **`Display` instance-ownership** (Alex: "the ability to instantiate a new Display if I called `display.deinit`... without reliance on the static `display` variable"): `Display.__init__` now constructs its own `self._pixels`/`self._lut`/`self._token` instead of reading module globals; constructing `Display()` claims the NeoPixel pin, so a second live instance now raises at construction (hardware-enforced) instead of silently sharing state — this is the fix for the 2026-09-21-review "Second `Display()`" finding, marked resolved in that file. `deinit()` frees the pin so a *new* `Display()` can be constructed independently. `Image._show_image`/`_scroll_image`/`_render_window` take the acting `Display` as an explicit `disp` param (passed as `self` by `Display.show_image`/`scroll_image`) instead of reaching for the module-level `display` name; `_render_colmajor`/`_render_ring_window` take `pixels`/`lut` as explicit params. New design note: `ai-notes/design/display-instance-ownership.md`.
- **Wording correction (Alex, applies going forward — see `CODING_PRINCIPLES.md` new row):** "Avoid wording such as 'this is not X but Y'. Just state what is." Swept every "rather than"/negation-first instance I had introduced *this session* (`core.py`, `README.md`, `geometry.py`, `ai-notes/design/display-instance-ownership.md`) to state the affirmative fact directly. Did not sweep pre-existing prose predating this session, nor `tier2-cancellation-semantics.md`'s alternative-comparison sections (contrast is that document's actual content). **First pass was incomplete**: Alex caught a 4th instance the same shape ("passed in by ... (self), not read from a module global") in `_show_image`'s docstring right after; grepping again with a wider pattern (`not read from`, not just `rather than`) found 2 more siblings I'd missed in `_scroll_image` and `_render_window` — same negation-tail phrasing, same authorship (all three written in the `Image`→`disp`-parameter refactor earlier this session). All 3 fixed same turn. Gap: my grep pattern the first time didn't include "passed in by X, not Y"'s specific phrasing, and I didn't re-check every sibling of an instance I *did* find (`_show_image`/`_scroll_image`/`_render_window` are near-identical triplets — fixing one should have prompted checking its two twins immediately).
- **Verified:** `py_compile` clean; host `tests/` 178 passed throughout (run from `tests/`, not repo root — `code.py` shadows stdlib `code`, breaks `pytest --pdb` import machinery from repo root). Not yet run on-device.

**Follow-up same session — hold-style Tier 2 waits are now cancellation-pollable:** Alex quoted an older code-review finding — `pause`, the single-render holds after `show_pattern`/`show_icon`/`show_arrow`/`show_image`, and `show_string`'s fit-on-screen hold each did one bare `await asyncio.sleep(...)`, so a superseding display operation wasn't noticed until the *full* wait elapsed (only scroll loops already polled per-frame) — and asked for a performance-grounded recommendation, flagging three specific engineering constraints himself: splitting long sleeps into checkable chunks, computing *remaining* time correctly (no naive per-chunk countdown drift), and avoiding pointlessly-frequent short sleeps. Researched against already-verified facts in `concepts/circuitpython-runtime.md` (bundled `asyncio`'s `sleep(t>0)` genuinely blocks via `_io_queue.wait_io_event`, no busy-spin; `sleep()` never allocates per call) — concluded per-wake overhead is negligible on this hardware, so the real question was granularity, not safety; recommended reusing the file's own pre-existing 50 ms precedent (already used in `show_string`'s `loop=True` fit-hold) rather than inventing a new constant. Initial design was one `_sleep_pollable(token, total_s: float | None, poll_s=0.05)` handling both the bounded and "sleep forever" cases via a `None` sentinel. Alex pushed back: split into two functions instead, to avoid the `None` checks. Agreed and implemented `Display._sleep_pollable(token, total_s)` (wall-clock-deadline chunked sleep, converges exactly to `total_s` when not cancelled) and `Display._sleep_until_cancelled(token)` (unbounded poll loop, no deadline math at all) — the split also simplified the unbounded case on its own merits (no `None`-branch inside the loop, no deadline math it never needed). Wired into `pause`, `show_pattern`, `show_icon` (covers `show_arrow`), `Image._show_image` (covers `show_image`), and both branches of `show_string`'s fit-on-screen hold (loop and non-loop); scroll paths untouched (already correct). Docstrings + `README.md` updated to say "waits up to X, returns early if superseded" instead of "waits X". Verified: `py_compile` + `tests/` 178 passed + no lints. **Not yet applied** (explicitly kept separate, per Alex): the `set_pixel`-out-of-range / `show_string("")` bug where `_acquire()` fires before the early-return guard, cancelling a running animation and then drawing nothing — still open, logged 2026-09-25.

**Immediate follow-up, same turn:** Alex caught that `_sleep_pollable`/`_sleep_until_cancelled` were attached to `Display` as methods despite neither body ever touching `self` — inconsistent with the reasoning that justified moving the *render* helpers into `Display` earlier this session (those had a real `self._pixels`/`self._lut` dependency; these have none, they operate only on the `Token` passed in). Moved both to module-level free functions next to the `Token` class; call sites (`pause`, `show_pattern`, `show_icon`, `show_string`×2, `Image._show_image`) changed from `self._method(...)`/`disp._method(...)` to plain `_method(...)`. README updated to match. Verified: `py_compile` + `tests/` 178 passed + no lints. **Pattern worth remembering**: when attaching a helper to a class, check it actually reads that instance's state — don't default to "method" just because a sibling helper in the same refactor pass needed to be one.

**Follow-up same session — redundant `interval_ms > 0` guards removed:** Alex asked to check for redundant range checks on `interval_ms`. Found: `_sleep_pollable(token, total_s)` already no-ops for `total_s <= 0` (returns before any `await asyncio.sleep(...)`, so no event-loop-yield difference either), yet 4 call sites (`_show_image`, `show_pattern`, `show_icon`, `show_string`'s fit-hold branch) wrapped the call in `if interval_ms > 0:` anyway — duplicating a boundary check the callee already made safe. `pause` already had the minimal, non-redundant form (validate sign once, call `_sleep_pollable` unconditionally). Removed the 4 redundant guards to match `pause`'s pattern; also rewrote a stale comment in `show_string` that had justified its guard via "`asyncio.sleep(0)` yields once" — true of a *direct* `asyncio.sleep()` call, no longer true once the call goes through `_sleep_pollable`. No double-`raise ValueError` existed anywhere (each Tier 2 entry point validates the sign exactly once; `show_arrow`/`show_number` delegate to `show_icon`/`show_string` without re-validating, correctly). Verified: `py_compile` + `tests/` 178 passed + no lints.

**Flagged, not fixed (separate concern — a validation *gap*, not a redundancy)**: `show_image`/`Image._show_image` never raise on `interval_ms < 0` (silently treated as "no wait", unlike `show_pattern`/`show_icon`/`show_string`/`pause`, which all raise `ValueError`). `scroll_image`/`Image._scroll_image` never validate `interval_ms` either, and call `asyncio.sleep(interval_seconds)` directly per scroll frame rather than through `_sleep_pollable` — so a negative `interval_ms` there hits raw `asyncio.sleep()` unguarded. Left as-is; only raised because it surfaced during the redundant-check analysis. Open question for Alex: should `show_image`/`scroll_image` validate `interval_ms < 0` the same way the other Tier 2 methods do?

## 2026-09-26 — Stage 2 step 11 estimate and Stage 3 arrow hold (recommended, not applied)

Alex asked whether to fix two script findings from the 2026-09-21 review. Recommendation presented in chat, no file edit.

- **Stage 2 step 11 — applied** in `code_stage2.py` as `_scroll_sleep_s`. Alex's three frame groups (1 empty screen, then `c` text columns, then `WIDTH` empty columns) sum to `(1 + c + WIDTH) × interval_ms`. The message wrote that product as `(1 + c × WIDTH)`; the function uses the sum, which is the sleep count in `show_string`. `"ROTATE"` is 32 feeder columns → 38 frames → 7.6 s at 200 ms. The 0.5 s slack is unchanged. The helper describes the scroll path only; fit-on-screen text holds `interval_ms * WIDTH`.
- **Stage 3:** `scroll_image` now returns a `Token`. When `is_expired`, `await asyncio.sleep(0.8)` on the display task before `show_string`. The handler has already drawn the arrow; `show_string`'s first frame replaces it. A press during `show_string` already lands in the existing 1 s sleep. A second press during the 0.8 s hold redraws the arrow and does not restart the hold.

**Follow-up same session — render helpers moved into `Display`:** `_write_pattern_on_the_fly`/`_render_colmajor`/`_render_ring_window` were module-level free functions taking `pixels`/`lut`/`off` as parameters (decoupled from any specific `Display`, mirroring `Image`'s `disp`-parameter pattern). Grepped all call sites: all four (in `render_pattern`/`render_icon`/`show_string`×2) are `Display`-internal, always passing `self._pixels`/`self._lut` — no second beneficiary of the decoupling exists (`Image` doesn't call these). Alex: "I would be inclined to move those methods to Display" — advised first (confirmed via grep the decoupling had no live consumer, confirmed the LOAD_FAST-caching discipline survives the move if `self._pixels`/`self._lut`/`OFF` are still cached to locals at the top of each method body), then implemented on "please proceed": all three are now private `Display` methods; `_write_pattern_on_the_fly` also dropped its `width`/`height` params (always called with `WIDTH`/`HEIGHT` — same no-real-degree-of-freedom pattern as its `off` param). One test broke and was fixed: `test_public_names.py::test_fused_scan_is_wired_in_render_pattern` AST-walked for a bare-`Name` call, now checks the `self._write_pattern_on_the_fly` `Attribute` call. README's "Rotation during an in-flight Tier 2 animation" section updated (no longer describes a `lut` parameter that no longer exists). Verified: `py_compile` + `tests/` 178 passed + no lints.

**Follow-up same session — `show_string` fit-on-screen hold factor changed from arbitrary `5` to `WIDTH`:** Alex asked whether the docstring's "not derived from `WIDTH`" claim was accurate; confirmed via git archaeology (exp14 `9ef8ac6`, `WIDTH=8` there vs. `5`, so the claim held at introduction — exp16's `WIDTH` happens to also be `5`, a coincidence). Alex then judged the fixed `5` inconsistent with the scroll path (whose duration already scales with column count) and asked to make the hold `interval_ms * WIDTH` instead. Changed the one `asyncio.sleep(interval_ms * 5 / 1000)` call site to `* WIDTH`, and rewrote the surrounding docstring + inline comment (deleted the now-false "arbitrary, not derived from WIDTH" language, replaced with "same per-column time unit the scroll case steps by, applied across one full screen-width"). **Numerically identical today** (`WIDTH == 5` on this board) — this is a derivation/portability change, not a behavior change; on a future non-5-wide geometry (e.g. an exp14-style 8×8 fork) the hold duration would now scale with that board's `WIDTH` instead of staying at a stale `5`. Verified: `py_compile` + `tests/` 178 passed + no lints. `CODING_PRINCIPLES.md`'s "Document magic constants honestly" entry got a follow-up note (constant went from honestly-arbitrary to honestly-derived).
