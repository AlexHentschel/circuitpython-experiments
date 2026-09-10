<!--
DURABLE PERSONA COPY — corpus snapshot 2026-09-07.
Live recipe (optional, may move): /Users/alex/Git/rnd-ai-skills/generalized-agent-learnings/plan-refinement-loop.md
This file is a capability snapshot (recipe), not house source of truth.
House SOT: always-injected `.mdc` files + `memory/universal/WORKING_STYLE.md`.
Do not port corpus `verified` tier, flat TECHNICAL.md, 08-Genesis, symlink-fanout, or 11's literal tree into the house.
Fireable cue: WORKING_STYLE.md § Workflow. Do not market 'meta-plan' jargon to the user.
-->

# The Plan-Refinement Loop — Iteratively Drafting, Self-Reviewing, and Converging a Plan

**Status**: established process (heuristic blueprint, not law — see § 7). **Authored**: 2026-06-15.
**Audience**: a cold AI that knows only the files in this folder (`generalized-agent-learnings/`). Self-contained on
purpose. **Companion files**: `Flexible Plans for AI Execution.md` (how to author *one* plan), `cold-ai-paradigm.md`
(the write-time gate every persisted artefact must pass), `10-ADAPTIVE-MEMORY-STRUCTURE.md` (structural decisions as
experiments; content/structure distinction), `11-MULTI-PROJECT-BOOTSTRAP.md` (a large worked flexible plan).

## 0. One-line purpose

A reusable process for turning a planning goal into a high-quality plan by **iterating**: draft → self-review →
refine → converge, with **higher-level reflection, self-monitoring of progress toward the goal, and self-adaptation**
engrained into the loop rather than left to chance. `Flexible Plans for AI Execution.md` tells you what a good plan
*is*; this file tells you the *process that reliably produces and hardens one*.

## 1. The core idea

A first-draft plan is rarely the plan you should execute. Quality comes from a bounded loop of critical self-review
against fixed lenses, with each pass persisted so the improvement is auditable and a cold AI can resume mid-loop. The
loop is **convergence-bounded** (it stops at diminishing returns or a user-set hard cap) and **cold-AI-safe** (every
artefact it produces passes the four-question gate in `cold-ai-paradigm.md`).

Internally this loop is governed by a small **process artefact** (a "meta-plan" — the plan for refining the plan).

> **Communication discipline**: do **not** market the "meta-plan" concept to the user. Frame it plainly — *"I'll
> internally and autonomously iterate over the plan to refine it before we commit"*. Surface to the user only the few
> things that genuinely need their input (§ 2) and the final result. Keep the loop's internal jargon internal.

## 2. Setup — adapt the process to the specific goal (do this first)

Before iterating, make the loop fit the task. Two parts: a brief user confirmation, and an internal adaptation pass.

**Confirm with the user — briefly (this is the only routine user touchpoint of the setup):**
1. **Hard convergence cap** — the maximum number of refinement iterations. *Ask the user for this limit* (e.g. "I'll
   refine it over up to N internal passes"). The cap guarantees termination regardless of the diminishing-returns
   signal.
2. **Location** — where the iteration artefacts live (a working/scratch folder, kept separate from durable memory).
3. **Naming blueprint** — a one-line file-naming convention, confirmed in passing (e.g. `plan_vX.Y.md` +
   `notes_vX.Y.md`, final → `plan_v1.0.md`). Keep this confirmation to a sentence; it is a courtesy check, not a
   negotiation.

**Adapt internally (reflect on what THIS instance needs):** decide which optional pieces earn their place — a
domain-specific design rubric (a standing input the substance review checks against), extra review lenses beyond the
default three, a sub-agent plan (§ 5), an experiment log, a risk register. Right-size to the goal; do not bolt on
machinery a small plan doesn't need (parsimony — `10-ADAPTIVE-MEMORY-STRUCTURE.md`). Record the adapted loop in the
per-instance process artefact, which must itself carry a **cold-AI onboarding section** (an ordered required-reading
list) so whoever executes it can familiarize first, then act (§ 6).

## 3. The blueprint (heuristic structure — present it, then adapt within limits)

The steps below are **illustrative shape, not mandate**. The load-bearing commitments are the *targets* each step
serves (audit trail, bounded convergence, paradigm-compliance, no-bloat); the exact mechanics — file moves, ordering,
artefact count — are adaptable per § 7. Read `always`/`step-1`-style phrasing here as "the reinforced default", and
ask whether the situation in front of you is the one it was shaped for (`Effective Behavioral Guidelines.md`).

### 3.1 Artefacts

| Artefact | Role | Lifecycle |
|---|---|---|
| Process artefact (the governance file) | encodes the adapted loop + onboarding reading | stable across iterations |
| The plan `plan_vX.Y.md` | the deliverable | iterated by copy + increment |
| Notes `notes_vX.Y.md` | per-version self-review (AI-only, dense) | one per produced version (none for the initial draft) |
| Design rubric (optional) | standing substance-review reference | semi-stable |
| Experiment log (optional) | sub-agent / technique tuning | append-only |
| Final `plan_v1.0.md` | converged sign-off candidate | produced once at close |
| Risk register (optional) | irreducible-uncertainty escalation set | produced once at close |

### 3.2 Versioning

`v0.0` = initial draft. Each iteration bumps the minor (`v0.1`, `v0.2`, …). The converged result is promoted to
`v1.0` at the close. The cap is expressed in minor versions (e.g. cap 5 → `v0.5` max → 6 plan files including `v0.0`).

### 3.3 The iteration loop (produce v(N) from v(N-1))

This is the closed-loop cycle from `Flexible Plans for AI Execution.md` (Observe → Evaluate → Revise → Continue),
made concrete:

1. **Copy** `plan_v(N-1).md` → `plan_v(N).md`; increment the version header. (The prior version stays intact as audit
   trail; the diff between consecutive files is the applied revision.)
2. **Create `notes_v(N).md`** and run the reviews below **in order**, each appending a section. Record findings
   compactly as `location → problem → change (what + how)`. Apply `cold-ai-paradigm.md` to the notes themselves —
   they are persisted AI-only artefacts.
3. **Append a Change-Magnitude Summary** to the notes (§ 3.5) — the convergence signal.
4. **Apply** the notes' changes into `plan_v(N).md`.
5. **Evaluate convergence** (§ 3.6) and **reflect audibly**: state, in the notes, either "here's what I'd revise next"
   or "nothing changes, continuing" — never leave the reflection silent (a skipped reflection looks identical from the
   outside but compounds drift; `Effective Behavioral Guidelines.md`). Surface this reflection to the user only at the
   § 2 / § 3.7 touchpoints, not every pass. → continue or run the close (§ 3.7).

### 3.4 The reviews (default three; ordered substance → form → economy)

The order is load-bearing — it mirrors the editing pipeline structural-edit → line-edit → trim, minimizing rework:

- **R1 — Substance / goal-fit (FIRST)**: does the plan's *core design actually achieve the goal*, and is it
  **adaptive** to information that will surface during execution (not over-committed)? This lens is the most
  instance-specific — define it from the goal. (Example: for a memory-restructuring plan, R1 = "does the target
  structure give efficient cold-AI retrieval and adapt as content grows?", checked against a design rubric.) R1 runs
  first because it can trigger the largest rewrites; doing it first means the later passes polish stable content.
- **R2 — Paradigm-compliance (SECOND)**: (a) **cold-AI gate** — every block decodable, purpose clear, signals
  present for forward-looking items, lifecycle/status stamped, how-to-check-status for anything verifiable later
  (`cold-ai-paradigm.md`); (b) **flexible-plans gate** — layered commitment present (fixed targets/constraints/
  known-unknowns/checkpoints/exit-ramps/authority-map; provisional-labelled approach/initial-criteria; open artifact
  shape), checkpoints with criteria-revision gates, diminishing-returns termination, scope-expansion escalates,
  sketches marked as hypotheses (`Flexible Plans for AI Execution.md`).
- **R3 — Focus / economy vs prior version (LAST)**: still focused, still carrying all necessary context, but **not
  accreting context-bloat**? Net out R1+R2 additions: for each, ask "does this earn its context cost, or can it
  compress / move to a standing reference / be cut?". Runs last because R1 and R2 *add* material — trimming earlier
  then re-adding is churn. Apply the § 3.8 economy model: cut pre-committed shape execution can deduce, keep targets +
  the reflection/adaptation machinery; a lean plan is the goal, not a maximally-complete one.

Within a single iteration the executing AI has full context, so R2's decodability is a property it *checks*, not a
precondition for its own reviewing — hence substance-first is safe. Review lenses are adaptable per instance (add a
domain lens, split R1) within the deviation limits of § 7.

### 3.5 Change-Magnitude Summary (the convergence signal; appended to each notes file)

A mechanical signal a cold AI reads to judge diminishing returns without re-diffing:
- **Breadth**: count + names of plan sections changed this iteration.
- **Depth** by tier (highest present is what matters): `T3 structural` (target/constraint/phase/core-design change) ·
  `T2 substantive` (criteria, authority, exit ramps, known-unknowns, open-decisions) · `T1 clarity` (wording/
  decodability/layering, no behaviour change) · `T0 cosmetic`.
- **Goal-adequacy unknowns discharged**: count + one-line each (questions about whether the plan is *good enough*
  that this pass answered).
- **Trend vs v(N-1)** and a **verdict**: `converging` / `converged` / `not-converged`.

### 3.6 Convergence & termination

Two stopping conditions, whichever fires first:
- **Converged (diminishing returns)**: an iteration shows highest depth tier ≤ `T1 clarity`, zero goal-adequacy
  unknowns discharged, and a non-increasing trend. If borderline, run **one** more pass to confirm (don't stop on a
  single ambiguous reading).
- **Cap (hard upper bound)**: the user-set iteration limit. At the cap, stop regardless; if still `not-converged`,
  do not spin — exit and surface the unresolved sticking points to the user in the close.

### 3.7 Post-loop close

1. **Promote**: copy the final version → `plan_v1.0.md` (the sign-off candidate).
2. **Risk scan (if used)** → a risk register. Scan all notes (and v1.0) for the **technically riskiest items that
   cannot be resolved by *executing* the plan** — irreducible a-priori judgment calls and assumptions, NOT normal
   known-unknowns that execution will reveal (those are handled by checkpoints). For each: the assumption/choice ·
   why execution won't settle it · blast radius if wrong · disposition in the plan (decided / open / **MISSING**) ·
   recommended hedge or escalation. Explicitly flag high-risk items absent from the plan as `MISSING`.
3. **Present** v1.0 (+ risk register) to the user. Any decisions reserved for the user's authority stay OPEN with
   options + a recommendation, never silently decided.

### 3.8 Parsimony vs necessary context (keep the plan lean — the economy model)

**Principle (load-bearing)**: keep the plan **lean** — commit the *fixed layer* (targets, constraints, checkpoints, the
reflection/adaptation loop) and leave shape + step detail **open**, derived at each checkpoint from execution results.
Leanness is safe *only because* that loop is explicit: it carries what a fat plan would pre-specify.

*Why lean, not just "not bloated":* a plan is task-scoped (read once during execution), so plan-bloat is far cheaper than
*memory*-bloat (loaded every session forever, where retrieval-efficiency outranks parsimony — a different cost model).
Stay lean anyway because of **surface area**: every up-front detail is surface to **over-prescribe** (bake in shape the
situation later contradicts) and **over-harness** (remove execution latitude). Lean ⇒ more efficient *and* more flexible.
(`Effective Behavioral Guidelines.md` *protect target, leave shape to the situation*; `Flexible Plans for AI Execution.md`
layered commitment; cues at § 3.3 step 5 · § 3.5 · § 4.)

- **R3 trim test (operational)**: per detail ask — *load-bearing for a target / constraint / checkpoint, or pre-committed
  shape execution can deduce?* Cut the latter, keep the former. **Never trim the reflection / monitoring / adaptation
  expressions** — they license the leanness; cutting them yields an under-specified plan, not a lean one.
- **Notes economy**: notes are per-version (`notes_vX.Y`), AI-only, **not** carried as live context into later iterations
  (only the closing risk scan, § 3.7, reads the full history). Accreting notes don't tax later passes; only the plan is
  the carried artefact kept lean.

## 4. What gets engrained (the point of the loop)

- **Higher-level reflection**: R1 forces a goal-fit judgment each pass, not just local fixes.
- **Self-monitoring of progress**: the Change-Magnitude Summary makes "are we still improving?" an explicit, persisted
  measurement.
- **Self-adaptation**: the loop revises the plan audibly each pass (Revise step), and the setup adapts the loop
  itself to the goal; sub-agent usage is tuned during execution (§ 5).

## 5. Sub-agents (optional accelerator)

When a planning instance involves crawling/extracting from many documents or notes, sub-agents help. Two classes:
- **Localized knowledge extraction** (high-volume, low-judgment scanning/inventory; read-only) → a
  **`composer-2.5`-class** model (or newer of that type), as a read-only explore sub-agent. Output: structured
  extraction only; no decisions.
- **Higher-level reasoning / learning distillation / decisions** (design, adjudication, the reviews, the risk scan) →
  an **`opus-4.8`-class** model (or newer of that type), or the parent agent directly.

**Cost gate**: sub-agents may incur API cost. If sub-agents seem *significantly* useful for an instance, **inform the
user before relying on them** (propose the two model classes above and what each will do). Do not silently spin up
costly sub-agent fleets.

**Per-dispatch discipline**: state the precise expected deliverable *before* dispatch; after it returns, self-audit
(Observe → Evaluate against the expectation: complete? accurate? right model class? → Revise the spec / switch class /
re-run → Continue); log the dispatch + verdict in the experiment log. Treat sub-agent usage as a hypothesis refined
during execution — accrete what works into a "current best practice" note rather than guessing the right prompts up
front.

## 6. Cold-AI onboarding requirement (for the per-instance process artefact)

The process artefact you write for an instance must let a fresh AI onboard before acting. Include an ordered
**required-reading** list: must-reads (this file; `Flexible Plans for AI Execution.md`; `cold-ai-paradigm.md`; the
current plan version; any design rubric) and read-as-needed (the source material the plan operates on). Reference,
do not duplicate — point at the source. State the floor ("read these first"), and that reading beyond it is
encouraged when context demands.

A working onboarding section unlocks a useful capability: the loop can be **handed to a fresh cold-AI chat** (same
persona/memory, no shared history) via a kickoff prompt that *references, never copies*, the process artefact + plan +
paradigm files. The exemplary instance (§ 8) was run this way. The test that onboarding is sufficient: a cold chat can
reach a correct first action reading only the referenced files.

## 7. Heuristics, not laws (bounded deviation)

This blueprint is the accumulated sense of what works — a heuristic, not a statute. The AI adapting it to a specific
planning instance **may deviate** when there is good reasoning (need not be conclusive) that deviating is likely
beneficial. Record every deviation with its rationale in the process artefact.

**This blueprint is itself an inherited spec — treat it (and any template/mandate the plan operationalizes) as an
adaptable prior, not a source of truth that wins by default.** When it conflicts with the live situation, present both
sides (what the inherited spec says, what the situation argues), let the deciding authority pick, and retain the losing
side with a dated note so the decision history survives (`Effective Behavioral Guidelines.md` — *contradictions have no
default winner*). Blind compliance and blind override are mirror failures.

**Invariants that should NOT be dropped** (deviation limits):
- The cold-AI gate on every persisted artefact (`cold-ai-paradigm.md`).
- Flexible-plans layered commitment in the plan itself.
- A convergence bound (a user-confirmed hard cap) so the loop terminates.
- An audit trail: versioned plan files + per-version notes, so improvement is reconstructable and a cold AI can resume.
- Reserving authority decisions for the user (escalate, don't silently decide).

Everything else — number and definition of review lenses, presence of a design rubric / experiment log / risk
register, sub-agent usage, file granularity — is adaptable.

## 8. Exemplary artifact

`exemplary-artifacts/warm-reset-plan_META.md` is one concrete adaptation of this process: the planning of a
multi-project memory restructuring ("warm reset"). Study it as a worked instance. Instance-specific choices visible
there (illustrating § 2 adaptation): R1 was specialized to *retrieval-efficiency + adaptivity of a memory structure*
and checked against a bespoke design-rubric file; a federated second project drove extra open decisions (its
`D1–D7` escalation set); the change-magnitude tiers were tuned to plan-structure edits; sub-agents were assigned
(composer-class crawl / opus-class reasoning) with an experiment log. Note: that artefact references files in a
specific workspace (absolute paths) — those are part of *its* instance, not part of this general process.

## 9. Recursive self-application & provenance

This file must pass `cold-ai-paradigm.md`'s test: every term is grounded inline or cross-referenced; its purpose is
stated (§ 0); its signals are the convergence/verdict mechanics (§ 3.5–3.6); its lifecycle is stamped (status +
date). It is the generalization of the warm-reset planning loop (the exemplary artifact), distilled 2026-06-15 from a
session that built that loop under the cold-AI + flexible-plans paradigms. If a future instance finds the blueprint
mis-fits a class of planning goals, revise this file (with provenance) rather than silently working around it.

**Signals this blueprint itself needs revision** (so the self-claim above is falsifiable, per `cold-ai-paradigm.md § 7`):
- Instances deviate (§ 7) on the *same* point across ≥2 unrelated planning goals → fold that deviation into the
  blueprint; the "default" was wrong.
- Convergence (§ 3.6) never trips before the user-set cap across multiple instances → the change-magnitude criterion is
  miscalibrated (too strict); loosen it or revisit the depth tiers.
- The risk scan (§ 3.7) routinely surfaces nothing, or routinely surfaces items the plan already handled via
  checkpoints → the irreducible-vs-execution-resolvable boundary in § 3.7 needs sharpening.
How to check: scan the per-instance process artefacts + their notes/experiment logs for these patterns at the next
time this file is reviewed.

## Cross-references

- `Flexible Plans for AI Execution.md` — authoring a single flexible plan (the per-plan discipline this loop wraps).
- `cold-ai-paradigm.md` — the write-time gate applied to every artefact this loop produces.
- `10-ADAPTIVE-MEMORY-STRUCTURE.md` — structural decisions as experiments; parsimony; content/structure distinction.
- `11-MULTI-PROJECT-BOOTSTRAP.md` — a large worked flexible plan (and the multi-project structures the exemplary instance targets).
- `exemplary-artifacts/warm-reset-plan_META.md` — a concrete adaptation of this process.
