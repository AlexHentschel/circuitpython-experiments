# Phase 2 audit ledger

Status: iteration 1 open (2026-04-23).

## Reflection (pre-audit)

### What actually changed

Phase 2 is the core-logic phase — 5 work items, one squashed commit (`8328488`).
Scope by item:

- **P2.1** — Extracted `_iter_pattern_rows(pattern_str)` in `core.py`; both
  `Image.from_pattern` and `Display.render_pattern` now consume it.
  `from_pattern` preallocates its multi-color buffer
  (`[OFF] * (w * HEIGHT)`); no more `append` + `tuple()`.
  Whitespace handling unified on `"".join(raw.split())`, matching
  `bitmap_codec`.
- **P2.2** — `IconNames` / `ArrowNames` integer-enum classes removed from
  `icons.py`; replaced by ordered string tuples `ICON_NAMES` /
  `ARROW_NAMES`. `core.py` constructs `Icons` / `Arrows` wrapper classes
  at import via `_build_image_namespace`, with each attribute an
  `Image` backed by a slice of the bulk bytes. `render_icon` /
  `render_arrow` / `show_icon` / `show_arrow` now take `Image`
  instances; `color` kwarg overrides stored color at render time.
  `__init__.py` re-exports adjusted; tests/test_icons_data.py rewritten
  around the name-tuple contract.
- **P2.3** — `create_image` / `create_big_image` now raise `ValueError`
  for non-WIDTH / non-2×WIDTH widths. `Image.from_pattern` stays
  flexible.
- **P2.4** — `Image._render_window(offset)` extracted; shared by
  `show_image` and `scroll_image`. Three-slice range split replaces the
  per-pixel `if 0 <= src_x < width` check in the 64-iteration inner
  loop. Negative `offset` supported.
- **P2.5** — `_GlyphColumnFeeder` + `_render_ring_window` +
  `show_string` rewritten. Ring size is `WIDTH` bytes (plan said
  3×WIDTH — derivation in the ring-sizing note below). Termination on
  `trailing_blanks >= WIDTH`.

### Deviations from the plan's design sketches (noted upfront)

- **P2.5 ring size**: plan sketched 3×WIDTH; I used WIDTH. Argument: the
  visible window is exactly WIDTH columns, and the incoming column
  overwrites the slot that just left the window (at position
  `read_head` before the post-write increment). So WIDTH bytes of
  ring + feeder state is sufficient. 3×WIDTH would add 16 bytes of
  unused "pre-read lookahead" with no semantic benefit.
- **P2.5 feeder**: plan's `_prime_ring` helper dropped; priming is a
  one-line `bytearray(WIDTH)`, not worth a named function.
- **P2.1** `from_pattern`: plan suggested a single-pass possible-once
  widths-are-fixed (P2.3). But P2.3 only fixed `create_image` /
  `create_big_image`; `from_pattern` stays flexible, so we still need
  a pass to learn the width. Two-pass retained.
- **P2.2** icon color default: plan sketch showed `color=None` in the
  `Image(..., color=None)` construction. That would break
  `Icons.HEART.show_image()` because the mono render uses
  `self._color` directly. Changed to `WHITE`; the
  `render_icon` / `render_arrow` kwarg still overrides.

### What was learned

- The plan's "the design sketches are hypotheses to critique" directive
  paid off on P2.5 ring sizing and on the `Icons` default-color hole.
  Both would have landed as defects if the sketch was implemented
  verbatim.
- `Icons` / `Arrows` can't live in `icons.py` without pulling `Image`
  (and therefore `board`) into the pure-sub-module set. Construction
  moved to `core.py`; `icons.py` stays importable on CPython. This is
  a minor architectural choice worth flagging to the auditor.
- `working-docs/font-distortion-probe.py` is referenced by
  `MONITORING.md` as an A/B reference and must stay runnable — the
  `IconNames` → `Icons` migration propagates there even though it's
  otherwise an ephemeral snapshot.

### What is worth auditing given that

1. **`show_string` ring-buffer correctness** — off-by-one risks in
   `read_head` wrap, initial-priming edge cases (text where first
   glyph has `shift_x == 0` or glyph missing), scroll-out termination
   (`trailing_blanks >= WIDTH` vs strict equality), `loop=True`
   re-seed behavior (new `_GlyphColumnFeeder` each pass — is the ring
   correctly re-zeroed?), cancellation responsiveness across the
   inner loop. This is the highest-risk item.
2. **`_render_window` range split** — boundary math: negative `offset`
   (`x_min = -offset`), large `offset` exceeding `self._width`
   (`x_max < x_min`), multi-color branch copying `HEIGHT` entries per
   column (divergence from current per-pixel loop — any off-by-one in
   `src_base = (offset + x) * HEIGHT`?).
3. **Parser dedup behavior parity** — did semantics of
   `render_pattern` change subtly for users who relied on the old
   `stripped.replace(" ", "")` behavior (spaces only) vs the new
   `"".join(raw.split())` (all whitespace)? Likely harmless, but worth
   naming.
4. **`Icons` / `Arrows` API ergonomics** — `Icons.HEART` is now an
   `Image`. Does `recolor` on it mutate the singleton (yes — shared
   state hazard across callers)? What happens if a user does
   `await Icons.HEART.show_image()` directly? Are there missed
   callers (tests, docs) still passing integers?
5. **`create_image` / `create_big_image` error messages** — are they
   useful enough to diagnose a bad pattern at author-time? Do they
   discriminate between width and height mismatches?
6. **`__init__.py` export surface** — did any previously-exported
   symbol get dropped without a compensating addition? E.g., callers
   importing `IconNames` would now fail; is that the intent? (yes —
   clean break per plan.)
7. **Memory / timing claims** — the ring-buffer scroll claims `O(1)`
   memory regardless of text length. Is that true including the
   `text` argument itself (held as `self._text` in the feeder)? Is
   `_glyph_columns` called once per character as claimed?

### What can be skipped or downweighted

- **Full Tier-1 re-coverage of rename mechanics** — the icon-name
  tuple contract is tested (+4 tests). Anything Tier-2 (on-device)
  is correctly batched to P3.6.
- **Performance micro-benchmarking** — the range split and ring
  buffer are correctness refactors with expected perf wins; any
  actual number belongs in a device run, not here.
- **README prose rewrite** — P3.4 owns that. Audit should only flag
  README contradictions with the code, not prose quality.
- **`_build_image_namespace` using `type(...)` vs a real class body** —
  stylistic; not a correctness concern.

## Iteration 1 — Auditor findings

16 findings: 1 high, 5 medium, 6 low-medium, 3 low, 1 low-opportunity.

| ID | Severity | Dim | Location | Observed |
|----|----------|-----|----------|----------|
| F1 | high | 4 | `core.py:291-294` (`Image.recolor`) applied to `Icons.*` / `Arrows.*` | `Icons.HEART` is a module-global singleton; `.recolor(RED)` mutates `_color` in place and persists for every subsequent caller -- two unrelated coroutines can silently interfere via direct `Image` methods. |
| F2 | medium | 1 | `core.py:638-654` (`show_string` scroll inner loop) | Termination `trailing_blanks >= WIDTH` breaks after the last meaningful col has reached `x=0` (leftmost) but *before* the all-blank frame is rendered -- contradicts docstring "ends when the last meaningful column has left the screen". |
| F3 | medium | 5 | `core.py:404-418` (`create_image` / `create_big_image`) | Size gates check width only; 3-row or 20-row patterns pass silently (rows padded / dropped by `from_pattern`). |
| F4 | medium | 7 | `lib/display/README.md:32-33` | Tier-1 bullets say "display an icon from `ICONS`" / "arrow from `ARROWS`" and list `render_arrow(direction, color=WHITE)` with the pre-P2.2 parameter name. |
| F5 | medium | 8 | `core.py:385-389` + `lib/display/README.md:122` + `CONTEXT_HANDOFF.md:245` | Docs say `Icons` / `Arrows` are "backed by slices of the bulk bytes" but `data[start:start+WIDTH]` on `bytes` copies; each icon Image owns an independent 8-byte allocation. |
| F6 | low-medium | 3 | `core.py:269` | `from_pattern` width calc now uses `rows[:height]` (only first HEIGHT rows); old used all rows. Silent parity change for pathological >HEIGHT patterns where a beyond-HEIGHT row is widest. |
| F7 | low-medium | 3 | `core.py:83` (`_iter_pattern_rows`) | Whitespace handling widened from "spaces only" to "all whitespace" (tabs, CR, FF). A literal `\t` inside a row now collapses the column instead of rendering as unknown/OFF. |
| F8 | low-medium | 7 | `README.md:66,81` | Tier-1 `render_arrow(direction, ...)` and Tier-2 `show_arrow(direction, ...)` API-table rows use the pre-P2.2 parameter name `direction`; actual signature is `arrow`. |
| F9 | low-medium | 8 | `core.py:659` (`show_number` docstring) | "Single digit: centered. Multi-digit: scroll." is approximate -- the real split is total glyph-column width ≤ WIDTH. |
| F10 | low-medium | 8 | `core.py:584-585,629-630` (`show_string` docstring vs code) | Short-text path with `interval_ms=0, loop=False` takes neither hold branch -- returns immediately; docstring's "held for `interval_ms * 5` ms" implies otherwise. |
| F11 | low | 4 | `core.py:492-508` (`render_icon` / `render_arrow`) | Int-index callers now hit `AttributeError: 'int' object has no attribute '_data'` with no library-specific diagnostic. |
| F12 | low | 5 | `core.py:408,417` | `create_image` error messages give the measured numbers but no hint toward common authoring mistakes (trailing spaces, literal tab). |
| F13 | low | 7 | `CONTEXT_HANDOFF.md:259` | Still documents `Lookup: ICONS[icon_id * WIDTH : (icon_id + 1) * WIDTH]` as the API-level lookup recipe; stale vs the name-keyed `Icons.<NAME>` surface. |
| F14 | low | 9 | `core.py:213-214` (`_GlyphColumnFeeder.__init__`) + show_string docstring | Feeder keeps `self._text = text`, so the full input string lives for the scroll's duration -- memory is O(len(text)) + O(WIDTH), not strictly O(WIDTH) as claimed. |
| F15 | low (opportunity) | 9 | `core.py:611-615` and `:634,645` | Fit-decision probe `_glyph_columns` work for the first 1-2 chars is re-done by the fresh feeder when the scroll path is taken. Per-wrap redo on `loop=True`. |
| F16 | low (opportunity) | 9 | `core.py:177-195` vs `:91-118` | `_render_ring_window` duplicates ~10 lines of inner-loop pixel writes with `_render_colmajor`; any future LUT/brightness change must be applied in both. |

Dimensions with no findings: **2** (`_render_window` boundary math — manually walked `offset ∈ {-20, -3, 0, 5, 10}` across `width ∈ {0, 6, 8, 16}`; all clamps land in bounds) and **6** (`__init__.py` export surface — removals match plan's clean-break mandate, `Icons`/`Arrows`/`ICON_NAMES`/`ARROW_NAMES`/`create_image`/`create_big_image` compensatingly exported on both import paths). Also explicit no-finding on other Dim-1 sub-concerns: `shift_x == 0` / missing-glyph feeder advance, `loop=True` ring re-seed, cancellation cadence across the await.

## Iteration 1 — ROI assessor dispositions

| ID | Disposition | Rationale |
|----|-------------|-----------|
| F1 | Accept (doc) | Shared-state hazard is real but ergonomic constraint; primary API (`render_icon` / `render_arrow`) takes `color` kwarg and bypasses `.recolor()`. Document the sharing + recommend `create_image` clone for users who want a private copy. Out-of-scope to add per-icon deep-copy layer. |
| F2 | Accept (fix) | Clear docstring-vs-code divergence; single-character fix (`> WIDTH` instead of `>= WIDTH`) restores the stated invariant. |
| F3 | Accept (fix) | The whole point of `create_image` / `create_big_image` is author-time diagnostics; height parity belongs under the same assert. |
| F4 | Accept (fix) | README should match the current code. Small effort. |
| F5 | Accept (fix) | Memory-model claim is cheap to correct; stale mental model would compound. |
| F6 | Accept (doc) | New behavior is arguably *more* correct (ignore rows past HEIGHT entirely) -- keep it, note explicitly in the docstring that excess rows are fully ignored. |
| F7 | Accept (doc) | Widening was intentional (aligns with `bitmap_codec`); document explicitly rather than hide. |
| F8 | Accept (fix) | Sibling of F4. |
| F9 | Accept (doc) | One-line tighten. |
| F10 | Accept (doc) | Clarifies the "render-and-return" shape when `interval_ms=0, loop=False`. |
| F11 | Defer | Plan explicitly chose a clean break; defensive isinstance check would grow code paths permanently to support a migration-era error message. Any user hitting `'int' object has no attribute '_data'` grepping the repo finds `Icons` in one step. |
| F12 | Defer | "Trailing space" / "literal tab" hint-text is a marginal UX lift; users who hit these will learn from the reported numbers. |
| F13 | Accept (fix) | Quick sentence tweak in the handoff. |
| F14 | Accept (doc) | "O(WIDTH) beyond the input text reference" is the accurate statement; fix the claim, don't redesign the feeder (caller already holds the text). |
| F15 | Defer | Per-show_string startup only; per-wrap on `loop=True` but still amortised across many frames. Low ROI. |
| F16 | Reject | The two helpers have fundamentally different column-index arithmetic; unifying via callback would lose the LOAD_FAST / LOAD_GLOBAL separation in a certified hot path. Duplication acknowledged as an intentional hot-path trade-off. |

**Tally**: 11 Accept, 4 Defer, 1 Reject.

## Iteration 1 — Implementer actions

- **F2** — `core.py` `show_string` scroll: termination condition `trailing_blanks > WIDTH` (was `>= WIDTH`) + inline comment pointing to the off-by-one argument. Final all-blank frame now actually renders.
- **F3** — `core.py` `create_image` / `create_big_image`: row-count gate added (`sum(1 for _ in _iter_pattern_rows(...)) != HEIGHT`), error message now reports both measured rows and columns against the required shape. Kept `from_pattern` lenient.
- **F4 + F8** — `lib/display/README.md` Tier-1 bullets and top-level `README.md` Tier-1 / Tier-2 tables: param name `direction` -> `arrow`; descriptions updated to mention `Image` instances (e.g. `Arrows.NORTH`).
- **F5** — `core.py` icon-namespace comment: clarified that `bytes` slicing copies so each `Image` owns its own 8-byte block; the bulk arrays exist for ordering, not byte-sharing. Mirrored in `lib/display/README.md § Sub-module responsibilities`.
- **F1 (doc)** — Added a "Sharing hazard" paragraph to the same comment block: `Icons.*` / `Arrows.*` are module-global singletons, `.recolor()` mutates shared state, primary API (`render_icon` / `show_icon` / `render_arrow` / `show_arrow`) already takes a `color` override, use `create_image` when a private copy is needed.
- **F6 + F7 (doc)** — `Image.from_pattern` docstring: explicitly states rows past `HEIGHT` are dropped *including from the width calc*, and whitespace handling is all whitespace (not just spaces). Sibling updates in `README.md` "Pattern string format" and `CONTEXT_HANDOFF.md` matching bullet.
- **F9 (doc)** — `show_number` docstring rewritten to point at `show_string`'s width-based decision; noted the monospace font makes "one digit fits" the common case.
- **F10 (doc)** — `show_string` docstring: render-and-return shape when `interval_ms=0 and loop=False` named explicitly; feeder memory-complexity claim reworded to "O(WIDTH) beyond the input text reference".
- **F13 (doc)** — `CONTEXT_HANDOFF.md` bitmap-format paragraph: `ICONS[icon_id * WIDTH : ...]` recipe replaced with a user-facing `Icons.<NAME>` description + note that the bulk bytes are an internal detail used by `_build_image_namespace`.
- **F14 (doc)** — merged into F10's docstring reword; no code change.
- **F11, F12, F15** — Deferred per ROI rationale.
- **F16** — Rejected; duplication documented as intentional hot-path trade-off (no code action).

Tier-1 suite: **123 passed** (same as pre-audit). The three code changes (F2, F3) are both Tier-2 behaviors (animation frame cadence, author-time diagnostic); Tier-1 pure-module tests are correctly unaffected.

## Stopping signal / close

**Iteration 2 reflection**: all 11 accepts applied, one behavioral fix (F2) plus one strictness fix (F3) plus documentation + consistency sweep. Further iteration would produce diminishing returns -- remaining open items (F11, F12, F15) are low-ROI by construction; F16 is an intentional trade-off. Exit.

**Plan-revision check**:

- Phase 2 items P2.1-P2.5 stand as executed; P2.6 closed by this ledger.
- P3.5 "cross-file consistency sweep for leaked internal terminology" now has concrete precedent (the `Icons`/`Arrows` migration exposed several strings-are-still-`ICONS` README slips caught here as F4/F8/F13).
- P3.6 on-device verification: F2 (termination frame) and F3 (author-time diagnostic `ValueError`) both merit a device check; already batched there.
- No new phases or items warranted. Retrospective L1-L8 remains scheduled for post-Phase-3.

**Conclusion**: no material plan revisions. Stated explicitly per the plan-revision discipline.


