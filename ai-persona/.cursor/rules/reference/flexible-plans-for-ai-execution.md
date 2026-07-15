<!--
DURABLE PERSONA COPY. Source: /Users/alex/Developed/AI/generalized-agent-learnings/Flexible Plans for AI Execution.md
(that folder is ephemeral — do not depend on it; this copy is authoritative). Copied verbatim 2026-06-14.
Operational trigger form (the fireable directive): WORKING_STYLE.md § Core Principles "Flexible-plan layered commitment",
which cross-references the pre-existing siblings "Pre-commit to targets, not shape" and "Reflect explicitly at every
meaningful checkpoint". This file is the reference form: read it when drafting or executing a multi-phase plan.
-->

# Flexible Plans for AI Execution

Compressed calibration for drafting plans executed by agents under closed-loop feedback, where the full evaluation criteria cannot be known at draft time because execution itself will surface new understanding. Receiver shares vocabulary and disposition; what follows is the accumulated sense of where plans quietly fail under autonomous execution.

## Structural tension

A plan executed by an agent must be two things at once:

- **Executable now** — decidable enough that the agent can take action without constant human interpretation.
- **Gracefully revisable** — structured so that new learnings surfaced during execution *update* the plan rather than being absorbed, ignored, or post-hoc rationalised.

These pull in opposite directions. Over-specified plans are executable but calcify; under-specified plans preserve flexibility but leave the agent without decidable next actions, producing drift or stalling. The resolution is **layered commitment**: pre-commit to targets and constraints, provisionally commit to approach and initial criteria (labelled as such), and leave artifact shape and step sequences to be decided per-situation by the executing agent.

## What to fix, label provisional, or leave open

**Fix (load-bearing, changes require authority escalation)**:

- **Targets** — outcomes, not artifacts.
- **Constraints** — invariants that must hold (safety, scope, authority handoffs, quality floors).
- **Known unknowns** — explicitly listed investigation targets the plan is designed to resolve.
- **Checkpoints** — where audible reassessment fires.
- **Exit ramps** — conditions that pause execution for plan revision rather than continuing.
- **Authority handoff map** — which decisions the agent takes autonomously vs. which escalate.

**Provisional (label as such; expected to evolve)**:

- **Approach / method** — investigation or construction direction.
- **Initial success criteria** — explicitly marked *initial*, revisable.
- **Design sketches, artifact proposals** — only as labelled *hypotheses* or *starting points for critical evaluation*, never as commitments.

**Don't fix**:

- Artifact shape (file layouts, function signatures, module structure, exact wordings).
- Step sequences beyond the first atomic next action.
- Criteria for properties that can only be evaluated after the system exists.

A plan that fixes too much becomes a script the agent follows regardless of what execution reveals. A plan that fixes too little lacks decidability and surfaces into the human layer for every choice.

## Evaluation criteria evolve — design for it

Some evaluation criteria are unknowable at draft time because the problem-from-inside is not yet visible. Pre-committing the full criterion set forces one of three failures:

- **Post-hoc rationalisation** — new criteria retrofitted as if always intended; decision history lost.
- **Criterion lock-in** — new criteria dismissed because they weren't in the plan; execution converges on the wrong surface.
- **Premature closure** — execution terminated when pre-committed criteria are met in a shallow sense that misses what now matters.

Mitigations:

- Mark every initial criterion *initial*; expectation of revision is explicit, not implicit.
- Include a **criteria-revision gate** at every checkpoint: *are the criteria still the right ones?* Answered audibly, not silently.
- Record newly-surfaced criteria with dated provenance (*what execution revealed this*) so deciding authority can evaluate adoption on evidence.
- Tag **load-bearing assumptions** (ones the plan's validity rests on) distinctly from peripheral ones; revisit load-bearing first when evidence arrives.

## Closed-loop cycle structure

Each loop iteration — phase, audit-revise cycle, spike — has four explicit moves:

1. **Observe** — what did execution reveal? New facts, contradictions, surprises, dead-ends, unexpected easy wins.
2. **Evaluate** — does this change targets, constraints, known unknowns, criteria, or approach? (If yes → which category; this routes the revision.)
3. **Revise** — state out loud either the specific plan change *or* explicit no-change ("nothing changes, continuing"). Silence at a revision gate is the default failure.
4. **Continue** — with the updated plan, explicitly.

Termination by **diminishing returns**, not iteration count. Iteration count is a fallback guard against non-termination, not the primary criterion. Diminishing returns means the latest loop produced no revision and no new known-unknown was discharged — if this is uncertain, iterate once more before terminating.

## Authority handoffs

Specify explicitly, at draft time, which kinds of decisions the agent takes autonomously during execution and which escalate:

- **Target-preserving adjustments** (different approach, artifact, or ordering that still serves the committed target under committed constraints) — autonomous.
- **Criterion additions** surfaced by execution — escalate for adoption decision; provisionally continue only if they don't conflict with existing criteria.
- **Scope changes, target revisions, load-bearing-assumption invalidations, contradictions with plan assumptions** — escalate; never silently absorb.

**Scope discipline under surprise**: when execution reveals that work is bigger than planned, surface the discovery and propose a plan revision *before* expanding. Silent scope expansion is the single most common way closed-loop autonomous execution produces drift.

## Failure modes

| Symptom | Root | Fix |
|---|---|---|
| Plan reads as script; agent executes steps regardless of what is revealed | Over-specified shape; target not separated from approach | Rewrite with explicit target / constraint / known-unknown / initial-approach layers |
| Agent silently expands scope when execution surfaces adjacent work | No exit ramp or escalation clause for scope change | Add authority handoff: scope changes require check-in |
| New criteria emerge but are absorbed without notice | No criteria-revision gate; criteria not marked *initial* | Add gate at every checkpoint; label initial criteria as such |
| Loop iterates indefinitely | No termination heuristic; or agent can't recognise diminishing returns | Specify diminishing-returns signal + iteration-count fallback |
| Loop terminates too early | Shallow criterion satisfaction; agent optimising the pre-committed surface | Require audible revision statement before declaring phase done |
| Design sketches in plan become de facto commitments | Hypothesis framing absent; register drifted from *might* to *will* | Explicit markers on every sketch; receiving agent prompts authority if marker is missing |
| Checkpoint passes without revision statement | Reflection silently skipped | Enforce: every checkpoint produces either a specific revision or explicit no-change |
| Contradiction between plan assumption and new finding absorbed without decision | New-is-right / old-is-right bias; no contradiction-handling clause | Escalate with both sides and evidence; authority decides; losing side retained with dated note |
| Execution bypasses the plan entirely ("planning was just the setup") | Plan treated as artefact, not control surface | Treat plan as living document; revision is the steady state, not the exception |

## Right-sized phases

Phase size should match the expected rate of new-learning surface. Too small → revision overhead dominates real work. Too large → drift accumulates before the revision gate fires. Signals:

- Phases running long with no new learnings → likely mechanical; compress or merge.
- Phases producing revisions every few minutes → likely too large; decompose at the learning-rate frequency.
- Phases whose known-unknowns are mostly unresolved at end → phase was correctly sized but approach was wrong; revise approach, not phase size.

## Distillation

> A flexible plan pre-commits to **targets, constraints, and reflection cadence**; labels its **approach and initial criteria provisional**; leaves **artifact shape to the situation**; and specifies **which decisions escalate**. Its execution produces one of two audible outputs at every checkpoint: a specific revision, or explicit no-change. Silence at a checkpoint is the primary failure mode.
