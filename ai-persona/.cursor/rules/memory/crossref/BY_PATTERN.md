# Cross-project index — BY PATTERN

**Purpose**: the promotion-ladder working surface. Tracks *candidate* cross-project patterns — recurrences of technique, process, or directive seen in one project that *might* generalize — before they earn a place in `universal/PATTERNS.md` (generalized patterns) or `universal/WORKING_STYLE.md` / `CODING_PRINCIPLES.md` (behavioral/coding directives). Read this when you notice a second occurrence of something you've seen before; record the first occurrence here so the second can trigger promotion.

**Promotion ladder**: `[project]` observation → here as a candidate (1 occurrence) → on 2nd project occurrence, promote to `universal/PATTERNS.md` (if technique/process) or the relevant `universal/` directive catalog (if behavioral/coding), tagged `[cross-experiment]`/`[user]`/`[universal]` → demote/retire if a counterexample surfaces. This file holds **candidates and their occurrence counts**, not the promoted statements themselves.

> **PROVISIONAL (2026-06-14 warm reset).** Empty of confirmed cross-project patterns by design (seed-on-evidence). Watch-for: see `concepts/_INDEX.md` header. Refute = a pattern recurred across projects but had no candidate row here to trigger promotion.

## Candidate patterns (occurrence log)

| Candidate pattern | Type | Seen in | Occurrences | Promotion target when 2nd occurrence lands |
|-------------------|------|---------|-------------|---------------------------------------------|
| "Audit + broad consistency sweep" as a phase-close ritual | process | exp14 (P1/P2 close) | 1 | `universal/WORKING_STYLE.md` if it recurs in another project's phase close (open Q carried in exp14 CONTEXT) |
| Preallocate-and-mutate-in-place for hot loops | coding/technique | exp14 (render buffers) | 1 (within one project) | Already a `concepts/circuitpython-runtime.md` entry; promote to `CODING_PRINCIPLES.md` only if it shows up as a *cross-language* habit, not just CircuitPython |
| Bind module-globals to function-locals in hot loops | coding/technique | exp14 (`_render_colmajor`) | 1 | Same as above — CircuitPython-specific for now (concept), watch for non-MPy recurrence |

_No pattern has reached 2 project-occurrences yet; `universal/PATTERNS.md` remains empty (correct under seed-on-evidence)._
