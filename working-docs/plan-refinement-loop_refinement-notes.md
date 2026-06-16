# Notes — transcript-coverage check + refinement of `plan-refinement-loop.md`

Consumer: AI only, dense (cold-AI applied to these notes). **Provenance**: crawl of this chat's transcript
`…/agent-transcripts/73251650-16c3-43ea-b176-951b86b300d8/73251650-16c3-43ea-b176-951b86b300d8.jsonl` (14 user turns),
done 2026-06-15 per USER#14. **Task**: compare important feedback given here on the warm-reset `_META.md` (the
exemplary instance) + the generalization request, against `~/Developed/AI/generalized-agent-learnings/plan-refinement-loop.md`
as first written 2026-06-15; record gaps; then refine the process doc, applying `Effective Behavioral Guidelines.md`
(EBG) + `cold-ai-paradigm.md` to the doc itself. The process doc is conceptually a generalized, template-driven plan,
so this is one pass of its own loop (review → notes → apply).

## Coverage matrix (feedback → location in doc → verdict)

| Feedback (transcript src) | In `plan-refinement-loop.md`? | Verdict |
|---|---|---|
| Draft v0.0 into a pre-made file; iterate (USER#5) | §3.2 versioning, §3.3 loop | COVERED |
| Iteration start = `cp` prior plan → new file, increment version only (USER#5) | §3.3 step 1 | COVERED |
| Per-iter review vs cold-ai + flexible-plans; versioned notes (same version #); compact "what+how" change descriptions; apply cold-ai to notes (USER#5) | §3.3 step 2, §3.4 R1/R2, notes discipline | COVERED |
| Compare-to-prior: focused / all context / not bloat; append to same notes; cold-ai (USER#5) | §3.4 R3 | COVERED |
| Notes are AI-only → detail-dense, cold-ai (USER#5) | §3.1, §3.3 step 2 | COVERED |
| Need a meta-plan (USER#5) | whole doc generalizes it; §1 names it internally | COVERED |
| Preliminary analysis → a distilled design rubric as standing input (USER#6) | §2 adapt, §3.1 (Design rubric optional), §8 | COVERED |
| Per-iter: plan must stay adaptive to evolving info; soft-parsimony; PRIORITY cold-AI retrieval (topic+detail) (USER#6) | R1 (adaptivity) + memory example; parsimony/retrieval is instance-specific → rubric | COVERED (instance specifics correctly delegated) |
| 3 reviews — beneficial order? → substance→form→economy (USER#6) | §3.4 order + rationale | COVERED |
| Convergence at diminishing returns; notes hold depth+breadth change summary (USER#7) | §3.5 Change-Magnitude, §3.6 | COVERED |
| Hard upper bound (5 iters) → generalize to "ask the user for the cap" (USER#7→USER#11) | §2.1(1), §3.6 | COVERED (correctly generalized to user-set) |
| Post-loop: copy final → v1.0 (USER#7) | §3.7 step 1 | COVERED |
| Post-loop: scan all notes for riskiest items NOT settleable by executing the plan; flag MISSING (USER#7) | §3.7 step 2 | COVERED |
| Self-contained; reference-not-duplicate; cold-AI reads context first (listed floor, more encouraged) then executes (USER#8) | §6 | COVERED |
| Sub-agents: composer-2.5 crawl / Opus 4.8 reason; self-audit technique; precise deliverable expectations; develop-during-exec; experiment log (USER#8) | §5, §3.1 | COVERED |
| Sub-agents: if significantly useful, INFORM user (API cost); composer-2.5 vs opus-4.8 (or newer) = extraction vs reasoning/distillation (USER#11) | §5 Cost gate | COVERED |
| Engrain higher-level reflection + self-monitoring of progress + self-adaptation (USER#11) | §4 | COVERED (strengthen: see G1) |
| Iterative; user-set hard cap; location; brief naming-convention confirm; adapt to goal (USER#11) | §2 | COVERED |
| Don't over-expose "meta-plan"; frame as internal autonomous iteration (USER#11) | §1 communication discipline | COVERED |
| Present as blueprint; heuristics-not-laws; deviate on good (non-conclusive) reasoning within limits (USER#11) | §3 title, §7 | COVERED |
| Run loop in a separate cold-AI chat via referencing-not-copying kickoff prompt (USER#9) | not in doc | GAP → G4 |
| APPLY EBG to the doc itself (USER#14) | partial | GAP → G1,G2,G3,G5 |
| APPLY cold-ai to the doc itself (USER#14) | §9 self-test present | COVERED (strengthen falsifiability: G3) |

## Gaps → refinement actions (apply to `plan-refinement-loop.md`)

- **G1 (EBG "reflect audibly at checkpoints" + USER#11 self-monitoring)**: the loop computes a convergence verdict
  (§3.5) but never mandates *stating* it. EBG: silence masks skipped reflection — same from outside, compounds drift.
  → §3.3 step 5 + §3.6: at every iteration close state, in the notes (and only at the §2/§3.7 surfacing points to the
  user), either "here's what I'd revise" or "nothing changes, continuing". Why: makes self-monitoring observable, not
  assumed.
- **G2 (EBG anti-over-prescription)**: the blueprint reads as procedure (`copy → review → apply`); EBG flags
  `always/step-1` shapes. The shape is a legitimate niche (mechanical + repeatedly-reinforced) BUT must be framed as
  illustrative shape protecting targets, adaptable per §7. → add one line at §3 intro: the steps are illustrative shape;
  the load-bearing commitments are the *targets* each serves; adapt shape per §7. Why: keeps the rule ageing well.
- **G3 (cold-ai §7 recursive + EBG falsifiability)**: §9 says "revise if it mis-fits" but gives no recognisable
  signal — an unfalsifiable self-claim. → add to §9 concrete refute-signals: (a) instances deviate on the *same* point
  repeatedly → fold the deviation into the blueprint; (b) convergence never trips before the cap across multiple
  instances → the change-magnitude criterion is miscalibrated. Why: makes the blueprint's own adequacy cold-AI-testable.
- **G4 (USER#9 handoff capability)**: an instance may hand the loop to a fresh cold-AI chat via a referencing-not-copying
  kickoff prompt — enabled precisely by the §6 onboarding requirement. → add a sentence at §6. Why: documents a real,
  used capability (the warm-reset instance did this).
- **G5 (EBG "contradictions have no default winner" + inherited-specs-are-adaptable-priors)**: this blueprint is itself
  an inherited spec a future instance applies; when it (or an inherited template/mandate the plan operationalizes)
  conflicts with the live situation, treat it as an adaptable prior — present both sides, the authority decides, retain
  the losing side with a dated note. → add a bullet to §7. Why: prevents both blind compliance and blind override.

## Non-actions (deliberate)
- Parsimony-vs-retrieval tie-breaker + topic→detail one-hop retrieval (USER#6) stay *instance-specific* to
  memory-structure plans → live in the design rubric / §8 example, NOT hoisted into the general R1. Hoisting would
  over-fit the general process to one problem class.
- The literal "5 iterations" cap (USER#7) stays generalized to "ask the user" (USER#11 superseded the literal with
  "request hard limits from the user"). Correct as-is.

## Second pass (Alex, parsimony/economy tension)

- **G6 (plan economy model)**: doc had anti-bloat (R3) + right-sizing (§2) but NOT (a) plan-bloat < memory-bloat
  asymmetry (memory = retrieval-efficiency > parsimony, loaded every session; plan = task-scoped, leaner still by
  default), (b) leanness buys flexibility = less surface to over-prescribe / over-harness, (c) leanness is safe *only
  because* reflection/monitoring/adaptation are explicit and carry what a fat plan pre-specifies → commit fixed layer
  (targets/constraints/checkpoints/the loop), leave shape open, derive at checkpoint. → new §3.8 + R3 cross-ref + R3
  trim test ("load-bearing for a target/checkpoint, or pre-committed shape execution can deduce?"; never trim the
  reflection/adaptation expressions). Notes-economy clarified: per-version notes aren't carried as live context (only
  the risk scan reads all) → notes don't tax later iterations; only the plan is kept lean.

## Applied
G1 ✓ · G2 ✓ · G3 ✓ · G4 ✓ · G5 ✓ — `plan-refinement-loop.md` §3, §3.3, §3.6, §6, §7, §9.
G6 ✓ — §3.8 + §3.4 R3.
