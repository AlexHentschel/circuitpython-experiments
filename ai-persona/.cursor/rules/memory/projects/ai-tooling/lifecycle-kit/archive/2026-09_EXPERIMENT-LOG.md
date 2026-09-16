# Experiment Log — CircuitPython ai-persona full memory-maintenance lifecycle

**WORKDIR** = `/Users/alex/Development/VsCode/CircuitPython/ai-persona/ai-notes/2026-09_CPy-full_memory_lifecycle` (gitignored)
**TARGET** = the CircuitPython `ai-persona` (this persona's own durable memory) — self-maintenance
**Branch** = `alex/ai-persona-maintanance`
**Fidelity baseline** = HEAD at cycle start = `8c4151b` (captured `baseline/BASELINE.txt` + `baseline/hash-manifest-head.txt`, 77 files)

Resumption contract: a cold AI of this persona can resume from this file + the ledger + git state. Read this top-to-bottom, then `git log`, then the ledger.

---

## Status at a glance (update as you go)

- [x] Phase 0 — launch-context self-check (CircuitPython persona confirmed, not HA), branch/WORKDIR clean, baseline hashed, harness copied
- [x] Phase I — analysis + evaluation framework (own read + 2 inventory subagents integrated)
- [x] Phase II — plan (v2, critique integrated); harness de-risked
- [x] Harness — TARGET probe pool (21) + expected-reach keys; permission granted; smoke + prior + candidate runs done
- [x] Phase III — 3 iterations, all ACCEPTED + committed: Iter1 `0ee148f` (C1+C2a+C2b, 3/3 orphan discoverability win), Iter2 `eacc84b` (C3 circup index + C4 bamboo R-6 fidelity fix, wrong→right), Iter3 `ea7987d` (C5 additive relation edge). Floor ≥3 met; stopped (marginal gain ≈ cost).
- [x] Consistency-close (iters 1–3) — integrity re-check vs baseline `8c4151b`: **zero unexpected drift**; only intended files touched.
- [x] Human-review digest — `HUMAN-REVIEW-DIGEST.md` (kept current: 5 iter1–3 enacted + iter4's 8).
- [x] **iter4 — Alex approved all 8 held proposals; enacted P1/P3/P4/P5/P-prov/P6/P7/P2** (commits `4c10a3b`→`1c7132c`, one per proposal). All lossless. Integrity re-close: `git diff --stat 8c4151b` = 38 intended files, tree clean, added pointers resolve, ~39 untouched baseline files unchanged. See § iter4 below.
- [x] **Snapshot removal** — Alex removed the pre-warm-reset rollback snapshot; committed the delete (git-recoverable) + updated live refs (`f5eade2`). See ai-tooling SESSION_LOG.
- [x] **Follow-up pass (P8 + central-log thin + final probe)** — `b1715bf` MONITORING compaction, `0989c5f` central SESSION_LOG thinning, `a2696ab` CHANGELOG provenance; final paired probe (`eval/iter-final/`) confirms **no discoverability regression** + index used as hub. See § Follow-up below.

---

## Phase 0 — setup (DONE)

- Launch-context self-check PASS: injected rules are CircuitPython persona's (`00-memory-system.mdc`, `04-multi-project.mdc`, `02-domain-structure.mdc` CircuitPython multi-experiment, `06-destructive-operations.mdc`); workspace root `/Users/alex/Development/VsCode/CircuitPython`. I am **not** HA. Self-maintenance confirmed.
- Branch `alex/ai-persona-maintanance`, tree clean. HEAD `8c4151b` = fidelity baseline.
- WORKDIR was clean (only the prompt); created `baseline/ plan/ harness/ ledger/`.
- Harness `run_probe.py` copied to `harness/run_probe.py` (frozen HA copy).
- Harness prereqs verified: `flow` venv (`/Users/alex/Development/PythonVEs/flow/bin/python`, py3.10) has `cursor-sdk 1.0.28`; `~/.cursor/permissions.json` exists but only allowlists HA's two dirs — **not mine** (permission ASK needed, §6 gotcha 1).

## Phase I — whole-persona inventory (own reading, complete)

### Tree shape (77 md/mdc files)
- **Auto-injected `.mdc` (6):** `00-memory-system` (116L), `01-interaction-style` (109L), `02-domain-structure` (72L), `03-memory-update-triggers` (23L), `04-multi-project` (58L), `06-destructive-operations` (25L). Lean, well cross-referenced. (Note: no `05-*` — numbering gap, harmless.)
- **`reference/` (22 files, ~4,600L):** read-on-demand depth layer. Mixed numbering (`00`–`11` numbered + named files). **NO `reference/_INDEX.md`** — biggest discoverability gap found.
- **`memory/`:** well-structured. `universal/` (WORKING_STYLE 187L very-long-lines, CODING_PRINCIPLES 106L, MONITORING 155L, PATTERNS 17L, CHANGELOG 406L), `concepts/` (`_INDEX`, `_RELATIONS`, 9 domains), `projects/` (`_INDEX` + 6 project folders), `crossref/` (BY_TOPIC, BY_PATTERN), `SESSION_LOG` (278L), `MAINTENANCE_BACKLOG` (empty), `PERMITTED_DESTRUCTIVE_ACTIONS` (fail-closed ledger, no active grants).
- **`memory-pre-warm-reset-20260614-150919/` (7 files, ~1000L):** deliberate rollback snapshot. Not injected. Dead weight but intentional.
- `COLLABORATOR_GUIDE.md` (140L), `mandates/` (README + multi-project.md 203L, executed).

### Quality assessment
This is an exceptionally dense, disciplined memory. Directives carry Goal/Evaluate/Act + reinforcement counts + provenance. Concept graph has one-hop index + typed relations. Evidence-status discipline enforced. **The bar for change is high** — most content is near-inviolable (learned behavior, human corrections, single-instance grounding). Leanness wins are scarce and mostly ASK-gated (they touch always-read provenance).

### Candidate findings (pre-framework; refined after subagents + framework)
1. **[AUTONOMOUS, high value] `reference/_INDEX.md` missing.** 22 large read-on-demand files, no index. A cold AI told "pull a `reference/*` on demand" must already know the filename. `.mdc` "See also" blocks reference some inline, but there is no one-stop discoverability map. Additive hub + back-links = squarely in autonomy envelope. **Primary measured-win candidate.**
2. **[ASK] Always-read header changelogs.** `WORKING_STYLE.md` + `CODING_PRINCIPLES.md` open with ~20–30 lines of dense `Previous:` provenance duplicating `universal/CHANGELOG.md`, paid on every session-start read. Compaction to a short pointer would improve session-start leanness — but it is provenance (near-inviolable) → propose, don't enact.
3. **[ASK/verify] `memory-pre-warm-reset-…` snapshot** — could be archived out of the rules tree; deliberate rollback ref → propose only.
4. Pending inventory subagent: dangling refs, per-project stale/oversize logs, concept `_INDEX`/`_RELATIONS` mismatches (additive/corrective fixes autonomous where clearly net-positive).

### Reference integrity
- Baseline manifest `baseline/hash-manifest-head.txt` (77 files, shasum). Re-verify at every milestone; unexpected drift on an untouched file = HARD STOP.

---

## Harness (DE-RISKED — smoke test PASSED 2026-09-15)

- Permission: human authorized me to edit `~/.cursor/permissions.json`; added a 3rd allowlist entry naming my `harness/run_probe.py` copy + interpreter `flow/bin/python`. JSON validated (3 entries).
- `CURSOR_API_KEY` present in env (len 69, login shell too). Harness reads it from env.
- Invocation shape: `Shell(required_permissions:["all"])` running `flow/bin/python harness/run_probe.py --rules <RULES_TREE> --setting project --model auto --prompt "..."`. Runs OUT of sandbox (temp dir under /var/folders + SDK network); auto-review does not block (allowlisted).
- **Smoke test result:** staged the current TARGET tree; cold agent read `04-multi-project.mdc` + globbed `memory/**/*`, then correctly cited M5 read-order and named `04-multi-project.mdc` as SoT. Tool-call observation works (we see which files it opens). ~25s/run.
- **Baseline data point:** read-order discoverability already strong (straight to the authoritative file, no thrash). Measured wins will therefore come from the *weaker* corners — esp. the un-indexed `reference/` layer.

## Open asks (surface to human)
- _A1 resolved_ (permission granted + harness working).
- Pending: PROPOSED-not-enacted list will accumulate for final human review (ledger § Proposed-but-not-enacted).

## Phase I integrated findings (subagents returned)
- HA method distiller: confirms my framework verbatim (`Discoverability > Fidelity(soft) ⟂ Leanness ≈ Relations > Distillation > Maintainability`), paired-delta, additive-first, calibrate→skeleton→fill→close→surface. A–G decisions carry as defaults. Gotchas: permissions wall (handled), stale keys (built fresh), SDK drift (smoke-tested OK v1.0.28), probe-shape mismatch, reference-drift hard-stop.
- Inventory: `reference/` no index + `07-meta-learnings` true orphan (0 inbound) + `02-interaction-style`/`11-multi-project-bootstrap` hub-only orphans + 6 weak named files. `concepts/_INDEX` missing the `circup` concept. `bamboo-lamp/CONTEXT § R-6` stale (symlink dropped 2026-07-15). exp14 CONCLUSIONS 78-vs-137 (dated row — hold). Session-log compaction candidates (propose, user-gated).

## Enactable set (PLAN-v1)
- **ENACT (autonomous):** C1 `reference/_INDEX.md`; C2 back-links from always-read non-`.mdc` files; C3 `concepts/_INDEX` circup line; C4 bamboo R-6 staleness correction (preserve history).
- **PROPOSE (held):** P1 anchor index from `00-memory-system.mdc` (ask-gated); P2 session-log compaction; P3 exp16 CONTEXT header trim; P4 exp14 78→137 note; P5 reference/* boilerplate dedup; P6 concepts/_INDEX skeleton tightening; P7 shrink promoted exp16 CONCLUSIONS rows.

## Measurement design insight (crux)
- P13–P16 targets are ALREADY reachable via injected `.mdc` See-also / `WORKING_STYLE` rows → they are CONTROLS (expect FLAT). The index's real win is for the **orphans** → new probes **P19 (07-meta-learnings), P20 (02-interaction-style)** are the DISCRIMINATING set; reachable in candidate tree only via `reference/_INDEX.md` anchored from always-read central `SESSION_LOG` (C2). Prior arm should MISS them — validating this empirically before applying C1/C2.

## Cold-path orphan enumeration (mechanical, 2026-09-15 — supersedes eyeballed buckets)
Grep each `reference/*.md` basename against the **cold-path set** = 6 `.mdc` + always-read memory (`WORKING_STYLE`, `MONITORING`, `CODING_PRINCIPLES`, central `SESSION_LOG`, `projects/_INDEX`, `concepts/_INDEX`). A file is a **cold-path orphan** iff zero inbound from that set (reachable only via the new index or off-cold-path `COLLABORATOR_GUIDE`).
- **True cold-path orphans (exactly 3):** `02-interaction-style.md`, `07-meta-learnings.md`, `11-multi-project-bootstrap.md`.
- **Corrections:** `09-recursive-learning.md` is **reachable** (← `MONITORING.md`), NOT an orphan (critique's eyeball wrong). `11-multi-project-bootstrap.md` **IS** an orphan (only inbound = off-path `COLLABORATOR_GUIDE.md`; PLAN-v1's bucket wrong). Vindicates the critique's "enumerate, don't eyeball" (F3).
- **Consequence:** discriminating probe set = **P19/P20/P21** (one per orphan). P13–P16 = controls (already cold-reachable).

## Critique integration → PLAN-v2 (2026-09-15) — from [Critique the lifecycle plan](34492db0-2c0f-4918-8b0b-84a735b90a5b)
Two decisive fixes (they mask each other — must ship together):
1. **Probes were unmeasurable:** P13–P16 saturated (prior already reaches). FIXED: discriminating set re-pointed to the 3 true orphans (P19/P20/P21); P13–P16 kept as controls; FLAT-on-controls pre-registered as expected.
2. **Index not cold-reachable without ASK-gated P1:** FIXED with an **autonomous** anchor the plan missed — a See-also line in a *non-foundational* always-injected `.mdc` (`01-interaction-style.mdc`; only `00`/`04`/`06` are ASK-gated). Now **C2a** (01 See-also) + **C2b** (central `SESSION_LOG` bullet → explicit index pointer). P1 (00 anchor) stays PROPOSE.
Three secondary fixes: **C1** now carries a `provisional`+watch-for marker (its own `10-adaptive-memory-structure §7` discipline) and drops drift-prone inbound-status from the durable artifact (F10). **C4** constrained to strike-through/annotate-in-place preserving the R-6 PASS verbatim, attributed to the *design decision* (symlink removed 2026-07-15), never recharacterized as a test failure (G-FIDELITY hard tier). **C3** to summarize the concept's own framing, not the probe's wording.

## iter4 — all 8 held proposals enacted after Alex's approval (2026-09-15)
Alex approved P1, P2, P-prov, P3, P4, P5, P6, P7. Executed risk-ascending, one commit each; all lossless (additive / annotation / verbatim relocation / claims-coverage-verified compaction; git-recoverable).
- `4c10a3b` **P1+P3+P4**: 00 See-also index anchor (+ index footer records the now-enacted 00-anchor); exp16 `CONTEXT.md` header → compact digest (chrono detail deferred to § Resumption/SESSION_LOG); exp14 `CONCLUSIONS.md` 78→137 annotation (2026-04-17 evidence kept verbatim).
- `e5b5344` **P5**: dedup 22× `reference/*` boilerplate → `_INDEX.md` header; per-file 1-line comment keeps unique source path + notes. −145L. Fail-safe skip-on-no-match script; all unique notes preserved.
- `e7fd3a2` **P-prov**: `WORKING_STYLE.md`/`CODING_PRINCIPLES.md` inline `Previous:` stacks → verbatim into `CHANGELOG.md § 2026-09-15 — relocated directive-header provenance`. HARD GATE + schema kept in place. −62 always-read lines.
- `f16621f` **P6**: re-skeletonize 5 drifted `concepts/_INDEX.md` bullets; detail verified present in `circuitpython-runtime.md`/`tooling.md`/`nezha.md` before trim.
- `24b774e` **P7**: 4 exp16 `CONCLUSIONS.md` rows → link-to-`concepts/*` + exp16-specific claim; Evidence column (byte-exact sizes, GPIO tables) intact.
- `1c7132c` **P2**: exp16 SESSION_LOG S1–9 planning cluster → thin index (−116L, outcomes verified in CONTEXT/CONCLUSIONS/concepts); exp14 dormant → only S1 thinned, **S2–9 retained** (meta-directive derivation provenance; rationale in its living summary).
- **Integrity close:** `git diff --stat 8c4151b` = 38 files, all intended (C1–C5 + P1–P7 + P-prov + the same-session `ai-tooling/SESSION_LOG.md` entry); working tree clean; added pointers (`reference/_INDEX.md`, `CHANGELOG §` heading) all resolve; ~39 untouched baseline files unchanged.

## Follow-up pass — P8 + central-log thin + final measurement (2026-09-15)
Alex requested 3 items after reviewing the "outstanding todos" assessment.
- `b1715bf` **P8 — compact always-read `MONITORING.md`**: relocate dated header provenance verbatim → `CHANGELOG § 2026-09-15 — MONITORING.md compaction`; merge two entries for one `[user]` pattern (Exp16 `ai-notes/` [already Closed] + `.kilo/`) → one *Local tool/agent state* entry. Schema + all active banked triggers untouched (Alex's "keep active triggers").
- `0989c5f` **thin central `SESSION_LOG.md`** (279→218L): warm-reset cluster Sessions 10–12 → index block; living summary / SoT map / recent sessions / Session 13 / RESOLVED block verbatim. Durable homes verified present first. `a2696ab` = CHANGELOG provenance for this + the P2 project-log thinnings.
- **Final paired probe** (`eval/iter-final/run.sh`, `VERDICT.md`): prior `8c4151b` vs candidate final HEAD, 6 probes × 2 arms, all `finished`. Prior tree = `git archive 8c4151b:ai-persona/.cursor/rules` (77 files); candidate = live HEAD (71). Result: **no discoverability regression** on the 3 compacted always-read files (R1 MONITORING / R2 concepts/_INDEX / R3 central SESSION_LOG all still HIT); `reference/_INDEX.md` **consulted as directed hub** on all 3 orphan probes (absent in prior); raw REACH saturated both arms (as pre-registered — `auto` is a strong navigator, so gains = directness + no-regression, not raw reach). Closes the iter4-unmeasured gap.

## Decision log
- 2026-09-15: Operating model = live edits on branch `alex/ai-persona-maintanance` + git checkpoints (per prompt §2). Harness = running (not blind).
- 2026-09-15: Fidelity baseline pinned at cycle-start HEAD `8c4151b` (not branch fork point).
- 2026-09-15: exp14 78-vs-137 test count held as PROPOSE (dated evidence row within audit-ledger carve-out; changing risks twisting historical evidence, ask-trigger b).
- 2026-09-15: Adopted autonomous non-foundational `.mdc` anchor (C2a in `01-interaction-style.mdc`) instead of relying on ASK-gated P1 — keeps the primary discoverability win inside the autonomy envelope.
