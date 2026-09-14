# Concept domain: nezha (ElecFreaks Nezha expansion board)

`[domain:nezha]` `[cross-experiment]` — **seeded 2026-09-14** (first concrete concept). Smart-motor / breakout I2C protocol for Nezha V2 (哪吒2), used by exp16 LightTower mast (later) and coding-tutor's Nezha2 target. Retrieval: `_INDEX.md` → here → `#concept`; lateral edges in `_RELATIONS.md`. **Not** general I2C-bus properties (`i2c.md`) and **not** PlanetX GPIO buttons (`lib/planetx/`).

**No CircuitPython driver exists yet.** Student API stays semantic (`mast` park/sweep/nudge), not `M4` / opcodes (`Notes/student-api-portability.md` G6).

## Concepts

### Nezha V2 smart-motor I2C protocol (8-byte frame @ `0x10`) — decode `evidence-supported`; on-device `unverified`

**Claim.** Nezha V2 intelligent motors (encoder servo-motor hybrids on ports M1–M4) are driven by **8-byte I2C writes** to 7-bit address **`0x10`**, header `0xFF 0xF9`. This is **not** Nezha V1 (`Nezha.py`: 4-byte DC-motor + 0–180° hobby-servo packets at the same address). Mixing V1/V2 frames is undefined.

**Bus on BPI-Bit-S2:** goldfinger P19/P20 = `board.SCL` / `board.SDA` (GPIO16/15). Every Nezha **IIC** jack is the **same** bus, not four independent I2C buses (`lib/planetx/ports.py` `I2C`). First on-device check: `0x10 in board.I2C().scan()`.

**Frame:**

```
[0]=0xFF  [1]=0xF9  [2]=motor(1–4 or 0=global)  [3]=arg_a
[4]=opcode  [5]=value_H  [6]=mode or filler 0xF5  [7]=value_L
```

16-bit values (move distance, target angle, speed-limit) are **split around byte 6** (high in `[5]`, low in `[7]`). Reads (position/speed/version) are little-endian.

**Opcodes — prefer MakeCode [`pxt-nezha2` `main.ts`](https://github.com/elecfreaks/pxt-nezha2/blob/master/main.ts) over MicroPython `Nezha_V2.py`:**

| Opcode | Job | Notes |
|--------|-----|--------|
| `0x70` | relative move | `[3]` dir CW=1 CCW=2; `[6]` Circle=1 Degree=2 Second=3; 16-bit value in `[5]`/`[7]` |
| `0x5D` | absolute angle 0–359 | `[6]` **ShortPath=1 CW=2 CCW=3** (MakeCode `ServoMotionMode`) |
| `0x60` | start at speed | `[5]` = abs(speed) 0–100; sign → `[3]` dir. Current MakeCode public `start()` |
| `0x5F` | stop | filler `0xF5` in `[6]` |
| `0x5E` | start, direction only | bak + MP `nezha2MotorStart`; **dropped from current MakeCode** |
| `0x77` | global speed-limit | `[2]=0x00`; limit = percent×9 (default 900 = 100%). MakeCode sends this **before** `0x70` |
| `0x46` | read position | wait ~4 ms; read 4 bytes LE; degrees = `(raw % 3600) * 0.1` |
| `0x47` | read speed | wait ~4 ms; read 2 bytes LE; MakeCode: `floor(raw/3.6)*0.01` laps/s |
| `0x1D` | encoder zero | MakeCode then host-delays 1 s |
| `0x88` | firmware version | read 3 bytes → `V x.y.z` |

**Do not copy MP blindly (`disputed` until on-device):**

| Axis | MakeCode (canonical) | `Nezha_V2.py` |
|------|----------------------|---------------|
| 0x5D path enum | ShortPath=1, CW=2, CCW=3 | clockwise=1, CCW=2, shortest=3 — MP “CW” is firmware ShortPath |
| start | `0x60` + speed | also public `0x5E` (no speed) |
| 0x70 | preceded by `0x77` | `0x77` omitted |
| 0x47 formula | `floor(raw/3.6)*0.01` laps/s | `raw * 0.0926` (not equivalent) |

**Host vs firmware:** MakeCode “wait until done” is an **estimated** `motorDelay` from `servoSpeedGlobal` (100% ≈ 900 deg/s + 500 ms fudge), not an encoder-done handshake. Absolute-move “sync” is a **fixed 0.5 s**. Relative-angle zero is a **host array**. Combo/diff-drive is two I2C writes + host wheelbase math — unused by LightTower.

**LightTower Watch II (M4):** 10°/240° nudges = `0x77` then `0x70` Degree; `parkposition` = `0x46` stored in a student variable; continuous spin = `0x60` until `0x5F`. Mounting decides which way is “West”.

**CircuitPython constraints (when a driver exists):** `board.I2C()` lock around write and around write+settle+read; **no yield** in the ~4 ms 0x5D/0x46/0x47 settle (MakeCode: “do not insert other tasks”). Do not wrap Exp09/`elecfreaks_planetx` (V1).

**How to check status:** on-device queue in the unpack digest §8 (`i2c.scan` → `0x88` → 0x60/0x5F smoke → 0x46 delta after 0x70 90° → 0x5D enum A/B). Until scan sees `0x10`, every on-device claim stays `unverified`.

**Unpack (gitignored, may vanish):** exp16 `ai-notes/digests/nezha-v2-motor-protocol.md` — full source ranking, bak-vs-current names, combo math, verification steps. Durable facts are **this concept**; do not treat the notes folder as the only home.

**Vendor sources (not CircuitPython imports):**
- MakeCode: <https://github.com/elecfreaks/pxt-nezha2> (GitHub only — not in the local snapshot tree)
- MicroPython V2: <https://github.com/elecfreaks/EF_Produce_MicroPython/blob/master/Nezha_V2.py>
- MicroPython V1 (wrong protocol): <https://github.com/elecfreaks/EF_Produce_MicroPython/blob/master/Nezha.py>
- Exp16 README § *ElecFreaks PlanetX / Nezha — protocol sources*
- **Local alternate (may vanish; check freshness):** exp16 `ai-notes/Elecfreaks-Repos/EF_Produce_MicroPython/{Nezha_V2.py,Nezha.py}` — pin `c0b3a53`; PlanetX sensors: `…/PlanetX_MicroPython/` pin `268740c`. Procedure: exp16 CONTEXT *Local vendor snapshots*.
