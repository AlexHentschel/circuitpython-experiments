# Cross-project index — BY PATTERN

**Purpose**: the promotion-ladder working surface. Tracks *candidate* cross-project patterns — recurrences of technique, process, or directive seen in one project that *might* generalize — before they earn a place in `universal/PATTERNS.md` (generalized patterns) or `universal/WORKING_STYLE.md` / `CODING_PRINCIPLES.md` (behavioral/coding directives). Read this when you notice a second occurrence of something you've seen before; record the first occurrence here so the second can trigger promotion.

**Promotion ladder**: `[project]` observation → here as a candidate (1 occurrence) → on 2nd project occurrence, promote to `universal/PATTERNS.md` (if technique/process) or the relevant `universal/` directive catalog (if behavioral/coding), tagged `[cross-experiment]`/`[user]`/`[universal]` → demote/retire if a counterexample surfaces. This file holds **candidates and their occurrence counts**, not the promoted statements themselves.

> Working surface for **candidates** (seed-on-evidence). First confirmed pattern promoted 2026-09-04 → `universal/PATTERNS.md`. Remaining candidates may stay sparse; emptiness of *this* file is no longer true. Refute of this index = a pattern recurred across projects but had no candidate row here to trigger promotion.

## Candidate patterns (occurrence log)

| Candidate pattern | Type | Seen in | Occurrences | Promotion target when 2nd occurrence lands |
|-------------------|------|---------|-------------|---------------------------------------------|
| "Audit + broad consistency sweep" as a phase-close ritual | process | exp14 (P1/P2 close) | 1 | `universal/WORKING_STYLE.md` if it recurs in another project's phase close (open Q carried in exp14 CONTEXT) |
| Preallocate-and-mutate-in-place for hot loops | coding/technique | exp14 (render buffers) | 1 (within one project) | Already a `concepts/circuitpython-runtime.md` entry; promote to `CODING_PRINCIPLES.md` only if it shows up as a *cross-language* habit, not just CircuitPython |
| Bind module-globals to function-locals in hot loops | coding/technique | exp14 (`_render_colmajor`) | 1 | Same as above — CircuitPython-specific for now (concept), watch for non-MPy recurrence |
| Public-repo third-party-material hygiene: confirm the grant before commit; either gitignore (default not-redistributable) or vendor **with attribution + license sidecar** so a repo-root LICENSE cannot swallow the file | process | coding-tutor (2026-07-15: gitignore papers + `REFERENCES.md`); exp16 (2026-09-04: BananaPi goldfinger JPEG + `.license` sidecar under CC BY-SA) | **2 — promoted 2026-09-04** | `universal/PATTERNS.md` `[cross-experiment]` (this row retained as provenance) |
| Apply the plan-refinement-loop **retrospectively** to an already-executed artifact (prediction vs. reality + lesson distillation), not just pre-use polishing — discovered mid-loop when the artifact under review turned out to have already been used | process | ai-persona tooling / exp16 (2026-09-11: `handoff_v0.0.md` vs. Session 17, `ai-notes/handoff-prompt-refinement-2026-09-11/`) | 1 | `universal/PATTERNS.md` `[cross-experiment]` on 2nd occurrence in another project; if it recurs, also revise `reference/plan-refinement-loop.md` itself per its own §9 self-revision signals (single-instance deviation — not folded into the blueprint yet, per that file's ≥2-occurrence bar) |

One pattern promoted 2026-09-04 (public-repo third-party hygiene) → `universal/PATTERNS.md`. Remaining candidates still at 1 occurrence.
