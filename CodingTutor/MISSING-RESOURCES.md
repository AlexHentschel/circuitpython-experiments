# Missing resources — to obtain

Standalone hand-off list of **things beneficial for the CodingTutor project that we don't yet have**, in two parts:
**Part 1 — inaccessible publications** (paywalled / library-only / not-yet-located papers + books), and **Part 2 —
non-paper resources** (open-source code, datasets/benchmarks, products to study, prompt libraries). Compiled from the
research-loop catalog (`notes-learnings-insights_for_building_tutor/05_research-corpus_iteration-1.md § B/C`) and
consolidated attribution (`REFERENCES.md`). Everything already downloaded lives (git-ignored) in `materials/papers/` and
is **not** repeated here.

Publication entries (Part 1): **title — authors (year). journal/venue, volume(issue):pages. DOI.** `[gated]` = paywall/
library; `[unconfirmed]` = existence/metadata not yet pinned; `[book]` = monograph. Metadata verified 2026-08-14 unless
flagged. Non-paper entries (Part 2) carry a link + a status: `[confirmed]` = link verified · `[to locate]` = need to find ·
`[separate workstream]` = tracked elsewhere.

Last updated: 2026-08-15.

---

# Part 1 — Inaccessible publications

## Tier 1 — highest value (exact stack / core design questions)

1. **From Blocks to Text: Bridging Programming Misconceptions** — Mladenović, M., Žanko, Ž., & Zaharija, G. (2024).
   *Journal of Educational Computing Research*, 62(5), 1082–1106. DOI **10.1177/07356331241240047**. `[gated]` (SAGE).
   → Our *exact* stack + age band: quasi-experiment, 163 sixth-graders, **MakeCode for micro:bit → Python** mediated
   transfer (bridging method); measures reduced misconceptions in variables/sequencing/selection/loops.

2. **Scheiter's LLM tutorial-dialogue tutoring system** — Katharina Scheiter et al. (year unknown). `[unconfirmed]`.
   → The system she describes in the *They Talk Tech* podcast ("we tried to build a system that engages the learner in a
   tutorial dialog"; sycophancy suppression; endless-question-loop failure mode). Not found in her Potsdam publication
   list. Candidate origins: an in-progress/workshop paper; a collaborator's system; or the AutoTutor lineage via co-author
   A. C. Graesser. **This is the single most valuable lead — the subject of the email to Prof. Scheiter.**

3. **STAP: A Socratic Tutor for Adaptive Programming with Pedagogical Scaffolding** — authors not captured (2025).
   *Proc. 2025 2nd International Symposium on Artificial Intelligence for Education (ISAIE '25)*. DOI
   **10.1145/3775073.3775165**. `[gated]` (ACM DL; no arXiv mirror).
   → Socratic *programming* tutor; formalizes "answer leakage", "minimum viable hint", tiered Socratic hints, prompt-policy
   guardrails — directly on our anti-gaming-for-code problem.

4. **When Generative AI Meets Socratic Method: Investigating Programming Learning Dynamics Through Behaviours, Interaction
   Qualities and Perceptions** — Sun, D., Zheng, Y., Xu, J., & Yang, Z. (2026). *Journal of Computer Assisted Learning*,
   42(2), e70210. DOI **10.1002/jcal.70210**. `[gated]` (Wiley).
   → High value for **Q7** (understanding-vs-solution gate): operationalizes "give the answer only once the student
   demonstrates clear understanding" = (1) correctly identifies the root cause (logic vs syntax vs conceptual, e.g.
   variable scope) + (2) states a coherent step-by-step solution path — an LLM-judgeable criterion.

---

## Tier 2 — strong foundations (pedagogy primaries we hold only in summary)

5. **Productive Failure** — Kapur, M. (2008). *Cognition and Instruction*, 26(3), 379–424. DOI
   **10.1080/07370000802212669**. `[gated]`.
   *and* **When Problem Solving Followed by Instruction Works: Evidence for Productive Failure** — Sinha, T., & Kapur, M.
   (2021). *Review of Educational Research*, 91(5), 761–798. DOI **10.3102/00346543211019105**. `[gated]`.
   → Primary + meta-analytic productive-failure evidence (we hold only a practitioner overview locally).

6. **PRIMM: Exploring pedagogical approaches for teaching text-based programming in school** — Sentance, S., & Waite, J.
   (2017). *Proc. 12th Workshop in Primary and Secondary Computing Education (WiPSCE '17)*. DOI
   **10.1145/3137065.3137084**. `[gated]`.
   *and* **Teaching computer programming with PRIMM: a sociocultural perspective** — Sentance, S., Waite, J., & Kallia, M.
   (2019). *Computer Science Education*, 29(2–3), 136–176. DOI **10.1080/08993408.2019.1608781**. `[gated]`.
   → Peer-reviewed PRIMM (the 2019 trial: ~500 students / 13 schools). We hold only the Raspberry Pi practitioner PDF.

7. **Self-explanation set (Chi):**
   - **Self-Explanations: How Students Study and Use Examples in Learning to Solve Problems** — Chi, M. T. H., Bassok, M.,
     Lewis, M. W., Reimann, P., & Glaser, R. (1989). *Cognitive Science*, 13(2), 145–182. DOI
     **10.1207/s15516709cog1302_1**. `[gated]`.
   - **Eliciting Self-Explanations Improves Understanding** — Chi, M. T. H., de Leeuw, N., Chiu, M.-H., & LaVancher, C.
     (1994). *Cognitive Science*, 18(3), 439–477. DOI **10.1207/s15516709cog1803_3**. `[gated]`.
   - **The ICAP Framework: Linking Cognitive Engagement to Active Learning Outcomes** — Chi, M. T. H., & Wylie, R. (2014).
     *Educational Psychologist*, 49(4), 219–243. DOI **10.1080/00461520.2014.965823**. `[gated]`.
   → Foundational for self-explanation + the ICAP active/constructive/interactive engagement ladder (a candidate rubric
   for measuring the three prime skills).

---

## Tier 3 — supporting / read-only-if-we-go-deep

8. **The Impact of Large Language Models on Students: A Randomised Study of Socratic vs. Non-Socratic AI** — authors not
   captured (2024). *SSRN* working paper 5040921. `[gated]` (SSRN returns 403 to non-browser clients — needs a manual
   browser download).
   → RCT, 122 students aged 14–18: Socratic AI raised engagement but not learning; retention/transfer collapsed when the
   AI was removed. Age-matched cautionary evidence.

9. **Adaptive teaching with technology enhances lasting learning** — Sibley, L., Fabian, A., Plicht, C., Pagano, L.,
   Ehrhardt, N., Wellert, L., Bohl, T., & Lachner, A. (2025). *Learning and Instruction*, 99, 102141. DOI
   **10.1016/j.learninstruc.2025.102141**. `[gated]` (Elsevier). *(Note: NOT a Scheiter paper — Tübingen/Lachner group;
   corrected 2026-08-14.)*
   → Long-term (delayed) effects of technology-enhanced adaptive teaching on cognitive/metacognitive/motivational
   outcomes; N=656, grades 7–12. Relevant to whether adaptive scaffolding pays off on a delay.

10. **Unskilled and Unaware of It: How Difficulties in Recognizing One's Own Incompetence Lead to Inflated
    Self-Assessments** — Kruger, J., & Dunning, D. (1999). *Journal of Personality and Social Psychology*, 77(6),
    1121–1134. DOI **10.1037/0022-3514.77.6.1121**. `[gated]` (low urgency — well summarized secondhand).
    → Overconfidence/calibration primary (justifies not trusting Alice's self-reported understanding).

11. **Computational Thinking for Youth in Practice** — Lee, I., Martin, F., Denner, J., Coulter, B., Allan, W., Erickson,
    J., Malyn-Smith, J., & Werner, L. (2011). *ACM Inroads*, 2(1), 32–37. DOI **10.1145/1929887.1929902**. `[gated]`
    (low urgency — the Use-Modify-Create progression PRIMM builds on; PRIMM sources cover it).

12. **Cognitive Load Theory** — Sweller, J., Ayres, P., & Kalyuga, S. (2011). Springer. DOI
    **10.1007/978-1-4419-8126-4**. `[book]` `[gated]`.
    *and* **Multimedia Learning** (2nd ed.) — Mayer, R. E. (2009). Cambridge University Press. DOI
    **10.1017/CBO9780511811678**. `[book]` `[gated]`.
    → Canonical CLT / multimedia texts. We hold the Mayer & Moreno (2002) article-level primer; the books only if we go
    deep on load management.

---

## Related same-lineage (lower priority — same team/finding as #1)

- **Mediated transfer: From text to blocks and back** — Mladenović, M., Žanko, Ž., & Granić, A. (2021). *International
  Journal of Child-Computer Interaction*, 29, 100279. DOI **10.1016/j.ijcci.2021.100279**. `[gated]`.
- **Mediated transfer: impact on programming misconceptions** — Žanko, Ž., Mladenović, M., & Krpan, D. (2023). *Journal of
  Computers in Education*, 10(1), 1–26. DOI **10.1007/s40692-022-00225-z**. `[gated]`.

## Secondary / foundational leads (named inside the downloaded corpus; not yet sought)

Lower priority; grab only if the relevant thread deepens. Full context: `05_research-corpus_iteration-1.md § C`.

- **Cognitive offloading** — Risko, E. F., & Gilbert, S. J. (2016). *Trends in Cognitive Sciences* — theoretical base under "metacognitive laziness".
- **Tracing-before-writing** — Lister, R., et al. (multiple, 2004+) — novices need trace competence before independent writing (empirical base under PRIMM's "read before write").
- **Worked examples in CS** — Morrison, B. B., Margulieux, L. E., & Guzdial, M. (2015). ICER.
- **Productive-failure theory** — Loibl, K., Roll, I., & Rummel, N. (2017). *Educational Psychology Review*.
- **Self-regulated learning framework** — Zimmerman, B. J. (2000/2002) — the SRL-phase scaffolding target.

---

# Part 2 — Non-paper resources

Resources beyond publications, worth collecting in parallel. Status (all rows located 2026-08-15): `[confirmed]` = openly
available, link verified · `[access by request]` = free but gated behind an email/registration · `[supplement only]` =
no code, but a data/prompt supplement exists · `[proprietary]` = closed product, study via paper/site · `[separate
workstream]` = tracked elsewhere · `[to locate]` = still unresolved (none remain). None of these are on a "fetch"
obligation yet — this is a tracked wishlist; the `[confirmed]` repos/datasets are cloneable whenever we start
building/testing.

## A. Open-source tutor code (we hold the paper; want the running system)

| Resource | Link | Status | Why it matters |
|---|---|---|---|
| **MWPTutor / AutoTutor-meets-LLMs** (Pal Chowdhury et al. 2024) | `github.com/eth-lre/MWPTutor` | `[confirmed]` | Reference implementation of the **FSM + LLM hybrid** (turn manager, script/state-space authoring) — closest architecture to our Q2 bet. |
| **Ruffle&Riley** (Schmucker et al. 2024) | `github.com/rschmucker/ruffle-and-riley` (MIT) | `[confirmed]` | Full CTS: LLM script authoring + two-agent learning-by-teaching orchestration; exact prompts + turn logic in-repo. |
| **Betty's Brain** (Vanderbilt OELE) | `dev.teachableagents.org` (no public repo) | `[access by request]` | **No open source.** Free for research/classroom use by emailing Prof. Gautam Biswas (`gautam.biswas@vanderbilt.edu`). NB: it's a *science* (causal-map) learning-by-teaching env, not programming — value is as a **design reference** (SRL scaffolding, mentor agent), not reusable code. (Third-party log-parser only: `github.com/NaveedMohammed/BB-Data-Formatter`.) |
| **SocratiCode** (2026) | Zenodo `10.5281/zenodo.20018098` (no code repo) | `[supplement only]` | The paper's tutor has **no public code**; a Zenodo supplement (study materials/prompts) exists — grab that. ⚠️ Name collision: `github.com/giancarloerra/SocratiCode` is an **unrelated** MCP code-search tool, not this system. |
| **Sakshm AI** (2025) | `sakshm.com` (Disha AI); no public repo | `[proprietary]` | Commercial product (founders ex-Microsoft Research). No open source; study via the paper (arXiv:2503.12479) + product site. |

## B. Benchmarks / datasets (to *test* anti-sycophancy + Socratic behaviour — Q3/Q4/Q7)

| Resource | Link | Status | Why it matters |
|---|---|---|---|
| **EduFrameTrap** (Kasneci & Kasneci 2026) | `github.com/KasneciLab/eduframetrap-icml2026` | `[confirmed]` | 360 misconception "trap families" × confidence × pressure (context-switch / authority / social-affective), **incl. a Computer-Science domain** — near-exact model for Alice's social-engineering attacks. |
| **SYCON-Bench** (Hong et al., Findings EMNLP 2025) | `github.com/JiseungHong/SYCON-Bench` (MIT) | `[confirmed]` | Multi-turn sycophancy: *Turn-of-Flip* / *Number-of-Flip* under sustained pressure — a concrete "does the tutor cave?" metric. |
| **MathDial** (Macina et al., Findings EMNLP 2023) | `github.com/eth-nlped/mathdial` · HF `eth-nlped/mathdial` | `[confirmed]` | ~2.9k teacher–student tutoring dialogues with a taxonomy of teacher moves + a solve-success-vs-telling-solutions trade-off metric. Domain is math, but the tutor-move taxonomy transfers. |
| **SocraticMATH** (Ding et al., CIKM 2024) | `github.com/ECNU-ICALK/SocraticMath` · HF `ulises-c/SocraticMATH` | `[confirmed]` | 6,846 multi-turn Socratic tutoring dialogues (review→heuristic→rectification→summarization), 513 primary-school math knowledge points. **Chinese-language, math domain; dataset CC BY-NC 4.0 (non-commercial)** — use the *strategy structure* + prompt design, not the content. Fine-tuned model: HF `CogBase-USTC/SocraticLM`. |

## C. Existing tutor products to study (design references)

| Resource | Status | Why it matters |
|---|---|---|
| **Khan Academy Khanmigo** | `[confirmed]` (public blog write-ups) | Mature Socratic-tutoring UX + answer-withholding guardrails, and unusually candid on *how*: 7-step prompt-engineering (`blog.khanacademy.org/khan-academys-7-step-approach-to-prompt-engineering-for-khanmigo/`), "How We Built AI Tutoring Tools", "Building a Better AI Tutor: Our Most Recent Learnings" (guardrail metrics: answer-give-away rate, cognitive-engagement; a separate "math agent" verifier; prompt-length degradation). Directly reusable design lessons. |
| **Anthropic Education Report** (Apr 2025) | `[confirmed]` | `anthropic.com/news/anthropic-education-report-how-university-students-use-claude` — 574,740 student conversations; four interaction patterns; **~47% "direct", minimal-effort** exchanges (the offloading figure); CS students 38.6% overrepresented. Evidence base for the metacog-laziness / cognitive-offloading risk (P3.10). |

## D. Prompt libraries / practitioner materials

| Resource | Status | Why it matters |
|---|---|---|
| **Published Socratic-tutor system prompts** (e.g. from the open-source systems in § A, Khanmigo write-ups) | `[to locate]` | Directly reusable prompt scaffolding for the guide-don't-answer policy. |
| **Raspberry Pi / Teach Computing PRIMM classroom materials** | `[to locate]` | Practitioner PRIMM lesson structures (we hold only the summary PDF). |

## E. Hardware / platform enablement

| Resource | Status | Why it matters |
|---|---|---|
| **CircuitPython driver availability for the Elecfreaks Nezha2 / PlanetX stack** | `[separate workstream]` (in progress with Alex) | Gates the CircuitPython pivot + feeds Q1/Q8. **Tracked outside this file** to avoid double-tracking; fold the outcome into Q1 when resolved. |

---

## How to hand a fetched PDF back for ingestion

Drop the PDF into `materials/papers/` (git-ignored). It'll be triaged + digested in the next research iteration and its
row moved from `REFERENCES.md § 2b` (to-fetch) to `§ 2a` (downloaded).

## Cross-references
- Ranked rationale + agenda mapping: `notes-learnings-insights_for_building_tutor/05_research-corpus_iteration-1.md § B`
- Full attribution incl. the 20 downloaded sources: `REFERENCES.md`
- Podcast that seeded the project: `digests/scheiter-they-talk-tech_digest.md`
