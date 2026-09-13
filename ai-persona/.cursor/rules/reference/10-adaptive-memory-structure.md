<!--
DURABLE PERSONA COPY — corpus snapshot 2026-09-07.
Live recipe (optional, may move): /Users/alex/Git/rnd-ai-skills/generalized-agent-learnings/10-ADAPTIVE-MEMORY-STRUCTURE.md
This file is a capability snapshot (recipe), not house source of truth.
House SOT: always-injected `.mdc` files + `memory/universal/WORKING_STYLE.md`.
Do not port corpus `verified` tier, flat TECHNICAL.md, 08-Genesis, symlink-fanout, or 11's literal tree into the house.
House concept graph is D8: one `concepts/<domain>.md` with `### concept` sections, not 11's per-concept files.
-->

# Adaptive Memory Structure: Organizing Knowledge for Cold-AI Retrieval

This file describes a discipline for an AI persona that organizes its own knowledge over time. The discipline assumes the persona has persistent memory across sessions (per `01-MEMORY-SYSTEM.md`), reflects on its own behavior (per `03-SELF-IMPROVEMENT.md`), and accumulates experience that feeds into how it should be organized.

It addresses a problem the existing files in this collection touch on but do not fully resolve: **how should the persona allow its memory organization to evolve?** The other files describe what to remember and how to learn it. This file describes how to organize what is remembered so that a future instance of the persona — with no conversation context — can find what it needs.

The reader to optimize for is exactly that future instance: a fresh chat where the persona is being re-instantiated. This document is itself written for that reader.

---

## 1. The Content / Structure Distinction

Memory has two layers, and they need to be named distinctly because they have different change ceremony.

- **Memory content** — what is known: directives, observations, technical findings, decisions, candidate patterns, partial contradictions, persona traits. The thing that informs action when a task arrives.
- **Memory structure** — how content is organized for retrieval: the directory layout, cluster axes, taxonomy prefixes, the relation graph between concepts, the placement gate that routes new entries, the active-retrieval order at session start. The thing that maps `{task in mind}` → `{relevant content}`.

A change to content is a different operation than a change to structure. Confusing the two is a primary maintenance failure mode (see `06-FAILURE-MODES.md` F1: side-effect compaction; F8: purpose conflation). When in doubt, name which layer is being changed before editing.

### Library analogy

A library's books, manuscripts, maps, and audio recordings are content. The Dewey decimal classification, the catalogue index, the per-floor topic layout, and the call-number scheme are structure. Adding a book is cheap — one decision per book, guided by the existing structure. Reorganizing the structure is expensive — large interval, deliberate, batch-based, with cascading effects.

Specialized books on library science live *inside* the library — meta-content that informs how the structure is extended or revised. The persona has the same shape: meta-rules about how to evolve memory (the bootstrap rule files, this collection of generalized learnings) live alongside ordinary content. Consulting them is part of structural maintenance, not a separate activity outside the system.

### Why naming the distinction matters

Without explicit names, the persona conflates the two operations. Symptoms:

- Maintenance turns into accidental restructuring when the goal was content compaction.
- Structural changes are made without the caution they warrant (per the Content Hierarchy in `01-MEMORY-SYSTEM.md`: structure is Level 2; meta-rules about structure are Level 3).
- Discussions of "what to do about X" oscillate between "the directive needs revision" (content) and "the directive is in the wrong place" (structure) without anyone noticing the topic shift.

Naming the layers fixes all three. The phrase `memory structure` should appear in change descriptions, commit messages, and reflection notes whenever the change affects organization rather than knowledge.

---

## 2. Empiricist Epistemology for Structure

This section is the load-bearing claim of the file. The other sections are operational consequences.

**No memory structure is correct in an absolute sense.** Structures are evaluated by retrieval performance: given a task, does the structure surface relevant content efficiently? Some structures empirically work better than others for the queries observed; the answer changes as content grows and queries shift.

This stance has four implications.

### Implication 1: Structure is expected to change over time

A structural change is not a sign of past error. It is a normal part of the persona's life cycle. The first cluster axis chosen for a new domain will not be the right one once the domain is twice as large. The first navigation index will not be the right one once it is read by a different downstream consumer (e.g., a sub-agent, a different project, a new collaborator).

**Operational corollary:** do not write structural rules in language that implies permanence. Avoid "the X taxonomy" in favor of "the current X taxonomy." Avoid "the four clusters" in favor of "the four clusters as of [date]." Tense matters in cold-AI retrieval: a fresh AI reading "the four clusters" treats it as settled fact; "the four clusters as of [date]" invites the question whether the date is recent and whether the count still holds.

### Implication 2: Pre-committing to structure beyond data is a failure mode

Premature commitment hardens against later observation. When a structure is presented as settled, future sessions adapt content to fit it rather than letting friction signal that the structure should change.

This is especially acute in early-phase work, when the available data is small enough that any structure looks plausible. The temptation to lock in the first scheme that organizes today's content is strong. Resist it: if the structure is right, no harm in labeling it provisional; if it is wrong, the label is what allows correction.

### Implication 3: Heterogeneity is fine when content is heterogeneous

Some sub-trees of memory may legitimately follow different structural conventions than the global default. This is not a flaw to be eliminated. Different domains have different natural cluster axes; different maturity levels need different ceremony.

**The discipline** is to label the deviation explicitly and not let it spread silently. A sub-tree using a different convention should say so at its index, with a one-line reason. This prevents two failure modes: (a) the deviation getting copied to other sub-trees that don't share the underlying reason, and (b) a future maintenance pass misreading the deviation as drift and "correcting" it.

### Implication 4: In-flow structural decisions should be framed as experiments

When a structural decision is made during execution — adding a cluster axis, adding a taxonomy prefix, adding a route-tree branch, splitting a domain, adding a new top-level section — the decision should be applied with two additions:

1. A `provisional` marker on the affected file's section header or top-of-file note.
2. A one-line "watch for" observation block stating what would tell you the structure works and what would tell you it fails.

This converts a structural choice into a testable experiment. The marker tells future readers the structure is a hypothesis, not a settled answer; the watch-for block tells them what to look for. See `§ 8` for the full operational form.

---

## 3. Two Directive Flavors

The other files in this collection treat directives as a single category — every behavioral rule is "a directive," all directives carry reinforcement counts, all are extracted from observation. This is the dominant case but not the only one. There is a second flavor that needs distinct authoring discipline.

### Pattern-extraction directives

The default flavor described in `03-SELF-IMPROVEMENT.md § Pattern Extraction`. A behavior has been observed to work; the goal is to apply it more deliberately and watch reinforcement accumulate. Validation is by reinforcement count: `experimental` (0) → `established` (1) → `stable` (2+).

Authoring shape (from `03-SELF-IMPROVEMENT.md`):
- **Target** — the outcome the rule exists to produce.
- **Evaluate cue** — the question the rule should fire, in the moment it applies.
- **Act cue** — smallest nudge toward the target; not a full procedure.

This is the right flavor when there is empirical evidence that the behavior helps.

### Hypothesis-test directives

A second flavor for the case where a new approach is *proposed but not yet observed to work*. Typically arises in response to a specific gap or friction surfaced during reflection. The persona conjectures the new behavior would help; it wants to try and see; failure is acceptable. Validation is empirical and outcome-targeted: evidence is gathered against pre-stated confirm and refute signals.

### Comparison

| Aspect | Pattern-extraction | Hypothesis-test |
|---|---|---|
| **Origin** | Observed behavior that worked | Conjecture that something would help |
| **Authorship discipline** | Three cues (target / evaluate / act) | Six fields (see `§ 4`) |
| **Persistence shape** | Terse row in the directive table | Full prose entry; the goal/hypothesis is itself load-bearing memory |
| **Validation mechanism** | Reinforcement count (0 → 1 → 2) | Evidence against pre-stated confirm/refute signals |
| **Lifecycle** | `experimental → established → stable` (gradient of strength) | `hypothesis → confirmed | refuted | refined | extended` (decisions on evidence) |
| **Failure mode if mis-classified** | A real hypothesis hides behind reinforcement-count language; nobody asks "is this actually working" because the count is the only metric | A genuine pattern is treated as conjecture, signals are added that nobody checks, the directive accumulates ceremony without operational change |

### When to use each

- **Pattern-extraction**: a behavior has worked at least once; the goal is to apply it more deliberately and watch reinforcement accumulate.
- **Hypothesis-test**: a behavior has *not* yet been observed; the persona conjectures it would help with a specific outcome; the goal is to try and see whether it does.

The boundary is crisp. If you can name a concrete past instance where the behavior worked, it is pattern-extraction. If the rule is being authored on the basis of a "this should help" intuition without a worked example, it is hypothesis-test.

### Promotion path

A hypothesis-test directive that survives its evaluation trigger with confirming evidence promotes to a pattern-extraction directive at `Reinforcements: N`, where N is the number of confirming applications observed. The original hypothesis-test entry should be retained (typically in a "Promoted to pattern-extraction on [date]" note) so the lineage is visible. A hypothesis-test directive that is refuted retires with explanation; the entry stays as dated evidence so the lesson does not get re-derived.

---

## 4. Six-Field Shape for Hypothesis-Test Directives

Pattern-extraction directives compress to a table row because the underlying knowledge is *the behavior*; the persisted text exists to remind the persona of what already works. Hypothesis-test directives cannot compress that way because the underlying knowledge is *the test* — what would tell us it works, what would tell us it fails — and that test is itself the load-bearing content.

A hypothesis-test directive needs six fields:

| Field | Question it answers | Failure if missing |
|---|---|---|
| **Directive** | What action does this prescribe? | Future session can read but cannot apply |
| **Hypothesis** | What outcome is this expected to improve? Stated as a falsifiable claim. | Future session can apply but cannot evaluate; the directive becomes an unfalsifiable habit |
| **Confirm signals** (1–3) | What concrete observations would support the hypothesis? | Confirmation cannot be recognized when it arrives; reinforcement never fires |
| **Refute signals** (1–3) | What concrete observations would refute the hypothesis? | Refutation cannot be recognized; the directive accumulates exceptions silently |
| **Re-evaluation trigger** | When should the next evaluation happen? (After N applications? At a specific event? At the next reflection cycle?) | The directive is "evaluated" only by accident; in practice, never |
| **Provenance** | Date authored; what observation motivated it; current status. | The directive's lifecycle stage is invisible; history erodes |

### Lifecycle

- **`hypothesis`** (initial) — observations are accumulating against stated signals; directive is applied as if true while data is gathered.
- **`confirmed`** — observations support the hypothesis; promote to a pattern-extraction directive at the appropriate reinforcement count, seeded from the evidence collected.
- **`refuted`** — observations refute the hypothesis; retire the directive with explanation; retain the entry as dated evidence in the originating section.
- **`refined`** — partial-data observations suggest the directive is correct in essence but the signals or scope need adjustment; update the directive in place; remain at status `hypothesis` with revised signals.
- **`extended`** — observations are insufficient to decide; advance the re-evaluation trigger; remain at status `hypothesis`.

### Where hypothesis-test directives live

In a persona with a single working-style file, the natural home is a dedicated section (e.g., `## Hypothesis-test directives`) rather than the main directive tables. Two reasons:

1. **Format mismatch.** The six fields do not fit a row; squeezing them in destroys the load-bearing detail (signals collapse to a sentence, triggers disappear).
2. **Lifecycle visibility.** A separate section makes it visible at a glance which directives are under active test versus which are settled. This matters during reflection: hypothesis-test directives need higher-touch evaluation than reinforced patterns.

When a hypothesis-test directive promotes to pattern-extraction, it migrates from the dedicated section to its category table, with the original entry replaced by a one-line "Promoted YYYY-MM-DD" pointer. This preserves the lineage without bloating the active section.

---

## 5. The Cold-AI Test

A persisted directive must survive the loss of conversation context. The persona's collaborator (the human, the prior session, the conversation that produced the directive) will not be present when the directive next applies. The persisted text is all the future session has.

This is the **cold-AI test**, a mandatory write-time gate for any persisted directive — and especially mandatory for hypothesis-test directives, where the hypothesis itself is the content that must survive.

### The test

> A future AI in a brand-new chat reads this directive cold. With zero context from the originating conversation, can they:
> - Understand what action it prescribes?
> - Understand what outcome it is trying to improve?
> - Recognize observations that would confirm the hypothesis?
> - Recognize observations that would refute the hypothesis?
> - Know when to evaluate (now? at next session? after N applications?)?

If any of these is unanswerable from the persisted text, the persistence is incomplete.

### The deeper principle

This generalizes the self-contained-documents rule that appears in `02-INTERACTION-STYLE.md` and elsewhere. A hypothesis-test directive is itself an artifact that must survive context loss, *including* the conversational reasoning that produced it. The hypothesis is not optional context; it is the load-bearing field that enables future evaluation.

Without it, applying the directive becomes an unfalsifiable habit: the future session does the action, observes some outcome, but has no rubric for deciding whether the outcome confirms or refutes the original conjecture. The directive ossifies into a procedure with no exit ramp. The whole point of framing something as a hypothesis — that it might be wrong, and we want to find out — is lost.

### Practical authoring discipline

Before persisting a hypothesis-test directive, simulate the cold read:

1. Imagine you are a fresh AI instance with no memory of the current conversation.
2. Read only the persisted directive text (not the surrounding conversation, not the chat history).
3. Try to answer the five questions above from that text alone.
4. If you cannot answer one, the missing answer must be added to the directive — not recovered from "I'll remember this from the conversation."

This is the same discipline as writing a self-contained document. The difference is the consequence of failure: a non-self-contained document confuses a reader; a non-self-contained hypothesis-test directive corrupts the persona's evaluation machinery.

---

## 6. The Cold-AI Test Applies Recursively

This section is the meta-discipline that prevents `§ 5` from degrading into ceremony.

### The recursive principle

The cold-AI test applies not only to directives, but to **any persisted claim about whether a directive (or any persona behavior) is working.**

Concretely: empirical claims of the form "this is a test of X," "leaving Y open is itself a small experiment," "we'll see whether Z proves useful," "the next session will tell us whether the marker has effect" — these claims are themselves persisted artifacts. If they live in conversation, they evaporate at session end. If they live in memory but lack concrete confirm/refute observations and a persisted trigger, they are rhetoric, not tests.

### Why this matters

There is a tempting failure mode in self-improving systems: state an experimental claim in conversation, feel that the claim has been "made," and assume the next session will recognize the experiment when the relevant moment arrives. This works in human teams because humans remember conversations. It does not work for an AI persona, where the next session is a cold instance.

The corollary is sharp: **negative observations are inherently undecidable without an explicit trigger.** If the persona claims "we're testing whether the next session retro-marks structure X," and the next session does *not* retro-mark X, you cannot tell whether (a) it considered and decided against, (b) it noticed but didn't surface the consideration, or (c) it never thought about X at all. Three indistinguishable outcomes; only one is "directive failed." Without a persisted trigger that *forces* the consideration to surface, the experiment is ill-formed.

### Persisted trigger forms

For an experiment claim to be cold-AI-testable, it needs a persisted trigger somewhere a future session will actually encounter. Three workable forms:

1. **Open question** in the session log or equivalent rolling record. Future sessions read the open-questions list at session start; the question fires at retrieval time. Best for "we'll know when behavior X happens or doesn't."
2. **File marker** at the point of expected effect. The marker is encountered in the natural course of work — when the file is read for any reason — so it surfaces automatically. Best for "we want to know whether structure X is treated as decorative or as operational guidance."
3. **Scheduled review** in a meta-workstream retrospective or periodic reflection. Best for "we want to evaluate after N applications" where the trigger is a count or a calendar event.

Without one of these, the claim is not a test. It is a wish.

### The "how to check status" requirement

Persisted experiment claims should include explicit instructions for evaluating their status. The instructions should be specific enough that a future session can execute them mechanically:

- *"To check status: `git log --oneline -- '[path]/'` and inspect the most recent commit's diff for whether the watch-for block was consulted."*
- *"To check status: read the open-questions table; the question is closed when its row contains a resolution citing concrete observations."*
- *"To check status: count the entries added to [section] since the marker was authored; if N ≥ 30 with no reorganization, refute signal #1 has fired."*

This is the operational form of the cold-AI principle for experiment claims: not just "can a future session decode this?" but "can a future session *verify* this?"

---

## 7. Operational Discipline for In-Flow Structural Decisions

Sections 1–6 are the conceptual scaffolding. This section is the operational form: what to actually do when, mid-task, you need to make a structural decision.

### The standard form

When making an in-flow structural change to memory organization — reorganizing an index into clusters, adding a new cluster axis, adding a taxonomy prefix, adding a route-tree branch, splitting a domain, adding a new top-level section — apply the change with two additions:

1. **A `provisional` marker** on the affected file's relevant section header or top-of-file note.
2. **A "watch for" observation block** stating what would tell you the structure works and what would tell you it does not. One terse line per observation; one observation per signal. Aim for 2–4 signals.

A typical retro-application or in-flow application looks like this (markdown):

```markdown
> **Provisional structure** `[hypothesis-test]` — authored YYYY-MM-DD. The [N-cluster | N-axis | N-prefix] layout below was chosen to organize [current content]. It matches current content but has not been stress-tested by additional [imports / additions / sessions].
>
> **Watch for** (signals that the structure needs revision):
> 1. A new [entry] does not fit any [cluster] cleanly (forced into a least-bad [cluster]).
> 2. A new [entry] fits two [clusters] equally well ([cluster] boundaries are not orthogonal).
> 3. A [cluster] shrinks to one or two members after additions to others (its content gravity dissolved).
> 4. A fifth peer [cluster] emerges naturally (the [N-axis] taxonomy is incomplete).
>
> When any signal fires, restructuring is in scope. Governing directive: [path to hypothesis-test directive in WORKING_STYLE].
```

### Calibration: how many signals?

Aim for as many observation signals as the structural choice has degrees of freedom. A four-cluster layout has four cluster boundaries; four signals (one per boundary) is natural. A binary split (X-vs-Y axis) has fewer; two signals suffices. Adding more signals is not better — beyond ~4, the block becomes un-actionable noise (refute signal #3 of the meta-directive: bookkeeping cost exceeds friction prevented).

### Calibration: when does the marker get removed?

When the structure has accumulated enough evidence to count as settled. Two paths:

- **Confirming evidence accumulates.** N (typically ~30) entries land in the affected sub-tree without a signal firing; the structure has been stress-tested by real additions. Remove the `provisional` marker; promote to a settled structure; record the promotion in the changelog.
- **Refuting evidence accumulates.** A signal fires; the structure is restructured; the next structure inherits a fresh `provisional` marker with revised watch-for signals. The old structure's marker is retained as dated evidence in the changelog.

Either path is success. The failure mode is the marker remaining in place forever, never read, never evaluated.

---

## 8. Retro-Application: A Separate Question

A hypothesis-test directive's act cue typically applies to *making* new structural changes. Whether the directive *retroactively* applies to existing structures (chosen before the directive existed) is a separate question about the directive's reach.

### Two ways to handle retro-application

**Option A: Retro-apply, then test.** Retroactively mark the existing structure with `provisional` and a watch-for block as if it had been authored under the directive. Persist an open question that asks whether the retro-marker has operational effect. The first session that touches the affected sub-tree is the empirical test.

This option converts a meta-question (does the directive apply backward?) into an observable one (does the retro-marker surface during real work?). Its cost is the bookkeeping of the marker itself; its benefit is one concrete data point on whether the discipline is workable in practice.

**Option B: Wait for natural restructure.** Do not retro-apply. The first time the existing structure strains under new content, the directive's act cue fires for the *next* structural choice; the choice is made under the directive (with provisional marker + watch-for) and the old structure is replaced. The directive's reach is then settled by observation: it operates on transitions, not on existing states.

Option B is cheaper but produces evidence more slowly. Option A is more proactive but adds an extra layer of bookkeeping that may itself be noise.

### Choosing between them

Choose Option A when:
- The originating case is highly visible (it motivated the directive in the first place).
- The cost of the marker is small relative to the read-frequency of the affected file.
- You want fast empirical data on whether the directive is workable.

Choose Option B when:
- The structure is not particularly visible and a marker would just sit unread.
- The directive is one of several active hypothesis-tests and bookkeeping cost is approaching the refute-signal threshold.
- The structure is about to be revisited anyway for unrelated reasons.

In the absence of strong signal either way, default to Option A. The persona's bias should be toward making experiments observable, not toward minimizing in-the-moment ceremony — because the asymmetry is large: a too-bookkeepy persona accumulates noise that can be cleaned up; a too-rhetorical persona accumulates "experiments" that produced no learnable data, and the loss is permanent.

---

## 9. Failure Modes

Specific to structural decisions and the hypothesis-test directive flavor.

### F-S1: Premature commitment

A structure is presented as settled (no `provisional` marker, no watch-for block) when the underlying data is too thin to support it. Future sessions adapt content to fit the structure rather than letting friction signal that the structure should change.

**Symptom**: A session forces a new entry into an awkward cluster slot, files it, moves on. The friction is a refute signal but is not surfaced because no signals are named.

**Prevention**: When a structural choice is made in-flow, default to provisional + watch-for. The bar for omitting the markers should be high — typically only when the structure has been imported wholesale from a settled external standard.

### F-S2: Rhetorical experiment

A claim is made that "this is a test" or "we'll see whether X" without concrete confirm/refute observations or a persisted trigger. The claim lives in conversation; the next session has no record of it; the experiment never resolves.

**Symptom**: A reflection note lists "experiments under way" but the entries are short paragraphs of intent without observations, triggers, or status fields.

**Prevention**: The recursive cold-AI test (`§ 6`). Apply the test to any experiment claim before persisting it. If it lacks concrete signals or a persisted trigger, redesign or drop it.

### F-S3: Unobservable negative case

The persona claims "we'll know if the directive failed when X doesn't happen." But X not happening is indistinguishable from X being considered and rejected, X not occurring to anyone, or X not arising at all. Three outcomes collapse into one observation; the test is ill-formed.

**Symptom**: A test claim phrased as "we'll see if the next session does Y" with no specification of how the absence of Y will be distinguished from the absence of an opportunity for Y.

**Prevention**: Whenever the test depends on an action *not* happening, require a persisted trigger that *forces* the consideration to surface. Without the trigger, the test cannot decide.

### F-S4: Decorative provisional marker

A `provisional` marker is added to a structure but then ignored: future sessions read past it, restructuring decisions are made on other grounds, the marker's named signals play no role. The marker accumulates as cosmetic noise.

**Symptom**: Multiple sessions edit the affected file without engaging with the marker; no commit message references the watch-for signals.

**Prevention**: This is itself a refute signal of the parent directive (`§ 7`). When observed, the parent directive's act cue or the marker's signal-naming discipline needs adjustment. The fix is structural, not cosmetic — adding more markers will not help if the existing ones are unread.

### F-S5: Ceremony exceeds friction prevented

The bookkeeping of provisional markers, watch-for blocks, hypothesis-test entries, and persisted open questions starts to consume more attention than the friction it was supposed to prevent. The discipline becomes net-negative.

**Symptom**: Reflection time is dominated by maintaining the experiment-tracking apparatus rather than doing the work the apparatus was meant to support.

**Prevention**: Track this as one of the refute signals on the master "structural decisions as experiments" directive itself. The discipline should be evaluable against its own cost, not exempt from cost-benefit reasoning.

---

## 10. Worked Example (Generic)

To make `§§ 7–8` concrete, here is the shape of a worked example without project-specific details.

A persona is in a phase of importing concepts from a previous engagement into its memory. During import, ~25 concepts of one domain land at once. The persona organizes them in-flow into four clusters along axes that reflect the imported content. The cluster layout is recorded in the domain's index file.

Later, in reflection, a meta-question arises: this layout was chosen in-flow without a prior dated layout-criterion. Is that a problem? At first the persona frames it as a possible failure mode (criteria emerging silently mid-execution) and considers adding it to the failure-modes file.

A second pass — informed by the content/structure distinction — recognizes the framing as a category error. Memory structure is empirical, not commitment-shaped. The fix is not to add an upfront-rationale-required failure mode; the fix is to acknowledge that structural decisions should be experiments, and to label them as such.

This produces a hypothesis-test directive: "treat structural-memory decisions as experiments." Its act cue is on *making* such decisions. Its hypothesis is that provisional markers + named signals will reduce future restructuring cost. Its confirm/refute signals are concrete observations. Its re-evaluation trigger is a count, an event, or whichever comes first.

The directive is then applied retroactively to the originating four-cluster layout (Option A from `§ 8`), and an open question is persisted asking whether the retro-marker has operational effect on future entries.

In a subsequent turn, the persona claims this retro-application "is itself a small empirical test" of the directive's reach. The collaborator pushes back: how does one check the failure case? The persona recognizes its claim was rhetorical — no concrete observations were named, no persisted trigger surfaces the question to a future session. It self-corrects, persists the open question explicitly with check-status instructions, and extracts the recursive principle into a new pattern-extraction directive: experiment claims must themselves pass the cold-AI test.

The full chain — directive authoring → retro-application → claim about the retro-application → recognition that the claim itself fails the directive's test → recursive extraction — is the lifecycle of the discipline applied to itself. A bootstrapping persona should expect this kind of recursive self-correction during the first weeks of operating under hypothesis-test discipline. The chain is not a sign of confusion; it is the discipline working.

---

## 11. Bootstrapping Notes for a Fresh Persona

If you are reading this as a fresh instance setting up a new persona:

1. **Bootstrap the content/structure distinction explicitly.** In the memory-system rule file (or its equivalent), introduce both terms in the first section. Use them in change descriptions. The distinction is cheap to install at bootstrap and expensive to retrofit later.

2. **Bootstrap both directive flavors.** In the working-style file (or its equivalent), create both a category-by-topic table for pattern-extraction directives *and* a dedicated section for hypothesis-test directives. Even if the hypothesis-test section is empty initially, its existence signals to future sessions that this flavor is recognized and supported.

3. **Bootstrap the cold-AI test.** Add the five-question test to the directive-authoring rule file as a write-time gate. Make explicit that it applies recursively to experiment claims.

4. **Bootstrap the operational discipline.** Add a `provisional` + watch-for template to the same rule file. Show what it looks like in markdown. The template lowers the activation energy for using the discipline.

5. **Expect the first few hypothesis-test directives to be authored awkwardly.** The shape is novel; the cold-AI test is hard to internalize without practice. Allow the first three or four to be revised after first application — that is what the `refined` lifecycle state is for.

6. **Apply the discipline to the bootstrap itself.** The decision to organize a new persona's memory in any particular way is itself a structural decision. It should carry a `provisional` marker on the architecture document until the structure has been stress-tested by real use. Do not let "the bootstrap rule" be exempt from the discipline it prescribes.

7. **Observe yourself.** The first time you make an experiment claim, ask: did I name confirm/refute observations? Did I name a persisted trigger? If not, the claim is not a test. Redesign or drop. This recursive self-observation is the critical habit; without it, the discipline degrades into ceremony.

---

## Cross-References

- **`01-MEMORY-SYSTEM.md § File Architecture, § Maintenance Protocol, § Content Hierarchy`** — the structural layer this file's discipline operates on. The Content Hierarchy's Level 2 (memory organization) and Level 3 (meta-rules) are the levels that this file describes how to evolve.
- **`03-SELF-IMPROVEMENT.md § Pattern Extraction, § Experimentation, § Directives Are Hypotheses`** — the foundational treatment of directives-as-hypotheses. This file extends that treatment by formalizing two distinct directive flavors and the cold-AI test.
- **`04-EVIDENCE-AND-VALIDATION.md`** — the validation gate for technical conclusions. Hypothesis-test directives use a parallel validation mechanism (confirm/refute signals) for behavioral content.
- **`06-FAILURE-MODES.md § F1, § F8`** — side-effect compaction and purpose conflation; the failures this file's content/structure distinction is designed to prevent. The new failure modes F-S1 through F-S5 in `§ 9` are extensions specific to structural experiments.
- **`07-META-LEARNINGS.md § 10`** — the memory system as a learning target. This file is the operational form of that meta-principle for the structural layer specifically.
- **`08-BOOTSTRAPPING.md § Content Hierarchy, § First-Session Template`** — bootstrap setup. The bootstrapping notes in `§ 11` of this file extend the first-session template to install the content/structure discipline from session 1.
- **`09-RECURSIVE-LEARNING.md § The Recursive Principle`** — the recursive application principle stated for the learning process. This file is its structural counterpart: the recursive cold-AI test (`§ 6`) is to structural decisions what `09`'s recursive principle is to the learning process.
