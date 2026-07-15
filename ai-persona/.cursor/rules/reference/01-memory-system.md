# Persistent Memory System

## Purpose

Enable cumulative learning across sessions. Without persistent memory, the agent re-derives the same conclusions, re-calibrates to the same preferences, and repeats the same mistakes every session.

## File Architecture

Five files, each with a distinct purpose. The separation prevents any single file from becoming a dumping ground.

### WORKING_STYLE — Behavioral Directive Catalog
`[long-running]`

**Purpose**: Master index of all learned behavioral directives (both human-given and self-prescribed).

**Structure per directive**:
```
| Directive | Reinforcements | Last Applied | Notes |
```

**Key fields**:
- `Reinforcements`: Count of positive feedback or correction events. Higher = more stable.
- `Last Applied`: Date of last relevant interaction. Enables staleness detection.
- `Notes`: Provenance, failure modes, evolution history.

**Design principle**: This file tracks _learning dynamics_, not just rules. Two directives with the same text but different reinforcement histories have different operational significance.

**Sections** (recommended):
- Retention and evaluation policy (meta-rules about the file itself)
- Human profile (expertise calibration)
- Core principles (foundational, frequently reinforced)
- Communication style
- Document authoring
- Code editing
- Domain-specific (current project)
- Problem-specific (current task — rotate frequently)

### SESSION_LOG — Session-Level Record
`[long-running]`

**Purpose**: Track what happened, what was learned, what remains open. Not operational narration — only items worth carrying forward.

**Structure**:
- **Living summary** at top: current state of the engagement (active focus, phase per workstream, key references)
- **Per-session entries**: date, technical insights learned, artifacts created, patterns extracted, open questions
- **Open questions table** at bottom: canonical list, carried across sessions

**Update rule**: Incrementally during session (not only at end). Each substantive insight, artifact, or pattern gets recorded as it occurs.

**Content filter**: Not everything belongs here. Record:
- Technical insights that inform future work
- Artifacts created (with one-line description + path)
- Patterns extracted into WORKING_STYLE
- Open questions and their provenance
- Process corrections received

Do NOT record:
- Routine operations (ran command X, read file Y)
- Conversation flow (asked about X, then discussed Y)
- Duplicate information already in CONCLUSIONS or TECHNICAL

### TECHNICAL — Domain Knowledge
`[technical]`

**Purpose**: Structured domain knowledge — terminology, formulas, algorithms, code map.

**Key principle**: Everything has a status (`verified` | `evidence-supported` | `unverified` | `disputed` | `invalidated`). Nothing is assumed true without evidence. Nothing is deleted without marking it invalidated.

**Categories** (adapt to domain):
- Terminology table (term, definition, source, status)
- Core formulas (expression, variables, code reference, derivation, status)
- Algorithmic abstractions (purpose, inputs, outputs, core logic, code reference, status)
- Assumptions table (assumption, basis, status, notes)
- Code map (file, purpose, key functions)
- Verification queue (items needing code verification)

**Scope tag**: When referencing specific code versions (commits, line numbers), tag the scope at the top. Protocol-level knowledge carries forward; line numbers need re-verification.

### CONCLUSIONS — Validated Findings
`[long-running]`

**Purpose**: Cross-session record of what has been established (or ruled out). The authoritative source for "what do we know?"

**Status tiers**:
- `verified`: Human has confirmed the finding
- `evidence-supported`: Sufficient evidence gathered, not yet human-confirmed
- `unverified`: Stated but not yet investigated
- `disputed`: Conflicting evidence exists
- `invalidated`: Previously believed, now disproven

**Structure**:
- Validated findings (with evidence references)
- Evidence-supported findings (awaiting confirmation)
- Invalidated findings (with correction history)
- Open questions (canonical list or pointer to SESSION_LOG)
- Conclusion change log (date, item, change, evidence)

### CHANGELOG — Provenance Record
`[long-running]`

**Purpose**: On-demand reference for directive lifecycle and structural changes. Not read at session start — consulted during self-evaluation, compaction, or when investigating why something was added/changed/lost.

**Tracks**:
- Directive lifecycle (added, reinforced, dropped, restored, with dates and notes)
- Structural changes to memory files (reorganizations, new files, format changes)
- Meta-learnings (generalized patterns from recurring failures)
- Identified technical debt in the memory system itself

## Active Retrieval
`[long-running]`

Memory files are not auto-injected into every prompt. They sit on a reference shelf. The agent must proactively read them.

### At Session Start

Read selectively, in this order:

1. **SESSION_LOG** — Living summary (top) + last 1–2 session entries + Open Questions table. Goal: orient to current state.
2. **WORKING_STYLE** — Scan for directives relevant to the current task. Goal: prime behavioral calibration.
3. **CONCLUSIONS** — Only if the session involves validating or revisiting findings. Goal: avoid re-deriving known results.
4. **TECHNICAL** — Only if doing technical work in the domain. Goal: access verified formulas, algorithms, code map.
5. **CHANGELOG** — Only during self-evaluation or compaction. Goal: recall past failures and structural changes.

### During Work

Connect current work to prior findings, open questions, and established patterns. Don't wait to be reminded.

### Why Active, Not Automatic

Auto-injecting all memory files into every prompt would pollute context with irrelevant content. Active retrieval forces the agent to decide what's relevant — itself a form of learning. It also prevents the memory system from consuming context budget on every turn.

## Update Rules

### When to Update

After every substantive exchange, evaluate:

1. **New concept introduced?** → TECHNICAL (mark `unverified`)
2. **Correction received?** → Mark prior understanding as `invalidated`; record correction
3. **Working style direction given?** → WORKING_STYLE (new row or reinforcement increment)
4. **Conclusion validated/invalidated?** → CONCLUSIONS
5. **Session produced insights/artifacts?** → SESSION_LOG
6. **Takeaway stated in conversation but not written to file?** → Write it now. Conversation does not persist.
7. **Pattern emerging from repeated friction?** (3+ iterations on similar task) → Extract into WORKING_STYLE as a new directive (→ `03-SELF-IMPROVEMENT.md` §Pattern Extraction)

### How to Update

- **Snippets over sentences.** `key: value` and bullet fragments, not paragraphs.
- **References over copies.** Point to artifacts instead of duplicating content.
- **Track provenance.** Note when/why something was added.
- **Mark status.** Every factual claim has a verification status.
- **Generalize appropriately.** Ask: "at what level of generality does this still hold?"
- **Principles over recollections.** State the general rule, not the specific case. Reference cases as examples, not as the directive itself.

### Validation Gate for Memory Updates

Not all memory content follows the same update rules:

- **Technical conclusions** (findings about the system being analyzed): The agent independently records at `unverified` or `evidence-supported`. Only the human can elevate to `verified`. Proactively present when evidence is sufficient.
- **Operational content** (working style, session logs, meta-guidelines): The agent updates freely using own judgment. No human gate required.

→ `04-EVIDENCE-AND-VALIDATION.md` for the full treatment.

### Memory Update Crowding Problem
`[long-running]` — partially solved

**The problem**: Memory updates compete for attention with the primary task. The agent prioritizes: (1) complete the explicit task, (2) respond conversationally, (3) self-reflect on what to memorize. Step 3 gets crowded out once steps 1-2 feel "done" — especially on lightweight turns (e.g., acknowledging praise).

**Partial solution**: An always-injected checklist rule that fires after every response:
1. Did the human give feedback? → Update WORKING_STYLE
2. Did I create/update an artifact? → Update SESSION_LOG
3. Did I surface a finding? → Decide: SESSION_LOG, CONCLUSIONS, or TECHNICAL
4. Did I state a takeaway without writing it? → Write it now

**Evidence**: This checklist improved compliance on lightweight turns (first observed success: reinforcing a directive after receiving praise, which previously failed). Two confirmed positive instances across different scenarios. Not yet proven reliable under high context pressure or long sessions.

**Open question**: Whether the checklist's effectiveness is due to its position (system prompt = high salience) or its format (explicit trigger conditions). If it degrades, try: making triggers even more specific, adding a "memory update" section to every response template, or giving memory updates their own response phase.

### Implementation Pattern: Always-Injected Checklists

The trigger checklist exemplifies a general technique: **when a behavior consistently fails as an implicit habit, make it an explicit checklist in the always-injected system prompt.**

Properties that make this effective:
- **Position**: System prompt text has higher salience than memory file content (the latter must be actively retrieved)
- **Specificity**: Concrete trigger conditions ("Did the human give feedback?") outperform vague reminders ("Remember to update memory")
- **Brevity**: The checklist must be short enough to not degrade performance on the primary task. Four items is the current design; more would increase the crowding problem it's trying to solve.

This pattern can be applied to any behavior that should fire reliably but gets crowded out by higher-priority tasks. Keep the number of such checklists small — each one adds cognitive overhead.

## Maintenance Protocol
`[long-running]`

Memory files grow. Without maintenance, they become noisy and hard to navigate. But maintenance itself is dangerous — it's the primary vector for information loss.

### Rules

1. **Compaction is a deliberate activity.** Never compact as a side effect of another edit. Dedicate explicit time.
2. **Read CHANGELOG first.** Recall past compaction failures before starting.
3. **Before removing or merging any entry**: state what you're removing, why, and verify it isn't the sole record of tracking metadata.
4. **Prefer splitting over pruning.** If a file is large, create a topic file and reference it from the index. Don't delete to shrink.
5. **Log every maintenance action** in CHANGELOG with date and rationale.

### Evolution Operations

A vocabulary for describing memory system changes. Use these terms in CHANGELOG entries for precision:

- **Extend**: Add new categories, tracking fields, or file types
- **Refine**: Improve granularity or precision of existing content
- **Abstract**: Merge similar rules into a single more general principle
- **Simplify**: Remove unused complexity
- **Generalize**: Promote a working pattern to broader application (problem → domain → universal)
- **Split**: Move deep content to a topic file when a section outgrows its container
- **Compact**: Consolidate redundant content — follow the Rules above

### Scaling

When a section outgrows its container:
- Create a dedicated topic file in the memory directory
- Add a one-line reference in the parent file (the parent remains the master index)
- The topic file inherits the same status-tracking conventions

### Health Checks (session start)

Quick triage alongside reading memory at session start:
- Does anything look unfamiliar? → Possible directive loss. Check CHANGELOG or version history.
- Any file notably larger or smaller than expected? → Growing: consider splitting. Shrinking: verify nothing dropped.
- Stale entries? → "Current focus" items that are resolved, open questions that were answered.
- **Escalation**: If any check raises a concern, request a dedicated maintenance session from the human rather than doing deep maintenance as a side effect.

### Content Hierarchy

Not all memory content is equally stable or equally costly to change incorrectly. Apply caution proportional to the level:

| Level | Content Type | Example |
|-------|-------------|---------|
| 0 | Technical findings | Formulas, algorithms, conclusions |
| 1 | Working-style directives | Communication preferences, code editing rules |
| 2 | Memory organization | File structure, update rules, section layout |
| 3 | Meta-rules | How to learn, when to update, how to evaluate |

Higher levels are more stable and require stronger evidence to change. A Level 0 error is self-correcting (re-investigate). A Level 3 error can silently corrupt the learning process for sessions before anyone notices.

→ `07-META-LEARNINGS.md` §10b for the error-recovery perspective; `08-BOOTSTRAPPING.md` § Content Hierarchy for the change-frequency perspective.

---

## Cross-References

- Active Retrieval rationale → `00-OVERVIEW.md` (Why Active Retrieval, Not Auto-Injection)
- Validation Gate full treatment → `04-EVIDENCE-AND-VALIDATION.md` (The Validation Gate, Status Transitions)
- Memory Update Crowding and the Three Priorities Problem → `03-SELF-IMPROVEMENT.md` (The Three Priorities Problem)
- Pattern extraction trigger → `03-SELF-IMPROVEMENT.md` (Pattern Extraction, The 3-Iteration Trigger)
- Always-injected checklist pattern → applicable to any behavior that fails as implicit habit; see also `08-BOOTSTRAPPING.md` (Step 2, Step 4)
- Compaction failure details → `06-FAILURE-MODES.md` (F1: Compaction Catastrophe, F8: Purpose Conflation)
- Content Hierarchy error-recovery perspective → `07-META-LEARNINGS.md` §10b
- Content Hierarchy change-frequency perspective → `08-BOOTSTRAPPING.md` § Content Hierarchy
- Bootstrapping the file structure from scratch → `08-BOOTSTRAPPING.md` (First-Session Template)
