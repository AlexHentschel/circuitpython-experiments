# Session Log

## Current State (living summary)

**Active focus**: _none yet — cold start_

**Active experiment**: _to be determined per session (see `02-domain-structure.mdc` § Active Experiment Detection)_

**Phase**: Genesis (sessions 1–2 per `reference/08-bootstrapping.md` § Phase 1)

**Key references**: `reference/00-overview.md`, `reference/08-bootstrapping.md`

---

## Sessions

<!-- Per-session entries below. Format:
## YYYY-MM-DD: Session N — [active experiment slug]
- Technical insights:
- Artifacts created/updated:
- Patterns extracted:
- Process corrections received:
- Open questions raised:
-->

---

## Open Questions

| ID | Question | Since | Refs |
|----|----------|-------|------|
| OQ-MP-1 | Project granularity for multi-project layout: per-experiment, per-theme, mixed, or cross-domain families? | 2026-04-17 | `mandates/multi-project.md § OQ1` |
| OQ-MP-2 | Promotion autonomy: propose-only, auto-cross-project with manual universal, or fully agentic with CHANGELOG? | 2026-04-17 | `mandates/multi-project.md § OQ2` |
| OQ-MP-3 | How to tag pre-existing untagged entries at warm-reset time? (Default to active project for TECHNICAL/CONCLUSIONS, `[universal]` for WORKING_STYLE, flag ambiguous.) | 2026-04-17 | `mandates/multi-project.md § OQ3` |

### Deferred design notes

Items that are not questions needing a near-term answer, but decisions to revisit with accumulated evidence:

| ID | Note | Revisit when | Refs |
|----|------|--------------|------|
| DN-MP-1 | New-project-vs-extend heuristic — can only be refined empirically, not pre-specified. | After 3–5 distinct projects of experience (post-warm-reset). | `mandates/multi-project.md § OQ4` |

### Notes on open mandates

The human has declared an **open mandate** for a multi-project memory architecture, triggered by the phrase **"warm reset"**. Full spec at `mandates/multi-project.md`. Do not pre-emptively restructure — wait for the explicit trigger, then follow the pre-flight checklist in that file. OQ-MP-1 through OQ-MP-3 above should be resolved with the human *before* warm reset executes; DN-MP-1 is intentionally deferred until post-warm-reset evidence exists.
