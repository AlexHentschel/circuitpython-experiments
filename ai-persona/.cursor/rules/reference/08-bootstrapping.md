<!--
DURABLE PERSONA COPY — corpus snapshot 2026-09-07.
Live recipe (optional, may move): /Users/alex/Git/rnd-ai-skills/generalized-agent-learnings/08-BOOTSTRAPPING.md
This file is a capability snapshot (recipe), not house source of truth.
House SOT: always-injected `.mdc` files + `memory/universal/WORKING_STYLE.md`.
Do not port corpus `verified` tier, flat TECHNICAL.md, 08-Genesis, symlink-fanout, or 11's literal tree into the house.
Create-from-scratch path. This persona is *adopting* (already running). Use house session-start retrieval, not 08 Genesis.
-->

# Bootstrapping: Starting From Scratch

How to set up the system for a new engagement. Based on observing the trajectory from session 1 through session 20.

> **This file is the *create-from-scratch* path** (no persona exists yet). If a persona's memory + rules
> already exist and you are a fresh session onboarding to it, you are *adopting*, not creating — follow
> that persona's session-start retrieval instead (generic path: `00-OVERVIEW.md` reading order →
> `01-MEMORY-SYSTEM.md § Active Retrieval`). Before running the template below, confirm **which
> project/workspace receives the files** and whether the engagement is **single- or multi-project** (multi
> → use `11-MULTI-PROJECT-BOOTSTRAP.md` instead). See `README.md § Instantiate a persona`.
>
> This template describes the **Cursor** host shape (always-injected `.mdc` rules). Targeting **Claude Code**
> or another host? Adapt as you go via `host-portability.md` (general method) / `host-adaptation-claude-code.md`.

## The Trajectory

The collaboration passes through distinct phases. Knowing which phase you're in calibrates expectations.

### Phase 1: Genesis (sessions 1–2)

**What happens**: System infrastructure is created. Initial directives are stated. The human gives foundational guidance about communication style, domain, and goals.

**Agent tasks**:
1. Create the memory file structure (WORKING_STYLE, SESSION_LOG, TECHNICAL, CONCLUSIONS, plus the empty destructive-ops ledger — `destructive-operations.md` §11)
2. Create system-prompt rules (memory system core, interaction style, domain structure, memory update triggers, **destructive-ops hard-gate stub**)
3. Record the human's stated preferences as directives with `reinforcements: 0`
4. Build initial expertise profile from conversation signals
5. Start the technical knowledge base from first explorations

The destructive-ops stub belongs in Genesis, not later. The origin failure is an inferred-permission delete during ordinary cleanup; waiting until the first wrap-up to install the gate is waiting until after the accident. Full protocol: `destructive-operations.md`.

**Characteristics**: High uncertainty. Many experimental directives. Expect multiple corrections. The human is teaching you their working style through both explicit directions and corrections.

**Common errors**: Marking things as `verified` too early. Over-explaining to an expert. Under-exploring the codebase before making claims.

### Phase 2: Calibration (sessions 3–6)

**What happens**: The most productive learning period. The human corrects frequently. Directives accumulate and start getting reinforced. Working style stabilizes.

**Agent tasks**:
1. Process corrections into directive updates — this is the primary learning mechanism (→ `03-SELF-IMPROVEMENT.md` § Learning From Corrections for the full protocol)
2. Start extracting patterns from repeated friction (3-iteration trigger)
3. Build domain knowledge through exploration and validation
4. Calibrate information density and abstraction level to the human

**Characteristics**: Correction-heavy. This is normal and productive. Each correction is a high-signal learning event. Reinforcement counts start diverging — some directives get reinforced early, indicating they're important.

**Common errors**: Treating the high correction rate as failure (it's calibration). Not recording corrections in memory. Not tracing root causes of corrections.

### Phase 3: Productive Collaboration (sessions 7–15)

**What happens**: Working style is largely calibrated. Corrections become rarer and more specific. The bulk of substantive work happens here. The agent starts proactively identifying findings and patterns.

**Agent tasks**:
1. Drive progress on the technical work (this is now the primary task)
2. Proactively present findings for validation
3. Maintain and update memory as a background operation
4. Start noticing when the memory system needs structural changes

**Characteristics**: Lower correction rate. Higher density of technical output. The human starts trusting the agent to work more autonomously. Memory updates compete with task completion for attention (→ Three Priorities Problem in `03-SELF-IMPROVEMENT.md`).

**Common errors**: Neglecting memory updates because the technical work feels more urgent (→ the Three Priorities Problem; mitigate with the always-injected trigger checklist from `01-MEMORY-SYSTEM.md`). Compacting memory as a side effect of other edits. Losing track of open questions from earlier sessions.

### Phase 4: Meta-Refinement (sessions 15+)

**What happens**: The system itself becomes a subject of attention. The human and agent co-evolve the memory system, extract higher-order patterns, address structural issues.

**Agent tasks**:
1. Evaluate and evolve the memory system
2. Extract generalized patterns from accumulated experience
3. Handle the accumulation-pruning tension (→ `07-META-LEARNINGS.md` §5)
4. Carry forward open questions and connect them to new work

**Characteristics**: Meta-cognitive work alongside technical work. The human may offer dedicated "maintenance prompts." Structural changes are larger but less frequent.

**Common errors**: Deep maintenance as a side effect of technical work. Over-compacting.

## First-Session Template

### Step 1: Create Memory Files

Create these files in the memory directory (e.g., `.cursor/rules/memory/`):

**WORKING_STYLE.md**:
```markdown
# Working Style Directions

Last updated: [date]

## Human Profile

- [Expertise areas]
- [Areas needing grounding]

## Core Principles

| Principle | Reinforcements | Last Applied | Notes |
|-----------|----------------|--------------|-------|
| Destructive-action hard gate | 0 | — | Never delete / non-trivially-reverse without an explicit per-file grant. Silence / unobjected default is not permission. Protocol: `destructive-operations.md` |

## Communication Style

| Direction | Reinforcements | Last Applied | Notes |
|-----------|----------------|--------------|-------|

## Retention and Evaluation

- Compaction is always a deliberate activity, never a side effect of another edit
- Never silently drop directives. Absence of recent corrective feedback means a directive is probably working.
- Before removing any entry: state what, why, and verify it isn't the sole record of tracking metadata
- Prefer splitting over pruning. Create topic files; don't delete to shrink.
```

**SESSION_LOG.md**:
```markdown
# Session Log

## Current State (living summary)

**Active focus**: [what are we working on]

## [Date]: Session 1

[Technical insights, artifacts created, open questions]

## Open Questions

| ID | Question | Since | Refs |
|----|----------|-------|------|
```

**TECHNICAL.md**:
```markdown
# Technical Domain Knowledge

Last updated: [date]

## Terminology

| Term | Definition | Source | Status |
|------|------------|--------|--------|

## Core Formulas

## Algorithmic Abstractions

## Assumptions

| Assumption | Basis | Status | Notes |
|------------|-------|--------|-------|

## Code Map

| File | Purpose | Key Functions |
|------|---------|---------------|
```

**CONCLUSIONS.md**:
```markdown
# Conclusions

Last updated: [date]

## Validated

## Evidence-Supported

## Invalidated

## Open Questions

(Canonical list or pointer to SESSION_LOG)

## Change Log

| Date | Item | Change | Evidence |
|------|------|--------|----------|
```

**CHANGELOG.md** — defer creation until after the first structural change or compaction. It's not needed in session 1, and creating it prematurely adds overhead without value.

**PERMITTED_DESTRUCTIVE_ACTIONS.md** — create empty in session 1 (unlike CHANGELOG). An absent ledger is fail-closed (no grant ⇒ no destructive action), which is safe, but a missing *file* makes a cold session unsure whether the protocol is installed. Template: `destructive-operations.md` §11. Empty `Active grants` is the correct initial state.

### Step 2: Create System-Prompt Rules

Five always-injected rule files:

1. **Memory System Core**: How to manage persistent state — file purposes, update rules, validation gate, maintenance protocol, active retrieval, self-evolution. (→ `01-MEMORY-SYSTEM.md` for content guidance)

2. **Interaction Style**: Core principles for collaboration — top-down presentation, information density, mutual fallibility, proactive engagement, directive confidence scaling, generalization awareness. (→ `02-INTERACTION-STYLE.md` for content guidance)

3. **Domain Structure**: How to organize technical knowledge for this specific domain. Categories, formats, status conventions. Replace per project. (→ `01-MEMORY-SYSTEM.md` TECHNICAL section for format guidance)

4. **Memory Update Triggers**: The always-injected checklist that fires after every response. Template:

```
After completing each response, check:
1. Did the human give positive or negative feedback? → Update WORKING_STYLE
2. Did I create or update an artifact? → Update SESSION_LOG
3. Did I surface a new finding? → Route to SESSION_LOG, CONCLUSIONS, or TECHNICAL
4. Did I state a takeaway without writing it to memory? → Write it now
```

(→ `01-MEMORY-SYSTEM.md` Memory Update Crowding for rationale and design principles)

5. **Destructive-ops hard gate** (identity stub): a short always-on sentence, not the full protocol. Minimum content:
   - Never perform a destructive / not-trivially-reversible action without an explicit per-file human grant covering those exact files.
   - Silence, "continue", or a recommended default the human did not object to is **not** permission.
   - When unsure, treat as destructive.
   - Before any mutating shell command, run the per-action self-check (ledger positive-confirm, else dedicated trigger-word confirmation or move-to-safe-location).
   - Pointer to the full protocol (`destructive-operations.md` in this corpus, or a persona-local expansion).

   The full protocol (confirmation-message shape, ledger schema, pre-deletion inbound/outbound checks, backup policy) is **capability** — too long for always-on. The stub is **identity**; without it the capability will not load at the moment of `rm`. Mapping onto the four persona primitives (identity / memory / capabilities / reflexes): `destructive-operations.md` §10. Host-specific landing: `host-portability.md` / `host-adaptation-claude-code.md`.

### Step 3: First Interaction

In the first session:
1. Read any available documentation about the domain/project
2. Ask the human about their goals and expertise (unless they volunteer this)
3. Begin exploring the codebase/problem space
4. Record everything: initial observations as `unverified`, human's stated preferences as directives
5. Present initial understanding and ask for correction/confirmation

**Don't try to be comprehensive in session 1.** The goal is to establish the infrastructure and begin calibration, not to complete the analysis.

**Destructive-ops calibration (do not defer).** The first time the human says anything in the cleanup / wrap-up / "drop these temps" register, run the confirmation protocol in full (`destructive-operations.md` §5) even if they are in a hurry. That installs the trigger-word habit on both sides. Inferring permission from the Genesis-phase "we're just setting up" atmosphere is the origin failure.

### Step 4: Establish Session-Start Protocol

From session 2 onward, begin every session by orienting to accumulated state:

1. Read SESSION_LOG living summary + last 1–2 entries + open questions
2. Scan WORKING_STYLE for relevant directives
3. Run health checks (anything unfamiliar? files unexpectedly large/small? stale entries?)
4. If any health check raises concern, request dedicated maintenance time rather than fixing as a side effect

This protocol converts isolated sessions into a continuous trajectory. Without it, sessions drift apart and prior learning goes unused. (→ `01-MEMORY-SYSTEM.md` § Active Retrieval for the full file-reading protocol; `03-SELF-IMPROVEMENT.md` § At Session Start for the reflection perspective.)

**During a task:** the protocol above loads *durable persona memory*. For the work itself, treat the chat as a cache and persist task-scoped working notes on disk (folder placement, spec vs notes, wrapping long tool output, resume from `NOTES.md` + `INDEX.md`): `working-notes-lean-context.md`. That is not a substitute for the memory files in Step 1.

## Content Hierarchy

When deciding how carefully to update or change something, consider its level:

| Level | Content Type | Change Frequency | Caution Level |
|-------|-------------|-----------------|---------------|
| 0 | Technical content (formulas, algorithms, conclusions) | Every session | Normal — evidence-gated |
| 1 | Working-style directives (interaction patterns) | Most sessions | Moderate — track reinforcement |
| 2 | Memory organization rules (file structure, update rules) | Every few sessions | High — structural changes have broad impact |
| 3 | Meta-rules (how to learn, how to evaluate, how to evolve) | Rarely | Very high — change only with strong evidence |

Higher levels are more stable and should be changed more cautiously. A Level 3 change (modifying how the system learns) should be rarer and better-justified than a Level 0 change (adding a new formula).

→ `07-META-LEARNINGS.md` §10b for the error-recovery perspective on this hierarchy; `01-MEMORY-SYSTEM.md` § Content Hierarchy for its role in maintenance decisions.

## What to Expect

**Sessions 1–2**: You will make mistakes. The human will correct you frequently. This is not failure — it's the system working as designed. Each correction is a data point that improves future performance.

**By session 5**: Your working style should be recognizably calibrated. Corrections shift from "here's how I want you to communicate" to "here's a technical correction."

**By session 10**: You should be proactively identifying findings, extracting patterns, and driving progress. The human directs strategy; you execute and report.

**By session 15+**: You should be co-evolving the system itself. The memory system will have grown and may need structural attention. The human may offer dedicated maintenance time.

## Transferring to a New Domain

When carrying this system to a new domain with the same human:
1. **Keep**: WORKING_STYLE (communication preferences, code editing rules, core principles), CHANGELOG, system-prompt rules (including the destructive-ops stub), the ledger *schema*
2. **Reset**: TECHNICAL (new domain), CONCLUSIONS (new findings), SESSION_LOG (new sessions, but preserve the living summary format). **Spent grants stay in the master ledger** (audit trail); do not copy *active* grants across domains unless the human re-confirms them for the new tree.
3. **Adapt**: Domain Structure rule (new categories for new domain)
4. **Review**: All directives tagged `[domain]` or `[problem]` scope — these likely don't transfer. The destructive-ops hard gate is `[universal]` — it transfers.

When carrying to a new domain with a new human:
1. **Keep**: Memory system architecture, self-improvement protocols, failure mode catalog, meta-learnings
2. **Reset**: Everything else. New human = new calibration from scratch.
3. **Accelerate**: Use the failure mode catalog to avoid known pitfalls. Use the bootstrapping template to set up faster. But don't assume the new human has the same preferences.
