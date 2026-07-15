# Font-distortion investigation (2026-04-21)

Status: closed. Code pipeline exonerated. Root cause is the font file; fix deferred.

## TL;DR

Scrolled text on the 8x8 matrix looked distorted after the Phase-2 `_render_colmajor` refactor. The refactor was not the cause. The rendering pipeline — font → `_glyph_columns` → column-major bytes → `_render_colmajor` → NeoPixels — is faithful end to end. The distortion comes from the font file itself: `font_free_mono_8/font.pcf` is a FreeType auto-rasterization of the GNU FreeMono *TrueType outline* at `PIXEL_SIZE: 8`. At that size there are not enough pixels to preserve strokes, so FreeType stores 3-5-pixel-wide bitmaps that do not resemble the intended letters. Our code renders those bitmaps truthfully; the letters are simply not in the file to begin with.

The fix is a font swap (to a hand-designed bitmap font sized for the 8x8 matrix), tracked separately from the Phase-2 refactor work.

## Running example

The end-to-end reproducer lives at `working-docs/font-distortion-probe.py`. It is a snapshot of `code.py` at the moment the root cause was identified. It instruments three nested probes that together bracket the entire pipeline:

- **Probe 3** reads the underlying `displayio.Bitmap` via both 1D flat-index (`bm[cx + cy*w]`) and 2D tuple (`bm[cx, cy]`) access, side by side, with an automatic `MISMATCH` marker.
- **Probe 2** prints the column bytes `_glyph_columns` returns, as hex *and* as a `.`/`#` row pattern with bit 0 = top row.
- **Probe 1** statically holds a single `'H'` glyph on the display so the probe-2 column bytes can be visually confirmed against the physical LEDs.

The observed output for `'H'` (same data every run):

```
'H': width=4 height=5 dx=0 dy=0 shift_x=5
   col 0: 0x1c  rows=..###...
   col 1: 0x0a  rows=.#.#....
   col 2: 0x08  rows=...#....
   col 3: 0x3e  rows=.#####..
   col 4: 0x00  rows=........
   bitmap pixel reads (1d = bm[cx+cy*w], 2d = bm[cx, cy]):
   row 0: 1d=.#.#  2d=.#.#
   row 1: 1d=#..#  2d=#..#
   row 2: 1d=####  2d=####
   row 3: 1d=#..#  2d=#..#
   row 4: 1d=...#  2d=...#
```

Referring back to this one output block is sufficient to reconstruct the diagnosis, so the rest of this writeup is about the *shape* of the reasoning, not the details of further glyphs.

## Diagnosis, stage by stage

Each probe pins one stage of the pipeline to ground truth or rules it out as a suspect. The stages, from nearest-to-display back to the source:

1. **NeoPixel write + LUT (`_render_colmajor`)**. Icons and static pre-encoded images render correctly; only text and numbers distort. Both code paths share `_render_colmajor`. By contraposition `_render_colmajor` is not at fault.

2. **Column-major byte buffer (`_glyph_columns`)**. Probe 1 holds a static `'H'` on the matrix while Probe 2 dumps the column bytes the function produced. The lit pixels on the LEDs exactly match the bits in Probe 2's bytes, so the function's output is rendered faithfully. What the function *outputs* is still garbled; the question is whether it's reading garbled pixels or generating them.

3. **Bitmap pixel read (`bm[...]`)**. Probe 3 compares 1D and 2D access on the same `displayio.Bitmap`. They agree for every row of every probed glyph, ruling out indexing or internal-stride quirks. Whatever pixels are in memory are being read truthfully.

4. **PCF loader (`adafruit_bitmap_font.pcf`)**. On the host, a minimal stdlib-only `struct` parser reads the same `font.pcf` file and recovers exactly the pixels the device sees. No loader divergence. The loader is reading what's in the file.

5. **Font file (`font.pcf`)**. This is where the garbage lives. The file's `_OTF_FONTFILE: FreeMono.ttf` property and `PIXEL_SIZE: 8` tell the full story: it is FreeType's automatic rasterization of an *outline* font at 8-pixel nominal height. The resulting glyph bitmaps are 3-5 pixels wide by 3-5 tall and do not resemble the intended letters — `I` loses its bottom serif, `H` loses its left vertical, `A` becomes an inverted trapezoid. The font renders illegibly because the input medium (TTF outlines) and the output size (8 px) are fundamentally mismatched.

## Generalizations

Two durable lessons fall out of this, each of which has been promoted into the memory system. They are stated here in the order they would save time on a similar future investigation.

**Bound the hypothesis space to include the input data.** A rendering pipeline is a chain of transforms, and by default we assume the bug is in a transform we wrote. But the input to the first transform is also a possible source, and if the input is a black-box artifact produced by third-party tooling (a font, an asset pipeline, a dataset) its correctness is no more axiomatic than the code's. The diagnostic cost of adding "is the input correct?" as an explicit hypothesis at the start of an investigation is small — often a single independent decoder on the host — and the cost of *not* adding it is the entire investigation up to the point where it's forced on you. On this one I burned five or six speculative hypotheses about indexing, stride, bit ordering, and library versions before writing the host decoder that made the data-side diagnosis immediate.

**Instrument each pipeline stage; don't speculate past the point where data would settle the question.** Once a pipeline is suspect, further *analytical* reasoning about which stage is wrong is almost always worse than writing a probe that dumps the stage's input and output. The probes in the running example cost under thirty lines of code and took two device syncs to deploy; they unambiguously localized the bug in a chain where analytical bisection had been circling for multiple turns. The pattern generalizes: when a pipeline produces wrong output, write probes in reverse order (output → input) that print each stage's inputs and outputs in a format a human can read directly. Continue until one stage's input is correct and its output is wrong — or until all stages are faithful and the source data itself is the suspect.

**Domain fact (font on pixel displays).** Outline fonts (TrueType / OpenType) auto-rasterized at very small pixel sizes produce bitmaps that cannot preserve stroke structure and are unusable on pixel-accurate displays. For 8x8, 8x16, or other tight pixel grids, use hand-designed bitmap fonts (PCF / BDF) sized exactly for the target — `tom-thumb`, `bitocra`, `scientifica`, `spleen`, `tewi`, and similar. The rule of thumb is that capital-letter height needs at least 6-7 pixels to preserve the two verticals + crossbar structure of letters like `H`, `E`, `A`, `M`.

## Fix direction (deferred)

The font swap is out of scope for the current Phase-2 refactor and is tracked as a follow-up. When picked up:

1. Choose a bitmap PCF font sized for the display (5x7 or 5x8 for 8x8 matrices; 6x8 or 5x8 gives good monospace pitch).
2. Drop it into `lib/display/font_<name>/font.pcf` alongside the existing `font_free_mono_8/`, update `_FONT_PATH` in `core.py`.
3. Verify `font.ascent`, `font.descent`, and per-glyph `shift_x` / `width` / `height` metrics; `_glyph_columns` and `show_string` are metric-agnostic so no code change should be needed beyond the path.
4. Re-run the demo; scrolled `"Hello!"` and `"42"` should now be legible.

The deferred nature is recorded in `SESSION_LOG.md § Open questions` and `MONITORING.md` (follow-up action: *font swap*, promote when re-prioritized).

## What did not make it into memory

- The specific probe shapes (Probe 1 / 2 / 3). These are one-off; the *pattern* they instantiate is captured in the generalizations above. The concrete code lives only in `font-distortion-probe.py` as a reproducer.
- The specific PCF format quirks (MSB bit, MSB byte, 4-byte glyph padding). Useful only if we author or patch a PCF loader — unlikely.
- The specific host-side `struct` parser. Reusable on the next PCF issue but of limited value past that, so it stays inline in this writeup / working-doc.

If any of these turn into recurring needs, promote them from here into the canonical memory files on the next incident.
