# Plan-refinement loop — instance setup (Exp16)

**Status:** loop **closed** 2026-09-04 (`plan_v1.0.md`). **Date:** 2026-09-04.
**Purpose:** a cold AI can start the loop without re-asking the §2 setup questions. Historical: start after digests (spent).
**How to check:** `plan_v1.0.md` exists ⇒ loop closed. Do not start a second loop unless Alex asks.

Corpus (read on demand, do not copy):  
`/Users/alex/Git/rnd-ai-skills/generalized-agent-learnings/plan-refinement-loop.md` (§2 setup, §3 blueprint, §5 sub-agents)  
`Flexible Plans for AI Execution.md` · `cold-ai-paradigm.md` · `working-notes-lean-context.md`  
Persona: `plan/reflection-cadence.md` (import, do not copy into the execution plan).

---

## Locked (Alex, 2026-09-04)

| Item | Value |
|------|--------|
| Hard convergence cap | **8 iterations** after `v0.0`. Cap is minor versions: `v0.8` max, then promote `plan_v1.0.md`. 9 plan files including `v0.0` if the cap is hit. Stop earlier on diminishing returns (`plan-refinement-loop.md` §3.6). At cap still `not-converged` → close and surface sticking points; do not spin. |
| When to start | After `ai-notes/digests/` exist (and the Exp14 `lib/display/` copy is in the Exp16 tree). Handoff 2026-09-04 authorized the executing chat to start the loop on own judgement at that point. Prerequisite from the 2026-09-04 clarification (“not this turn”) is **spent**. |
| Sub-agents | Authorized. Extraction → `composer-2.5`-class (read-only, structured extract, no decisions). Reviews / distillation / risk scan → parent or stronger reasoning class. Wrapper returns: short summary in chat + full payload on disk (`working-notes-lean-context.md` §4). Log each dispatch in an experiment log once the loop exists. |

## Location + naming (proposed default — courtesy lock unless Alex objects)

| Artefact | Path |
|----------|------|
| Plans + per-version notes | `ai-notes/plan/plan_vX.Y.md`, `ai-notes/plan/notes_vX.Y.md` |
| This process artefact | `ai-notes/plan/loop-setup.md` (this file). Loop may add `_META.md` onboarding list at start. |
| Sub-agent briefs / returns | `ai-notes/briefs/`, `ai-notes/returns/` (lean-context layout; create on first dispatch) |
| Design rubric | already: `ai-notes/design/student-api-portability.md` (R1 standing input) |
| Cadence (import) | `ai-notes/plan/reflection-cadence.md` |

Final → `plan_v1.0.md`. Present v1.0 + irreducible-risk scan to Alex (corpus §3.7) before execution of the PoC, unless he later waives that touchpoint.

## Must live *inside* the execution plan (cold-AI digest, not a dump)

When the loop runs, the plan itself carries a **short digest + pointers** (further reading, not pasted corpus):

- Chat = cache; detail on disk; resume = `INDEX.md` + `NOTES.md` (`working-notes-lean-context.md`)
- Layered commitment + audible checkpoints (`Flexible Plans for AI Execution.md`)
- Destructive-ops hard gate + Exp16 park (`destructive-operations.md`; `ai-notes/_parked/`)
- Reflection + extract at every gate (`reflection-cadence.md`; `09-RECURSIVE-LEARNING.md`)
- Router for anything else: corpus `README.md` / `00-OVERVIEW.md`

## Not decided here

Overnight bar, button smoke, font, copy timing — **locked 2026-09-04** in `../NOTES.md` (same-day question round).
