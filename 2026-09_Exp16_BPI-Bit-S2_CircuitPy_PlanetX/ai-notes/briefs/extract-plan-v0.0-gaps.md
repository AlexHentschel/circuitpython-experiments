# Brief — extract gaps in plan_v0.0 vs locks/digests (read-only)

**Date:** 2026-09-04
**Model class:** composer-2.5 (extraction, no decisions)
**Return path:** `ai-notes/returns/extract-plan-v0.0-gaps.md`

## Deliverable

A structured inventory only. Do **not** rewrite the plan. Do **not** recommend phase order unless quoting a lock that already states it.

For each finding, use:

- **id** (G1, G2, …)
- **location** (plan section or “MISSING from plan”)
- **source** (path + short quote/paraphrase)
- **kind:** `lock-miss` | `digest-miss` | `contradiction` | `over-committed-shape` | `undecoded-term`
- **one-line fact**

## Sources (read these; do not scan the whole workspace)

1. `/Users/alex/Development/VsCode/CircuitPython/2026-09_Exp16_BPI-Bit-S2_CircuitPy_PlanetX/ai-notes/NOTES.md`
2. `/Users/alex/Development/VsCode/CircuitPython/2026-09_Exp16_BPI-Bit-S2_CircuitPy_PlanetX/ai-notes/design/student-api-portability.md`
3. `/Users/alex/Development/VsCode/CircuitPython/2026-09_Exp16_BPI-Bit-S2_CircuitPy_PlanetX/ai-notes/plan/plan_v0.0.md`
4. `/Users/alex/Development/VsCode/CircuitPython/2026-09_Exp16_BPI-Bit-S2_CircuitPy_PlanetX/ai-notes/digests/INDEX.md` and the four digest files it lists
5. `/Users/alex/Development/VsCode/CircuitPython/2026-09_Exp16_BPI-Bit-S2_CircuitPy_PlanetX/ai-notes/plan/reflection-cadence.md` (confirm the plan imports it rather than copying)

## Checks

- Every NOTES lock appears in the plan’s Fix layer (or is explicitly deferred with a reason).
- LightTower student ops (letter, pause, YES/NO/DIAMOND, number, A/B/C/D press) are success-criteria-visible.
- Swap units listed: geometry/LUT, icons, arrows, font.
- Copy path of `lib/display/` is the Exp16 tree.
- Font: recommendation present, source not locked; GPLv3 pitchfork flagged.
- IO13/IO14 labelled hypothesis.
- Overnight = host tests, not on-device.
- No instruction in v0.0 to scaffold `.vscode/` or implement in the planning chat.
- Cold-AI: any coined term in the plan that isn’t decoded.

End with a count of findings by kind. No verdict on whether to iterate.
