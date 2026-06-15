# META — warm-reset planning loop governance

Consumer: AI only (future cold instance resuming this loop). Dense-by-design. This file governs the *iterative
planning loop*; it is NOT the warm-reset plan and NOT the warm-reset content. Stable across iterations — edit only
to change the loop itself. Provenance: created 2026-06-14, Bamboo-Lamp session 1, at Alex's request to plan Option B
(the `warm reset` mandate) under the cold-AI + flexible-plans paradigms.

## What is being planned (one line)

A plan to execute the `warm reset` mandate (`/Users/alex/Development/VsCode/CircuitPython/.cursor/rules/mandates/multi-project.md`):
reorganize the flat `.cursor/rules/memory/` into a multi-project layout. The plan is the deliverable; executing the
warm reset is OUT OF SCOPE here and additionally gated on Alex saying the exact phrase "warm reset" + confirmation.

## Context & required reading (cold-AI onboarding — do this FIRST)

You (a cold AI) cannot rely on chat history; the files below are the only context. **Read the must-reads before
touching the loop**, then read the as-needed files when a step touches their subject. This section *references*, it
does not duplicate — go to the source. Paths are workspace-relative to `/Users/alex/Development/VsCode/CircuitPython/`
unless absolute.

**Must-read (load-bearing — read in this order):**
1. `_META.md` (this file) — the planning loop you will execute.
2. `working-docs/warm-reset-plan/microcontroller-multi-project-memory-guidelines.md` — the retrieval-optimized, parsimony-favouring design rubric the plan's target structure must satisfy (R1 checks against it).
3. `working-docs/warm-reset-plan/warm-reset-plan_v<latest>.md` — the current plan draft (highest minor version present; or `v1.0` if the loop has closed).
4. `.cursor/rules/mandates/multi-project.md` — the mandate being operationalized (its §Warm-Reset-Protocol steps, §Pre-execution-review divergences, OQ1–3, and its pre-flight checklist are the spec; on conflict the mandate wins unless the plan records an Alex-approved deviation).
5. `.cursor/rules/reference/flexible-plans-for-ai-execution.md` and `.cursor/rules/reference/cold-ai-paradigm.md` — the two paradigms every review applies (R2). Durable copies; do not depend on the ephemeral `~/Developed/AI/generalized-agent-learnings/` originals.

**Read as-needed (when a step/phase touches them):**
- `.cursor/rules/memory/{WORKING_STYLE,CODING_PRINCIPLES,SESSION_LOG,TECHNICAL,CONCLUSIONS,MONITORING,CHANGELOG}.md` — the content the warm reset will move/tag (the actual material being restructured).
- `.cursor/rules/{00-memory-system,02-domain-structure,03-memory-update-triggers}.mdc` — always-injected rules that reference memory paths and must be updated by the warm reset.
- `/Users/alex/Projects/Family/Bamboo-Lamp/memory/` (README + SESSION_LOG + CONCLUSIONS) and `/Users/alex/Projects/Family/Bamboo-Lamp/AI-Notes.md` — the federated second project (D7).
- `.cursor/rules/reference/06-failure-modes.md` §§ F1/F8/F10 — required by the mandate's pre-flight before any structural execution.

You are encouraged to read beyond this list when context demands it — the list is the floor, not the ceiling.

## Artifacts + naming

| Artifact | File | Lifecycle | Consumer |
|---|---|---|---|
| Loop governance (this) | `_META.md` | stable | AI |
| Design rubric (standing input) | `microcontroller-multi-project-memory-guidelines.md` | semi-stable (revise if a better structure principle emerges) | AI |
| The plan | `warm-reset-plan_vX.Y.md` | iterated (copy + increment); capped at `v0.5` | AI now; Alex at sign-off |
| Per-iteration review notes | `notes_vX.Y.md` | one per produced version (none for v0.0); ends with Change-Magnitude Summary | AI only |
| Sign-off candidate | `warm-reset-plan_v1.0.md` | produced once, at Post-loop close (`cp` of final converged version) | Alex |
| Risk register | `risk-register.md` | produced once, at Post-loop close (cross-notes scan) | Alex (escalation set) |
| Experiment log | `experiment-log.md` | append-only across the whole effort; top "current best practice" block evolves | AI only |

**Preliminary analysis (done once, before iterating; output = the guidelines doc above)**: distilled `generalized-agent-learnings` files `11-MULTI-PROJECT-BOOTSTRAP` + `10-ADAPTIVE-MEMORY-STRUCTURE` into `microcontroller-multi-project-memory-guidelines.md` — the retrieval-optimized, parsimony-favouring design rubric the plan's target structure is reviewed against. Re-distill only if the source paradigms change.

Version: start `v0.0` (initial draft, no notes). Each iteration bumps the minor (`v0.0`→`v0.1`→…). Bump major
(`v1.0`) only when the plan is deemed sign-off-ready and presented to Alex.

## The iteration loop (one iteration = produce v(N) from v(N-1))

Maps the flexible-plans closed-loop cycle (Observe→Evaluate→Revise→Continue) onto Alex's stated steps. The three
reviews append, IN ORDER, to one `notes_v(N).md`; apply afterwards. Order rationale in the next section.

1. **Copy (shell `cp`)** `warm-reset-plan_v(N-1).md` → `warm-reset-plan_v(N).md`. Increment the version header inside the new file. (Preserves the prior version intact as audit trail; the diff between consecutive files = the applied revision.)
2. **Create `notes_v(N).md`** and run the three reviews below in order, each appending a section. Record findings as `[finding-id] location → problem → change (what + how)`. Compact, AI-dense (cold-AI applies to the notes themselves). This is the audible "Revise" step, persisted.
   - **R1 Structure-fit** (substance) — see below.
   - **R2 Paradigm-compliance** (form) — see below.
   - **R3 Focus/economy** (economy; runs last) — see below.
3. **Append the Change-Magnitude Summary** to `notes_v(N).md` (schema below) — the convergence signal.
4. **Apply** the notes' changes into `warm-reset-plan_v(N).md`. (Copy made it identical to v(N-1); now edit it to realize the notes.)
5. **Evaluate convergence** (criterion below) → continue (next iteration) or exit (run the Post-loop close).

**Sub-agent use within any step**: crawling/extraction sub-tasks (scanning the memory files, all `notes_v*.md`, hunting path references, inventorying candidate domains/concepts) may be delegated per § Sub-agent strategy. High-judgment work (R1–R3 reviews, placement, structure design, risk reasoning) stays with Opus 4.8. Every delegation is logged + audited in `experiment-log.md`.

## Review order (answer to "is there a beneficial order?": yes — substance → form → economy)

Pipeline = structural-edit → line/standards-edit → trim, mirroring how editing minimizes rework:

- **R1 first (substance)** because it can cause the largest rewrites (the target memory *design* changes); doing it first means R2/R3 polish stable content, not soon-to-be-replaced content.
- **R2 second (form)** ensures whatever R1 produced is decodable + properly layered.
- **R3 last (economy)** is reductive: both R1 and R2 can ADD material, so trimming must come after them — trimming earlier then re-adding is churn. R3 also nets out R1/R2's additions ("R1 adds X; cut Y to stay lean").

Within one iteration I have full context, so R2's decodability is a property I *check*, not a precondition for my own reviewing — hence substance-first is safe.

## R1 — Structure-fit (substance) [runs FIRST]

Does the plan's target memory structure (a) **fit the information the persona memorizes about itself and its projects, which evolves over time** — i.e. is it adaptive, not over-committed; and (b) **let a cold AI retrieve efficiently** given a high-level topic + a related lower-level detail (one-hop topic→domain-index→concept→detail, plus lateral relation traversal)? **Soft favour parsimony to counter bloat, but retrieval-efficiency outranks parsimony** (the explicit tie-breaker). Check against `microcontroller-multi-project-memory-guidelines.md` (esp. §0 target, §2 empiricism/seed-on-evidence, §3 concept-graph + graduation, §9 parsimony-vs-retrieval). Flag: over-committed/empty scaffolding; structures that force multi-hop or speculative search; missing relation edges; non-adaptive (present-tense-permanent) framing; bloat with no retrieval payoff. Apply the cold-AI paradigm to the findings.

## R2 — Paradigm-compliance (form) [runs SECOND]

(a) **Cold-AI gate** — every block: Decode every term/ref inline · Purpose · Signals (forward-looking: confirm/refute + trigger) · Lifecycle (status/date/provenance) · How-to-check-status (mechanical). Any unanswerable → fix in text, never defer to live memory. Ref `.cursor/rules/reference/cold-ai-paradigm.md`. (b) **Flexible-plans gate** — layered commitment present (Fixed: targets/constraints/known-unknowns/checkpoints/exit-ramps/authority-map; Provisional-labelled: approach/initial-criteria; Open: artifact shape/step sequences); every phase has a checkpoint + criteria-revision gate; diminishing-returns termination; scope-expansion escalates; sketches marked hypotheses. Ref `.cursor/rules/reference/flexible-plans-for-ai-execution.md`.

## R3 — Focus/economy (vs prior version) [runs LAST]

Comparing to `warm-reset-plan_v(N-1).md`: is the plan still focused, still carrying all necessary context, but NOT accreting context-bloat that taxes future iterations? Net out R1+R2 additions — for each addition ask "does this earn its context cost, or can it compress / move to the guidelines doc / be cut?". Flag specific add/cut/compress/relocate actions. Apply the cold-AI paradigm to the findings.

## Change-Magnitude Summary (schema; appended to every `notes_v(N).md`)

The mechanical convergence signal — a cold AI reads it to judge diminishing returns without re-diffing files. Per iteration record:

- **Breadth**: number of distinct plan sections/elements changed this iteration (count) + which ones.
- **Depth**: count of applied findings by tier (highest tier present is what matters):
  - `T3 structural` — target/constraint added·removed·redefined; phase added·removed·resequenced; the memory-structure design changed.
  - `T2 substantive` — success criteria, authority handoffs, exit ramps, known-unknowns, decisions (D-items) changed.
  - `T1 clarity` — decodability / wording / layering fixes; no behavior change to the plan.
  - `T0 cosmetic` — formatting, typos, cross-ref tidies.
- **Known-unknowns about plan adequacy discharged**: count + one-line each (a question about whether the plan is *good enough* that this iteration answered).
- **Trend vs v(N-1)**: is highest-tier and breadth decreasing? (one line)
- **Convergence verdict**: `converging` / `converged` / `not-converged` + one-line why.

## Convergence & termination (of THIS planning loop)

Two stopping conditions; whichever fires first:

- **C-converged (diminishing returns)**: an iteration's Change-Magnitude Summary shows highest depth tier ≤ `T1 clarity` (no T2/T3 changes) **AND** zero known-unknowns-about-adequacy discharged **AND** the trend is non-increasing. Per flexible-plans, if the verdict is borderline, run **one** more iteration to confirm before declaring converged (don't stop on a single ambiguous reading).
- **C-cap (hard upper bound)**: **5 iterations maximum** → `v0.1 … v0.5`, i.e. **6 plan files total including `v0.0`**. At `v0.5`, stop regardless. If `v0.5` is reached still `not-converged`, do NOT keep spinning — exit the loop and flag the unresolved sticking points to Alex in the Post-loop close.

Either way, loop exit → run the **Post-loop close**.

## Post-loop close (after the loop exits, by either stopping condition)

1. **Promote to sign-off candidate**: `cp` the final converged version (`warm-reset-plan_v0.X.md`) → `warm-reset-plan_v1.0.md`. v1.0 = the version presented to Alex for the warm-reset go/no-go (a separate authority gate; execution still needs the exact "warm reset" phrase).
2. **Cross-notes risk scan** → write `risk-register.md`. Scan ALL `notes_v*.md` (and v1.0) and extract the **technically riskiest / most-uncertain items**: assumptions, design choices, and details that **cannot be resolved evidence-driven *during* plan execution** — i.e. irreducible a-priori judgment calls, NOT things execution will reveal (the latter are normal known-unknowns the plan already handles via checkpoints). For each: `risk-id · the assumption/choice · why it can't be settled by executing the plan · blast radius if wrong · current disposition in the plan (decided / open / MISSING) · recommended hedge or escalation`. **Explicitly check: is any high-risk item absent from the plan entirely?** — surface gaps as `MISSING`. These items are the priority escalation set for Alex (they overlap heavily with D1–D7 but the scan may surface new ones).
3. Present v1.0 + `risk-register.md` to Alex.

## Sub-agent strategy (model assignment + develop-the-technique-during-execution)

Sub-agents accelerate this effort but their *precise* deliverable spec is not fully knowable up front — so treat
sub-agent usage itself as a **hypothesis-test refined during execution** (flexible-plans: provisional approach,
confirm/refute signals, audit-and-tweak each cycle). Do not over-specify dispatch prompts in advance; develop them.

**Model assignment (task → model):**
- **Crawl / extract / inventory** (high-volume, low-judgment scanning of docs, memory files, notes, path references) → Cursor sub-agent on **composer-2.5** (slug `composer-2.5-fast`), `subagent_type: explore`, `readonly: true`. Output: structured extraction (tables/lists), no decisions.
- **Reason / abstract / generalize / decide** (placement-gate calls, structure design, contradiction adjudication, promotion, the R1–R3 reviews, the risk scan) → **Opus 4.8**: the parent agent directly, or a sub-agent on slug `claude-opus-4-8-thinking-high` for parallel heavy reasoning. Sub-agents do not get the final call on structure — the parent integrates.

**Per-dispatch discipline (every sub-agent call):**
1. **State the precise deliverable expectation BEFORE dispatch** — exact output shape (columns/fields), scope (which files), and what NOT to do (e.g. "extract only; make no placement decisions"). Write it into `experiment-log.md` as the dispatch's expectation.
2. Dispatch.
3. **Self-audit the return (OERC)**: Observe what came back → Evaluate against the stated expectation (complete? accurate? right format? right model tier — was judgment needed that composer couldn't give, or was Opus overkill?) → Revise the dispatch spec / switch model tier / re-run if needed → Continue.
4. **Log the dispatch + audit verdict** in `experiment-log.md`.

**Confirm/refute signals for "sub-agents are helping here"** (evaluated in the experiment log):
- *Confirm*: extraction is accurate + complete + correctly formatted, and delegating saved parent context/time.
- *Refute*: output needed heavy rework, missed items, hallucinated content, or the round-trip cost exceeded doing it inline → narrow the task, tighten the spec, change model tier, or stop delegating that task type.

Over cycles, accrete what works into the **"Current best practice" block at the top of `experiment-log.md`** (which model for which task shape, prompt patterns, deliverable-spec patterns). That block is the durable takeaway; the per-dispatch entries are its evidence.

## Experiment log (`experiment-log.md`)

Append-only record of sub-agent experiments (and any other technique-tuning), AI-consumed, dense. Two parts:
- **Top — "Current best practice" (evolving)**: the distilled how-to-use-sub-agents-well summary; updated when a cycle confirms/refutes a technique. This is what a future cold AI reads to skip re-deriving.
- **Per-entry log**: `exp-id · date · task-type (crawl|reason) · model+agent-type · precise deliverable expectation · dispatch summary · outcome · audit verdict (worked|partial|failed + why) · tweak-for-next`.

## Authority handoffs (during planning)

- **Autonomous**: all plan-quality revisions (decodability, layering, phase sizing, checkpoint/exit-ramp/criteria wording).
- **Escalate to Alex (do NOT decide in the plan)**: the warm-reset content decisions the mandate flags — OQ1 project granularity, OQ2 promotion autonomy, OQ3 scope-tagging of existing entries; the two mandate reconciliations `Recon-A` (3-tier vs 4-tier scope model) and `Recon-B` (drop stale `verified`/human-elevation tier); plus two new ones surfaced this session — where behavioral memory physically lives post-reset (Bamboo-Lamp-standalone reachability) and whether warm reset absorbs Bamboo-Lamp's existing external memory home or leaves it federated. (NB: `Recon-A/B` here are the mandate's reconciliations — distinct from the review steps `R1/R2/R3`. The plan currently labels them `D4/D5`; unify labels in a future iteration.) The plan records these as OPEN with options + a recommendation, never as settled.
- **Hard gate**: executing the warm reset requires Alex's exact phrase "warm reset" + explicit go-ahead. Planning does not.

## Exit ramps (pause the loop, surface to Alex)

Any of: a decision in the escalate list blocks further useful iteration; the plan reveals the mandate itself is
internally inconsistent in a way needing Alex's call; scope of the planning task itself grows beyond "plan the warm
reset" (e.g. turns into redesigning the mandate).
