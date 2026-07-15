# Pre-design considerations & research agenda (v1, 2026-07-15)

Purpose: the **first high-level overview of what must be considered and researched before designing the tutor**. Seeded
from one source (the Scheiter *They Talk Tech* episode — digest: `../digests/scheiter-they-talk-tech_digest.md`) plus the
project picture (`01_project-picture.md`) and the exemplar-tutorial techniques
(`../digests/exemplar-tutorials_pedagogy-and-stack_digest.md`). It is deliberately **considerations + open questions**, not
a design. Expect it to grow and reshape as more sources are ingested.

Status convention: each consideration tagged `[grounded]` (supported by an ingested source), `[hypothesis]` (plausible,
not yet evidenced), or `[project-constraint]` (given by Alex). Research items are prioritized P1 (needed before design) /
P2 (needed early in design) / P3 (deepening).

---

## A. Framing insight — the project's core requirement is a *known-hard* research problem
The single most useful takeaway: an independent domain expert who has actually **built** a tutorial-dialogue system on an
LLM confirms that our central requirement — *don't hand over the solution; ask clever questions instead* — is genuinely
hard, and names the exact failure modes we'll hit. `[grounded]`
- Off-the-shelf LLMs are trained to be **sycophantic / confirming** (commercially, to bind users); this is structurally
  opposed to good tutoring and must be actively **system-prompted away**. `[grounded]`
- Even when suppressed, two failure modes recur: (1) staying **polite while being honest** ("that wasn't brilliant yet"),
  (2) falling into **endless follow-up-question loops** for lack of *didactic instinct* (when to stop, when to switch
  tack, when to change route because the learner is stuck). `[grounded]`
- This is a direct, external match to Alice's **social-engineering** risk and the **shallow-transfer** risk from the
  project brief. Implication: budget real design + evaluation effort here; do not assume prompt-tuning alone suffices.

## B. Considerations for tutor behavior (what to get right)

1. **Think-first-then-AI ordering.** `[grounded]` Sequence matters: independent cognitive work *first*, AI for
   revision/refinement/formatting *after* (brain-first groups benefited; AI-first groups produced less and worse). Maps
   onto the tutoring contract (Alice owns the algorithmic solution). *Consider*: enforce an "attempt before assist"
   gate for algorithmic work; let AI freely help on the giveaway layer (env/interpreter/IDE/Python-syntax) at any time.
2. **A reflection phase after assisted work.** `[grounded]` (a) review the collaboration (when did I accept vs. reject
   the tutor's input?), (b) an **unaided retry** of the task or a *genuinely different* variant. The unaided-retry is
   also our anti-shallow-transfer instrument — it must not be a rename of the just-seen solution.
3. **Confidence is not a progress signal.** `[grounded]` Illusion of understanding + novice overconfidence mean Alice's
   "yes I get it" is unreliable, especially early. *Consider*: measure progress via **unaided transfer probes**, not
   self-report or "did that make sense?" check-ins.
4. **Self-regulated learning [SRL] / metacognition as the backbone.** `[grounded]` Repeatedly prompt "what do I already
   know? what are my next steps?" (monitoring + regulation), **embedded in the concrete task**, not taught as a detached
   framework. Candidate backbone for the "track the three prime skills" requirement. Caveat: struggling learners lack SRL
   and default to copy-paste, so the tutor cannot *assume* self-regulation — it must scaffold and gradually fade it.
5. **Productive struggle must be preserved (and felt).** `[grounded]` The reward of overcoming an obstacle (pride,
   self-efficacy) is what sustains persistence; removing the obstacle removes the reward. *Consider*: calibrate challenge
   to "manageable uncertainty" (matches the exemplars' mini-challenge design and Alice's temperament) — hard enough to
   earn the win, not so hard she disengages.
6. **Honest, polite, non-flattering register.** `[grounded]` + `[project-constraint]` Converges with the brief's "Alice
   dislikes being sucked up to." The tutor must be able to say "not yet right" kindly and mean it.
7. **Understanding the problem vs. solving it.** `[project-constraint]` Help generously with comprehension of the task;
   protect the solution as Alice's work. *Open*: an operational test to classify a given Alice-question into
   "understanding" vs "solution-seeking" in real time (this is where social-engineering attacks land).
8. **Factual/base knowledge still matters.** `[grounded]` Can't reason without content in your head. For us: Alice needs
   genuine command of core CircuitPython + hardware concepts (events, state, sync/async), not just the ability to prompt
   for them. Distinguish *must-internalize* vs *fine-to-look-up* per concept.
9. **Learning-by-explaining (reverse tutoring).** `[grounded]` Have Alice explain her approach to a deliberately
   naive listener; explaining forces understanding and models the audience's knowledge state. The lighthouse
   *reflection worksheet* already does a paper version of this — a live analogue is promising.

## C. Considerations for tutor architecture / mechanism (how to build it)
- **Hybrid LLM + rule-based logic** rather than a free chatbot. `[grounded/hypothesis]` Scheiter's bet: LLM language
  power + ITS-style hand-encoded didactic rules (diagnose learner state → choose next move: example? second task? what
  complexity?). *Open (Q2/Q3)*: how much rule-structure do we need vs. can we get with a strong system prompt + explicit
  state tracking?
- **Explicit learner-state tracking.** `[hypothesis]` The tutor should maintain a running model of the three prime
  skills + per-concept mastery, updated from unaided-probe evidence — this is the "track continuously" requirement made
  concrete, and it is *not* something an LLM does on its own.
- **Anti-gaming as an explicit mechanism, not just a prompt.** `[hypothesis]` Given B/A above, consider structural guards:
  attempt-gates, a solution-withholding policy the tutor cannot be talked out of, toy-problems that require a genuine
  conceptual step (not a rename), and detection of "salami-slicing" question chains.

## D. Where the exemplars already embody good practice (reuse, don't reinvent)
The two MakeCode tutorials already implement several grounded principles — useful design capital: scaffolded
**mini-challenges** (manageable struggle), **"your turn" decision points with a branch per answer** (productive
reasoning, not answer-delivery), per-section **Check/Self-test** (monitoring), **decision tables + reflection worksheets**
(externalize logic; learning-by-explaining), **deliberate bugs** (diagnosis practice), explicit **transfer tasks**
(lighthouse reuses feeder). The gap: they are *static documents* built slowly with Alex in the loop; the tutor must do
this *live and interactively*, which is exactly where anti-gaming becomes a per-turn concern.

---

## E. Research agenda (locate + read primary sources before/at design time)

**P1 — before designing:**
1. **Scheiter's own tutorial-dialogue-system work.** She says "we tried to build a system that engages the learner in a
   tutorial dialog." Find these publications (Potsdam / Leibniz-IWM Tuebingen); extract what worked, what failed, how they
   suppressed sycophancy and handled the question-loop problem. Highest-value single lead.
2. **"Your Brain on ChatGPT" study** (small-n EEG essay study). Get authors, exact design, and the *reversal* result
   (brain-first vs AI-first). Confirm the "AI-first hinders subsequent independent thinking" claim and its limits.
3. **Intelligent Tutoring Systems [ITS] fundamentals + LLM-hybrid state of the art.** How ITS encode "diagnose state →
   next didactic move"; current LLM+ITS hybrids. (Search terms: intelligent tutoring systems, cognitive tutors, model
   tracing, LLM tutor guardrails, "Socratic" LLM tutors.)
4. **Programming-education-specific pedagogy for children/novices with prior experience.** Scheiter flags programming as
   *especially* hard to teach without AI — our exact domain. Novice-programmer misconceptions; transfer in programming;
   PRIMM / Use-Modify-Create / worked-examples-with-fading for code; block→text transition.

**P2 — early in design:**
5. **Self-regulated learning [SRL] & metacognition frameworks** (monitoring & regulation; how to embed, scaffold, and
   *fade* them). Practical instruments suitable for a 12-year-old.
6. **Desirable difficulties & productive failure** (Bjork; Kapur) — calibrating "manageable uncertainty."
7. **Self-explanation & learning-by-teaching / teachable agents** (Chi; protégé effect; Betty's Brain) — grounding the
   reverse-tutoring idea and worked-example use.
8. **Overconfidence / metacognitive calibration in novices** (Dunning-Kruger; expert judgment of "what I know") — to
   justify not trusting self-reported understanding.

**P3 — deepening:**
9. **Cognitive load theory & multimedia learning** (Sweller; Mayer) — Scheiter's home turf; relevant to how much the
   tutor should explain/show at once (also connects to the exemplars' heavy use of figures).
10. **"Metacognitive laziness" / AI-reliance recent literature** — is the offloading effect measured; mitigations.
11. **Delay-of-gratification** nuance (marshmallow replications; the affluence critique) — light; mostly a motivation lens.

---

## F. Open design questions this overview raises (feed back into `03_open-questions-todos.md`)
- Q3 (measure the 3 skills): candidate = unaided transfer probes + explicit learner-state model updated from them; needs
  concrete probe designs per skill (translate / critique / transfer).
- Q2 (architecture): LLM-only-with-strong-prompt vs. LLM+rule-based hybrid — decide after research P1.1 & P1.3.
- New: how to operationally classify an Alice-turn as "understanding the problem" vs "seeking the solution" (the
  anti-social-engineering decision boundary).
- New: which CircuitPython/hardware concepts are *must-internalize* vs *fine-to-look-up* (needs Q1: the actual API).

## Cross-references
- Detailed source digest: `../digests/scheiter-they-talk-tech_digest.md`
- Project picture / prime goals / anti-gaming: `01_project-picture.md`
- Open questions register: `03_open-questions-todos.md`
- Exemplar pedagogy + stack: `../digests/exemplar-tutorials_pedagogy-and-stack_digest.md`
