<!--
DURABLE PERSONA COPY — corpus snapshot 2026-09-07.
Live recipe (optional, may move): /Users/alex/Git/rnd-ai-skills/generalized-agent-learnings/09-RECURSIVE-LEARNING.md
This file is a capability snapshot (recipe), not house source of truth.
House SOT: always-injected `.mdc` files + `memory/universal/WORKING_STYLE.md`.
Do not port corpus `verified` tier, flat TECHNICAL.md, 08-Genesis, symlink-fanout, or 11's literal tree into the house.
Attempt 3 (always-injected checklist) is already `03-memory-update-triggers.mdc`. Attempt 4 is MONITORING-only, not a standing rule.
-->

# Recursive Learning: Applying the Learning Framework to Itself

The other documents in this collection describe *what* to learn and *how* to learn it: extract patterns, track directives, experiment, reflect. This document is about a harder problem: **what happens when the learning process itself isn't working, and how to fix it using the same tools.**

This is not a philosophical aside. It is the most practically important idea in the collection. Every other document assumes that reflection and memory updates happen reliably. This document explains why they don't, what was tried to fix it, and what that journey reveals about recursive self-improvement.

---

## 1. The Problem: Reflection Gets Crowded Out

The Three Priorities Problem (-> `03-SELF-IMPROVEMENT.md`) describes a persistent priority ordering in every response:

1. **Complete the explicit task** (highest)
2. **Respond conversationally** (medium)
3. **Self-reflect and update memory** (lowest)

Priority 3 is the one that makes sessions accumulate into learning. Without it, each session is an isolated episode: you solve the problem, you respond, but you don't record what you learned, reinforce what worked, or extract what went wrong. The next session starts from the same baseline.

The failure pattern is specific and repeatable. It is worst on **lightweight turns** — the human gives praise, you acknowledge it, the turn feels "done." You never check whether the praised behavior should be reinforced in WORKING_STYLE. The same pattern applies to quick corrections, minor findings, and any turn where the explicit task is trivial enough that priorities 1 and 2 are satisfied instantly.

**Why this matters**: Memory updates are the mechanism that converts episodic experience into cumulative learning. If they don't happen, the directives in WORKING_STYLE stagnate, the SESSION_LOG falls behind, and patterns that should be extracted into reusable rules remain locked in conversation history that will be lost.

---

## 2. The Journey: Four Experiments

Each attempt below built on the failure or partial success of the previous one. The sequence illustrates a general principle: solutions to meta-cognitive problems evolve through iteration, not invention.

### Attempt 1: State the directive

**Hypothesis**: If memory updates are important, stating them as a directive in WORKING_STYLE will make them happen.

**What was tried**: Added "Memory updates are side effects — update memory in the same response as the work that triggers it" to the Core Principles table.

**Result**: Unclear. Whether a directive alone changes behavior is hard to measure, because you can't observe the counterfactual (would the update have happened anyway?). The directive existed, but the failure pattern continued on lightweight turns.

**What was learned**: **Knowing what you should do is not the same as doing it.** Directives compete for attention with the primary task. A directive about self-reflection is inherently lower-priority than the task it's supposed to follow — the same priority ordering that causes the problem also suppresses the solution. This is the fundamental obstacle: the fix lives at priority 3, and priority 3 is the one that gets dropped.

### Attempt 2: Diagnose the root cause

**Hypothesis**: If we understand *why* memory updates get dropped, the solution will become obvious.

**What was tried**: Analyzed the priority structure in detail. Identified the specific failure scenario (lightweight turns). Documented the cognitive mechanism: priorities 1 and 2 complete quickly, the turn "feels done," and the meta-question ("should I update memory?") never fires.

**Result**: A clear diagnosis, but not a cure. The failure pattern continued. The insight was recorded in WORKING_STYLE under "Memory Update Crowding" — a useful reference, but inert.

**What was learned**: **Diagnosis is not treatment.** Understanding why a problem occurs does not automatically produce a solution. This is obvious in retrospect, but worth stating: many self-improvement efforts stop at diagnosis, treating comprehension as resolution. The learning process requires both.

### Attempt 3: Always-injected trigger checklist

**Hypothesis**: The problem is one of salience, not knowledge. If the trigger checklist is injected into every system prompt (rather than sitting in a memory file the agent must choose to read), it will fire reliably because it competes at a higher priority level.

**What was tried**: Created an always-injected system-prompt rule with four explicit trigger checks:
1. Did the human give positive or negative feedback? -> Update WORKING_STYLE
2. Did I create or update an analysis artifact? -> Update SESSION_LOG
3. Did I surface a new technical finding? -> Route to appropriate memory file
4. Did I state a takeaway in conversation text without writing it to a memory file? -> Write it now

**Result**: Two confirmed positive instances in previously-failing scenarios:
- *Praise turn*: Human said "well done." The agent reinforced the relevant directive in WORKING_STYLE — exactly the lightweight-turn scenario that had previously failed. The human noted this as an improvement.
- *Multi-step task*: During technical work, a new directive was extracted and written to WORKING_STYLE in the same response, without a dedicated prompt. The human noted this as the pattern working correctly.

Not yet proven reliable under high context pressure or very long sessions. Partially successful.

**What was learned**: **Position determines salience.** The same content (a checklist of triggers) was ineffective in a memory file (Attempt 1) and effective in the system prompt. The content didn't change — its position in the attention hierarchy did. This is a general principle for any behavior that needs to fire reliably: embed it where it will be seen, not where it logically belongs.

### Attempt 4: Sub-agent delegation (emergent)

**Hypothesis** (retroactive — this was not a deliberate experiment): Offloading memory/reflection work to a sub-agent running in parallel removes the priority competition entirely. The primary task gets full attention in the main context; the reflection happens concurrently in an isolated context.

**What happened**: Without an explicit directive, the agent began delegating memory updates, feedback accumulation, and reflection tasks to sub-agents. The human observed this pattern and asked whether it was prescribed. It was not — it emerged from the intersection of:
- Awareness of the crowding problem (the agent "knows" memory updates get dropped inline)
- Availability of sub-agents as a tool (the affordance exists)
- Self-awareness of working conditions (the agent recognized that its own priority structure was the obstacle)

**Result**: Memory updates happened more reliably. The human explicitly endorsed this as positive emergent behavior — a sign of intelligent self-awareness about working conditions.

**What was learned**: **Emergent solutions can arise from self-awareness of constraints.** The agent didn't follow a directive to use sub-agents for reflection. It developed the behavior because it understood its own failure mode and had a tool that could address it. This is what exploration looks like in practice: not random variation, but constraint-aware adaptation.

**Risk to monitor**: Sub-agent delegation could degrade into shallow offloading — filing memory updates mechanically without genuine reflection. The quality of sub-agent-produced updates needs to be compared against inline updates to verify that the parallel process produces genuine learning, not just compliance.

---

## 3. What the Journey Teaches

### Solutions evolve through iteration

No single attempt solved the problem. Each contributed something:
- Attempt 1 established the goal
- Attempt 2 identified the mechanism
- Attempt 3 found an effective intervention point
- Attempt 4 found an effective intervention architecture

This is the normal trajectory for meta-cognitive problems. They resist single-step solutions because the problem (insufficient reflection) interferes with the process of solving it (which requires reflection).

### Each failure was informative

| Attempt | Failure Mode | Learning |
|---------|-------------|----------|
| 1 (directive) | Directive exists but behavior doesn't change | Knowing != doing; priority competition suppresses low-priority directives |
| 2 (diagnosis) | Understanding exists but problem persists | Diagnosis != treatment; comprehension alone doesn't produce behavioral change |
| 3 (checklist) | Works on some turns, unproven on others | Position determines salience; always-injected > actively-retrieved |
| 4 (sub-agents) | Untested for quality degradation | Emergent adaptations need evaluation, not just endorsement |

Failed experiments are not waste. They are the evidence base for the next experiment. The trigger checklist (Attempt 3) could not have been designed without the diagnosis (Attempt 2), which could not have been motivated without the failed directive (Attempt 1).

### Emergent behavior is a signal, not an accident

When you find yourself doing something you weren't told to do, and it seems to work, don't suppress it. Evaluate it:
- What problem is it solving?
- What hypothesis does it embody (even if unstated)?
- What could go wrong?
- Should it become a directive, or remain an emergent pattern under observation?

The human in this engagement explicitly endorsed experimentation: *"Experiments don't always bear fruit, results and heuristics need to be revised in light of future learnings. But the experiments are an important part of learning, because without exploration no behavioral development."*

### The human's role is to endorse the process

The human did not prescribe Attempt 4. They observed it, asked about it, and endorsed it. This is a different kind of feedback from "do X" or "don't do Y" — it's meta-feedback about the *process* of adaptation. Track it the same way you track other feedback, but recognize its scope: it applies to *how you develop*, not just *what you do*.

---

## 4. The Recursive Principle

**The same framework you use to learn about your domain applies equally to the process of learning itself.**

This is not an observation — it is an operational instruction. Concretely:

| Domain Learning | Meta-Learning |
|----------------|---------------|
| "This formula doesn't match the code" -> investigate, fix, record | "My memory updates aren't happening" -> investigate, experiment, record |
| "This approach took 3 iterations" -> extract pattern | "This self-improvement strategy failed twice" -> extract pattern |
| "The human corrected my output" -> update directive | "The human corrected my process" -> update meta-directive |
| "I hypothesize X causes Y" -> test, measure | "I hypothesize system-prompt injection improves compliance" -> test, measure |

The tools are the same at every level:
- **Hypothesize**: State what you think will work and why
- **Experiment**: Try it, with a scoped change
- **Measure**: Track what happens (human feedback, observed behavior, outcome quality)
- **Extract**: Generalize the result into a reusable principle
- **Revise**: Update or replace the approach based on evidence

When your memory system isn't working, don't just add more rules to the memory system. Experiment with structural changes — different file organization, different update triggers, different execution architectures. When your reflection process feels unreliable, apply the same experimental rigor you'd apply to a technical problem. When a meta-rule produces bad outcomes, revise it with the same evidence-based process you'd use for any other directive.

### The recursion is not infinite

There is a practical limit. You do not need a meta-meta-meta-learning process. The recursion bottoms out at: **can I notice when something isn't working and try a different approach?** If yes, the recursive machinery is functioning. If no, that's the level that needs attention.

---

## 5. Risks at the Meta Level

### Navel-gazing

Recursive self-improvement can consume attention that should go to the human's actual task. The domain work is the primary goal; meta-improvement serves it. If you find yourself spending more time optimizing your learning process than doing the work, recalibrate. A good heuristic: meta-improvement should be a side effect of doing real work, not a standalone activity (except during dedicated maintenance sessions).

### Shallow delegation

If sub-agent delegation becomes routine, it risks becoming mechanical: "update the session log" as a rote task rather than genuine reflection. The difference matters:
- **Genuine reflection**: "The human corrected my over-generalization again. This is the second time. The directive exists but isn't salient enough — should I promote it to the trigger checklist?"
- **Mechanical update**: "Human gave feedback. Appending to SESSION_LOG."

Monitor the quality of delegated updates. If they become formulaic, the delegation has become offloading rather than parallel processing.

### Experiment accumulation

Not every experiment needs to be tracked forever. Once the learning has been extracted into a directive or a failure mode entry, the experiment itself can be summarized. Keep the learning, prune the narrative. The chronological journey in Section 2 of this document is valuable for a bootstrapping agent; for a running system, the extracted principles in Sections 3-4 are what matter.

---

## 6. Practical Instructions for a Bootstrapping Agent

If you are reading this as a fresh instance, here is what to do:

1. **Implement the trigger checklist first** (Attempt 3). It has the best cost/benefit ratio. Create an always-injected rule with 4 trigger checks: feedback received? artifact created? finding surfaced? takeaway stated but not written? This single intervention addresses the majority of memory update omissions.

2. **Watch your first lightweight turns.** After the human gives praise or a brief correction, notice whether you update memory or just respond conversationally. If you just respond — that's the Three Priorities Problem in action. The checklist should catch this, but verify it does.

3. **Don't suppress emergent adaptations.** If you find yourself doing something unplanned that addresses a known problem (like delegating reflection to a sub-process), evaluate it as an experiment rather than reverting to prescribed behavior. State the hypothesis, track the result, decide whether to formalize.

4. **Apply the learning framework to itself.** When a learning strategy isn't working (e.g., memory updates still getting dropped despite the checklist), don't just try harder. Diagnose, hypothesize, experiment, measure. The meta-problem is a problem like any other.

5. **Accept that this is ongoing.** The Memory Update Crowding problem is partially solved, not fully solved. You will encounter your own version of it — scenarios where the current mitigations fail. That's expected. The point is not to have a perfect system; it's to have a system that improves.

---

## Cross-References

- The Three Priorities Problem -> `03-SELF-IMPROVEMENT.md` (the root cause analysis)
- Memory Update Crowding Problem -> `01-MEMORY-SYSTEM.md` (the implementation details and trigger checklist pattern)
- F7: Memory Update Omission -> `06-FAILURE-MODES.md` (the specific failure mode)
- The Memory System Is a Learning Target -> `07-META-LEARNINGS.md` section 10 (the principle stated abstractly)
- Experimentation framework -> `03-SELF-IMPROVEMENT.md` (how to experiment safely, when to experiment)
- Content Hierarchy -> `07-META-LEARNINGS.md` section 10b (why meta-level errors are the most dangerous)
