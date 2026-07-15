# Concepts — Relations (typed concept↔concept edge list)

Read on placement (to find where a new concept connects) and on lateral traversal (rubric §0 capability (b): topic → concept → laterally-related concept). Distinct from `crossref/` — this is the concept↔concept axis; `crossref/BY_TOPIC|BY_PATTERN` is the cross-*project* axis. Edges are bidirectional; record once.

**Closed relation vocabulary**: `refines`/`generalizes` · `alternative-to` · `composes-with` · `instantiates`/`abstracts` · `pairs-with` · `conflicts-with` · `contradicts-in-context-X` · `complemented-by`.

Format: `<concept A>  —<relation>—  <concept B>   (note)`

## Edges (as of 2026-06-14 warm reset — sparse; only 2 domains seeded)

- `fonts: outline-fonts-unsuitable`  —complemented-by—  `circuitpython-runtime: memoryview`   (glyph raster access goes through buffer-protocol views / `displayio.Bitmap`).
- `circuitpython-runtime: name loading (LOAD_FAST)`  —composes-with—  `circuitpython-runtime: neopixel allocation`   (both are hot-path render-loop optimizations applied together in `_render_colmajor`).
- `i2c: back-feeding (ESD-diode)`  —pairs-with—  `power: power-domain isolation & powered-off protection (Ioff)`   (same ESD-diode mechanism; `i2c` = the SDA/SCL-bus instantiation, `power` = the general domain-boundary framing + Ioff part-selection. Read both; neither duplicates the other).
- `i2c: open-drain / wired-AND`  —composes-with—  `power: fuel gauge (MAX17048)`   (the MAX17048 SDA/SCL-low sleep entry is a direct consequence of open-drain line behaviour).
- `i2c: pull-up sizing`  —pairs-with—  `power: standby current budgeting`   (held-low / idle-high pull-up current is a standby-power line item).

## Anticipated edges (record when the target concept is seeded — do not pre-create the target)

- `fonts: glyph coordinate model`  —pairs-with—  `display: matrix render` (when a `display` domain is seeded; the concept currently lives in `fonts.md`).
- `circuitpython-runtime: preallocate` / `neopixel allocation`  —composes-with—  `led-driving: WS2812 timing` (when `led-driving` is seeded — exp11/13 ws2812 work).
