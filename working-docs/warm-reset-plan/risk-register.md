# Risk Register — warm-reset plan (priority escalation set for Alex)

**Consumer**: Alex (decisions) + AI (execution). **Produced**: 2026-06-14, at the `_META.md` Post-loop close. **Scope**: the *irreducible a-priori judgment calls* — assumptions and design choices that **cannot be settled by executing the plan** (they are decided up front or not at all). Normal known-unknowns that execution *will* reveal (and the plan handles via checkpoints/exit-ramps) are deliberately excluded. **Method**: cross-scan of `notes_v0.1.md`…`notes_v0.5.md` + `warm-reset-plan_v1.0.md`. **Overlap note**: many map onto D1–D8 (expected — those are the escalation set); items **R-7…R-11 are surfaced by this scan beyond the D-list**, including ones the plan does not yet handle (`MISSING`).

**Load-bearing first** (decide these before anything else — most phases invalidate if wrong): **R-1 (D1 granularity), R-2 (D4 scope-model), R-3 (D8 concept-graph).**

---

## A. A-priori decisions already in the plan as OPEN escalations (D-items)

### R-1 · Project granularity (D1 / OQ1)
- **Choice**: per-experiment projects under a `circuitpython` family + Bamboo-Lamp as its own family (rec (a)+(d)).
- **Why not settleable by execution**: taxonomy choice — moving files doesn't tell you whether exp11+exp13 *should* have been one "ws2812-lighting" project; you only learn that after months of retrieval experience.
- **Blast radius**: shapes `projects/` tree, `_INDEX.md`, every content tag, the active-project globs (M1). Re-deciding later = a second migration.
- **Disposition**: **DECIDED by Alex 2026-06-14 = (a)+(d)** (recommendation accepted).
- **Hedge**: start per-experiment (finest grain) — coarsening later (merge folders) is cheaper than splitting; `_INDEX.md` family column absorbs grouping without a structural change.

### R-2 · Scope-model (D4 / Recon-A)
- **Choice**: keep directive-scope (4-tier `[universal]/[user]/[project]/[task]`) and content-scope (`family`/`project`) as **orthogonal** dimensions (rec).
- **Why not settleable by execution**: it is a modeling decision about *how* knowledge is categorized; no move-time observation confirms it.
- **Blast radius**: the tagging taxonomy on every entry + `04-multi-project.mdc`'s scope rule. A wrong collapse loses either user-cross-project prefs (`[user]`) or project-grouping (`[family]`).
- **Disposition**: **DECIDED by Alex 2026-06-14 = keep orthogonal** (recommendation accepted).
- **Hedge**: orthogonal is the non-destructive choice (keeps both axes); can collapse later if proven redundant, but cannot un-collapse without re-tagging.

### R-3 · Concept-graph adoption (D8 / DV3)
- **Choice**: graduated concept-graph — `concepts/_INDEX.md` + `_RELATIONS.md` from day one, one `concepts/<domain>.md` per evidenced domain, split-to-files later (rec (c)).
- **Why not settleable by execution**: it is a bet on a *retrieval* architecture; its payoff only shows over many post-reset sessions (and is gated by the C7 provisional watch-for), not during the move itself.
- **Blast radius**: the entire domain-knowledge retrieval layer; deviates from the mandate's flat per-project files (so it is also an authority call).
- **Disposition**: **DECIDED by Alex 2026-06-14 = (c) graduated** (recommendation accepted). **Interaction now resolved**: R-9 (anti-goal tension) → reshaping is an approved exception scoped to the two existing sections; R-8 (no-loss verification) → use claims-coverage check.
- **Hedge**: (c) is the minimal-commitment middle — gets one-hop + lateral edges at low scaffolding cost; if the C7 watch-for refute signals fire post-reset, fall back toward (a).

### R-4 · Promotion autonomy (D2 / OQ2)
- **Choice**: auto-promote cross-project at the 2-project trigger, sign-off only for `[universal]` (rec (b)).
- **Why not settleable by execution**: a governance/authority preference, not an empirical fact.
- **Blast radius**: how/whether patterns flow up the ladder; over-autonomy risks premature universals, under-autonomy stalls cross-pollination.
- **Disposition**: **DECIDED by Alex 2026-06-14 = (b)** (recommendation accepted).
- **Hedge**: (b) + the M6 demotion path (mark `disputed`, log in CHANGELOG) makes wrong promotions reversible.

### R-5 · Reachability of the single unified memory (D6 + D7) — **DECIDED (unified)**
- **Choice**: **DECIDED by Alex 2026-06-14 — one unified persona memory in one location, reachable from all workspaces; NOT federated** (D7 = unified; supersedes the prior hybrid/federation recommendation). High-level memory is central; project folders hold linked technical artifacts. **D6 path also decided**: the central tree stays in the CircuitPython workspace's `.cursor/rules/` and is symlinked into the other workspaces (not a user-level root).
- **Why still a risk after the decision**: federation is no longer a fallback, so **cross-workspace reachability is now load-bearing, not optional** — if the single location can't be reached from a workspace, that project's session has no memory (harder failure than the old hybrid). Pushes weight onto R-6.
- **Blast radius**: C4 (the *entire* memory reachable from every workspace); a standalone Bamboo-Lamp session's correctness depends entirely on the link resolving.
- **Disposition**: decision CLOSED (unified; in-workspace tree + symlinks); **R-6 reachability test is now mandatory**, not a hedge.
- **Hedge**: removed (no federation fallback). Mitigation is R-6 — prove the symlink resolves before relying on it; if it fails, an alternative single-location reachability mechanism must be found (still not federation).

---

## B. Risks surfaced by the scan BEYOND the D-list (some not yet handled by the plan)

### R-6 · Symlink reliability for the single cross-workspace memory (now load-bearing, sub-risk of D6)
- **Assumption**: a symlink (`.cursor/rules` → the single central memory root) resolves correctly under Cursor's rule loader **and** survives git operations across separate workspace roots.
- **Why not settleable by executing the plan**: the plan executes in the CircuitPython workspace; it does not exercise Cursor's rule-loading from the Bamboo-Lamp root, nor git's symlink handling there.
- **Blast radius**: **raised by R-5's unified decision** — with no federation fallback, a failed symlink means a workspace's session loads *no* memory (not just missing behavioral files) — a silent, total correctness failure for that project.
- **Disposition**: **MANDATORY pre-check** (was: partial hedge). Guidelines §7 lists symlink-vs-federation but federation is now off the table, so symlink resolution must be proven before sign-off.
- **Mechanical evidence (2026-06-14, `evidence-supported`)**: inspected the live layout. Canonical persona = **real files** at `/Users/alex/Development/VsCode/CircuitPython/.cursor/rules/` (memory/ within). `exp14/.cursor/rules` is already a **working symlink** → `../../.cursor/rules` (realpath confirmed) — so the in-workspace symlink pattern D6 chose is proven for an intra-tree case. exp13/11/09 have no `.cursor` (inherit by directory ascent). **Bamboo-Lamp has no `.cursor` and no symlink** — it reaches the persona only via co-opening in the multi-root `CircuitPy_VSCode.code-workspace`; opened standalone it would load no persona memory. No `~/.cursor/rules` global exists. → R-6's remaining unknown narrows to: does Cursor's rule loader follow a `Bamboo-Lamp/.cursor/rules` symlink (cross-tree, into `/Users/alex/Development/...`) when Bamboo-Lamp is opened **standalone** (not co-opened)? That single test is the gate; the intra-tree symlink mechanism itself is already confirmed working.
- **Hedge**: run a `realpath` + rule-load smoke test from each workspace root **before** committing to D6's path. If symlinks fail, find another single-location reachability mechanism (e.g. a Cursor-supported shared rules path) — do NOT fall back to federation (contradicts the unified decision). Add as a Phase-0.5 / Phase-4 pre-check.

### R-7 · D3's "default untagged → active project" mis-tags already-cross-scoped content
- **Assumption (in D3)**: pre-existing untagged `TECHNICAL`/`CONCLUSIONS` entries default to the single active project (exp14).
- **The problem (concrete, from the content inventory)**: the two populated `TECHNICAL.md` sections are **already scoped broader than exp14** — "Memory Management on CircuitPython" is `[universal]`-across-CircuitPython (RP2040-anchored) and "Fonts for pixel-accurate displays" is `[cross-experiment]`. Blindly defaulting them to `[project:circuitpython-exp14-display]` would **bury genuinely cross-project knowledge inside one project**, directly defeating the cross-pollination goal that motivates the warm reset.
- **Why not settleable by execution**: the correct scope is a judgment about the knowledge's generality, already encoded in the existing tags — a default rule that ignores them is wrong a-priori, not discoverable mid-move.
- **Blast radius**: the most valuable (already-generalized) technical knowledge lands at the wrong scope; future cross-project retrieval misses it.
- **Disposition**: **RESOLVED by Alex 2026-06-14** — the fix is adopted into D3 (and generalized to a Core Principle: *Don't guess an association into a deep, specific bucket*).
- **Fix (adopted)**: D3 now reads — "honor any scope tag already present; the active-project default applies ONLY to genuinely untagged entries; route `[universal]`/`[cross-experiment]` technical content to central (`concepts/`/`universal/`), not to a project." The governing principle: never trade a findable placement for a confidently-wrong (deep, buried) one.

### R-8 · No-content-loss verification (S2) may not be mechanically runnable under a restructure
- **Assumption (S2/C1)**: no-loss is provable by diffing the pre-reset snapshot's entry set against post-reset.
- **The problem**: a clean set-diff works for a pure move+tag, but if D8=(b)/(c) reshapes `TECHNICAL.md` prose into per-concept entries, the text is *reorganized*, not relocated — a naive diff won't line up, so S2 as written can't certify no-loss.
- **Why not settleable by execution**: the verification *method* must be chosen a-priori to match the chosen transform; you can't discover a working diff method after you've already reshaped and possibly lost something.
- **Blast radius**: inability to prove C1 (no loss) — the core safety guarantee of the whole reset.
- **Disposition**: **RESOLVED by Alex 2026-06-14** — since D8 = (c), S2 is the claims-coverage method (folded into D8 + S2).
- **Fix (adopted)**: S2 = a *claims-coverage* check (enumerate every claim/finding in the snapshot; confirm each appears, by content, somewhere post-reset) rather than a line/entry diff. Snapshot remains ground truth.

### R-9 · Concept-graph (D8 b/c) is in tension with the mandate's "no content rewrite" anti-goal
- **Assumption**: warm reset is a pure structural move + tag (mandate anti-goal: "not a content rewrite … only moved and tagged").
- **The problem**: building `concepts/<domain>.md` entries from the current monolithic `TECHNICAL.md` prose is a *reshaping* of content — arguably the rewrite the anti-goal forbids.
- **Why not settleable by execution**: it is a definitional/scope tension to resolve before acting; executing won't tell you whether you've crossed the "rewrite" line.
- **Blast radius**: scope creep from a bounded structural move into a content-rewrite session (which the mandate says should be a *separate* later maintenance pass) → larger risk surface, harder rollback.
- **Disposition**: **RESOLVED by Alex 2026-06-14 = option (ii)** — with D8 = (c), the prose→concept reshaping is an explicitly-approved exception to the "no content rewrite" anti-goal, **scoped to the two existing `TECHNICAL.md` sections only**. Any broader reshaping remains a separate later maintenance pass.
- **Residual guard**: if execution finds the reshaping creeping beyond those two sections, STOP and surface (the §8 exit ramp: "task drifts from execute toward redesign").

### R-10 · The design rubric itself is an unvalidated v1 draft
- **Assumption**: `microcontroller-multi-project-memory-guidelines.md` (the R1 rubric) is a sound basis for judging the structure.
- **The problem**: it self-describes as "v1 (draft, will be stress-tested by the warm-reset plan)" — the plan is reviewed against a rubric that is itself unproven.
- **Why not settleable by execution**: rubric validity is a methodological prior; the move can't confirm the rubric was the right yardstick.
- **Blast radius**: low-probability but broad — if the rubric over-values the concept-graph, R-3/R-9 inherit the error.
- **Disposition**: OPEN (inherent; acceptable).
- **Hedge**: the C7 `provisional` marker + post-reset watch-for is exactly the empirical stress-test the rubric anticipates; treat the first post-reset month as rubric validation, demote structure if the watch-for refute signals fire.

### R-11 · The whole persona memory is single-sourced; warm reset must not fork it
- **Assumption**: per Alex's unified decision, the **entire** persona memory (behavioral `universal/*` **and** per-project digests/concepts) is single-sourced centrally; Bamboo-Lamp references it, never copies it (D7 unified, C4, DV1).
- **The problem**: Bamboo-Lamp currently maintains its own `memory/` home; Phase 4 migrates its high-level content out and leaves a pointer. If migration is incomplete (some high-level content stays behind), the memory forks (two copies drifting) — the F10 hazard at the cross-project level, now spanning *all* memory, not just behavioral.
- **Why not settleable by execution**: it is a single-source-of-truth policy choice spanning two repos, decided a-priori (and now decided: unified).
- **Blast radius**: forked memory = contradictory digests/directives across projects (the exact thing the SESSION_LOG routing note guards against today).
- **Disposition**: decision made (unified); invariant should be stated explicitly — Alex's directive + C4/C8 + Phase 4 now encode it, but assert it as a hard invariant: **"exactly one persona memory home; project folders hold linked artifacts only, never a second copy of high-level memory."**
- **Hedge / fix**: Phase 4 must verify the emptied `Bamboo-Lamp/memory/` retains *only* a pointer (no high-level content left behind). Ties R-5/R-6 (the single home must be *reachable* from Bamboo-Lamp for this to hold).

---

## Summary for Alex — ALL DECISIONS RESOLVED (2026-06-14)

Every a-priori judgment call in this register is now decided by Alex:

| Item | Decision |
|---|---|
| R-1 (D1 granularity) | per-experiment projects + `circuitpython` family; Bamboo-Lamp own family |
| R-2 (D4 scope-model) | keep the two scope dimensions orthogonal |
| R-3 (D8 concept-graph) | (c) graduated |
| R-4 (D2 promotion autonomy) | (b) auto-promote, sign-off for `[universal]` |
| R-5 (D6/D7 unify+reach) | one unified memory, not federated; central tree in CircuitPython `.cursor/rules/`, symlinked into other workspaces |
| R-7 (don't mis-default cross-scoped) | fix adopted into D3 + Core Principle (don't bury in a wrong deep bucket) |
| R-8 (no-loss method) | claims-coverage check (S2) |
| R-9 (anti-goal tension) | reshaping = approved exception, scoped to the two existing sections only |
| R-11 (single-source memory) | invariant asserted: one memory home; project folders hold linked artifacts only |
| R-10 (rubric is v1 draft) | accepted as inherent; C7 provisional watch-for is the empirical stress-test |

**Remaining before execution (only two):** (1) **R-6** — mandatory symlink reachability smoke-test (no federation fallback); (2) the hard gate — Alex's exact phrase **"warm reset"** + go-ahead. No file mutation until both clear.
