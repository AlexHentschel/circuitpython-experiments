# Microcontroller Multi-Project Memory Guidelines

**Status**: distilled best-practice, v1 (draft, will be stress-tested by the warm-reset plan). **Authored**: 2026-06-14. **Consumer**: AI (this persona, cold). **Provenance**: distilled from `~/Developed/AI/generalized-agent-learnings/` files `11-MULTI-PROJECT-BOOTSTRAP.md` + `10-ADAPTIVE-MEMORY-STRUCTURE.md` (ephemeral source; durable copies of the two paradigm docs already in `.cursor/rules/reference/`), focused on *this* situation: a persona spanning multiple microcontroller projects (CircuitPython experiments exp09/11/13/14/15 + the Bamboo-Lamp electronics build) with more self-contained microcontroller-realm projects expected over time.

**How to use this file**: it is the design rubric for the warm-reset target structure (review step R1 "structure-fit" in `_META.md` checks the plan against it). Not itself the plan. May be promoted to `.cursor/rules/reference/` post-warm-reset if it proves durable.

---

## 0. The single optimization target (everything below serves this)

A cold AI arrives with **a short high-level topic + one related lower-level detail**, and wants **more detail from memory**. The structure must answer this in **one navigational hop**:

```
topic  →  domain index (high-level)  →  concept entry (the detail)  →  full detail
                                     ↘  relations  →  laterally-related detail
```

Two capabilities are load-bearing and rank ABOVE parsimony: (a) **topic-first navigation** via small always-read indices; (b) **lateral traversal** to related concepts via an explicit relation graph. **Priority order, non-negotiable: retrieval-efficiency > parsimony > everything else.** Parsimony is a *soft* favour applied only after retrieval is satisfied.

---

## 1. Content vs structure (name the layer before editing)

- **Content** = what is known (findings, directives, decisions, project facts). Cheap to add — one placement decision per item.
- **Structure** = how content is organized for retrieval (directory layout, indices, relation graph, placement gate, scope-tag taxonomy, session-start read order). Expensive to change — deliberate, batched, cascading.

Always state which layer a change touches. Structure is a high-caution (Level 2) change; meta-rules about structure are Level 3. Confusing the two is the primary maintenance failure (side-effect compaction / purpose conflation).

## 2. Empiricist epistemology for structure (drives the parsimony favour)

No structure is correct in the absolute; it is judged only by retrieval performance on the queries actually seen, and the right answer shifts as content grows. Consequences:

- **Expect structure to change** — a structural change is lifecycle, not past error. Write structure in present-tense-with-date ("the domains as of 2026-06-14"), never as permanent fact.
- **Seed only what current evidence supports.** Do NOT pre-create empty domain folders / per-concept files "in case". Premature commitment hardens against later observation. (This is the parsimony mechanism: structure grows from content, not ahead of it.)
- **Split over prune.** When a file/domain grows large, split it; don't delete to shrink.
- **Heterogeneity is fine when labelled.** A sub-tree may use a different convention; say so at its index with a one-line reason, so it isn't copied blindly or "corrected" as drift.
- **In-flow structural decisions are experiments**: apply a `provisional` marker + a 2–4 line "watch-for" block (what would show the structure works / fails). Remove the marker once ~N real additions land without a signal firing.

## 3. The two load-bearing shifts (adapted + right-sized for our scale)

### 3.1 Shift one — concept-graph navigation (the retrieval engine)

Replace "read the big technical file and scan" with **domain-indexed concept entries + a relation graph**. Canonical (full-scale) shape:

```
memory/concepts/
├── _INDEX.md        one line per concept; always read at session start
├── _RELATIONS.md    edge list; read on placement / lateral traversal
├── <domain>/_INDEX.md + <concept>.md ...
```

Concept-entry template: one-line purpose · mechanism · where it applies (reinforcement + last-applied) · where it does NOT apply · refinement history (dated) · related concepts (typed bidirectional links) · provenance (origin work-context + cross-context evidence).

Relation vocabulary (closed): `refines`/`generalizes`, `alternative-to`, `composes-with`, `instantiates`/`abstracts`, `pairs-with`, `conflicts-with`, `contradicts-in-context-X`, `complemented-by`.

**Parsimony adaptation for our current volume (KEY DECISION):** per-concept *files* are justified at ~10× single-project volume; we are below that. So **graduate**:
- Start each domain as a single `concepts/<domain>.md` file with one `## <concept>` section per concept (still one-hop: `concepts/_INDEX.md` → `concepts/<domain>.md#concept`).
- Split a domain into a folder of per-concept files only when that domain file grows unwieldy (the split-over-prune trigger) or a concept accumulates enough refinement history/relations to warrant its own file.
- Keep `_INDEX.md` and `_RELATIONS.md` from day one — they are the retrieval skeleton and are cheap. Updating the index is part of the concept write, not a follow-up.

Candidate microcontroller domains (seed only those with ≥1 concrete concept now): `power` (battery, LiPo thresholds, boost/buck, standby µA budgets), `i2c` (bus, pullups, back-powering, muxing), `deep-sleep` (MCU sleep modes, wake sources, CircuitPython `alarm`), `led-driving` (WS2812 timing, level-shifting, current), `circuitpython-runtime` (memory model, type hints, on-device quirks), `display` (matrix render, fonts, column-major), `fuel-gauge` (MAX17048/SOC), `tooling` (schemdraw, circup, VS Code config). Several are inherently cross-project (power, i2c, deep-sleep) → this is where cross-project pollination pays.

### 3.2 Shift two — self-containment durability

The persona must survive any external source folder being deleted/moved. **Hard rule: no file under the persona may hard-depend on an absolute path into an ephemeral/external persona directory.** Reference external knowledge by *work-context name* + *in-context evidence description* ("during the Bamboo-Lamp standby analysis, June 2026"), not by a fragile absolute path. (We already hit this: the cold-AI directive first pointed at the ephemeral `generalized-agent-learnings/` folder; fixed by copying into `reference/`.) When you must record an absolute path (e.g. a venv), it is a tool-config fact, not a memory dependency — keep those localized and clearly labelled.

## 4. Placement gate (deterministic home for every new item)

Run on every new finding, at write time (not "wherever feels right"):
1. Code-craft (how code should be written)? → coding concept (`concepts/coding[/<language>].md` or section).
2. Domain knowledge (power, i2c, sleep, …)? → `concepts/<domain>`.
3. Cross-session finding with evidence status? → project `CONCLUSIONS` (status-tagged) and/or a concept entry.
4. Collaboration / process / judgment? → `style/WORKING_STYLE.md`.
5. Per-person preference? → `style/HUMAN_PROFILE.md`.
6. Project-specific narrative / status / open question? → that project's `SESSION_LOG` + `CONTEXT`.
Ambiguous → holding section flagged for human review; never silently drop.

## 5. Scope-tag taxonomy (prefixed, orthogonal — combine cleanly)

`[universal]` · `[domain:<x>]` (e.g. `[domain:power]`) · `[language:<y>]` (`[language:python]`) · `[family:<z>]` (`[family:circuitpython]`) · `[project:<slug>]` / `[workstream:<slug>]` (provenance: which project surfaced it) · `[problem]` (transient task tag). Record at the **narrowest** scope the originating evidence justifies; promote to broader scope only after a **second clean application in a non-originating context**. These are orthogonal to the behavioral-directive scope tags already in `WORKING_STYLE.md` (`[universal]/[user]/[project]/[task]`) — keep the two dimensions separate (directive-scope vs content-scope), do not collapse.

## 6. Project / family granularity for the microcontroller realm

- **One project = one self-contained build/experiment** (exp14, exp15, Bamboo-Lamp). New project when: new board AND new primary focus, or a new problem domain.
- **Family = a tag, NOT a directory.** Do not create `families/circuitpython/`. A concept question must land at the concept regardless of family; family lives only as `[family:circuitpython]` / `[family:bamboo-lamp-electronics]` on entries. (This is the design lesson that failed the "land-at-the-concept" test — heed it.)
- **Future-proofing**: adding the 6th microcontroller project must cost = one `workstreams/<slug>/CONTEXT.md` + one `_INDEX.md` roster row (with path-glob) + reuse of existing domains. If adding a project forces structural change, the structure was over-committed.

## 7. Cross-workspace reachability + federation (our specific constraint)

Projects live in **different workspace roots** (CircuitPython workspace vs `~/Projects/Family/Bamboo-Lamp`). Two reachability options for the shared persona/behavioral memory:
- **(a) Symlink attach**: each consumer workspace's `.cursor/rules` → host persona `rules/` (relative symlink, `realpath`-verified). Makes "one persona" reachable from any project root. Canonical multi-project answer.
- **(b) Federation**: project keeps its own memory home in its own repo (travels with the project); a roster `_INDEX.md` records its external path/glob. Better when a project's memory should version with that project's git repo (true for Bamboo-Lamp).
Recommended hybrid: **shared behavioral + cross-project concept graph live in the host persona** (symlink-attachable); **project-local technical/session memory federates with each repo**. The roster maps project → memory-home path-glob for active-project detection.

## 8. Retrieval acceptance tests (how to verify the structure works)

1. **Domain one-hop**: a domain question (e.g. "how low can XIAO standby go?") is answered via `concepts/_INDEX` → `concepts/power` → answer, no speculative search. 
2. **Cross-concept relation**: a related-detail query surfaces the linked concept via `_RELATIONS.md` without hand-derivation (e.g. `deep-sleep` ↔ `i2c back-powering during sleep`).
3. **Cross-project pollination**: a pattern found in project A lands at a deterministic home reusable by project B (placement gate yields one destination, no ambiguity).
Any failure = structure defect → revise indices/clustering, not the content.

## 9. Parsimony vs retrieval — the explicit tie-breaker

When a leaner structure and a more retrievable structure conflict: **choose retrievable.** Apply parsimony only to remove genuinely unused scaffolding (empty folders, decorative markers, indices nobody reads, duplicated content). Counter-bloat tactics that do NOT cost retrieval: graduate (sections before files), seed-on-evidence, split-over-prune, one canonical home per fact (reference, don't copy), prune decorative provisional markers once settled. Bloat tactics to avoid: pre-created empty domains, per-concept files below volume threshold, duplicated facts across files, ever-growing always-injected rules.

## 10. Implications for the warm-reset plan (D1–D7)

- **D1 granularity** → §6: per-project projects + family-as-tag (no `families/` dir).
- **D2 promotion autonomy** → §2/§5: within-domain refinement autonomous; cross-project/`[universal]` promotion needs a 2nd-context application (propose, then confirm).
- **D3 tag policy** → §5: narrowest-scope; orthogonal prefixed tags.
- **D4 scope model** → §5: keep directive-scope and content-scope orthogonal; adopt prefixed content tags.
- **D6/D7 reachability** → §7: hybrid — shared concept-graph + behavioral memory in host (symlink), project-local memory federated per repo.
- **Whole plan** → §2: mark the new structure `provisional` with watch-for signals; seed only domains with concepts in evidence now.

## Cross-references

- `.cursor/rules/reference/cold-ai-paradigm.md` — write-time gate every entry must pass.
- `.cursor/rules/reference/flexible-plans-for-ai-execution.md` — plan layering this guideline feeds into.
- `.cursor/rules/mandates/multi-project.md` — the warm-reset mandate this guideline operationalizes (note: mandate predates these guidelines; reconcile its 3-tier scope model + `families/`-implying language against §5/§6 here).
- `working-docs/warm-reset-plan/_META.md` — the planning loop that consumes this file (review step R1).
