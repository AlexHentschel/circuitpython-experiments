# Memory Architecture Changelog

Provenance log for **structural changes** to the memory system — new files, schema evolutions, consolidations, splits, tier-model changes, cross-file migrations. Per-session insight accretion lives in `SESSION_LOG.md`; per-entry lifecycle detail (Reinforcements increments, status promotions, abstraction liftings) lives in the Notes column of the entry itself. This file captures only events that affect the *shape* of the memory architecture.

Evolution-vocabulary reminder (from `00-memory-system.mdc § Evolution vocabulary`): `extend` · `refine` · `abstract` · `simplify` · `generalize` · `split` · `compact`.

## 2026-06-14 — extend/generalize: memory-lifecycle directives + § Maintenance rules 4–6

**Change**: codified two memory-lifecycle patterns Alex stated as general, and extended the always-injected maintenance rule to match.

- New `WORKING_STYLE.md § Core Principles` directive *Categories form by accumulate-then-split, not up-front design; expect overlap, cross-link it* `[universal]` — generalizes the persona's own defer-creation rule + the warm-reset C7/D8(c) graduation + `_RELATIONS.md` cross-refs into a persona-wide structural-epistemics principle.
- New `WORKING_STYLE.md § Core Principles` directive *Batch heavy memory restructuring into deliberate, user-gated lifecycle iterations; keep a backlog and recommend when beneficial* `[universal]` — adds (a) a maintenance backlog register (`MAINTENANCE_BACKLOG.md`, deferred-creation) and (b) a proactive-recommend duty atop the existing "compaction is always deliberate" rule.
- `00-memory-system.mdc § Maintenance`: extended item 4 (accumulate-then-split + cross-link) and added item 5 (lifecycle-iteration batching + backlog + recommend); old item 5 (CHANGELOG logging) renumbered to 6.

**Trigger**: Alex described both as common patterns and asked to plan heavy reorg as broader, user-gated memory-lifecycle iterations with an accumulated TODO list, recommending iterations when clearly beneficial.

**Deferred-creation note**: `MAINTENANCE_BACKLOG.md` is named but not yet created — no substantive backlog beyond the warm reset (which has its own plan dir as that iteration's todo list). Create on the first real deferred restructure item, per the same discipline `MONITORING.md` uses.

**Level note**: item 5/6 touches the always-injected `00-memory-system.mdc` (Level 3 meta-rule) — additive, precedent-following (mirrors the MONITORING.md addition), logged here per § Maintenance.

## 2026-06-14 — extend: durable reference copies + two persona directives (cold-AI, flexible-plans)

**Change**: imported two external persona docs into durable in-workspace storage and wired each to an operational directive.

- New reference files (verbatim copies with a provenance header) in `.cursor/rules/reference/`: `cold-ai-paradigm.md`, `flexible-plans-for-ai-execution.md`. These join the existing `00-08` reference set.
- New `WORKING_STYLE.md § Core Principles` directive *Apply the cold-AI write-time gate before persisting any content* `[universal]` — operational trigger form of the cold-AI paradigm.
- New `WORKING_STYLE.md § Core Principles` directive *Flexible-plan layered commitment for agent-executed plans* `[universal]` — umbrella over the pre-existing siblings *Pre-commit to targets, not shape* and *Reflect explicitly at every meaningful checkpoint*; adds authority-handoff map, criteria-revision gate, exit ramps, diminishing-returns termination, scope-discipline-under-surprise. Deliberately NOT a duplicate — cross-references the two siblings as its sub-parts.
- `WORKING_STYLE.md § Human Profile` calibrated for Alex.

**Trigger**: Alex asked to integrate the cold-AI paradigm (session start) and *Flexible Plans for AI Execution* (this turn) into the persona, explicitly flagging the `~/Developed/AI/generalized-agent-learnings/` source folder as **ephemeral** — so referencing files there is fragile; copy them locally. The flexible-plans doc will be used next to draft the Option-B (`warm reset`) plan.

**Rationale for copy-not-reference**: a directive whose reference form lives in an ephemeral folder fails the cold-AI lifecycle test (a future session may find the pointer dangling). Durable copies in `reference/` make the persona self-contained. Verbatim (not derived) because both docs are already dense, cold-AI-compliant, and needed at full fidelity for the upcoming planning use.

**Anti-duplication discipline**: the flexible-plans directive overlaps heavily with two existing Core Principles. Per the abstraction-lifecycle rule, it was written as an umbrella that *names* the siblings as its operational sub-parts rather than restating them — only the genuinely-new mechanisms (authority handoffs, criteria gates, exit ramps, termination heuristic) are spelled out.

**Files changed**: `reference/cold-ai-paradigm.md` (new), `reference/flexible-plans-for-ai-execution.md` (new), `WORKING_STYLE.md` (header + Human Profile + two Core Principles directives), this file. No `.mdc` rule-file changes. No `warm reset`.

**Verification**: both reference files exist and are readable; both directives point at the local copies (grep `reference/cold-ai-paradigm.md` and `reference/flexible-plans-for-ai-execution.md` in `WORKING_STYLE.md`). Flexible-plans directive promotes to `established` after one clean application — the warm-reset plan is the first candidate.

## 2026-04-26 — refine: placement-gate in always-injected trigger

**Change**: strengthened `03-memory-update-triggers.mdc` item 1 with an explicit discriminator question ("Does this directive govern the shape of a code artifact?") as a mandatory placement gate before writing any new directive. Updated the placement-discipline bullet in `WORKING_STYLE.md § Retention and Evaluation` with the three-incident recurrence log and a pointer to the always-injected gate as the systemic fix.

**Trigger**: third proximity-bias mis-placement incident (session 7: *Public contract, not private coupling* placed in `WORKING_STYLE.md § Document Authoring`, should have been `CODING_PRINCIPLES.md § Core Principles`). Same failure mode as session 6 (two incidents). The existing placement-discipline bullet described the correct procedure but lived in a retrospective section with insufficient salience at decision time. User asked: "reflect on what you would need to change to do it correctly right away next time."

**Root-cause analysis**: the gate question ("code-shape vs. collaboration-posture?") was documented only in `WORKING_STYLE.md § Retention and Evaluation` — a reference section read during reviews, not during the placement act itself. `03-memory-update-triggers.mdc` item 1 said "pick by content domain" — a routing hint without a concrete discriminator. The fix moves the discriminator to the only file with guaranteed salience at decision time: the always-injected trigger.

**Files changed**: `03-memory-update-triggers.mdc` (item 1 rewritten with gate question), `WORKING_STYLE.md § Retention and Evaluation` (placement-discipline bullet updated with recurrence log + systemic-fix pointer), this file.

## 2026-04-21 — extend: font-distortion investigation closure

**Change**: added content-only entries across four files as closure for the font-distortion investigation (session 6 continuation). No schema changes, no file-structure changes. Logged here because the additions span four memory files and the coherence of the batch is load-bearing — reading any one entry in isolation without the others would lose the context chain.

**Changes by file**:

- `CODING_PRINCIPLES.md § Core Principles`: new `(experimental)` directive ***When localizing a bug in a pipeline, instrument stages before speculating***. `[universal]`. Derived from the font-distortion debugging cycle where analytical narrowing circled for multiple exchanges and was settled by two probe passes. Consolidates two candidate sub-directives (hypothesis-space-bounding to include input data; instrumentation-over-speculation) into one entry because the action is unitary.
- `TECHNICAL.md § Fonts for pixel-accurate displays`: new section. `[cross-experiment]`-scoped domain fact on why outline fonts auto-rasterized at small pixel sizes fail structurally, with the mechanism argument, practical rule, candidate bitmap fonts, and rendering-code implication for exp14.
- `MONITORING.md § Entries`: two new entries. (1) *Follow-up: font swap for pixel-accurate display on exp14* — deferred action with concrete trigger and replacement-font candidates. (2) *Status-promotion trigger* for the new pipeline-investigation directive, tracking the path from `(experimental)` → `established` at second cross-domain incident.
- `SESSION_LOG.md § Session 6`: continuation sub-entry below the existing session-6 block capturing the font-distortion investigation.

**Trigger**: font-distortion investigation closed with enough structure to be worth preserving as both a reproducer (in `working-docs/`) and a set of promoted learnings (across memory files). User direction: "collect and memorize learnings; consolidate and condense and generalize memories".

**Consolidation vs enumeration discipline**: the investigation produced multiple candidate directives — bound the hypothesis space, instrument rather than speculate, validate third-party data independently, outline fonts are unsuitable at tiny sizes. Applied the abstraction-lifecycle rule from `WORKING_STYLE.md § Retention`: merged the first three into a single code-craft directive (their action is unitary — "write probes, let data decide") rather than three separate entries. The fourth is a domain fact, not a directive, and landed in `TECHNICAL.md` as such.

**Propagated updates**: per-file header notes updated with session-6-continuation stamp pointing at this entry. No workspace-level (`.cursor/rules/*.mdc`) changes — this batch is content within existing schemas.

**Verification**: the reproducer at `working-docs/font-distortion-probe.py` + writeup at `working-docs/font-distortion-findings.md` are the out-of-memory anchor for the content. `MONITORING.md` entries will self-verify on recurrence.

## 2026-04-21 — extend: introduced `MONITORING.md`

**Change**: created new memory file `MONITORING.md` as sibling to `TECHNICAL.md` / `CONCLUSIONS.md` / `WORKING_STYLE.md`. Seeded with two entries from session 6 (scope-lift candidate for *Cross-runtime citations require a grounding note*; promotion trigger for further MicroPython perf-guidance source-verification).

**Trigger**: user flagged a recurring pattern within this session — "I present a convincing argument that acting now is premature; user chooses to act pre-emptively anyway because the memory system has no way to notice deferred observations on recurrence". Two instances this session (the LOAD_FAST carry-over claim; the two-pass vocabulary-migration directive earlier). User directive: "add a bucket to note 'considerations under monitoring' where you very very briefly record aspects where we want to do something if it comes up again."

**Problem this closes**: the stateless-retrieval memory architecture offers no primitive for detecting recurrence of a deferred observation across sessions. Writing down the observation *plus an explicit trigger + action-on-trigger* converts the recurrence-detection problem into a retrieval problem, which the system does handle: at session start, `MONITORING.md` is scanned, entries become resident, and when a potentially-triggering situation appears, recognition fires.

**Rationale for separate file (not a section of an existing file)**:

- Content shape is distinct — each entry is a *trigger registered against a hypothetical future situation*, not a directive (current posture), a finding (status-tagged claim), or a session insight (accretive record). Folding into `WORKING_STYLE.md` or `CODING_PRINCIPLES.md` would blur the triggered-action semantics; folding into `SESSION_LOG.md` would lose cross-session residency (session-local entries fall out of the active-retrieval window over time).
- `TECHNICAL.md § Verification Queue` is the closest structural analog — a queue of items pending action — but is scoped to on-device verification of CircuitPython claims. `MONITORING.md` is broader: it can hold directive scope-lift candidates, meta-patterns, and non-technical observations.
- Per `00-memory-system.mdc § Maintenance` — "prefer splitting over pruning. If a file grows large, create a topic file and reference it from the index."

**Schema**: bulleted entries with Observation / Trigger / Action on trigger / First observed / Scope fields. Brief — user's framing "very very briefly". Retention: on recurrence → execute action → remove entry (action handles it). Stale entries (no recurrence in 3+ sessions of relevant work) trigger re-evaluation per file header.

**Propagated updates** (workspace-level — shared across all four projects in `/Users/alex/Development/VsCode/CircuitPython/.cursor/`):

- `00-memory-system.mdc § File Architecture`: new row for `MONITORING.md`.
- `00-memory-system.mdc § Active Retrieval`: new step 4 — read `MONITORING.md` at session start whenever present (residency is necessary for recognition).
- `00-memory-system.mdc § Update Rules`: new rule 9 — route single-incident + recurrence-gated observations here, with explicit guard against using it as a "later" bucket for items that should be acted on now.
- `03-memory-update-triggers.mdc`: folded into existing step 3 (finding routing) rather than adding a 5th item — the file explicitly warns against growing past four items.
- `COLLABORATOR_GUIDE.md` tree diagram: added MONITORING.md plus the two previously-missing files (`CODING_PRINCIPLES.md`, `CHANGELOG.md`).

**Propagated updates** (per-project — this exp14 project only):

- `SESSION_LOG.md § Source-of-truth map`: new row.
- `SESSION_LOG.md § Session 6`: entry captures the architectural correction and seed entries.

**Deferred items**: none — the bucket is itself the deferral mechanism, so there is no need to defer *this* change.

**Verification**: mechanism test at next session start — if the LOAD_FAST scope-lift situation arises (e.g. a CPython-from-CircuitPython citation comes up), entry 1 of `MONITORING.md` should fire and route to the documented action. If it doesn't fire, the residency-at-session-start step was insufficient and the rule needs strengthening.

## 2026-04-21 — refine: re-placed two directives added in session 6

**Change**: two directives added earlier in session 6 to `WORKING_STYLE.md § Document Authoring` were re-placed after a user-prompted review of placement criteria:

1. ***Function and method docstrings should be self-contained*** — migrated to `CODING_PRINCIPLES.md § Core Principles`. Docstrings are part of the code artifact; directives that shape their content belong with other code-shape rules.
2. ***Announce memory edits concisely; don't present them verbatim unless uncertainty warrants a check*** — moved within `WORKING_STYLE.md` from § Document Authoring → § Communication Style. Collaboration-posture directive about calibrating verbosity on memory surfacing, not a convention for how written artifacts look.

**Preserved verbatim**: Direction, Scope, Reinforcements, Last Applied, Notes — both migrations copy columns without change. Added a terminal Notes sentence to each entry recording the re-placement and reason.

**Trigger**: user question "what's your rationale for not placing these close to other coding conventions?" — placement had defaulted to proximity (existing § Document Authoring neighbors like *abbreviations on first use*, *line length 130*) rather than to the split criteria from the 2026-04-21 `CODING_PRINCIPLES.md` introduction.

**Root cause**: placement-by-proximity is a weak signal when the candidate sections both contain entries touching similar-looking surface concerns (comments, docstrings). The boundary test from the earlier split entry — *"does this describe how code should look, or how I should collaborate / communicate / edit?"* — discriminates cleanly but must be applied explicitly at first-placement time to avoid the retroactive-migration overhead.

**Propagated updates**:
- `WORKING_STYLE.md` header: session-6 note captures the re-placement.
- `WORKING_STYLE.md § Retention and Evaluation`: new bullet on placement discipline — apply split criteria at first-placement time, not retroactively.
- `CODING_PRINCIPLES.md` header: session-6 note captures the migration-in.
- `SESSION_LOG.md § Session 6`: updated to reflect the correction.

**Meta-pattern**: this is a small-scale reinforcement of the pattern already flagged in the 2026-04-21 `split` entry above — *deferral rationales should be evaluated against their own cost model*. Placement rationales have the same property: "§ Document Authoring fits because the neighbors look similar" is a plausible-sounding framing whose actual discrimination against the split criteria is zero.

## 2026-04-21 — extend: introduced `CODING_PRINCIPLES.md`

**Change**: created new memory file `CODING_PRINCIPLES.md` as sibling to `WORKING_STYLE.md`, seeded with six `(experimental)` directives.

**Trigger**: retrospective on the `display.geometry.build_lut` refactor produced a batch of coding-craft learnings (algebra-before-implementation, clarity-debt accounting, primitive-convenience cost test, strict validation on cold sites, high-level structure in code, test design by bug taxonomy). User flagged that these are "adjacent to technical insights" and "we are going to accumulate lots more coding conventions and best practises", and asked for an upfront organization rather than mixing them into `WORKING_STYLE.md`.

**Rationale for split (not extend `WORKING_STYLE.md`)**:
- Content boundary is clean: `WORKING_STYLE.md` catalogs how I *collaborate* (communication posture, process, judgment, artifact conventions); `CODING_PRINCIPLES.md` catalogs how *code itself* should be written (API shape, structure, correctness-argument hygiene, test construction).
- Accumulation rate: expected high enough to earn its own home. Per `00-memory-system.mdc § Maintenance` — "prefer splitting over pruning. If a file grows large, create a topic file and reference it from the index."
- Sibling not sub-file: both sit directly in `memory/`, both update freely, same authority model.

**Schema inheritance**: `CODING_PRINCIPLES.md` inherits `WORKING_STYLE.md`'s metadata schema, abstraction lifecycle, scope tags (`[universal]` / `[user]` / `[project]` / `[task]`), and status notation (`(experimental)` → `established`). Single source of truth for those conventions stays in `WORKING_STYLE.md` header and § Retention and Evaluation; the new file references them rather than duplicating.

**Propagated updates**:
- `00-memory-system.mdc § File Architecture`: new row for `CODING_PRINCIPLES.md`.
- `03-memory-update-triggers.mdc § item 1`: broadened from "Update `WORKING_STYLE.md`" to "Update `WORKING_STYLE.md` or `CODING_PRINCIPLES.md` depending on the directive's domain". No fifth item added — brevity constraint preserved.
- `WORKING_STYLE.md § Domain-Specific` — existing MCU-specific "library primitives do not bake convenience" directive: added cross-reference Note line pointing to the universal form in `CODING_PRINCIPLES.md § Core Principles`.
- `SESSION_LOG.md` SoT map: new row for `CODING_PRINCIPLES.md`.

**Boundary case deferred** (original position — superseded same-day by the follow-on migration entry below; retained here for provenance): two entries in `WORKING_STYLE.md § Code Editing` — *Immutable defaults go directly in the signature* and *Decompose procedural logic into small helpers* — were identified as arguably coding-craft directives that belong in `CODING_PRINCIPLES.md`. Deferral rationale at the time was "preserve the Reinforcements / Last Applied trail without the overhead of a migration note". User challenged the rationale: the schema is identical, so the entries copy across verbatim with no data loss. Rationale didn't hold; migration executed — see next entry.

**First structural change trigger met**: per `00-memory-system.mdc § File Architecture`, this file was "defer creation until first structural change". This is that change.

## 2026-04-21 — split: migrated two entries from `WORKING_STYLE.md § Code Editing` to `CODING_PRINCIPLES.md § Core Principles`

**Change**: moved two entries verbatim, same-session follow-on to the `CODING_PRINCIPLES.md` creation above:

1. ***Immutable defaults go directly in the signature*** — code-shape rule (API signature property). `[universal]`, Reinforcements 1, Last Applied 2026-04-20. Evidence anchor: `core.py` P1.2 remap cleanup.
2. ***Decompose procedural logic into small, self-contained helpers*** *(experimental)* — code-structure rule (helper size, invariant naming). `[universal]`, Reinforcements 1, Last Applied 2026-04-20. Evidence anchor: Phase-2 cross-cutting directive for `display_library_refactor_*.plan.md`.

**Preserved verbatim**: Direction text, Scope, Reinforcements, Last Applied, Notes — all columns copied without modification. No text rewording at migration time; the entries read identically in their new home.

**Stayed in `WORKING_STYLE.md § Code Editing`**: two editing-posture directives:
1. ***Rewrite-vs-edit trade-off for early-phase library code*** *(experimental)* — frames the change-shape decision in terms of user review cost and phase-dependent default posture. Collaboration/process, not code-shape.
2. ***Re-read the current file state before editing when collaborative-edit drift is plausible*** *(experimental)* — editing discipline / tool-use posture. Collaboration/process.

**Trigger**: user challenged the "Boundary case deferred" deferral in the prior entry — "why don't we migrate them now?" The cited deferral rationale (preserve Reinforcements trail) didn't survive scrutiny: schema identity means verbatim copy preserves the trail at zero cost.

**Boundary test applied**: *"Does this describe how code should look (code-shape) or how I should edit (collaboration/process)?"* The two migrated entries describe code properties (signature shape, helper decomposition). The two that stayed describe editing behavior (when to rewrite vs edit; when to re-read the file). Clean cut.

**Propagated updates**:
- `WORKING_STYLE.md` header: session-5 note extended to cover the migration.
- `CODING_PRINCIPLES.md § Core Principles`: two new rows appended, count 6 → 8.
- `WORKING_STYLE.md § Code Editing`: two rows removed; section now tightly scoped to editing-posture directives.
- `SESSION_LOG.md`: Session 5 entry updated to note the migration; open-question about these entries resolved.

**Meta-pattern captured** (worth flagging for `SESSION_LOG.md § Patterns extracted`): *deferral rationales should themselves be evaluated against the cost model they invoke.* The original "preserve the trail" framing was plausible-sounding but factually wrong — the schema guarantees preservation at zero cost. Cargo-culted caution can substitute for real caution when not evidence-checked. Evaluate deferral rationales the same way directive proposals get evaluated: "does the stated cost actually exist?"

**Log style for future entries** (convention, not mandate):

- Date-stamped header: `YYYY-MM-DD — <verb>: <one-line summary>` using the evolution vocabulary.
- Sections: Change / Trigger / Rationale / Propagated updates / Deferred items / Verification.
- Keep entries as short as the change allows. Cross-reference the session log for narrative; this file is just the structural ledger.
