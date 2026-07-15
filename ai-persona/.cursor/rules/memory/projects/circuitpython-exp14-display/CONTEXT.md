# Context — circuitpython-exp14-display

**Family**: `circuitpython` · **Status**: active (Phase 3 in progress) · **Repo folder** (workspace-relative to `/Users/alex/Development/VsCode/CircuitPython/`): `2026-04_Exp14_DisplayLibrary_CPy_on_RPi-Pico-2040/` · **Branch**: `alex/display-mvp`.

## Scope & goal

A MakeCode-style two-tier display library for an **8×8 WS2812b** LED matrix on a **YD-RP2040** board, CircuitPython. Tier 1 = synchronous primitives (`render_pattern`, `render_icon`, pixel/brightness/rotation); Tier 2 = async animations (scroll, show_string/number, cooperative cancellation via a `_seq` token). Goal: a clean, allocation-conscious, well-documented MVP library.

## Entry points (further reading — links into the repo's technical artifacts, not copied here, C8)

- **Authoritative standalone handoff**: `2026-04_Exp14_DisplayLibrary_CPy_on_RPi-Pico-2040/CONTEXT_HANDOFF.md` — exhaustive project context (purpose, API surface, internals, lifecycle). The canonical technical reference for exp14; this `CONTEXT.md` deliberately does not duplicate it.
- **Library source**: `2026-04_Exp14_.../lib/display/` — `core.py` (Display/Image, render hot-paths), `geometry.py` (`build_lut`, `xy_to_index`), `bitmap_codec.py` (pattern↔colmajor), `icons.py`, `_constants.py`. Sub-module README at `lib/display/README.md`.
- **User-facing README**: `2026-04_Exp14_.../README.md`.
- **Tests**: `2026-04_Exp14_.../tests/` (Tier-1 pytest suite, 137/137 green as of 2026-06-11).
- **Working docs**: `2026-04_Exp14_.../working-docs/` — `audit-phase-1.md`, `audit-phase-2.md`, `font-distortion-findings.md`, `font-distortion-probe.py`, `refactor-round-todos.md`.
- **Active plan**: `~/.cursor/plans/display_library_refactor_d42ccd55.plan.md` (Cursor global plan store).

## Domain knowledge (in central concepts, not here)

CircuitPython memory model, name-loading, neopixel allocation → `../../concepts/circuitpython-runtime.md`. Font legibility + glyph coordinate model → `../../concepts/fonts.md`. These were surfaced by exp14 but are family-wide / cross-experiment, so they live centrally (R-7).

## Resumption point

Phase 3 in progress: P3.1–P3.5 done (type hints; `deinit()`; `build_lut(dest=)`; README refresh; consistency sweep). **Remaining**: P3.6 (Tier-1 already 137/137 green + on-device smoke covering `deinit`, in-place `set_rotation`, carried-over font legibility) and P3.7 (audit loop), then the L1–L8 retrospective. Carry-over open items: Pattern-A-vs-PEP-563 uniformity in `bitmap_codec.py`/`geometry.py`; `colmajor_to_pattern` `bytes`/`bytearray` widening; cryptic `IndexError` on `width > len(data)`. The font swap (illegible `font_free_mono_8`) is tracked in `../../universal/MONITORING.md`.

## Outstanding follow-up (carried from session 4 open question)

Whether the "audit + broad consistency sweep" pair is a general phase-close pattern — revisit at Phase 2/3 close (was already noted; Phase 2 closed without forcing the decision).
