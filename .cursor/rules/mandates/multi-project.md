# Open Mandate: Multi-Project Memory Structure

**Status**: declared, not yet implemented.
**Explicit trigger**: the user saying **"warm reset"** initiates implementation (see § Warm Reset Protocol below).
**Declared**: 2026-04-17, session 0 (pre-Genesis setup).

## Pre-execution review (read before triggering)

This mandate was declared 2026-04-17. Before executing, reconcile these divergences from the subsequent memory-architecture state (introduced 2026-04-20, session 3):

- **M3 promotion ladder** retains `cross-project + human-confirmed ──▶ universal`. The current workspace has no human-elevation tier for technical findings (see `00-memory-system.mdc § Evidence-Status Discipline`): the user is project owner but not the CircuitPython domain authority, so technical-finding promotion depends on independent corroboration, not user ratification. For *working-style* content the user *is* the authority and a sign-off path remains appropriate. Decide at warm-reset time: split by content type, drop the human-confirmation step, or explicitly amend § Evidence-Status Discipline.
- **Target Architecture — scope tiers** use a three-tier model: `[universal]` / `[family:<name>]` / `[project:<slug>]`. The current `WORKING_STYLE.md` uses a four-tier model: `[universal]` / `[user]` / `[project]` / `[task]`. These are not equivalent: `[family:]` captures project grouping (absent from the four-tier); `[user]` captures cross-project user preferences (absent from the three-tier). Decide at warm-reset time: merge the two with a documented mapping, keep them as orthogonal dimensions, or collapse to one.
- **Warm Reset Protocol step 8** proposes adding item 5 to `03-memory-update-triggers.mdc` for cross-project retrieval. That file explicitly warns a fifth item degrades its brevity-based salience, and recommends creating a new always-injected file instead — which step 8's own parenthetical already allows (`Add 04-multi-project.mdc …`). Decide whether to inline or split; default to split unless a strong argument emerges for inline.
- **Vocabulary**: any remaining `verified` / "validation gate" references inside this mandate refer to the superseded tier model. Treat as to-reconcile, not authoritative, during execution.

A warm-reset executor should re-read `00-memory-system.mdc`, `01-interaction-style.mdc`, `02-domain-structure.mdc`, and `memory/WORKING_STYLE.md` in full before writing, and surface each divergence above to the user as an explicit decision before proceeding with any structural step in § Warm Reset Protocol.

## Motivation

The deployed memory system (`memory/WORKING_STYLE.md`, `SESSION_LOG.md`, `TECHNICAL.md`, `CONCLUSIONS.md`) assumes **one domain, one timeline**. In reality, this persona will span:

- Multiple hardware experiments inside CircuitPython (`Exp14`, later `Exp13`, `Exp11`, …)
- Possibly different problem spaces beyond CircuitPython in the future

Today, everything lives in a single flat `memory/`. That works for one project but breaks down when:

1. Working on Project A should not pollute memory about Project B.
2. The agent should be able to *notice cross-project patterns* ("I saw this failure in both Exp11 and Exp14").
3. A completely unrelated domain (e.g. non-CircuitPython) would need its own `TECHNICAL` / `CONCLUSIONS` space without discarding the persona's accumulated working-style calibration.

The generalized blueprint (`reference/08-bootstrapping.md § Transferring to a New Domain`) treats multi-domain as *sequential* (keep some files, reset others). This mandate extends it to **parallel, coexisting projects with cross-pollination as a first-class feature**.

## Target Architecture

```
.cursor/rules/memory/
├── universal/                   Level 2-3 content; applies to any project
│   ├── WORKING_STYLE.md         communication/editing prefs (was top-level)
│   ├── PATTERNS.md              cross-project generalized patterns (new)
│   └── CHANGELOG.md             structural changes to the memory system
├── projects/
│   ├── _INDEX.md                roster: slug, status, family, last-touched, path globs
│   ├── circuitpython-exp14-display/
│   │   ├── CONTEXT.md           scope, goals, success criteria, phase, open-questions
│   │   ├── SESSION_LOG.md       per-project timeline
│   │   ├── TECHNICAL.md         per-project domain knowledge
│   │   └── CONCLUSIONS.md       per-project validated findings
│   └── <future projects>/
└── crossref/                    agent-curated lookups (cheap, always safe to read)
    ├── BY_TOPIC.md              e.g. "GPIO timing" -> [exp11, exp13]
    └── BY_PATTERN.md            e.g. "Pylance stub mismatch" -> [exp10, exp14]
```

### Scope tiers (generalize the existing blueprint tiers into operational tags)

Every entry carries exactly one tag:
- `[universal]` — applies to any project (lives in `universal/`)
- `[family:<name>]` — applies to a project family, e.g. `[family:circuitpython]`
- `[project:<slug>]` — applies to one project only

## New Mechanisms (absent in the current single-domain layout)

### M1. Active-project identifier
Agent determines the current project by looking up the most-recently-edited file path against `projects/_INDEX.md`'s `path globs` column. If no match or ambiguous, **ask before writing per-project memory**. This prevents cross-contamination — the highest-risk failure mode of this architecture.

### M2. Scope tagging (mandatory on every new entry)
Every memory entry begins with its scope tag. The tag determines its home file and the caution level for changes.

### M3. Promotion ladder with explicit triggers

```
observed-once ── 3x in same project ──▶ recurring-in-project (stays in TECHNICAL)
              ── 2+ projects ─────────▶ cross-project (move to universal/PATTERNS.md)
              ── cross-project + human-confirmed ──▶ universal
```

Agent **proposes** promotions in `SESSION_LOG`. Promotion is **executed only with human sign-off** (reuses the blueprint's validation gate).

### M4. Cross-project retrieval protocol
New item to add to `03-memory-update-triggers.mdc` at warm reset time:

> *"5. Before finalizing a finding: scan `crossref/BY_TOPIC.md` for related entries in other projects. If a similar issue is recorded elsewhere, reference it and consider whether to propose a promotion."*

Keeps context cost low (read the cheap index, not full project memory).

### M5. Attention scoping
Session start reads:
- **Always**: `universal/*` (small), `projects/_INDEX.md` (roster)
- **Active project only**: its `CONTEXT.md`, last 1–2 `SESSION_LOG` entries, `TECHNICAL`, `CONCLUSIONS`
- **Other projects**: not read unless `crossref/` points to them or user explicitly asks

This is the "context-dependent attention" the user requested, made operational.

### M6. Demotion / falsification path
If `PATTERNS.md` claims "X is universal" and a new project refutes it:
1. Mark the `PATTERNS.md` entry `disputed`
2. Record counter-evidence in that project's `CONCLUSIONS.md`
3. Log the demotion in `universal/CHANGELOG.md`

Prevents universals from silently rotting.

### M7. Warm reset protocol (the trigger, defined below)

## Warm Reset Protocol

**Trigger**: user says the exact phrase **"warm reset"** (case-insensitive, but strict phrase match — no paraphrases). If the user says something that *sounds* like a trigger but isn't the exact phrase (e.g. "initialize multi-project memory", "let's promote the memory", "start using projects now"), do **not** treat it as a trigger — instead restate the mandate and ask the user to confirm by saying the canonical phrase. This prevents accidental structural changes from near-miss phrasing.

**Precondition check**: confirm with user before executing — warm reset is a structural (Level 2-3) change. Read `reference/06-failure-modes.md § F1 (Compaction Catastrophe)`, `§ F8 (Purpose Conflation)`, and `§ F10 (Duplicated Data Drift)` first. Announce what will be done; proceed only on explicit confirmation.

**Steps** (executed as one deliberate maintenance session, never as a side effect):

1. **Snapshot the current `memory/`** into `.cursor/rules/memory-pre-warm-reset-<YYYYMMDD-HHMMSS>/` (unchanged copy; serves as rollback). Use a timestamp with seconds precision so repeated attempts never clobber an earlier snapshot.
2. **Create `CHANGELOG.md`** at `memory/universal/CHANGELOG.md` (if it doesn't exist per blueprint's deferred-creation rule). First entry: the warm reset itself, with date, trigger, and list of structural changes to follow.
3. **Create new directory tree** per § Target Architecture: `universal/`, `projects/`, `crossref/`.
4. **Move `WORKING_STYLE.md`** unchanged from `memory/` to `memory/universal/`. Create empty `memory/universal/PATTERNS.md`.
5. **Create `projects/_INDEX.md`** with header + one row per *currently attached* experiment (initially just Exp14). Schema:

   | slug | title | family | path globs | status | last-touched | notes |
   |------|-------|--------|-----------|--------|--------------|-------|
   | `circuitpython-exp14-display` | Exp14 Display Library | circuitpython | `2026-04_Exp14_*/**` | active | (date) | initial project at warm reset |

6. **Move existing `TECHNICAL.md`, `CONCLUSIONS.md`, `SESSION_LOG.md`** content into `projects/circuitpython-exp14-display/` (preserving any accumulated content, tagging untagged entries `[project:circuitpython-exp14-display]`). Create empty `CONTEXT.md` with a stub for project scope/goals.
7. **Create empty `crossref/BY_TOPIC.md` and `crossref/BY_PATTERN.md`** with header explaining the format.
8. **Update `.mdc` rule files**:
   - `00-memory-system.mdc`: replace "File Architecture" section with new multi-project paths; preserve all other rules (validation gate, active retrieval, update rules — just re-point paths).
   - `02-domain-structure.mdc`: replace "Active Experiment Detection" with the new **active-project identifier** (M1) that uses `projects/_INDEX.md`.
   - `03-memory-update-triggers.mdc`: add item 5 (cross-project retrieval, M4). Check that total size stays acceptable; if not, split into two always-injected files.
   - Add `04-multi-project.mdc` (new, alwaysApply: true) containing: scope tagging rule (M2), promotion ladder (M3), attention scoping (M5), demotion path (M6). Keep under 3 KB.
9. **Remove the now-empty `memory/WORKING_STYLE.md`, `SESSION_LOG.md`, `TECHNICAL.md`, `CONCLUSIONS.md`** (their content has been moved or referenced). Verify no orphaned references remain.
10. **Update `COLLABORATOR_GUIDE.md`** to describe the new layout.
11. **Log completion** in `memory/universal/CHANGELOG.md` with a summary of moves + a `status: warm-reset-completed` flag.
12. **Verify** with the human: open questions (§ Open Questions below) should be resolved before warm reset; if any remain unresolved, flag them and request decisions before writing to the new structure.

**Anti-goal**: warm reset is **not** a content rewrite. It is a structural reorganization. No existing content is deleted or summarized during the reset — only moved and tagged. Compaction/rewriting, if needed, happens as a separate maintenance session after warm reset stabilizes.

## Open Questions (resolve at warm-reset time)

These are unanswered at declaration time. The user tabled them when the broader multi-project conversation paused. Any of them could materially change the warm reset.

### OQ1. Project granularity

What counts as a project? Options:
- **(a)** Each experiment is its own project (`Exp11`, `Exp13`, `Exp14`, … each with own `projects/<slug>/`).
- **(b)** Group experiments into themes (e.g. "ws2812-lighting" covers `Exp11` + `Exp13`; "display-libraries" covers `Exp14`). One project per theme.
- **(c)** Mixed: most experiments = own project; closely related ones share a project. Decide case-by-case via `_INDEX.md`.
- **(d)** Projects span beyond CircuitPython (future). CircuitPython becomes one family; wholly different domains (e.g. Isana crash-sensor) are separate families under the same persona.

### OQ2. Promotion autonomy

How much autonomy does the agent have to promote patterns up the ladder?
- **(a)** Propose only — agent writes promotion proposals into `SESSION_LOG`; human explicitly approves before moving anything into `PATTERNS.md` or `universal/`.
- **(b)** Auto-promote cross-project on the 2-projects trigger; human approval only for the final step to `universal`.
- **(c)** Full agentic promotion, but every promotion logged in `CHANGELOG` with evidence and demotable at any time.

### OQ3. Scope-tagging of pre-existing entries

At warm-reset time, existing memory may contain untagged entries. Policy:
- Default all pre-existing `TECHNICAL` / `CONCLUSIONS` entries to the single project active at that moment.
- Default all pre-existing `WORKING_STYLE` entries to `[universal]` (since working-style is about the human, not a project).
- Flag ambiguous entries for human review rather than guess.

### OQ4. When to spin up a new project vs extend existing

Proposed heuristic in `_INDEX.md` header: *"New project if ≥1 new board, new primary library focus, or new problem domain."* Subject to revision after 3–5 projects of experience.

> **Note**: this item is tracked in `memory/SESSION_LOG.md` as **DN-MP-1** (deferred design note), not as a true open question — it cannot be resolved pre-warm-reset because it requires empirical evidence from multi-project operation. Warm reset may execute with DN-MP-1 unresolved; it only blocks on OQ1–OQ3.

## Pre-warm-reset checklist for the agent

When the user says "warm reset", before executing:

- [ ] Read this file (`mandates/multi-project.md`) end-to-end
- [ ] Read `reference/06-failure-modes.md § F1 (Compaction Catastrophe), § F8 (Purpose Conflation), § F10 (Duplicated Data Drift)` — the three failure modes most relevant to a structural reorganization
- [ ] Read `memory/WORKING_STYLE.md` current state
- [ ] Confirm answers to OQ1, OQ2, OQ3 are recorded (ask if not)
- [ ] State the planned changes back to the user
- [ ] Wait for explicit "go ahead" before writing

## Per-project operational calibrations

Operational calibrations (posture, authority breadth, collaboration style) that are valid for the currently-attached project and should be **re-evaluated whenever a different project becomes active** — whether via warm reset, adding a new project to the roster, or the user's focus shifting. Recorded here so they don't silently transfer across project boundaries. Parallels the § Pre-execution review divergences but at runtime, not at structural-reorganization time.

Entry schema: name, active project, granted posture, fallback when a different project is active, source of the grant.

### Authority breadth for resolving low-stakes directive tensions

- **Active project**: `exp14` — *Display library for 8×8 WS2812b on YD-RP2040 (CircuitPython)*. Under the target multi-project architecture this will be `[project:circuitpython-exp14-display]` / `[family:circuitpython]`.
- **Granted posture**: the agent is granted authority to resolve *any* low-stakes directive tension encountered during operational work — not just tensions within its own memory/rule system. Scope examples inside the grant: plan item vs. observed evidence; stated-user-preference vs. inferred-user-preference; two memory directives pulling opposite ways; plan shape vs. in-flight learning on the same phase.
- **Always-on constraint**: transparency. Surface observation + conclusion to the user in the same turn so they can correct if they disagree. Silent adjudication remains off-limits regardless of stakes.
- **Fallback on other projects / problem spaces**: narrower — default back to "within my own memory/rule system only" and escalate everything else, pending a fresh authority grant from the new project's owner. Re-evaluate explicitly at project-switch time.
- **Source**: user statement 2026-04-20 during Phase-1 memory updates on `display_library_refactor_d42ccd55.plan.md`. Direct quote: *"For the problem space at hand (CircuitPython), any low-stakes directive tension you encounter you have the authority to resolve (as long as you do it with the necessary attention to detail). This trade off might be different for other problem spaces."*
- **Directive text (where the posture itself is defined)**: `memory/WORKING_STYLE.md § Judgment & Escalation`.

## Rationale references (on demand)

- Full blueprint on transferring to new domains: `reference/08-bootstrapping.md § Transferring to a New Domain`
- Content hierarchy (why warm reset is a Level 2-3 change): `reference/01-memory-system.md` (not copied locally; see generalized-agent-learnings source) / `00-memory-system.mdc § Content Hierarchy`
- Scaling rule (split over prune): `00-memory-system.mdc § Maintenance`
- Generalization tiers this architecture operationalizes: `reference/00-overview.md § Generality Tiers`
