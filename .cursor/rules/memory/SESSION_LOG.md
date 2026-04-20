# Session Log

## Current State (living summary)

**Active focus**: Polishing Exp14 display library code quality (design-time authoring helpers first).

**Active experiment**: `[exp14]` — MakeCode-style display library for 8×8 WS2812b on YD-RP2040.

**Phase**: Genesis (sessions 1–2 per `reference/08-bootstrapping.md` § Phase 1).

**Key references**: `reference/00-overview.md`, `reference/08-bootstrapping.md`, `CONTEXT_HANDOFF.md` (exp14 root).

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

## 2026-04-17: Session 1 — [exp14]
- Technical insights:
  - `lib/display/bitmap_codec.pattern_to_colmajor` is a design-time authoring helper, not a runtime path; perf micro-optimizations are not worth structural complexity here.
  - `"".join(raw.split())` is the idiomatic whitespace-collapse in Python: handles all Unicode whitespace uniformly, avoids the chained `.strip()` + per-char `.replace()` anti-pattern.
  - Tier 1 pytest suite (78 tests) is green on CPython post-restructure — first PENDING item in handoff §7 "Tier 1" can move to DONE.
- Artifacts created/updated:
  - `lib/display/bitmap_codec.py`: fused two-phase rows-list-then-encode into a single pass; unified whitespace handling via `"".join(raw.split())`; fail-fast on row overrun; updated docstring + inline rationale comment.
  - `WORKING_STYLE.md`: recorded evidence-driven critique directive.
- Patterns extracted:
  - When a proposal is framed as "perf concern", quantify the concern (bytes, frequency, call site) before accepting or rejecting. If the cost is negligible *and* the alternative hurts readability/error-reporting, keep the readable version.
- Process corrections received: none.
- Open questions raised: none.

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
