# TinyUF2 4MB partitions (Adafruit CSV)  `evidence-supported`

`[domain:tooling]` — sidecar of `tooling.md` (stream on demand). Fetched 2026-09-11. Dual-OTA `partitions-4MB.csv` **0.32.0 ≡ 0.35.0** data rows. CP10: 0.35.0 `partitions-4MB-noota.csv`. Adafruit 4MB tables only.

Shared: nvs 20K@0x9000 · otadata 8K@0xe000 · uf2 256K@0x2d0000 · **ffat 960K@0x310000**

| | dual-OTA | no-OTA / CP10 |
|---|---|---|
| ota_0 | 1408K@0x10000 | **2816K@0x10000** |
| ota_1 | 1408K@0x170000 | — |

1408+1408=2816=0x2C0000=`INFO_UF2` Flash Size. 0x310000+960K=0x400000=4MiB end. Below 0x9000: boot~0x1000, table 0x8000. [#6285](https://github.com/adafruit/circuitpython/issues/6285) Size 963072=`ffat`.
Upstream: tinyuf2 `0.35.0` `ports/espressif/{partitions-4MB,partitions-4MB-noota}.csv`
