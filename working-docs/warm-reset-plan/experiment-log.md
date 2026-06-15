# Experiment Log — warm-reset planning (sub-agent technique tuning)

Consumer: AI only, dense. Append-only. Records sub-agent dispatches (and other technique-tuning) so a future cold AI
inherits *how to use sub-agents well here* without re-deriving it. Governance: `_META.md § Sub-agent strategy`.
Model slugs: crawl/extract → `composer-2.5-fast` (explore, readonly); reason/abstract → `claude-opus-4-8-thinking-high`
(or the Opus 4.8 parent directly). Created 2026-06-14.

## Current best practice (evolving — update when a cycle confirms/refutes a technique)

**After cycle 1 (exp-1, exp-2):**
- **Path/reference inventory (exp-2): composer-2.5 explore = strong fit.** Exhaustive ripgrep enumeration with file:line + a by-file rollup is exactly the crawl shape composer does well. H1 *confirmed* for this task type. Caveat: a 600+ row table will be truncated in the returned message and spilled to the agent-tools file; ask for a **rollup + the decision-critical subset inline** (here: the `.mdc`/mandate/COLLABORATOR_GUIDE rows that gate dead-path risk) rather than the full dump — the long tail (prose mentions in SESSION_LOG/CHANGELOG/reference) is low-value.
- **Content-by-domain inventory (exp-1): partial.** The narrative summary surfaced (and was correct on the load-bearing fact: only display/fonts/runtime populated; power/i2c/deep-sleep/fuel-gauge empty), but the **actual T-A/T-B tables did not appear in the returned message body**. Lesson: for extraction whose *value is the table itself*, instruct the sub-agent to **paste the tables inline in its final response** (not "produce tables" — they can end up only in scratch). When the target files are small (TECHNICAL/CONCLUSIONS here are mostly empty schema), reading them directly in the parent is cheaper + more reliable than delegating. H1 *partially refuted* for table-deliverable tasks via this output-surfacing failure mode (not a judgment failure).
- **H3 (one crawl per bounded question): confirmed.** Two independent bounded crawls ran in parallel cleanly; no benefit would have come from merging them.
- **Net rule**: delegate exhaustive *mechanical enumeration over many files* (paths, refs, greps) to composer; do *small-file content reads* and all *judgment* (R1–R3, placement, structure) in the Opus parent. H2 not yet tested (no judgment task delegated).

_Original seed hypotheses (retained for provenance):_
- H1: composer-2.5 explore does accurate/complete/well-formatted extraction given exact schema + "extract only". → cycle-1: confirmed for path-ref crawl; partial for table-deliverable crawl (output-surfacing failure).
- H2: judgment tasks (structure design, R1–R3, risk scan) need Opus 4.8. → untested.
- H3: one crawl per well-bounded question, not a mega-crawl. → confirmed cycle-1.

## Dispatch entries

<!-- Schema (one block per dispatch):
### exp-<n> — <date> — <task-type: crawl|reason>
- Model / agent-type:
- Deliverable expectation (stated BEFORE dispatch):
- Dispatch summary:
- Outcome:
- Audit verdict (worked | partial | failed) + why:
- Tweak for next:
-->

### exp-1 — 2026-06-14 — crawl
- Model / agent-type: `composer-2.5-fast`, `explore`, readonly.
- Deliverable expectation (stated BEFORE dispatch): a structured inventory (markdown tables, no prose narrative) of what content currently lives in the CircuitPython memory files `.cursor/rules/memory/{TECHNICAL.md,CONCLUSIONS.md,CODING_PRINCIPLES.md,SESSION_LOG.md}`. Two tables: (T-A) candidate-domain → concrete concepts in evidence NOW, columns `[domain | concept (1 phrase) | source file#section | which project/experiment it pertains to]`, using the guidelines §3.1 candidate domain list (power, i2c, deep-sleep, led-driving, circuitpython-runtime, display, fonts, fuel-gauge, tooling) plus an `ungrouped/other` bucket for anything that fits none; (T-B) per-project content split → rows `[project/experiment slug | files/sections holding its content | approx entry count]` covering exp14, exp15, any exp09/11/13 residue, cross-experiment, Bamboo-Lamp mentions. Constraint: EXTRACT ONLY — make NO placement/structure decisions, propose no reorganization, just report what exists and where. If a file is empty or schema-only (no populated entries) say so explicitly.
- Dispatch summary: dispatched composer-2.5 explore readonly over the 4 memory files for T-A (domain→concept) + T-B (project split).
- Outcome: high-level summary returned correctly (exp14-dominant ~20 session blocks/2 TECHNICAL sections/15 coding principles; exp15 1 entry; exp09/11/13 residue-only; Bamboo-Lamp = routing notes only; power/i2c/deep-sleep/fuel-gauge empty) — but the actual T-A/T-B tables did NOT appear in the response body.
- Audit verdict: **partial** — load-bearing fact (which domains are populated) delivered + accurate; the table detail (per-concept rows with file#section) was not surfaced. Compensated by reading TECHNICAL.md + CONCLUSIONS.md directly in the parent (both nearly empty schema → cheap), which fully grounded R1.
- Tweak for next: for table-as-deliverable crawls, instruct "paste the completed tables inline in your final response"; or skip delegation when target files are short and read directly.

### exp-2 — 2026-06-14 — crawl
- Model / agent-type: `composer-2.5-fast`, `explore`, readonly.
- Deliverable expectation (stated BEFORE dispatch): an exhaustive inventory of every memory-path / cross-file reference that the warm reset would have to keep valid (feeds plan C3/S3 dead-path check + risk register). Scope: `.cursor/rules/*.mdc`, `.cursor/rules/memory/*.md`, `.cursor/rules/COLLABORATOR_GUIDE.md` (if present), `.cursor/rules/reference/*.md`. Output one table: columns `[referencing file:line | the referenced path or filename | reference kind: memory-file | rule-file(.mdc) | reference-doc | absolute-path | mandate]`. Include references to `memory/WORKING_STYLE.md`, `SESSION_LOG.md`, `TECHNICAL.md`, `CONCLUSIONS.md`, `CODING_PRINCIPLES.md`, `MONITORING.md`, `CHANGELOG.md`, the `reference/` folder, and any absolute `/Users/alex/...` paths. Constraint: EXTRACT ONLY — do not judge which are at risk, do not propose fixes; just list every reference and its location.
- Dispatch summary: dispatched composer-2.5 explore readonly; ripgrep over .mdc / memory / COLLABORATOR_GUIDE / reference / mandates.
- Outcome: 628 reference rows across 17 files; full `.mdc` + mandate + COLLABORATOR_GUIDE detail returned inline; long tail (SESSION_LOG 205, CHANGELOG 93, reference docs) spilled to scratch file with a by-file rollup. Key decision-critical facts: all FOUR `.mdc` carry memory refs (00:37, 01:10, 02:25, 03:16) — including **01-interaction-style.mdc** (CONCLUSIONS@36, WORKING_STYLE@66/84/93), which plan v0.0 Phase 6 omits; ~15+ `reference/<file>` path refs across 00/01/03/mandate/COLLABORATOR_GUIDE that a reference/ move would orphan.
- Audit verdict: **worked** — exhaustive, accurate, correctly formatted; surfaced two concrete plan gaps (missing 01-mdc in Phase 6; reference/-move dead-path surface).
- Tweak for next: request "rollup + decision-critical subset inline" up front to avoid the truncation round-trip; the long prose-mention tail is low value for dead-path analysis.
