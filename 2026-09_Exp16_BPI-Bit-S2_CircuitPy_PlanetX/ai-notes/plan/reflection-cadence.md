# Reflection + learning-extraction cadence (fixed constraint)

**Status:** standing plan constraint. Applies to **planning and execution, every stage**, not only phase close. **Date:** 2026-09-03.
**Purpose:** stop learnings from dying in chat. Every meaningful checkpoint must Observe → Evaluate → Revise-or-no-change **and** extract/distill/record. Silence at a checkpoint is the failure mode.
**Authority:** target-preserving API tweaks autonomous; changes to the *student-API stability target* or to these cadence rules escalate to Alex.
**How to check:** grep the current plan + session notes for checkpoint outcomes; each listed gate has a dated Observe/Evaluate/Revise line plus a learning record (or explicit "nothing to extract").

Corpus (read on demand, do not copy):  
`/Users/alex/Git/rnd-ai-skills/generalized-agent-learnings/Flexible Plans for AI Execution.md`  
`/Users/alex/Git/rnd-ai-skills/generalized-agent-learnings/plan-refinement-loop.md`  
`/Users/alex/Git/rnd-ai-skills/generalized-agent-learnings/09-RECURSIVE-LEARNING.md`  
Persona: `WORKING_STYLE.md` *Reflect explicitly at every meaningful checkpoint* + *Flexible-plan layered commitment*.

---

## What is fixed vs provisional

| Layer | Commitment |
|-------|------------|
| **Fix** | Cadence exists; every gate is audible; learnings get written; design guidelines in `../design/student-api-portability.md` are re-opened at gates, not only when something breaks |
| **Provisional** | Exact phase list of the execution plan (arrives when that plan is drafted) |
| **Open** | File names of future learning entries; whether a sub-agent runs the extract step |

Create `../learnings/` on first real entry (accumulate-then-split). Promote durable items to persona `projects/circuitpython-exp16-planetx/` or `universal/` via the placement gate — conversation does not persist.

---

## Required gates (minimum set; execution plan may add, not remove)

At **each** gate: (1) Observe what execution/planning revealed; (2) Evaluate targets / constraints / known-unknowns / criteria / approach, **and** "are the criteria still the right ones?"; (3) Revise the plan *or* write "no change, continuing"; (4) **Extract** — what guideline confirmed/refuted, what TODO, what API leak; (5) **Record** — `learnings/` and/or persona memory; (6) Continue.

| Gate | When | Must re-open |
|------|------|----------------|
| P-plan | Each plan-refinement loop pass (when drafting/revising the execution plan) | this file + portability guidelines |
| P-phase | Close of every execution phase | portability G1–G7; load-bearing A1–A4 |
| P-api | First time a student-facing name is introduced or changed | G1–G4; "would this survive RP2350+8×8?" |
| P-device | First on-device run; any time the board wedges / needs physical reset | A2 (`keypad`/asyncio on 10.3.0); toolchain notes |
| P-human | Each planned human-test window | which checks only a human can do (font legibility, button feel) |
| P-surprise | Any contradiction with a plan assumption | escalate if target/constraint; else record both sides |
| P-done | Milestone declared done | distill: keep / drop / refine each Gi; list student-sketch edit budget |

**Diminishing returns:** a gate that produces no revision *and* no discharged known-unknown *and* no new learning still writes "nothing to extract". That statement *is* the record.

**Do not skip** the extract step because the primary task felt done (`09-RECURSIVE-LEARNING.md` crowding). If the turn is too full, a short `learnings/` stub + "expand next gate" beats silence.

---

## Learning record shape (cold-AI)

One block per extract:

- **Claim** (one line)
- **Evidence** (path, on-device, or "hypothesis only")
- **Status** (`unverified` / `evidence-supported` / `refuted`)
- **Guideline touched** (`G#` / `A#` / none)
- **Action** (keep / refine / drop / escalate)
- **Date**

---

## When the execution plan is drafted

The execution plan **imports** this file (link, do not duplicate). It must list its phases with these gates attached. It must **not** treat this cadence as optional flavour. Plan-refinement loop still needs Alex's hard iteration cap when that loop starts — ask then, not in this file.
