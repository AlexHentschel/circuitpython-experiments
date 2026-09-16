# Exp16 vs. Exp14 — `lib/display/` design & API divergence

**Status (2026-09-12):** living record, current-state only. Exp16 forked
`lib/display/` from Exp14 (`2026-04_Exp14_DisplayLibrary_CPy_on_RPi-Pico-2040/lib/display/`)
onto the BPI-Bit-S2's onboard 5×5 matrix; the two copies now evolve
independently. This file tracks **what differs today**, not a session-by-
session history of how it got that way — session narrative belongs in
`SESSION_LOG.md` / `ai-notes/`. **Update entries in place** as divergence
changes; delete/rewrite superseded rows rather than appending a dated log.

**Why this file exists:** the plan is to eventually return to an 8×8 matrix
on an RP2350-class board (see `Notes/student-api-portability.md`). At that
point Exp16 will likely become the *base* to move forward from (it carries
fixes and test coverage Exp14 doesn't), not Exp14 — so decisions made here
about *why* something diverged need to survive the switch, even though the
concrete 5×5 code mostly won't.

## 1. Hardware-forced (expected — re-derive per board, don't port verbatim)

| Element | Exp14 (8×8, YD-RP2040) | Exp16 (5×5, BPI-Bit-S2) | Forward note |
|---|---|---|---|
| Wiring LUT (`geometry.py::build_lut`) | Progressive, row-major, bottom-up left-to-right: `idx = (HEIGHT-1-y)*WIDTH + x` | Column-major, right-to-left (Exp09/BananaPi sequential list): `idx = y + HEIGHT*(WIDTH-1-x)`, i.e. `idx = y + 20 - x*5` for 5×5 | **The LUT formula is a property of the physical strip wiring, not the library.** At the next board switch, re-derive it from that board's actual sequential-index map (as Exp09 did for this one) — do not carry over either formula. The four-rotation derivation *technique* in `build_lut`'s comments (given rotation-0 idx, apply progressive transforms for 90/180/270) is reusable; the base-case formula is not. |
| `PIXEL_PIN` (`core.py`) | `board.GP0` (external, via level shifter) | `board.NEOPIXEL` (GPIO18, onboard) | Per-board config constant, expected to change every time. |
| `BRIGHTNESS` default (`core.py`) | `0.05` | `0.20` (Alex currently running the live test script at `0.10`, a local override — see `code.py`, not a library-default change) | Per-board/LED-density tuning, not an API concern. |
| `WIDTH` / `HEIGHT` (`_constants.py`) | `8`, `8` | `5`, `5` | The one dimension the library is explicitly designed to parametrize (`_constants.py`'s own docstring). Not a divergence to resolve — it's the intended axis of variation. |

## 2. Architectural divergence (intentional design decisions)

### 2.1 Font backend swapped entirely

- **Exp14**: loads a real PCF font at runtime via `adafruit_bitmap_font.load_font()` (`font_free_mono_8/font.pcf`), preloads printable ASCII glyphs at import, and maps each glyph's PCF metrics (`ascent`, `dy`, `dx`, `shift_x`) into display rows/columns at render time — a nontrivial right-handed→left-handed coordinate transform (documented at length in Exp14's `_glyph_columns`).
- **Exp16**: replaced this with a **precomputed column-major glyph table** (`font_makecode_5/`, consumed via `font_makecode_5.glyph_columns`) — no `adafruit_bitmap_font` dependency, no runtime metric math.
- **Rationale** (see persona `concepts/fonts.md`): outline/PCF fonts don't render legibly at 5-pixel glyph heights — a hand-designed, MakeCode-style bitmap font was required, not just a smaller point size of the same font.
- **Forward implication:** at 8×8 either approach is viable again — PCF fonts have enough vertical resolution to work, which is exactly why Exp14 used one. Decide explicitly rather than defaulting to whichever repo is closer at hand:
  - Keep the precomputed-table approach (Exp16's direction): simpler, zero external font-rendering dependency, but needs a new hand-designed 8×8 glyph table (or a script to derive one from a PCF source at build time, not runtime).
  - Revert to PCF (Exp14's direction): more flexible (any installed font, not just a hand-tuned table) but reintroduces the `adafruit_bitmap_font` dependency and the coordinate-crossing metric mapping.

### 2.2 `render_pattern` hot path already fused in Exp16

- **Exp14**: `_write_pattern_on_the_fly` (the fully-fused single-pass scanner) exists but is *intentionally unused* — `render_pattern` still goes through the two-stage `_iter_pattern_rows_fast` + per-row write loop. Tracked as Exp14's own open TODO (`working-docs/refactor-round-todos.md` #1, effort M, disposition open as of 2026-06-14).
- **Exp16**: already integrated `_write_pattern_on_the_fly` as the live hot path for `render_pattern`.
- **Forward implication:** Exp16 is ahead here. If Exp16 becomes the new base at the next switch, this is already resolved; if not, backport this specific change to Exp14 rather than re-doing the analysis.

### 2.3 Icon bitmap corrections (data, not API)

- `GHOST` and `LEFT_TRIANGLE` bitmaps redrawn in Exp16 to match the official MakeCode reference grids. Both libraries inherited the originals from Exp09's `microbit.Image.*` port, which were wrong independent of resolution: Exp09's `GHOST` lit the top corners instead of a rounded head, and `TRIANGLE_LEFT` dropped the base edge. Not yet applied to Exp14.
- `ICON_NAMES` / `ARROW_NAMES` (the ordered name lists) are otherwise **identical** between the two libraries — same 40 icons + 8 arrows, same order, same slot semantics. Only two icons' pixel content differs, and only because it was a correctness fix, not a resolution adaptation.
- **Forward implication:** carry the corrected grids forward regardless of resolution — they're fixes to the reference art, not artifacts of being 5×5. Re-verify visually once redrawn at 8×8 (a corrected grid can still be transcribed wrong at a different pixel count).

### 2.4 Tier 2 (async) API — identical until this session

Confirmed **byte-identical** between the two libraries' `core.py` (verified 2026-09-11, full diff of the Tier 2 section: zero differences). Every divergence below this line is new as of this record.

## 3. Divergences introduced this session (2026-09-11)

- **`Image.scroll_image`'s per-frame parameter renamed `offset` → `step`** (Exp16 only). `show_image(offset)` and `scroll_image(offset)` used the same name for two different concepts — a window *position* (can be negative, can overhang) vs. a per-frame *increment* (always starts at position 0, no way to change that). Renamed to `step` in Exp16; `show_image`'s `offset` is unchanged (it's the correct name for what it does).
  - **Prior art**: this exact ambiguity was already flagged, independently, in Exp14's own `working-docs/refactor-round-todos.md` #12(a) (added 2026-06-14, "Rename scroll step to `step`/`columns_per_frame` — API change, small, no external consumers," disposition open) — not yet applied there. Exp16 now diverges from Exp14 on this parameter name for what was, until today, identical code.
  - **Recommendation**: apply the same rename in Exp14 next time that repo is touched, so the two don't silently drift apart on naming for otherwise-shared logic. Cross-project promotion candidate — see persona `crossref/BY_TOPIC.md`.

- **Docstring-quality pass on Exp16 `lib/display/core.py` + `lib/display/README.md`** (2026-09-12; doc/comment-only, no logic or signature change; `py_compile` clean, `pytest` 149 green). Applied a four-axis docstring review (coupling / audience-accessibility / typical-case-first ordering / honesty about constants — persona `CODING_PRINCIPLES.md § Docstring quality triage is multi-axis`): moved private mechanism out of public docstrings into internal comments (module globals; the cancellation sequence-counter; `render_pattern`'s LUT/no-buffer strategy; `set_rotation`'s LUT rebuild; the `_data` slot and `_iter_pattern_rows` names); added a caller-facing shared-instance hazard note to `recolor`; dropped "singleton" jargon; reordered the `Image` class docstring caller-first (storage demoted to a closing note). `_render_window`'s docstring was **left entirely untouched** (Alex-reserved, hand-polished).
  - **Back-port to Exp14: YES — the *restructuring*, re-authored against Exp14's own text.** These are board-agnostic doc-quality improvements; Exp14's counterpart docstrings (`module` / `Image` / `Display` / `render_pattern` / `set_rotation` / `columns` / `create_image`) carry the same coupling/ordering issues. Port the *pattern*, not the literal strings — the embedded facts differ (see the next entry). This narrows §2.4's "Tier 2 byte-identical" note to *code*: the docstrings now differ.

- **8×8 / RP2040-heritage fact corrections in Exp16 docs — DO NOT BACK-PORT** (2026-09-12). Exp16 inherited docstring/README facts that were true for Exp14 (8×8, YD-RP2040) but false on the BPI-Bit-S2. Corrected in Exp16 only; **each is correct as-is in Exp14 and must not be carried back:**

  | Fact | Exp14 (keep) | Exp16 (corrected) |
  |---|---|---|
  | Matrix size in prose (`Display` docstring, README §single-instance) | 8x8 | 5x5 |
  | Board (README §single-instance) | YD-RP2040 | BPI-Bit-S2 |
  | Data pin (README `deinit`) | GP0 | GPIO18 (`board.NEOPIXEL`) |
  | Per-icon `Image` backing block (README sub-module table) | 8-byte | `WIDTH`-byte (= 5) |
  | `create_big_image` width (`core.py` docstring) | 16-wide | `2 * WIDTH`-wide (= 10) |
  | Font node (README mermaid) | `font_free_mono_8/font.pcf` | `font_makecode_5/glyphs.py` (see §2.1) |
  | NeoPixel driver peripheral (`deinit` docstrings + README, 5 sites) | **PIO state machine** | **RMT peripheral** |

  - **The PIO→RMT row is the trap**: it reads like a generic doc fix but is hardware-specific. **Exp14's RP2040 genuinely drives NeoPixels via a PIO state machine**, so "PIO" is *correct* there (same for Exp15's RP2350). Only ESP32-class MCUs have no PIO — CircuitPython's espressif `neopixel_write` uses the **RMT** peripheral. When Exp16 becomes the forward base on an RP2350 board, this reverts to PIO — re-derive per silicon, do not treat "RMT" as the canonical wording.
  - **Deliberately left** (portable as-is, *not* a stale fact): README §"Column-major bytes" "an 8x8 mono bitmap is exactly 8 bytes" + the letter-`F` example — a correct statement about the encoding format's 8-bit-per-column capacity (the format caps at 8 rows on any board), not a claim about this matrix.

## 4. Exp16-only surface (no Exp14 counterpart at all)

- **`lib/buttons.py`** — async onboard/generic button-event API (`Button`, `ButtonPair`, `OnboardButtons`). Not a fork of anything in Exp14.
- **`lib/planetx/`** — ElecFreaks PlanetX modules (`PlanetXButtonSensor` C/D via `keypad`). Net-new; further sensors join this package.
- **`font_makecode_5/`** — the precomputed glyph table package replacing Exp14's `font_free_mono_8/` + PCF loader (see §2.1).
- **Font-spacing build pipeline (2026-09-13, Phases 1-3 of `ai-notes/plan/font-spacing-impl/plan_v1.0.md`)** — `scripts/dal_pendolino3.py` (shared DAL-fetch/convert helper, pinned commit SHA), `scripts/verify_dal_font_conversion.py` + `scripts/generate_spaced_font_table.py` (dev-machine-only, never deployed), `lib/display/font_makecode_5/spaced_glyphs.py` (generated `[length, ink...]` table) + `ink.py` (`glyph_ink` accessor), `lib/display/text_layout.py` (`SpacedGlyphColumnFeeder`, pure/no hardware import). All net-new, no Exp14 counterpart. **Not yet wired into `core.py`** — live `show_string` still uses `_COLUMN_MAJOR`/`_GlyphColumnFeeder`; the cutover (Phase 4) is gated on an explicit go-ahead. Once cut over, this whole pipeline becomes portable rollout precedent for the eventual 8×8 font (re-run the same two-script pipeline against a new glyph source).

## 5. Using this record at the next platform switch

1. Re-derive the wiring LUT from scratch for the new board's actual physical layout (§1) — never port a formula.
2. Decide the font backend explicitly (§2.1) rather than by default.
3. Carry forward the icon corrections (§2.3) and the fused `render_pattern` path (§2.2) regardless of which repo is treated as the base.
4. Check whether any Tier 2 API divergences accumulated here (starting with §3) should become the new shared baseline — Exp16 is likely the more current copy by then, given its Stage 0-3 on-device test progression has no Exp14 counterpart.
5. Re-run this diff exercise (`diff` the two `lib/display/` trees) rather than trusting this file to be exhaustive if significant time has passed — it reflects a point-in-time comparison as of 2026-09-11, not a continuously-verified sync.

## See also

- `Notes/student-api-portability.md` — the *student-facing* portability spec (what LightTower sketches need to survive the switch); this file is the *maintainer-facing* counterpart (what the library's own internals changed and why).
- Exp14 `working-docs/refactor-round-todos.md` — source of the `offset`/`step` and `render_pattern` fusion prior-art items.
- Persona `concepts/fonts.md` — the outline-font-fails-at-small-sizes finding behind §2.1.
- `lib/display/README.md` (this repo) — current Exp16 API reference (not a diff against Exp14).
