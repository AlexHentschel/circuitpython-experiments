# Session Log

## Current State (living summary)

**Active focus**: Exp14 display library refactor on branch `alex/display-mvp`. Plan captured in `.cursor/plans/display_library_refactor_*.plan.md`. **Phase 1 complete** (commits `84e2d5f`…`6cc2c73`): API-hygiene renames (`interval`→`interval_ms`, `_cancelled`→`_is_cancelled`), immutable-defaults migration, cancellation-doc rewrite, `loop=False` addition to `show_string`/`show_number`, Phase-1 audit loop (6 findings fixed, 1 deferred to on-device), plus memory updates (TECHNICAL §Memory Management on CircuitPython, WORKING_STYLE three new directives). Tier 1 suite 78/78 green throughout. Awaiting user go-ahead for Phase 2 (core-logic changes).

**Active experiment**: `[exp14]` — MakeCode-style display library for 8×8 WS2812b on YD-RP2040.

**Phase**: Execution — Phase 1 complete; Phase 2 pending.

**Key references**: `CONTEXT_HANDOFF.md` (exp14 root), `.cursor/plans/display_library_refactor_*.plan.md`, `.cursor/rules/reference/` (on-demand reading material — concepts absorbed into own memory in self-contained form, not referenced from memory entries).

**Source-of-truth map** (which file owns which kind of content; pre-empts duplication-and-drift):

| Content type | Source of truth | Other files may | Update authority |
|---|---|---|---|
| Behavioral directives (text, scope, status, reinforcement count) | `WORKING_STYLE.md` | reference by descriptive name in prose | Agent (operational) |
| Per-session insights, artifacts, patterns extracted, process corrections, open questions | `SESSION_LOG.md` (this file) | summarize at higher level (e.g. retrospective in plan file) | Agent (operational) |
| Cross-session findings about the system being built (formulas, behaviors, divergences, perf claims) with status | `CONCLUSIONS.md` | restate finding wording with link back; never duplicate the status field | Agent records `unverified` / `evidence-supported` / `disputed` / `invalidated` based on independent evidence sufficiency. No human-elevation tier — user is project owner but not the CircuitPython domain authority. |
| Domain knowledge digest (CircuitPython memory model, encoding conventions, terminology, code map) | `TECHNICAL.md` (schema in place since cold start; content populated starting at P1.7 of the active plan) | reference by section name | Agent records with source tags; promotion happens when independent corroboration is obtained |
| Active plan for the current project | `~/.cursor/plans/display_library_refactor_d42ccd55.plan.md` (Cursor IDE's global plan store at the user's home directory, *not* the project-relative `.cursor/`) | summarize phase-level state in this file's living summary | Agent maintains; phase-close revisions presented to user before applying |
| Provenance of structural memory changes | `CHANGELOG.md` (to be created when the first non-trivial structural change to the memory architecture happens) | n/a | Agent (operational) |

When the same fact has to live in two places (rare; only when duplication serves distinct consumers), log the duplication explicitly here and add a sync-check item to the next phase-close reflection.

**Known consumer-distinct duplications** (sync-check these together on any structural change):

- **Evidence-status tier definitions** — authoritative in `00-memory-system.mdc § Evidence-Status Discipline`; restated for distinct consumers in `02-domain-structure.mdc § CONCLUSIONS.md Conventions` (domain conventions), `memory/CONCLUSIONS.md` header (agent write-time cue when adding entries), `memory/TECHNICAL.md` header (same, for technical entries), and `COLLABORATOR_GUIDE.md § Evidence-status discipline` (user-facing). Sweep all five when the tier model changes — use the two-pass technique in `WORKING_STYLE.md § Document Authoring § Vocabulary-migration sweep` to catch English-sense residue.
- **Scope-tag dimensions** — there are two *orthogonal* dimensions, each with its own authoritative home. (1) *Directive scope* (four-tier `[universal]` / `[user]` / `[project]` / `[task]`): authoritative in `WORKING_STYLE.md` header legend; echoed in `01-interaction-style.mdc § Scope Definitions`. (2) *Domain-content scope* (experiment tag `[expNN]` / `[tooling]` / `[cross-experiment]` / `[universal]`): authoritative in `02-domain-structure.mdc`; echoed in `03-memory-update-triggers.mdc`, `memory/CONCLUSIONS.md` header, `memory/TECHNICAL.md` header. The two dimensions are independent by design — a behavioral directive is tagged by its behavioral scope; a technical finding is tagged by its experiment scope. Don't collapse the two dimensions.

---

## Sessions

<!-- Per-session entries below. Format:
## YYYY-MM-DD: Session N — [active experiment slug]
- Technical insights:
- Artifacts created/updated:
- Patterns extracted:
- Process corrections received:
- Open questions raised:
-->

## 2026-04-17: Session 2 — [exp14] (planning)

- Technical insights:
  - None from the code itself this session — the session was entirely about planning and process.
  - CircuitPython vs. MicroPython divergence is enough of a trap that the technical-memory review loop must force per-claim source tagging (5 divergence examples captured in the plan, sourced from prior general knowledge — *not yet verified*, flagged for verification when P1.7 runs).
- Artifacts created/updated:
  - `.cursor/plans/display_library_refactor_*.plan.md`: full 3-phase plan with audit loops, technical-memory loop, git workflow, working-docs lifecycle, and retrospective tracker. Went through roughly eight revision rounds as the user surfaced meta-principles. Audit & technical-memory loops later restructured around explicit reflection-first opening steps.
  - `working-docs/`: created (empty) as scratch-space convention.
  - `.cursor/rules/memory/WORKING_STYLE.md`: initially added five specific directives, then consolidated four of them into two abstract Core Principles (*pre-commit to targets not shape*, *reflect explicitly at every meaningful checkpoint*) after recognizing the cross-incident pattern. The contradictions-no-default-winner principle stays as its own entry (distinct mechanism: adjudication, not shape). Abstraction-lifecycle convention documented in Retention and Evaluation.
- Patterns extracted (meta-level on planning and memory-keeping):
  - **Memory entries have an abstraction lifecycle**: start specific ("in X situation Y worked") and lift to generalized principles once multiple similar-but-not-identical situations show the same underlying mechanism. Specific incidents become dated evidence in the Notes column, not separate rows. Single-incident entries remain legitimate for stated conventions (commit format, line length) where portability to unseen situations isn't the goal. Consolidation is a deliberate compaction — nothing is dropped, only the level of description changes.
  - **Meta-level default, not universal law**: plans operate primarily at the meta-level (scope, approach, success criteria, unknowns, evidence). Mechanical work with learnings in hand is a legitimate exception. Design work with detailed sketches is acceptable *only if* the sketch is framed as a hypothesis for critical evaluation, with complete rewrite as a legitimate outcome. The failure mode is register drift — shifting from "this is what we might do" to "this is what we will do" without flagging the change.
  - **Framing markers that work**: explicit preamble ("design hypothesis, not mandate"), `target + constraints + open questions` structure, success criteria stated separately from implementation shape. Anti-patterns: embedded pseudo-code presented as spec, specific line numbers for code that may move, exact formulas whose derivation depends on choices not yet made.
  - **Contradiction handling**: never assume the new side or the old side wins. Present both, let user decide, dated-note the loser. The agreement-bias trap has a mirror image: assuming new evidence is automatically more trustworthy than prior memory.
  - **Artifacts vs. templates**: a mandated template is an agreement-bias device in disguise — it pre-commits to a shape before the information is in. Rough examples are useful as illustration; mandatory schemas are not.
  - **Plan-revision check**: silence after a phase is not enough. Either motivate revisions or explicitly state none are warranted — the act of stating it forces the question to be asked.
- Process corrections received:
  - Initial P2.5 ring-buffer section was too prescriptive (helper names, exact sizes, pseudo-code). User: thought itself is fine, framing is wrong — make it a hypothesis, not a mandate.
  - Working-docs folder described with five mandatory file types and naming schemas. User: let structure emerge from content.
  - Memory-loop line said new findings would "correct" old memory. User: no default winner.
  - Commit message examples used conventional-commits prefixes (`refactor(display):`). User: switch to grouped sentence snippets with scope labels (`Display:`).
- Open questions raised (deferred to post-Phase-1):
  - Demo-script scope during refactor: does `code.py` get updated to exercise new API, or stay as-is?
  - P1.7 memory digest: should the Researcher cross-reference existing `TECHNICAL.md`, or start clean?
  - Deferred Tier 2 tests: in scope to unblock, or all punted?

## 2026-04-20: Session 3 — [exp14] (meta-memory pass + evidence-status reconciliation)

- Trigger: user asked me to read `.cursor/rules/reference/00–08` for carry-over learnings from a different (data-science) project the same agent persona had worked on. Decision: keep `reference/` as on-demand reading material; absorb useful concepts into own memory in self-contained form (no cross-references from `WORKING_STYLE.md` / `SESSION_LOG.md` body to `reference/`); reference folder remains useful but doesn't appear in memory wording.
- Patterns extracted (additions):
  - **Implicit-goal preamble for directives**: every behavioral directive should state its *Goal* in addition to Evaluate/Act. Without a stated goal, the directive is unfalsifiable — there's no axis to evaluate whether it's working. Added `Goal:` lines to all three pre-existing Core Principles.
  - **Status notation distinct from Reinforcements count**: a freshly-lifted abstraction inherits incident count but has not been tested at the abstracted form. Marking it `(experimental)` until clean application on situations *outside* the originating set prevents premature confidence in a generalization. Promotes after at least two clean applications.
  - **Generalization stopping rule**: when ascending the abstraction ladder, stop one level *below* a counterexample at the next level OR below the level where the principle loses operational guidance (Evaluate/Act no longer suggest a concrete next move). Over-generalization is the mirror of under-generalization; both cost evaluability.
  - **Scope-transfer-check before importing directives**: directives carry implicit assumptions (authority structure, code maturity, risk profile, collaboration phase). Before importing one observed elsewhere, check each assumption against the current context. Two demonstration cases this session: (1) "validation gate requires user sign-off" failed transfer because user is not the CircuitPython domain authority on this project; (2) "minimal invasiveness — prefer edits" failed transfer because the project is early-phase library code where larger localized rewrites are first-class. Promoted to Core Principle.
- Artifacts updated:
  - `WORKING_STYLE.md`: added Scope column + scope-tag legend (`[universal]`, `[user]`, `[project]`, `[task]`); added Status notation convention; backfilled Scope on all existing entries; added `Goal:` preamble to three pre-existing Core Principles; marked the two consolidated abstractions as `(experimental)` at the abstracted form; added Core Principle (scope-transfer check); added Code Editing directive (rewrite-vs-edit trade-off, `[project]` scope); appended generalization stopping rule and freshly-lifted-abstraction status rule to Retention and Evaluation; added date-verification directive after stamp-error correction.
  - `SESSION_LOG.md`: added Source-of-truth map to the living summary (pre-empts duplication-and-drift across `WORKING_STYLE` / `SESSION_LOG` / `CONCLUSIONS` / forthcoming `TECHNICAL` / future `CHANGELOG` / active plan file). This Session 3 entry.
  - `00-memory-system.mdc`: added bullet 8 to § Update Rules ("state the goal of any new directive"); replaced § Validation Gate section with § Evidence-Status Discipline (no human-elevation tier — promotion depends on independent corroboration, since user is project owner but not CircuitPython domain authority); updated frontmatter description and File Architecture table accordingly; updated See-also reference to flag the validation-gate framing in `reference/04-` as not-applicable.
  - `02-domain-structure.mdc`: pending — see Open work below.
  - `memory/TECHNICAL.md`: updated front matter to drop the human-elevation language from the status-default rule.
  - `memory/CONCLUSIONS.md`: dropped `verified` tier; merged "Validated" + "Evidence-Supported" sections into a single "Evidence-Supported" section; updated header text and the existing pytest-suite entry to reflect mechanical-verification framing.
- Process corrections received:
  - Initial proposal mis-imported the validation-gate and minimal-invasiveness directives without scope-transfer checking. User flagged both. Corrective: do the assumption check *before* the import, not after the user catches the mismatch. Captured as the new Core Principle (scope-transfer check).
  - Initial proposal phrased new memory entries with cross-references to `reference/` folder ("per 04 §Validation Gate", "see 06 §F1"). User: keep memory self-contained. Then on follow-up: granted autonomy if I find the references useful. Final synthesis (mine, retained): keep `reference/` as on-demand reading; memory entries written self-contained with provenance grounded in this project's incidents.
  - Date drift: I stamped multiple session-3 edits with `2026-04-17` (the date in the system-prompt context line) instead of the actual `2026-04-20`. User flagged. Corrective: shell out to `date '+%Y-%m-%d'` before stamping; treat the context date as a hint only. Captured as a new Document Authoring directive.
- Handled-with-care log:
  - This session contains multi-purpose `WORKING_STYLE.md` edits: schema change (added Scope column + Status convention) + backfill on existing entries + addition of three new directives + addition of two convention bullets to Retention + post-hoc date corrections. Multi-purpose edits carry the risk of inadvertently dropping or rewording existing content during structural changes. Mitigation: each sub-change executed as a separate `StrReplace` against an exact-match block; existing directive text preserved verbatim; only column additions and prefixes (`Goal:`, `(experimental)`) added inside existing rows; no entries removed; "Last updated" header lists the kinds of change made. Verified post-edit by re-reading the file.
  - Reconciliation across `00-memory-system.mdc`, `02-domain-structure.mdc`, `memory/TECHNICAL.md`, `memory/CONCLUSIONS.md`, and `memory/SESSION_LOG.md` SoT map was driven by a grep of `verified` and `elevat*` to catch all stale references. F10-style drift mitigation.
- Open questions raised: none new from this pass.
- Session-3 audit pass (triggered by user request after date fix: "reconcile COLLABORATOR_GUIDE.md, then analyze the entire `.cursor/` rules / persona / memory system from scratch for completeness and consistency"):
  - Resumed and completed the interrupted `02-domain-structure.mdc` § CONCLUSIONS Conventions reconciliation; routing row "Validated end-to-end behaviour" now points to `Evidence-Supported (with [expNN])`.
  - `COLLABORATOR_GUIDE.md` reconciled: dropped `verified` tier and "Validated table" references across six locations (file map, intervention mention, § Validation gate renamed to § Evidence-status discipline, where-this-came-from divergence note added, first-session smoke-test bullet 3 rewritten, Mark-a-conclusion intervention rewritten).
  - Cross-file drift fixes:
    - `00-memory-system.mdc`: Active Retrieval item 3 (`validating` → `evaluating`) and Update Rule item 4 (`Conclusion validated/invalidated?` → `Conclusion reached (with supporting evidence) or invalidated?`) — stale tier vocabulary.
    - `03-memory-update-triggers.mdc`: item 3 `validated/evidence-supported claim` → expanded to all four status values; added a one-line note that `WORKING_STYLE.md` uses a distinct four-tier scope dimension.
    - `02-domain-structure.mdc`: TECHNICAL Categories count corrected from "Seven sections" to "Eight sections" (the section list had 8 items).
    - `01-interaction-style.mdc`: § Scope Definitions updated from the legacy three-tier Universal/Domain/Problem model to the four-tier `[universal]` / `[user]` / `[project]` / `[task]` model used in `WORKING_STYLE.md`, with a one-line supersession note; § See also now flags the `reference/04-evidence-and-validation.md` validation-gate framing as not-applicable.
    - `SESSION_LOG.md` SoT map: corrected TECHNICAL.md row from "to be created at P1.7" to "schema in place since cold start; content populated starting at P1.7" (the schema file already exists with templates).
    - `memory/TECHNICAL.md`: `Last updated` bumped to 2026-04-20 and parenthetical clarified (schema unchanged, still cold-start on content).
- Patterns extracted (audit-pass additions):
  - **Vocabulary drift around removed tiers**: when removing or renaming a status tier, a grep for the removed term name is necessary but not sufficient — English-sense uses of the same word (e.g. "validating", "validated", "Validated end-to-end") also need a pass. The `00 → 02 → 03 → 01 → COLLABORATOR_GUIDE → memory/*` traversal caught six distinct occurrences after the primary tier-removal edits missed them.
  - **Parallel schema drift**: when a more-specific model (four-tier scope) supersedes an earlier one (three-tier scope), the older file retains the superseded model until actively reconciled. The cross-injection guarantee of `.mdc` files means both are loaded, silently contradicting each other, until someone reads both end-to-end. Memory-architecture changes need an explicit supersession sweep across all always-injected files.
  - **Schema-vs-content staleness**: "Last updated" headers and SoT map entries can go stale even when the file's *structure* is unchanged. The TECHNICAL.md header said "initial cold-start; no entries yet" but a front-matter rule had been edited in session 3 — the header conflated "schema unchanged" with "file unchanged".
- Audit-pass round 2 (user decisions on the medium-confidence items):
  - **M1** (document `.cursor/plans/` and `working-docs/` in File Architecture): resolved as not-needed. The active plan file already has a dedicated `## Working-docs folder` section plus multiple inline references; as long as the plan mentions the folder, documentation need not propagate to the always-injected rules.
  - **M2** (pre-execution review callout on `mandates/multi-project.md`): applied. Added a new `## Pre-execution review (read before triggering)` section at the top of that file covering four divergences: M3 human-confirmation step vs evidence-status discipline, three-tier vs four-tier scope model, step-8 fifth-item-addition vs `03-` brevity constraint (default: split into `04-multi-project.mdc`), and residual `verified` / "validation gate" vocabulary. Executor instructions: re-read `00`, `01`, `02`, `WORKING_STYLE.md` in full before writing; surface each divergence to the user before proceeding.
  - **M3** (COLLABORATOR_GUIDE phase-expectations table): dropped. The Genesis/Calibration/Productive/Meta-refinement table was prior-project calibration and didn't transfer cleanly.
  - **M4** (`01-interaction-style.mdc § Proactive Engagement` "most reinforced directive in the source engagement" line): retained with generalization. User confirmed prescriptive emphasis is acceptable for this rule (Proactive Engagement was specifically struggled with and repeatedly reinforced). Rewording: "This directive has been repeatedly reinforced and shapes the overall posture of the collaboration — when in doubt about the right level of initiative, err toward proactive surfacing rather than waiting to be asked." Preserves the emphasis signal; drops the "source engagement" cross-reference-to-prior-persona phrasing.
- Patterns extracted (audit-pass round 2):
  - **Single-source-of-truth for cross-artifact facts**: when a fact is covered authoritatively by one document (e.g. the active plan's `## Working-docs folder` section), propagating that fact into every file that could reasonably mention it creates maintenance burden without reducing confusion. Preferred: leave coverage at its natural home and reference if needed, rather than duplicating.
  - **Prescriptive emphasis has legitimate uses**: the default is to avoid prescriptive framing in favor of general principles, but rules that were specifically struggled-with and repeatedly reinforced earn heightened emphasis in their rule text. The framing should be universally-applicable in content even when emphatic in tone.
  - **Inert mandates need divergence callouts, not rewrites**: a declared-but-unexecuted mandate shouldn't be edited to match the current architecture (that defeats the "it represents what was decided at declaration time" purpose). The right move is a top-of-file pre-execution review listing the divergences for the future executor to reconcile.

---

## 2026-04-17: Session 1 — [exp14]

- Technical insights:
  - `lib/display/bitmap_codec.pattern_to_colmajor` is a design-time authoring helper, not a runtime path; perf micro-optimizations are not worth structural complexity here.
  - `"".join(raw.split())` is the idiomatic whitespace-collapse in Python: handles all Unicode whitespace uniformly, avoids the chained `.strip()` + per-char `.replace()` anti-pattern.
  - Tier 1 pytest suite (78 tests) is green on CPython post-restructure — first PENDING item in handoff §7 "Tier 1" can move to DONE.
- Artifacts created/updated:
  - `lib/display/bitmap_codec.py`: fused two-phase rows-list-then-encode into a single pass; unified whitespace handling via `"".join(raw.split())`; fail-fast on row overrun; updated docstring + inline rationale comment.
  - `WORKING_STYLE.md`: recorded evidence-driven critique directive.
- Patterns extracted:
  - When a proposal is framed as "perf concern", quantify the concern (bytes, frequency, call site) before accepting or rejecting. If the cost is negligible *and* the alternative hurts readability/error-reporting, keep the readable version.
- Process corrections received: none.
- Open questions raised: none.

---

## Open Questions

| ID | Question | Since | Refs |
|----|----------|-------|------|
| OQ-MP-1 | Project granularity for multi-project layout: per-experiment, per-theme, mixed, or cross-domain families? | 2026-04-17 | `mandates/multi-project.md § OQ1` |
| OQ-MP-2 | Promotion autonomy: propose-only, auto-cross-project with manual universal, or fully agentic with CHANGELOG? | 2026-04-17 | `mandates/multi-project.md § OQ2` |
| OQ-MP-3 | How to tag pre-existing untagged entries at warm-reset time? (Default to active project for TECHNICAL/CONCLUSIONS, `[universal]` for WORKING_STYLE, flag ambiguous.) | 2026-04-17 | `mandates/multi-project.md § OQ3` |

### Deferred design notes

Items that are not questions needing a near-term answer, but decisions to revisit with accumulated evidence:

| ID | Note | Revisit when | Refs |
|----|------|--------------|------|
| DN-MP-1 | New-project-vs-extend heuristic — can only be refined empirically, not pre-specified. | After 3–5 distinct projects of experience (post-warm-reset). | `mandates/multi-project.md § OQ4` |

### Notes on open mandates

The human has declared an **open mandate** for a multi-project memory architecture, triggered by the phrase **"warm reset"**. Full spec at `mandates/multi-project.md`. Do not pre-emptively restructure — wait for the explicit trigger, then follow the pre-flight checklist in that file. OQ-MP-1 through OQ-MP-3 above should be resolved with the human *before* warm reset executes; DN-MP-1 is intentionally deferred until post-warm-reset evidence exists.
