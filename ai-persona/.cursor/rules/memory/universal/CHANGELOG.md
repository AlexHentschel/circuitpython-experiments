# Memory Architecture Changelog

Provenance log for **structural changes** to the memory system — new files, schema evolutions, consolidations, splits, tier-model changes, cross-file migrations. Per-session insight accretion lives in `SESSION_LOG.md`; per-entry lifecycle detail (Reinforcements increments, status promotions, abstraction liftings) lives in the Notes column of the entry itself. This file captures only events that affect the *shape* of the memory architecture.

Evolution-vocabulary reminder (from `00-memory-system.mdc § Evolution vocabulary`): `extend` · `refine` · `abstract` · `simplify` · `generalize` · `split` · `compact`.

## 2026-09-15 — relocated directive-header provenance (compact: WORKING_STYLE.md + CODING_PRINCIPLES.md)

**Trigger:** Alex — full memory-maintenance lifecycle, proposal P-prov: the always-read behavioral catalogs had accreted a long inline `Previous:` provenance stack in their headers, adding session-start read cost with no retrieval value (per-entry lifecycle detail already lives in each directive's own Notes column, and structural events here).

**Change** (`compact`; no information loss — entries moved verbatim, not deleted):

- `WORKING_STYLE.md`: removed the inline `Previous:` stack from the header, kept the title + current `Last updated:` line + the **HARD GATE — Destructive operations** block (in place, high-salience) + the schema content (Abstraction convention / Scope tags / Status notation). Added a one-line pointer to this section.
- `CODING_PRINCIPLES.md`: same treatment (no HARD GATE block in that file). The current `Last updated:` line — which bundles the most-recent inline `Prior:` chain — is retained as-is.
- **Preserve:** the relocated entries are reproduced verbatim below; each directive's own Notes column remains the authoritative per-entry lifecycle record; this move changes only *where the chronological header digest lives*, not any directive content. Reversible (git-tracked).

### Relocated verbatim — `WORKING_STYLE.md` header provenance (newest first)

Previous: 2026-09-13 (**refine** § Document Authoring *Line length* — CircuitPython-profile Black wrap set to 160; code+docstring wrap now matches the 120-160 band instead of Black's default 88. Reinforcements 3→4.)
Previous: 2026-09-11 (same day, cont'd: **reinforced** § Document Authoring *Describe current state, not the delta to an older version* (reinforcements 1→2) — self-caught after Alex asked whether this had been discussed, pointing at a `code_stage0.py` comment narrating what it "used to state" instead of the current fact; swept and fixed 3 more instances same-turn across `code.py`/`CONCLUSIONS.md`/`CONTEXT.md`. Prior: **refine** § Workflow & Artifacts *code_stageN.py parking* — Alex correction: not a standing default; ask once per project when it first becomes relevant, then memorize; policy may change, rarely. Prior: new § Document Authoring row *Log lifecycle operations as "happened and is done," not a temporal step-by-step* — consolidated an over-narrated exp16 `SESSION_LOG.md` entry and a central-log wrap-up entry to match. Prior: new § Domain-Specific row *Batch on-device deploy operations* — every board file-write resets it, per Alex's exp16 Session 19 note; be pragmatic, not rigid, about batching. Prior: `/experiment-wrapup-to-memory` first content run on this persona's own human-AI interaction patterns — new Core Principles row *A null result is a valid, expected outcome of a review/distillation/wrap-up task*; folded a Self-confirmation-loop clause into the cold-AI write-time gate row (*verify institutionalization via the file, not recall*). Third candidate (Alex's reusable meta-instruction) demoted to `MONITORING.md`, not written here. Prior: new § Domain-Specific row *Local-first, then mirror to the board*. Prior: wrap-up destillation row. Prior: `esptool` venv named + Domain-Specific *probe freely, never mutate*. Prior: raw device-file I/O `required_permissions:["all"]`. Prior: 2026-09-08 ai-notes authority-is-per-claim-confidence.)
Previous: 2026-06-14 (warm-reset EXECUTION + post-execution memory-lifecycle maintenance iteration: (a) two distilled directives — *Prefer the file-edit tools over shell for file mutations; hand off an unavoidable shell file-op rather than let it hang* (`[user]` § Workflow & Artifacts, evidence = 3 in-session approval-gate stalls on `sed`/`ln`/`printf`-redirect under `.cursor/`) and a new § Retention bullet *Verify no-loss by claims-coverage, not line-diff, when restructuring*; (b) consistency sweep — re-pointed dead `TECHNICAL.md` forward-routing pointers → `concepts/<domain>.md` in `MONITORING.md` + `CODING_PRINCIPLES.md` (the warm-reset grep had only covered `.mdc` rule files, not memory data). Full provenance in `CHANGELOG.md § 2026-06-14 — post-warm-reset maintenance iteration`.)
Previous: 2026-06-14 (CircuitPython session 10, warm-reset planning cont'd: two new `[universal]` § Core Principles directives — *Categories form by accumulate-then-split, expect overlap, cross-link it* and *Batch heavy memory restructuring into deliberate, user-gated lifecycle iterations; keep a backlog and recommend when beneficial* — both stated by Alex as common memory-lifecycle patterns. Also extended `00-memory-system.mdc § Maintenance` (items 4–6) to encode them. Prior same-day: new directive *Don't guess an association into a deep, specific bucket* — Alex on D3: the load-bearing part of scope-tagging is not the default rule but never burying a memory association in a wrong deep bucket (asymmetric cost: mis-buried = invisible + rots; under-tagged = findable + cheap to fix). Generalizes to every placement-gate decision; status `(experimental)`.)
Previous: 2026-06-14 (CircuitPython session 10, warm-reset planning: new `[universal]` § Core Principles directive *Inherited specs are adaptable priors, not rigid sources of truth* — Alex corrected the warm-reset plan's framing of the multi-project mandate from "source of truth, mandate wins on conflict" to "prior-execution template to assess/adapt against current persona state during execution". Sibling to *Contradictions have no default winner* + *Scope-transfer check*; status `(experimental)`.)
Previous: 2026-06-14 (Bamboo-Lamp session 1: (a) integrated the cold-AI paradigm — new `[universal]` § Core Principles directive *Apply the cold-AI write-time gate before persisting any content*; (b) integrated *Flexible Plans for AI Execution* — new `[universal]` § Core Principles directive *Flexible-plan layered commitment for agent-executed plans*, the plan-lifecycle umbrella over the pre-existing *Pre-commit to targets, not shape* + *Reflect explicitly at every meaningful checkpoint* siblings. Both reference docs copied into the durable persona home `.cursor/rules/reference/` (cold-ai-paradigm.md, flexible-plans-for-ai-execution.md) because the `~/Developed/AI/generalized-agent-learnings/` source folder is ephemeral; directive pointers updated to the local copies. Calibrated § Human Profile for Alex (strong SW/maker, home-workshop tooling not lab-grade, designs own agent-memory architecture). These are `[user]`/`[universal]` and shared across the parallel Bamboo-Lamp + CircuitPython work — this file is the single behavioral catalog for both. No structural restructure; `warm reset` not triggered. See `CHANGELOG.md § 2026-06-14`.)
Previous: 2026-06-12 (session 8 continuation: § Document Authoring line-length directive widened from "130-150 acceptable" to "target the 120-160 band, deviation OK to better fit content; don't crowd adjacent code". Reinforcements 2 → 3. User restatement of the same wide-monitor preference, now with an explicit lower target and a content-fit carve-out.)
Previous: 2026-04-26 (session 7 continuation: re-placed *Public object descriptions should describe public contract, not private coupling* from § Document Authoring here → `CODING_PRINCIPLES.md § Core Principles`. Split-criteria rationale: the directive governs what content belongs in a code artifact (docstring), not a prose-authoring posture. Same re-placement failure mode as session 6 — proximity to other docstring directives overrode the split criteria.)
Previous: 2026-04-25 (session 7 continuation: new `[user]`-scope directive in § Document Authoring — *Match explanation depth to reader context: don't explain what's apparent, do explain what isn't.* Triggered by a user flag on `core.py:15-22` ("cancellation counter" used without introduction); generalizes to all prose-heavy code documentation. Includes explicit audit-loop enforcement clause — review subagents are to apply this directive on doc-quality passes. Sister to the current-state directive (both reader-context calibration). Status `(experimental)` — one incident.)
Previous: 2026-04-23 (session 7: new `[user]`-scope directive in § Document Authoring — *Describe current state, not the delta to an older version.* Triggered by a user flag on `README.md:32-33` "imports ... are unchanged"; generalizes to any user-facing prose where history-relative framing leaks in. Explicit carve-out for commit messages / audit ledgers / session logs. Status `(experimental)` — one incident.)
Previous: 2026-04-21 (session 6: line-length directive in § Document Authoring relaxed from "up to 130" to "130-150 acceptable" per user; same wide-monitor / scroll-cost justification as the original entry. Reinforcements 1 → 2.)
Previous: 2026-04-21 (session 6: two directives added this session got re-placed after a user-flagged review — *Self-contained docstrings* migrated out to `CODING_PRINCIPLES.md § Core Principles` (code-shape rule), *Concise memory-edit announcements* moved within this file from § Document Authoring → § Communication Style (collaboration-posture rule). Root-cause captured in § Retention and Evaluation as a new bullet on placement-at-first-time. Full provenance in `CHANGELOG.md § 2026-04-21 — refine`.)
Previous: 2026-04-21 (session 5: file scope narrowed — coding-craft directives split off into sibling `CODING_PRINCIPLES.md`. This file now catalogs collaboration / process / judgment / artifact-convention directives only. Schema, scope-tag legend, status notation, and § Retention and Evaluation remain the single source of truth here — `CODING_PRINCIPLES.md` inherits them. One new directive added to § Code Editing: *Re-read the current file state before editing when collaborative-edit drift is plausible*. One Note-line cross-reference added to the § Domain-Specific MCU-economy directive pointing to its universal-form sibling in `CODING_PRINCIPLES.md`. **Second-pass migration later in the same session** (user-prompted): two pre-existing § Code Editing entries — *Immutable defaults go directly in the signature* and *Decompose procedural logic into small, self-contained helpers* — were reclassified as code-shape directives (not editing-posture directives) and migrated verbatim to `CODING_PRINCIPLES.md § Core Principles`, preserving Reinforcements / Last Applied / Notes. § Code Editing here now holds only editing-posture directives (*Rewrite-vs-edit trade-off*, *Re-read file state before editing*). Full structural-change provenance in `CHANGELOG.md § 2026-04-21 — extend: introduced CODING_PRINCIPLES.md` and the follow-on migration entry.)
Previous header content preserved for continuity: 2026-04-20 (session 4: P1.8 — added immutable-defaults, decompose-into-small-helpers, and `working-docs/` folder directives; four of seven requested items were already captured at higher abstraction in Core Principles and were not duplicated, per abstraction-lifecycle rules. Post-P1.9: bumped Reinforcements on *Reflect explicitly at every meaningful checkpoint* from 2 → 3 with the generative-reflection evidence from the Phase-1 audit ledger. End-of-session-4: new § Judgment & Escalation section added between Core Principles and Communication Style — holds decision-posture directives that are sibling to the already-lifted *Contradictions have no default winner* and *Scope-transfer check* but have not yet accumulated enough incidents to lift themselves. First entry is *Resolve low-stakes directive tensions with transparent judgment*; broadened beyond the originating memory/rule-system case after the user granted authority to resolve *any* low-stakes tension on this project. The project-specific calibration is cross-noted to `mandates/multi-project.md § Per-project operational calibrations`.)

### Relocated verbatim — `CODING_PRINCIPLES.md` header provenance (newest first)

Previous: 2026-09-12 (exp16 Session 24 — applied the four axes to `lib/display/core.py` via a Grok 4.6-high plan-refinement loop (converged iteration 2 of cap 6). Reinforced *Docstring quality triage is multi-axis* 1→2 (first *prospective* application: caught 2 false 8×8-era facts + 6 public-docstring private-name/mechanism leaks + an added `recolor` hazard + a class-docstring reorder; 11 doc-only edits, `pytest` 149 green). No new rows. Provenance: gitignored plan-refinement working folder, deleted 2026-09-12 after apply.)
Previous: 2026-09-11 (session 21 continuation, API-doc-feedback wrap-up migrate: 3 new § Core Principles rows + 1 reinforcement, all from the exp16 API-doc-feedback thread. (1) NEW *Docstring quality triage is multi-axis* — the higher-level synthesis over coupling/audience/ordering/honesty; generalizes the former "second calibration axis" addendum on the *Public object descriptions...* entry (that addendum replaced by a pointer). (2) NEW *Order docstrings typical-case-first*. (3) NEW *Document magic constants honestly*. (4) *Avoid frequent use of `--`* reinforcement 2→3 — Alex's forward preference for `;`/`:`/restructuring over em-dash substitution. Staging + provenance: gitignored working folder, deleted 2026-09-12 after migration.)
Previous: 2026-09-11 (session 21 continuation: new `[user]`-scope § Core Principles row *Prefer f-strings over `str.format()`/`%` in CircuitPython/MicroPython; no runtime cost trade-off* — grounded in MicroPython's lexer-level f-string-to-`.format()` rewrite (source-linked), so the two are bytecode-identical on this runtime, unlike CPython. Applied to `create_image`/`create_big_image`'s `ValueError` messages in exp16 `lib/display/core.py`.)
Previous: 2026-09-11 (session 21 continuation: (1) *Public object descriptions should describe public contract, not private coupling* — Incident 3 (reinforcement 2→3): two further `show_string` docstring paragraphs triaged; surfaced a second, distinct calibration axis — audience-appropriate language (jargon-level), orthogonal to public/private coupling — with 1 instance (a Big-O clause) added to the entry as not-yet-promoted. (2) *Avoid frequent use of `--`…* (reinforcement 1→2): Alex requested the previously-optional retroactive sweep; applied to the 3 originally-flagged files (`core.py`/`README.md`/`code.py`), excluding decorative dashes, table syntax, Mermaid arrows, an anchor link, and `Notes/Button_chat.md` (a transcript, not authored doc).)
Previous: 2026-09-11 (new `[user]`-scope § Core Principles row *Avoid frequent use of `--` in human-facing documentation; acceptable in AI-facing documents* — raised while reviewing a `show_string` docstring rewrite; applied same turn to that docstring plus new `ValueError`-guard docstrings on `show_leds`/`show_icon`/`show_arrow`/`pause`. Explicitly does not mandate a retroactive sweep of existing `--`-heavy files.)
Previous: 2026-09-11 (new `[user]`-scope § Core Principles row *Disambiguate a parameter name reused across sibling methods for a different concept* — cross-project promotion (M3, no sign-off needed): exp14's own open TODO (`scroll_image`'s `offset` vs. `show_image`'s `offset`) plus exp16 independently rediscovering and fixing the same ambiguity same-day. Renamed exp16's `Image.scroll_image` parameter `offset` → `step`; full divergence context in exp16 `Notes/exp14-divergence.md`.)
Previous: 2026-09-11 (new `[project]`-scope § Core Principles row *Custom pattern strings render one grid row per source line, columns space-aligned* — Alex asked to reformat exp16 `code.py`'s inline `_DIAMOND`/`_RING_PATTERN` constants from single-line `\n`-joined strings to multiline triple-quoted form; matches `bitmap_codec.py`'s own docstring convention, mechanically verified byte-identical decode.)
Previous: 2026-09-11 (new `[user]`-scope § Core Principles row *Structure milestone/stage test scripts additively, not repetitively* — Alex trimmed exp16 `code.py`'s Stage 1 draft to drop steps duplicating the already-frozen/confirmed `code_stage0.py`, to save his own on-device validation time; flagged the future unified-end-to-end-test question as a separate call, not yet decided.)
Previous: 2026-09-04 (Exp16: no host paths in library/test code; talk *experiment* not parent git repo.)
Previous: 2026-06-15 (added `[user]`-scope directive *Comments and docs target 120–140 char lines on wide monitors* in § Core Principles — stated general guideline; gradual phase-in on code touched anyway. Same session widened the just-reflowed `Image._render_window` docstring in `lib/display/core.py` from ~100 → ~120–140 cols as first application.)
Previous: 2026-06-11 (session 8 continuation: extended the type-hinting directive in § Core Principles with **Pattern C — `from __future__ import annotations`** for files that need typing imports or compound PEP 585 subscripts; first applied to `lib/display/core.py` in the same session. Directive reinforcement 1 → 2. Also added new `(experimental)` `[user]`-scope directive in § Core Principles: *PEP 585 subscript syntax (`Type[X]`) is for annotation contexts only; never at runtime call sites* — second-incident promotion (after `enumerate[str]` in session 8 and `list[str]` in this session's `core.py` pass, both fixed on discovery), `(experimental)` because both incidents are in adjacent code within the same project; awaiting a clean application in a different setting before promotion to `established`.)
Previous: 2026-05-25 (session 8: two new directives in § Core Principles. (1) `[user]`-scope *Type-annotate public function signatures; prefer builtin types, guard `typing` imports* — stated preference for type hints across user's CircuitPython work, Adafruit-standard `try/from typing import …/except ImportError` pattern for non-builtins, URL references pinned in the directive body so they propagate into every Pattern B guard comment. (2) `[universal]`-scope *Validate symmetrically across paired transformations* — derived from the `bitmap_codec.py` encoder/decoder height-check asymmetry; user-promoted directly after the symmetry-fix turn without waiting for a second incident, on the strength of the pattern's broad applicability beyond this codec (any encode/decode, serialize/deserialize, read/write, marshal/unmarshal, hash/verify pair). Both `established` from the start per § Retention "single-incident entries are legitimate when describing a stated preference".)
Previous: 2026-04-26 (session 7 continuation: refined *Public object descriptions should describe public contract, not private coupling* — added fact-vs-mechanism calibration to the Act section after over-pruning the `from_pattern` docstring. Reinforcements 1 → 2. Same entry also re-placed from `WORKING_STYLE.md § Document Authoring` → here earlier this session.)
Previous: 2026-04-21 (session 6 continuation: added *When localizing a bug in a pipeline, instrument stages before speculating* to § Core Principles. Derived from the font-distortion investigation — several turns of analytical narrowing about which pipeline stage was at fault were dominated in cost by two probes that settled the question with data. Generalization also surfaces a hypothesis-space-bounding corollary: input data authored by third-party tooling is as much a candidate suspect as our own transforms. Full provenance in `working-docs/font-distortion-findings.md` and `CHANGELOG.md § 2026-04-21 — extend`.)
Previous: 2026-04-21 (session 6: refined *Cross-runtime citations require a grounding note* — renamed from "carry-over" to "grounding", expected verification level lifted from AI-confirmed-via-mechanism-argument to source-verified-when-broadly-applicable-and-promoted-to-`TECHNICAL.md`. Triggered by a user-raised process gap: *"I'll verify on the next incident"* is not an actionable deferral in a stateless-retrieval memory system, so broad-applicability claims must be verified at first-incident time or explicitly accepted as unverified folklore with that tag visible. Concrete follow-through: LOAD_FAST vs LOAD_GLOBAL claim verified against `py/vm.c` + `py/runtime.c`; grounded finding now lives at `TECHNICAL.md § Name loading: LOAD_FAST vs LOAD_GLOBAL` with `[CPy-src]` tags.)
Previous: 2026-04-21 (session 6: appended *Function and method docstrings should be self-contained* to § Core Principles after re-placement from `WORKING_STYLE.md § Document Authoring`. Boundary case: docstrings are part of the code artifact, so docstring conventions belong here despite their surface similarity to prose-authoring conventions in `WORKING_STYLE.md`. Full provenance in `CHANGELOG.md § 2026-04-21 — refine`.)
Previous: 2026-04-21 (session 5: file seeded with six directives extracted from the `display.geometry.build_lut` refactor retrospective. Sibling to `WORKING_STYLE.md` — same metadata schema, same abstraction lifecycle, same scope tags, same status notation. Split introduced because coding-craft directives were diluting the behavioral-collaboration catalog, and the expected accumulation rate warrants a dedicated home.)

## 2026-09-15 — extend: new `[meta]` project `ai-tooling` + anticipatory-seed `concepts/ai-tooling.md` (deliberate C7 exception)

**Trigger:** Alex — (1) add a persona category for AI tooling incl. self-improvement of *this* persona, with a reference to the full memory-maintenance lifecycle launcher prompt; (2) explicitly "already create" `concepts/ai-tooling.md` even without a concrete concept — "kind of exception to our standing rule of not anticipating knowledge" (C7). Context: kicking off a full memory-maintenance lifecycle reusing the external `high-assurance-engineering` persona's method/harness (as a resource, not as this persona's identity).

**Change** (`extend`; first `[meta]` family + first anticipatory domain seed):

- New `projects/ai-tooling/{CONTEXT,SESSION_LOG}.md` (family `meta`; provisional) — workstream home for persona self-improvement + AI tooling. `CONTEXT.md § Entry points` references the launcher prompt `ai-persona/ai-notes/2026-09_CPy-full_memory_lifecycle/2026-09_CPy-full_memory_lifecycle_prompt.md` (gitignored) + the read-only HA method/harness source. Roster row + path-globs (`ai-persona/**`) added to `projects/_INDEX.md`. (commit `f4608f8`)
- New `concepts/ai-tooling.md` `[domain:ai-tooling]` `[meta]` — **seeded ahead of evidence at Alex's direction (exception to C7)**. No `### concept` yet (none evidence-supported); candidate concepts recorded as `[anticipated]` pointers only (cold-AI probe harness; harness permissions gotcha; stale expected-reach keys; additive-first structural wins). `_INDEX.md` domain section + "Seeded since" line note the exception. Domain count 8 → 9.

**Preserve:** C7 (seed-on-evidence) remains the standing rule — this is a *named exception*, not a repeal; `[anticipated]` items are explicitly not citable as findings. Process discipline stays in `reference/*` + `00-memory-system.mdc` (not duplicated into the concept). Gitignored-reference concern (launcher prompt lives in `ai-notes/`) flagged, decision deferred to end of cycle. No foundational-file (`00`/`06`/`04`) change.

## 2026-09-14 — extend: seed `concepts/nezha.md` (first concept, C7)

**Trigger:** Alex — persist the Nezha V2 motor-library analysis with cold-AI discoverability in persona memory (not only gitignored `ai-notes/`). Opcode table is a public, non-confidential fact; wrap-up rule forbids leaving it solely in notes that may vanish.

**Change** (`extend`; C7 new domain — ElecFreaks breakout command set, **not** folded into `i2c.md` because that domain is bus-general NXP/TI properties; device packets would bury retrieval):

- New `concepts/nezha.md` with `### Nezha V2 smart-motor I2C protocol (8-byte frame @ 0x10)`: decode `evidence-supported` from `pxt-nezha2` `main.ts` + `Nezha_V2.py`; on-device `unverified`. `_INDEX.md` domain line; Candidate-domains updated (`nezha` now seeded; `led-driving` candidate leftover in `02-domain-structure.mdc` also corrected). `_RELATIONS.md`: `nezha` —instantiates— `i2c: 7-bit addressing`. Domain count 7 → 8.
- Retrieval hops: exp16 `CONTEXT.md` Domain knowledge + entry points; `CONCLUSIONS.md` Unverified; `crossref/BY_TOPIC.md` Nezha row now points at the concept first. Unpack remains exp16 `ai-notes/digests/nezha-v2-motor-protocol.md`.

**Preserve:** `i2c.md` stays bus-general. PlanetX GPIO buttons stay in exp16 `lib/planetx/` (`sensors` still unseeded). No motor driver.

## 2026-09-12 — extend: seed `concepts/led-driving.md` (first concept, C7)

**Trigger:** Alex — "promote that" (the PIO-vs-RMT-per-MCU-family fact surfaced while correcting stale "PIO" wording in exp16's ESP32-S2 docs). Reserved candidate domain `led-driving` received its first concrete, evidenced concept.

**Change** (`extend`; C7 new domain — `led-driving` was a reserved candidate since the warm reset; NOT folded into `circuitpython-runtime` because it is a hardware-peripheral fact, not a VM/runtime one, and `circuitpython-runtime` is RP2040-anchored):

- New `concepts/led-driving.md` with `### WS2812/NeoPixel output peripheral is MCU-family-specific (RP2 → PIO; ESP32 → RMT)`, `evidence-supported` (concordant official CP sources: PR adafruit/circuitpython#3232, commit 9537b1d, both ports' `common-hal/neopixel_write`). `_INDEX.md` domain line added + Candidate-domains section updated (led-driving now seeded). `_RELATIONS.md`: realized the anticipated `circuitpython-runtime: neopixel allocation —composes-with— led-driving` edge (buffer vs output-peripheral); a distinct `WS2812 timing` edge remains anticipated. Domain count 6 → 7.
- Cross-ref: in-repo provenance is exp16 `Notes/exp14-divergence.md` §3 (the do-not-back-port PIO→RMT correction) + `SESSION_LOG.md` Session 24.

**Preserve:** `circuitpython-runtime`'s existing `neopixel.NeoPixel allocation` concept (allocation/heap axis) stays put — the new concept is the orthogonal output-peripheral axis, linked not merged.

## 2026-09-11 — extend: 4MB-partition sidecar + wrap-up destillation (notes may vanish)

**Trigger:** Alex — compile the enumerated TinyUF2 4MB CSV tables (the only home was gitignored `ai-notes/esp32-4mb-circuitpy-vs-ota/`) into a ≤1 KB durable artifact; wrap-up must assume `ai-notes/` may later be gone; notes remainder = confidential/sensitive only unless specified. This research and Exp16 are not confidential (Exp16 dump-all deferred to that wrap-up).

**Change** (`extend`; same domain `tooling`, not a C7 new domain; D8 stream-on-demand detail file, not a per-concept folder split):

- New `concepts/tooling-4mb-partitions.md` (789 B; Adafruit 4MB CSV rows + 1408+1408 arithmetic + 0.32≡0.35 identity). `_INDEX` line + `_RELATIONS` —refines— edge. Pointers retargeted: `tooling.md` how-to-check-status, `MONITORING.md`, exp16 CONCLUSIONS + SESSION_LOG.
- New `[user]` Workflow row *Wrap-up assumes `ai-notes/` may vanish* (sibling of *Persist task working notes*). Playbook Objective 3 / G7 / extract schema / SKILL hard-stop / durable-target row updated: source-only-until-cleanup **superseded** for non-confidential.

**Preserve:** parent `tooling.md` mechanism claims; G10 credentials sanitization; Exp16 not dump-all this turn. Notes folder later moved to Trash by Alex (`G-2026-09-11-3`); workspace-absent 2026-09-11.

## 2026-09-11 — extend: seed `concepts/tooling.md` (first concept)

**Trigger:** exp16 walkthrough — upgrade BPI-Bit-S2 CP 10.0.3 → 10.3.0 via esptool + TinyUF2. `tooling` was a C7 candidate; first concrete evidenced concept arrived.

**Change** (`extend`; seed-on-evidence, not a reorg): new `concepts/tooling.md` (Espressif 4MB TinyUF2 + ROM/esptool v5). Index line + candidate-list note in `concepts/_INDEX.md`; one `_RELATIONS.md` edge to `circuitpython-runtime: mpy-cross`; `02-domain-structure.mdc` seeded-domain list. Board-specific boot sequence also in exp16 CONCLUSIONS.

## 2026-09-08 — refine: retrieval/placement layout **confirmed** (drop June-14 experiment banners)

**Trigger:** Alex “please proceed with pass” on `ai-notes/provisional-marker-pass/plan_v1.0.md`. Watch-for (~5 additions, no refute) exceeded since 2026-06-15 / 2026-07-15; ingest 2026-09-07 (R3) explicitly did not bundle this.

**Change** (`refine`; status of existing structure, not a reorg / not a second warm-reset):

- **Confirmed** retrieval/placement (one-hop index→domain/project→detail; deterministic placement; no recorded wrong-bucket or no-home finding) on `concepts/_INDEX.md`, `projects/_INDEX.md`, `04-multi-project.mdc`. Echo updated in `00-memory-system.mdc` layout paragraph.
- **Did not re-open** dedicated-root / no symlink-fanout (settled 2026-07-15).
- **Did not rewrite** `00-memory-system.mdc § Content vs structure` — future structure still gets a `provisional` marker + watch-for.
- **Hygiene (headers that had become false):** `crossref/BY_PATTERN.md` no longer claims empty of confirmed patterns (first `PATTERNS.md` entry 2026-09-04); `crossref/BY_TOPIC.md` no longer “only 3 projects” (roster has 5); `concepts/_RELATIONS.md` no longer “only 2 domains” (5 domain files); `02-domain-structure.mdc` seeded-domain list updated (`power`/`i2c`/`git` were still listed as unseeded; `fuel-gauge` folded into `power`; `sensors` remains a candidate).
- Living summary updated. `MAINTENANCE_BACKLOG.md` item struck.

**Evidence counted:** `power` 6 + `i2c` 6 + `git` 3 = 15 concepts in *new* post-reset domains; five roster projects; taxonomy forks (`fuel-gauge`→`power`, `sensors` deferred) used the placement gate. No refute recorded.

**Preserve (not this pass):** per-concept file split; symlink restore; Exp16 `ai-notes/` untrack; wrap-up-to-memory skill; DN-MP-1 heuristic refine; hypothesis-test first entry; `verified` tier; TECHNICAL.md flatten.

## 2026-09-08 — refine: `ai-notes/` authority is per-claim confidence

**Trigger:** Alex correction — “scratch, not SOT” was too coarse. A claim in `ai-notes/` can be SOT depending on the confidence of the analysis/source; the content must classify its own reliability. Typical folders are exploratory; that is not required. Notes unpack (dead-ends, lighter structure); persona memory is where structure/semantic links/higher-level extraction pay off (wrap-up compresses later). Written for a cold AI of the same persona; vanilla dumps get incorporated when asked.

**Change** (`refine`; same cue, no new row, no new `.mdc`):

- Corpus `ai-notes-convention.md` §2 rewritten (two orthogonal axes: git vs authority). `working-notes-lean-context.md`, `00-OVERVIEW.md`, corpus `README.md` aligned.
- Persona shelf copies refreshed 2026-09-08. WS *Persist task working notes* Goal/Act updated (reinforcements 2 → 3). Living summary + SoT map + COLLABORATOR_GUIDE + `BY_TOPIC` wording.
- Wrap-up playbook **not** instantiated here; pointer on the WS row to the HA skill/concept Alex named.

**Preserve:** git/lifecycle rules (gitignore default, one-way team-deliverable refs, do not untrack without grant). Exp16 tracked notes still not untracked.

## 2026-09-08 — extend: `ai-notes/` git/lifecycle (companion to working-notes)

**Trigger:** Alex gitignored `ai-persona/ai-notes/` and pointed at corpus `ai-notes-convention.md` (recipe). Fold into the existing working-notes cue; avoid a second always-on rule.

**Change** (`extend`; no layout restructure; no compaction):

- **Shelf:** `reference/ai-notes-convention.md` (snapshot 2026-09-08). Fireable cue remains `WORKING_STYLE.md § Workflow` *Persist task working notes* — contents half already pointed at `working-notes-lean-context.md`; git/lifecycle half now in the same row.
- **House default:** gitignored at the work unit (persona root or experiment folder). One-way dependency: notes may cite the repo; committed deliverables must stand alone. Durable claims lift to `memory/` or versioned spec/code. Never untrack a checked-in `ai-notes/` without a grant.
- **Instance:** `ai-persona/.gitignore` → `ai-notes/` (never tracked). Exp16 tracked notes left in place — `MONITORING.md`.
- **Wiring:** COLLABORATOR_GUIDE on-demand row; `00.mdc` See also; `concepts/git.md` cross-ref; SoT map row. No 5th `03-triggers` item.

**Preserve:** Exp16 `ai-notes/` not untracked; Exp14 `working-docs/` not merged into `ai-notes/`.

## 2026-09-07 — extend: corpus → persona ingest (shelf + fireable cues + reachability hygiene)

**Trigger:** Alex “Please execute. Sign-off granted.” (ingest plan was local scratch under `ai-persona/ai-notes/`; that folder is gitignored as of 2026-09-08 — this CHANGELOG entry is the durable record). Corpus: `/Users/alex/Git/rnd-ai-skills/generalized-agent-learnings/` (recipe, not house SOT).

**Change** (`extend`; no compaction; no memory-layout restructure):

- **`reference/` shelf** — corpus snapshot dated 2026-09-07, durable-copy headers on every file. New: 09, 10, 11, working-notes, plan-refinement-loop, EBG, host-portability, host-adaptation-claude-code (not instantiated), PR/commit authoring. Refreshed: 00–08, cold-ai, flexible-plans, destructive-operations. **Not copied:** `writes-thinks-speaks.md`, corpus `README.md`, `EXTRACTION-PLAN.md`, `exemplary-artifacts/`.
- **Fireable cues** in `WORKING_STYLE.md`: working-notes `[user]` Workflow; plan-refinement loop `[user]` Workflow; hypothesis-test section seeded empty (plan default R1); self-confirmation loop folded into cold-AI Notes; PR altitude on existing commit-message row (Alex format unchanged); EBG pointer in Retention. `MONITORING.md`: 09 Attempt 4 quality-risk (not a standing “always delegate memory” rule).
- **Hygiene:** `00-memory-system.mdc` + `04-multi-project.mdc` no longer state live symlink-fanout as current reachability (dedicated `ai-persona` root, 2026-07-15). Content/structure named in `00.mdc`. `COLLABORATOR_GUIDE.md` deployment section rewritten; on-demand `reference/` table added. `06-destructive-operations.mdc` host-portability pointer now local.
- **`03-memory-update-triggers.mdc`:** still four items (no 5th).

**Preserve-list intact:** no `verified` tier restored; no TECHNICAL.md flatten; no per-concept split; 11 not re-executed; no symlink-fanout restore; PROVISIONAL markers left (R3 — MAINTENANCE_BACKLOG item remains user-gated).

**Open defaults taken:** R1 seed hypothesis-test section; R2 copy Claude Code adaptation file labelled not-instantiated; R3 do not bundle PROVISIONAL promotion.

**Inventory / claims-coverage:** verified at execution (P4); local notes were gitignored 2026-09-08. Durable ingest record is this CHANGELOG section + WS/reference/ diffs.


## 2026-09-04 — refine: *Cross-runtime citations* lifted `[project]` → `[user]` (MONITORING trigger)

**Trigger:** Alex, Exp16 — do not conflate host Miniconda CPython venv (`CircuitPython_3.13_VsCode`) with CircuitPython firmware; do not assume MicroPython APIs carry over.

**Change:** MONITORING scope-lift candidate removed (action taken). Directive in `CODING_PRINCIPLES.md` broadened to three runtimes (host CPython / CircuitPython / MicroPython). Not lifted to `[universal]` (M3 needs sign-off).

## 2026-09-04 — extend: first `universal/PATTERNS.md` entry (public-repo third-party hygiene)

**Trigger:** exp16 2nd-project occurrence of the coding-tutor (2026-07-15) candidate: BananaPi goldfinger JPEG vendored unmodified under CC BY-SA with a sidecar, vs coding-tutor’s gitignore-by-default papers folder.

**Change** (`extend`; M3 auto-promote to `[cross-experiment]`, not `[universal]`):
- `universal/PATTERNS.md`: first real pattern (was empty since warm reset).
- `crossref/BY_PATTERN.md`: occurrence count 2; row retained as provenance.

## 2026-09-04 — extend: instantiate destructive-ops hard gate (always-on stub + fail-closed ledger)

**Trigger**: Alex updated `/Users/alex/Git/rnd-ai-skills/generalized-agent-learnings` with `destructive-operations.md` and asked to prominently summarize the core rules in Exp16 notes **and** persona memory so they cannot be missed.

**Change** (`extend`; no compaction):
- **Always-on identity stub** `06-destructive-operations.mdc` (`alwaysApply: true`) — §0+§3 sentence + pointer. Cursor has **no** pre-tool `rm` hook; reflex coverage is lossy; the stub is the intercept (corpus §10–§11 install recipe).
- **Fail-closed ledger** `memory/PERMITTED_DESTRUCTIVE_ACTIONS.md` — empty Active grants. Absence of a matching entry = no permission.
- **Capability copy** `.cursor/rules/reference/destructive-operations.md` (corpus treated as potentially ephemeral, same pattern as `cold-ai-paradigm.md`). Live source remains `/Users/alex/Git/rnd-ai-skills/generalized-agent-learnings/destructive-operations.md`.
- **`WORKING_STYLE.md`**: HARD GATE banner immediately under the header (outranks the rest of the file); new Core Principle *Destructive-action hard gate* `[universal]`; split the 2026-09-03 env+destructive row so setup/scripts stay `[user]` Workflow & Artifacts. Invalidates the 2026-09-03 flag that the corpus had no named entry.
- **File table / M5**: ledger added to `00-memory-system.mdc § File Architecture`; M5 on-demand note in `04-multi-project.mdc` (ledger is **not** a session-start always-read). `COLLABORATOR_GUIDE.md` tree + human-facing section.

**Exp16 (content, not architecture):** prominent banners in `ai-notes/INDEX.md` and `ai-notes/NOTES.md`; pointer in `projects/circuitpython-exp16-planetx/CONTEXT.md`.

**Did not copy the full protocol into always-on context** — stub + banner only; procedure stays on-demand (corpus §10 identity vs capability split).

## 2026-07-15 — extend: seed `concepts/git.md` (first cross-project tooling domain); log git-hygiene pattern + topic; add escalation directive

**Trigger**: coding-tutor session — an attribution/gitignore task escalated into a full copyright remediation on a public repo (untrack + `git filter-repo` history scrub + accepted PR-ref residual). Yielded reusable, evidence-supported git/publishing knowledge and a repeatable attribution workflow. User then gated a short maintenance iteration.

**Change** (all `extend`, no restructuring):
- **New concept domain `concepts/git.md`** (`[domain:git]` `[cross-experiment]`, `evidence-supported`) — 3 concepts: (1) history rewrite ≠ removal via merged-PR refs / bare-SHA / fork networks (only GitHub Support purges); (2) scrub-a-file-from-history recipe (`clone --mirror` + `filter-repo` + `push --force --mirror`); (3) `git rm --cached` is all-or-nothing across pathspecs. First **non-CircuitPython** domain — validates the graph holds general tooling knowledge, not just hardware. Index lines added to `concepts/_INDEX.md`.
- **`crossref/BY_PATTERN.md`**: candidate row "Public-repo third-party-material hygiene" (process, coding-tutor, 1 occurrence → `PATTERNS.md` on 2nd public-release project).
- **`crossref/BY_TOPIC.md`**: row "Git history/publishing hygiene" → coding-tutor / `concepts/git.md`.
- **`universal/WORKING_STYLE.md § Judgment & Escalation`**: new `(experimental)` directive — *Verify blast radius before mutating shared/published state; surface exposure beyond the literal ask* (`[universal]`, 1, 2026-07-15).
- **`MAINTENANCE_BACKLOG.md`**: appended this session's confirm evidence to the provisional-marker-removal item; recommended running it.

**Propagated updates**: `concepts/_INDEX.md` (new domain block + "Seeded since" line); project trail in `projects/coding-tutor/{CONTEXT,SESSION_LOG}.md` (task narrative).

**Verification**: every write landed one-hop via the placement gate with no ambiguity, including a domain unlike the existing hardware ones — a positive `confirm` signal for the still-PROVISIONAL multi-project layout (recorded in the backlog).

## 2026-07-15 — simplify: single dedicated `ai-persona` root replaces symlink-fanout (Cursor multi-root rule-duplication bug)

**Trigger**: Alex recalled a prior realization — that symlinking the same `.cursor/rules` tree into multiple workspace roots caused repeated inclusion in the context window — and asked for it to be re-validated. Confirmed via Cursor's own bug reports/forum (not previously recorded anywhere in this memory, i.e. it had only ever lived in an unpersisted conversation — a gap per `03-memory-update-triggers.mdc` item 4): Cursor scans `.cursor/rules/` independently per workspace root in a multi-root session, with **no content-based deduplication**. `alwaysApply: true` rules are injected unconditionally (not glob-gated) once per root where the file is filesystem-reachable — real copy or symlink, doesn't matter. N roots reachable to the same rule content = N× token cost. Confirmed still open/unfixed as of this session (Cursor team: "no dedup yet... team is already working on a fix... no ETA").

**Change**: Alex (independently, before this session) relocated the physical rules tree `CircuitPython/.cursor/rules/` → `CircuitPython/ai-persona/.cursor/rules/`, and added an `ai-persona` folder to the Cursor multi-root workspace file. This orphaned the two pre-existing cross-root symlinks that pointed at the old location:
- `2026-04_Exp14_DisplayLibrary_CPy_on_RPi-Pico-2040/.cursor/rules` → `../../.cursor/rules` (relative; dangling)
- `Bamboo-Lamp/.cursor/rules` → `/Users/alex/Development/VsCode/CircuitPython/.cursor/rules` (absolute; dangling)

Agent provided the exact `rm` commands (not executed by the agent — Alex's explicit request to do the deletion himself, consistent with the *hand off unavoidable shell file-ops* directive but user-initiated here rather than an approval-gate stall). Alex confirmed both deleted; verified via `readlink`/`stat` this session — both gone.

**Decision (Alex-gated, accepted trade-off)**: keep `ai-persona/` as the **sole** physical location going forward. No repair-symlinks. Considered and rejected: (a) repair the two symlinks to point at the new location — restores per-project standalone-open reachability but re-accepts N× duplication whenever ≥2 symlinked roots are co-attached in one workspace; (b) migrate to Cursor's global User Rules (app settings, not a repo) — zero duplication and standalone-safe, but forfeits git-versioning/inspectability of the persona. Alex's stated rationale for (dedicated-root-only): "entirely compatible with my work setup."

**New reachability model (supersedes the D6/R-6 symlink-fanout model from the 2026-06-14 warm reset)**: the persona (`alwaysApply` rules + all of `memory/`) loads **only when `ai-persona` is a folder in the currently-open Cursor workspace**. Live entry point confirmed: `/Users/alex/Development/Cursor Workspaces/circuitpython.code-workspace` already lists `ai-persona` as its first folder, alongside Exp15/Exp14/Exp13/Exp11/Exp09/Bamboo-Lamp/CodingTutor/Isana-LightTower/Isana-Crash-Sensor — no edit needed there. An older, no-longer-used VS Code workspace file (`CircuitPython/CircuitPy_VSCode.code-workspace`) predates the move to Cursor, lacks `ai-persona`, and was confirmed by Alex to be inactive; left untouched, out of scope.

**Regression accepted, not a bug**: the 2026-06-14 "R-6 fully CLOSED — standalone-open test PASSED" finding (`SESSION_LOG.md` Session 11) is now **historical, not current state** — it depended on the `Bamboo-Lamp/.cursor/rules` symlink just deleted. Opening any project folder directly (bypassing a `.code-workspace` file that includes `ai-persona`) now yields **zero** persona coverage, with no error surfaced. Retained in `SESSION_LOG.md` as provenance rather than corrected in place (F1/F10 guard — don't rewrite history, supersede it explicitly).

**Not yet re-validated this session**: whether a *single* `alwaysApply` rule living in exactly one attached root (`ai-persona`) is actually injected globally across the whole chat session regardless of which other attached root's files are being edited (vs. being scoped only to files within `ai-persona` itself). Cursor's own docs describe `Always Apply` as "included in every conversation" (unconditional, not glob-gated), and a forum answer distinguishes this from glob-scoped rules ("a rule from root A only applies to files in root A" — stated specifically about glob-matched rules, not `alwaysApply`) — so the inference is that a single copy in `ai-persona` should apply workspace-wide. This is a **plausible-but-unconfirmed mechanism claim**, not yet checked against on-device/in-session behavior (e.g. asking the agent to list its always-applied rules while an Exp14 file is the active context, per the reproduction method in the duplication bug reports).

## 2026-06-15 — extend: seeded `concepts/i2c.md` + `concepts/power.md`; `fuel-gauge`/`sensors` taxonomy decision

**Change**: first concept-domain seeding since the warm reset (user-gated; Alex approved I2C, then power). Two new domain files, both `[cross-experiment]` `evidence-supported`, populated from the Bamboo-Lamp standby thread but written as **general** domain knowledge (lamp = illustration only). Each claim verified this session against ≥2 independent/authority sources before being marked evidence-supported (Alex's standing instruction).

- **`concepts/i2c.md`** (6 concepts): open-drain/wired-AND · ratiometric logic levels · pull-up sizing (Rp min/max, modes, Cb) · 7-bit addressing/reserved/conflict-resolution · clock stretching · back-feeding (ESD-diode). Sources: NXP UM10204, TI SLVA689/SLVA704/SBAA565/SCDA015, Nexperia AN90044, Microchip, Sofics, Broadcom.
- **`concepts/power.md`** (6 concepts): self-discharge floor · standby budgeting · power-domain isolation & Ioff · power gating & fail-off · fuel gauge MAX17048 (voltage-based ModelGauge + mode ladder) · COTS-LED standby heuristic. Sources: 5 battery refs (self-discharge), MAX17048 datasheet Rev.7 (+3 mirrors), TI SCDA015/szza030, Pololu 2808 page.

**Taxonomy decisions (Level-2, Alex-gated)**:
- **`fuel-gauge` is NOT a separate domain** — folded into `power` (MAX17048's reusable knowledge is energy/SoC management; a per-device domain stays near-empty; D8 graduation = seed coarse, split when unwieldy).
- **`sensors` deferred** — power-*measurement* devices (fuel gauge, current/voltage monitor) live in `power`; **environmental/physical** sensors (temperature LM75A, motion, light) → a future `sensors` domain seeded on first concrete sensing concept (seed-on-evidence C7; none yet — LM75A is address-only so far).
- **Cross-domain components** live in their primary domain + are cross-referenced (MAX17048 → `power`, cross-ref `i2c`).

**Cross-records updated**: `concepts/_INDEX.md` (added both domain blocks; rewrote candidate-domains note: removed `power`/`i2c`/`fuel-gauge`, recorded the sensors taxonomy); `concepts/_RELATIONS.md` (3 realized i2c↔power edges, replacing the anticipated ones); `crossref/BY_TOPIC.md` (I2C-bus, power, and fuel-gauge rows now point at the seeded concept files); `projects/bamboo-lamp/SESSION_LOG.md` (Session-3 addendum). Digest §6/§9/§10 promotion-flags now satisfied.

**Refinement surfaced during verification**: LiPo self-discharge corroborated at **~2–5 %/mo** (premium 1–3 %), refining the digest's earlier "3–5 %"; conclusion (dominates µA electronics) unchanged. Recorded in `power.md`.

## 2026-06-14 — refine/extend: post-warm-reset maintenance iteration (consistency sweep + distilled learnings)

**Change**: first lifecycle iteration after the warm reset (user-gated; Alex: "refine your memory ... consistency, conciseness, cross-records, distill learnings"). Three actions, all additive/refining — no structural reorg, no entry dropped.

- **Consistency (refine)**: re-pointed the residual **active forward-routing** `TECHNICAL.md` pointers → `concepts/<domain>.md`. The Phase-7 dead-path grep had only swept `.mdc` rule files, not the memory *data*; `MONITORING.md` (4 spots: the "what does/doesn't go here" routing lines, the cross-ref-on-promotion line, and the MicroPython-perf + font-swap + `str.translate` action-on-trigger pointers) and `CODING_PRINCIPLES.md` (the domain-knowledge routing line + the *Cross-runtime citations* directive's promote-to and "now lives in" pointers) still told a future session to write to the retired file. **Historical** `TECHNICAL.md` mentions (this changelog's warm-reset entry, exp14 `SESSION_LOG.md` narrative, the `concepts/*` "reshaped from" provenance notes) were left intact — they correctly describe past state.
- **Distilled learning → directive (generalize)**: `WORKING_STYLE.md § Workflow & Artifacts` *Prefer the file-edit tools over shell for file mutations; hand off an unavoidable shell file-op rather than let it hang* `[user]` `(experimental)`. Evidence = 3 approval-gate stalls during the warm-reset execution (`cp -R` snapshot, `sed` range-append, `ln -s` symlink) — non-allowlisted file-mutating shell commands stall the whole turn rather than erroring. Generalizable core: prefer `Write`/`StrReplace`/`Delete`; elevate or hand off unavoidable shell file-ops.
- **Distilled learning → maintenance discipline (generalize)**: `WORKING_STYLE.md § Retention and Evaluation` new bullet *Verify no-loss by claims-coverage, not line-diff, when restructuring* — lifts the warm-reset C1/R-8/S2 no-loss invariant to a persona-wide restructuring rule.

**Headers/cross-records updated**: `WORKING_STYLE.md` Last-updated line; central `SESSION_LOG.md` gained **Session 11 (warm-reset EXECUTION + this maintenance)** — the execution narrative the Session-10 handoff anticipated but which only this changelog had captured.

**Not done (deliberate)**: no compaction (memory is fresh, no redundancy); `PATTERNS.md` stays empty (still only 1 project with substantial content — correct); `MAINTENANCE_BACKLOG.md` still uncreated (backlog empty). No further lifecycle iteration recommended now.

## 2026-06-14 — split/generalize: WARM RESET — flat memory/ → unified multi-project layout (`status: warm-reset-completed`)

**Change**: executed the `warm reset` mandate (`mandates/multi-project.md`). Reorganized the flat single-project `memory/` into a single **unified, multi-project** persona memory — one memory home, reachable from every project workspace, NOT federated. This is a **Level 2–3 structural change**, run as one deliberate, Alex-gated maintenance session (trigger: Alex's exact phrase "warm reset" + go-ahead, 2026-06-14). Governing plan: `working-docs/warm-reset-plan/warm-reset-plan_v1.0.md`; judgment calls: `risk-register.md` (same folder). Decisions D1–D8 closed by Alex 2026-06-14 (see plan §3).

**New layout** (`.cursor/rules/memory/`):
- `universal/` — behavioral / cross-project memory: `WORKING_STYLE.md`, `CODING_PRINCIPLES.md`, `MONITORING.md`, `CHANGELOG.md` (this file), `PATTERNS.md` (new, empty — cross-project generalized patterns, seeded on evidence). *(DV1: moved more than the mandate's `WORKING_STYLE.md`-only step 4 — the other three postdate the 2026-04-17 mandate and are behavioral, so they belong with it.)*
- `concepts/` — domain-knowledge concept graph (D8 = (c) graduated): `_INDEX.md` (always-read skeleton), `_RELATIONS.md` (typed edge list), one `concepts/<domain>.md` per evidenced domain — today `circuitpython-runtime.md`, `fonts.md`. *(R-9: the two populated `TECHNICAL.md` sections were reshaped — prose → concept entries — an explicitly Alex-approved exception to the mandate's "no content rewrite" anti-goal, scoped to those two sections only.)*
- `projects/` — per-project digests + entry-points: `_INDEX.md` (roster + path-globs for active-project detection, M1), `circuitpython-exp14-display/`, `circuitpython-exp15-microbit/` (stub), `bamboo-lamp/`. Each holds `CONTEXT.md` (links into the project repo's technical artifacts, never copies them — C8), `SESSION_LOG.md`, and `CONCLUSIONS.md` where content exists.
- `crossref/` — `BY_TOPIC.md` + `BY_PATTERN.md` (header-only at reset — cross-project patterns need ≥2 projects with content; expected, not a C7 violation).

**Content disposition** (C1 no-loss, verified by **claims-coverage** S2, not a line diff — R-8):
- Behavioral files: moved unchanged into `universal/`.
- `SESSION_LOG.md`: split by project (move, verbatim) — exp14 sessions 1–8 → `projects/circuitpython-exp14-display/SESSION_LOG.md`; exp15 session 9 → `projects/circuitpython-exp15-microbit/SESSION_LOG.md`; the `[tooling]` warm-reset session 10 + the cross-project living summary/SoT map → central `memory/SESSION_LOG.md` (living summary rewritten to the unified layout — a status/structure update, not a findings rewrite).
- `TECHNICAL.md`: 2 populated sections reshaped → `concepts/` (R-9); 8 empty schema sections **retired** (zero claims; superseded by the placement gate + concept-graph; the pre-reset snapshot retains them).
- `CONCLUSIONS.md`: the one `[exp14]` finding → `projects/circuitpython-exp14-display/CONCLUSIONS.md`.

**Adaptations of the mandate-template (it is an adaptable prior, not a rigid source of truth — plan header)**: DV1 (universal/ holds 4 files, logged above); DV2 (`reference/` left in place — moving it would orphan ~15+ path refs for zero retrieval gain); DV3 = D8 concept-graph (Alex-approved structural deviation). Low-stakes adaptation made this run: seeded 2 concept domains, not the plan's illustrative 3 — `display` would be near-empty, so the glyph-coordinate concept folds into `fonts.md` (C7 seed-on-evidence; accumulate-then-split later).

**Rule-file updates**: `00-memory-system.mdc` (paths + M5 read order defers to `04`); `02-domain-structure.mdc` (Active-Experiment-Detection → M1 active-project identifier); `01-interaction-style.mdc` + `03-memory-update-triggers.mdc` (path refs); new `04-multi-project.mdc` (M2 scope tagging, M3 promotion ladder, M5 attention scoping, M6 demotion, the placement gate); `mandates/multi-project.md` (D5: stale `verified`/human-elevation/validation-gate vocabulary **superseded via a document-wide "EXECUTED" banner** — the historical protocol text is retained beneath it as provenance, not deleted line-by-line); `COLLABORATOR_GUIDE.md` (new layout).

**Cross-workspace reachability (D6, unified)**: central tree stays at `.cursor/rules/` in the CircuitPython workspace; `exp14/.cursor/rules` symlink resolves; **`Bamboo-Lamp/.cursor/rules` → canonical tree CREATED + verified resolving 2026-06-14** (Alex ran `mkdir`+`ln -s`; `realpath` = `/Users/alex/Development/VsCode/CircuitPython/.cursor/rules`; reaches all 5 `*.mdc` + `memory/projects/bamboo-lamp/CONTEXT.md`). Filesystem reachability (S5) ✅ for exp14 / base / Bamboo-Lamp. **R-6 fully CLOSED — standalone-open test PASSED 2026-06-14** (`evidence-supported`, on-device/observed): Alex opened Bamboo-Lamp alone (CircuitPython workspace NOT attached) and the Cursor Rules panel listed `00`–`04`, confirming Cursor's rule loader follows the cross-tree `.cursor/rules` symlink standalone. The user-level-root fallback is therefore **not needed**. S4 (cold-AI start) + S5 now pass unconditionally for all three workspaces; no open reachability items remain.

**Provisional marker (C7)**: the new structure is tagged `provisional (as of 2026-06-14)` with a cold-AI-testable watch-for (in `concepts/_INDEX.md` + `projects/_INDEX.md`). Confirm = a real query resolves one-hop; refute = needs multi-file/speculative search or a finding has no deterministic placement-gate home; trigger = re-evaluate after ~5 real memory additions or next maintenance session.

**Rollback** (exact, from the CircuitPython workspace root unless noted):
> **Note (2026-09-15):** the `memory-pre-warm-reset-20260614-150919/` snapshot was removed from the working tree (Alex). It is git-tracked, so step 1 below first requires restoring it: `git checkout 2e93f17 -- ai-persona/.cursor/rules/memory-pre-warm-reset-20260614-150919` (or from `master`). The rollback is otherwise unchanged.
1. `rm -rf .cursor/rules/memory && cp -R .cursor/rules/memory-pre-warm-reset-20260614-150919 .cursor/rules/memory`
2. `git checkout -- .cursor/rules/*.mdc .cursor/rules/COLLABORATOR_GUIDE.md .cursor/rules/mandates/multi-project.md` — reverts the edited rule files / guide / mandate. **Confirmed git-tracked 2026-06-14** (`git status` shows them as `M`/`D`), so this is clean; the `memory/` snapshot does not cover these (they live above `memory/`), git does.
3. `rm -f .cursor/rules/04-multi-project.mdc` (new untracked file, no prior version).
4. Bamboo-Lamp (repo root `/Users/alex/Projects/Family/Bamboo-Lamp`): `rm -f .cursor/rules` (the handoff symlink, if/when created) ; `rm -rf memory && cp -R memory-pre-warm-reset-20260614-171818 memory` (restores README/SESSION_LOG/CONCLUSIONS to pre-reset content).

**Failure-mode guards honored**: F1 (deliberate, not a side effect; no directive dropped), F8 (no purpose-conflation dedup), F10 (single source of truth — C8 links-not-copies; exactly one file prescribes the session-start read order).

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
