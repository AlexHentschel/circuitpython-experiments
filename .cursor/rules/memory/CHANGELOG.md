# Memory Architecture Changelog

Provenance log for **structural changes** to the memory system — new files, schema evolutions, consolidations, splits, tier-model changes, cross-file migrations. Per-session insight accretion lives in `SESSION_LOG.md`; per-entry lifecycle detail (Reinforcements increments, status promotions, abstraction liftings) lives in the Notes column of the entry itself. This file captures only events that affect the *shape* of the memory architecture.

Evolution-vocabulary reminder (from `00-memory-system.mdc § Evolution vocabulary`): `extend` · `refine` · `abstract` · `simplify` · `generalize` · `split` · `compact`.

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
