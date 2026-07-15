# Bamboo-Lamp — Conclusions

Scope: findings about the Bamboo-Lamp system only. Routing → `CONTEXT.md` (this folder). Status tiers:
`unverified` · `evidence-supported` · `disputed` · `invalidated`. Promotion to `evidence-supported` needs
independent corroboration (datasheet / bench measurement / multiple concordant sources), not just assertion —
Alex is design authority on intent/requirements but not on electronics-domain facts. Each row passes the cold-AI
test: claim + evidence + status decodable alone. Migrated to central at the 2026-06-14 warm reset from
`Bamboo-Lamp/memory/CONCLUSIONS.md` (verbatim; no claim added or dropped).

## Evidence-Supported

| Finding | Evidence | Date |
|---------|----------|------|
| _none yet_ | | |

## Unverified

| Finding | Why noted | How to verify | Date |
|---------|-----------|---------------|------|
| XIAO ESP32-C6 board-level deep-sleep ~14–15 µA from BAT | Seeed/community figures cited in `open-discussions/Standby-sleep-mode.md`; not bench-confirmed on Alex's board | Measure BAT current in deep sleep on the exact board + CircuitPython version + wake GPIO | 2026-06-14 |
| TPS63802 buck-boost module ~20 µA quiescent (3.3 V mode) | AliExpress module copied-datasheet claim; module may hide LED/load | Measure no-load input current from LiPo; reject if hundreds of µA / mA | 2026-06-14 |
| Unpowered I2C breakouts on a live SDA/SCL bus can back-power via protection diodes (extra standby drain / stuck bus) | Standard I2C failure mode; noted in handoff, not yet tested on these specific breakouts | Power each breakout off with bus alive; measure standby + confirm MAX17048 still reads | 2026-06-14 |

## Disputed

| Finding | Conflicting evidence | Date |
|---------|----------------------|------|
| Host MCU choice: XIAO **ESP32-S3** vs **ESP32-C6** | `AI-Notes.md` architecture/diagrams assume ESP32-S3; `Standby-sleep-mode.md` argues ESP32-C6 is the better low-power candidate (lower deep-sleep current, onboard LiPo path). Unresolved — Alex to decide; affects pin maps + low-power ceiling. | 2026-06-14 |

## Invalidated

| Former finding | What disproved it | Date |
|----------------|-------------------|------|
| _none yet_ | | |
