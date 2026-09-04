# ai-notes — INDEX

Working notes for Exp16 (BPI-Bit-S2 CircuitPython + PlanetX). Cold-AI resume: read this file, then `NOTES.md`, then only the files this session's work needs.

> **HARD GATE — Destructive operations.** Never delete or non-trivially-reverse anything (untracked/gitignored files, `rm -rf`, git history rewrite, force-push, backups, overwrite without a verified restore) without an **explicit per-file grant**. Silence / "continue" / an unobjected default / approving this project's plan is **not** permission. Ledger: persona `memory/PERMITTED_DESTRUCTIVE_ACTIONS.md` (empty = nothing permitted). If blocked: **move** to the standing park `_parked/` (see below), don't delete. Confirmation: dedicated warning + exhaustive list + **fresh trigger word**.
>
> **Standing §4 park (Exp16, confirmed 2026-09-04):** `/Users/alex/Development/VsCode/CircuitPython/2026-09_Exp16_BPI-Bit-S2_CircuitPy_PlanetX/ai-notes/_parked/` — policy in `_parked/README.md`; index `_parked/MANIFEST.md`. Deleting a parked copy is still gated.
>
> Further reading: `/Users/alex/Git/rnd-ai-skills/generalized-agent-learnings/destructive-operations.md` (§0, §2 what counts, §3 hard gate, §4 move, §5 confirmation, §6 ledger, §7 self-check, §8 backups). Durable copy: `ai-persona/.cursor/rules/reference/destructive-operations.md`. Always-on stub: `ai-persona/.cursor/rules/06-destructive-operations.mdc`. Exp16 reminder: `NOTES.md` (banner at top).

**Location (agreed):** `/Users/alex/Development/VsCode/CircuitPython/2026-09_Exp16_BPI-Bit-S2_CircuitPy_PlanetX/ai-notes/`
**Lifetime:** execution-local to this project; durable findings promote to persona `memory/projects/circuitpython-exp16-planetx/` or `concepts/`.
**Spec (durable, human-facing):** `../Notes/overall_goal.md`

| File | Purpose | Status |
|------|---------|--------|
| `INDEX.md` | This router | live |
| `NOTES.md` | Locked decisions + current checkpoint | live 2026-09-04 |
| `design/student-api-portability.md` | Is a stable LightTower student API across BPI-Bit-S2→RP2350 realistic? Guidelines G1–G7 + assumptions A1–A4 with revisit triggers | live 2026-09-03; **re-open at every cadence gate** |
| `plan/reflection-cadence.md` | Fixed constraint: Observe/Evaluate/Revise **and** extract/distill/record at every planning+execution checkpoint | live 2026-09-03; execution plan must import, not copy |
| `plan/loop-setup.md` | Plan-refinement instance lock | locked 2026-09-04; **loop closed** |
| `plan/plan_v1.0.md` | Overnight PoC execution plan | **2026-09-04 kickoff** — executing chat starts P1–P6; risks in `plan/risk-register.md` |
| `digests/` | Cold-AI extracts | live 2026-09-04 — `digests/INDEX.md` |
| `learnings/` | Cadence extracts | first entry `learnings/p-plan-digest-collection.md` |
| `briefs/` · `returns/` | Sub-agent briefs and payloads | first dispatch 2026-09-04 |
| `_parked/` | Standing §4 safe-location (move here instead of delete). `README.md` = policy; `MANIFEST.md` = cold-AI index; payloads gitignored | confirmed 2026-09-04 |

Project tree (not under `ai-notes/`): `../lib/display/` — Exp14 copy, work on this copy (2026-09-04). Third-party: `../Notes/bpi_bit_v2_goldfinger.jpg` (CC BY-SA, unmodified) + sidecar `../Notes/bpi_bit_v2_goldfinger.jpg.license`.
