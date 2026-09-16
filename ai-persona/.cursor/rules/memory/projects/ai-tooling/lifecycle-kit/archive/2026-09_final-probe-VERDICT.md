# Final paired probe verdict — prior (`8c4151b`) vs candidate (final HEAD)

Run 2026-09-15 via `run.sh` (12 runs: 6 probes × 2 arms; `flow` venv + cursor-sdk, `--setting project --model auto`, staged rule-tree copies out-of-workspace). All 12 runs `finished` (no errors). Raw traces: `{prior,cand}_<probe>.txt`. Prior tree = `git archive 8c4151b:ai-persona/.cursor/rules` (77 files, no `reference/_INDEX.md`); candidate = live final HEAD (71 files = 77 − 7 removed warm-reset snapshot + 1 index).

## Scoring — did the cold agent OPEN the expected-reach file(s), and via what route?

| Probe | Target (primary) | prior reach | cand reach | Route delta |
|---|---|---|---|---|
| **P19** meta-learning lessons | `reference/07-meta-learnings.md` | HIT (glob/guess; no index) | HIT | **cand also consults `reference/_INDEX.md`** as hub |
| **P20** deep interaction-style ref | `reference/02-interaction-style.md` | HIT (no index) | HIT | **cand routes via `reference/_INDEX.md`** |
| **P21** multi-project bootstrap record | `reference/11-multi-project-bootstrap.md` | HIT (no index) | HIT | **cand routes via `reference/_INDEX.md`** |
| **R1mon** ai-notes/.kilo gitignore guidance | `universal/MONITORING.md` (merged entry) | HIT | HIT | no regression from P8 merge |
| **R2idx** circup version-pinning | `concepts/_INDEX.md` + `concepts/tooling.md` | HIT both | HIT both | no regression from P6 tighten |
| **R3log** 2026-06-14 warm reset record | central `SESSION_LOG.md` + `CHANGELOG.md` | HIT both | HIT both (leaner: went straight to the two) | no regression from log thinning |

## Findings

1. **No discoverability regression from any lifecycle compaction.** All three regression probes (R1/R2/R3) targeting the files this lifecycle compacted — `MONITORING.md` (P8 merge), `concepts/_INDEX.md` (P6 tighten), central `SESSION_LOG.md` (warm-reset cluster thinning) — still reach the same primary target file(s) in the candidate arm. The compactions relocated/condensed content without breaking retrieval. R3 candidate was actually *leaner* (opened only `SESSION_LOG.md` + `CHANGELOG.md`, following the thinned cluster's pointer straight to the authoritative home).

2. **`reference/_INDEX.md` is live and used as a directed hub on all three orphan probes** (P19/P20/P21) — consulted in the candidate arm, absent in prior. This is the primary structural win of the lifecycle.

3. **Raw REACH is saturated (both arms HIT everything) — as pre-registered.** The `auto` model is a strong navigator (globs `reference/`, guesses filenames), so the metric ceilings on raw reach; the measurable candidate gains are **route directness + hub consultation + no-regression**, exactly the `directness/precision/robustness, not raw reach` outcome the measurement design predicted (`../../harness/probe-pool-v1.md § Measurement design`; `../../EXPERIMENT-LOG.md § Critique integration`). A stronger discriminator would need a weaker model or a filename the model cannot guess; not worth the run given the clean regression result.

## Bottom line
Final HEAD is **safe to keep/merge**: the iter4 + P8 + central-log-thinning compactions demonstrably did not degrade discoverability of the compacted content, and the `reference/_INDEX.md` hub is exercised as intended. Verification gap (iter4 compactions were unmeasured) is now closed.
