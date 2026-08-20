# Research corpus — iteration 1 (2026-07-15)

Purpose: the catalog produced by the **first autonomous research loop** (web-search -> triage -> download -> follow secondary
leads). It maps the corpus onto the research agenda cells in `04_pre-design-considerations-and-research-agenda.md § E`, gives a
one-line relevance triage + read-priority per source, and lists the **relevant-but-inaccessible sources ranked for Alex to
fetch**. Deliberately triage-depth, not digest-depth: per Alex's iteration plan, deep analysis / digests come next.

Method note (bias applied): inspect-first, dismiss-if-irrelevant. False positives (kept a source, later dropped) preferred over
false negatives (filtered out something relevant before inspecting). Balance struck: broad abstract-level triage across all agenda
cells; PDFs pulled for everything plausibly on-target that was openly accessible.

Local copies: `../materials/papers/` (git-ignored — third-party copyright; see `../REFERENCES.md § Licensing`). **20 PDFs downloaded**
(17 in the first pass; 3 added when arXiv preprint mirrors of previously-gated items were found — MWPTutor + two K-12/programming
Socratic tutors). Access note: arXiv is off the Cursor *sandbox* allowlist, so downloads run via elevated network (`full_network`);
an attempted sandbox allowlist of arXiv (2026-07-15) did not take effect this session. Non-arXiv gated hosts (SAGE, SSRN, ACM DL,
Elsevier, Wiley, APA, T&F) remain inaccessible without institutional access — see § B.

Evidence-status reminder: every empirical claim below is `unverified` until the source is read in full; this file records *what the
corpus is + why it's relevant*, not validated findings. Scheiter interview claims remain expert-opinion until primary sources corroborate.

---

## A. Downloaded corpus (local, accessible) — 20 sources

Read-priority: **T1** = read first (most directly on-target), **T2** = strong, **T3** = supporting/foundational.

| # | Source (short) | Agenda cell | Why relevant (triage) | Local file | Prio |
|---|----------------|-------------|-----------------------|------------|------|
| 1 | **Bauer, Greiff, Graesser, Scheiter, Sailer (2025), "Looking beyond the hype: understanding the effects of AI on learning", Educational Psychology Review 37:45** | P1.1 / B / C | Scheiter's *own* peer-reviewed synthesis of how AI affects learning — the scholarly backbone behind her podcast claims. CC-BY. Co-authored with Graesser (AutoTutor). | `Bauer-Scheiter-2025_Looking-beyond-the-hype_EPR.pdf` | T1 |
| 2 | **Kosmyna et al. (2025), "Your Brain on ChatGPT: Accumulation of Cognitive Debt…", arXiv:2506.08872** | P1.2 / B1 | The EEG essay study the podcast centers on; brain-first vs AI-first reversal; "cognitive debt"; recommends delaying AI until self-driven effort. Directly grounds the think-first-then-AI ordering. | `Kosmyna-2025_Your-Brain-on-ChatGPT_arXiv-2506.08872.pdf` | T1 |
| 3 | **Fan, Tang, Le, Shen, Tan, Zhao et al. (2024), "Beware of metacognitive laziness…", British Journal of Educational Technology 56:489-530 (arXiv:2412.09315)** | P3.10 / A | Coins/operationalizes "metacognitive laziness"; 117-learner experiment; cognitive-offloading mechanism (Risko & Gilbert). The mechanism behind Alice's social-engineering + copy-paste risk. | `Fan-2024_Metacognitive-laziness_arXiv-2412.09315.pdf` | T1 |
| 4 | **Weintrop & Wilensky (2019), "Transitioning from introductory block-based and text-based environments to professional programming languages…", Computers & Education** | P1.4 | Empirical block->text transition in HS CS; finding: early block-vs-text advantage *fades* after transition unless transition is scaffolded. Our exact move (MakeCode -> CircuitPython). | `Weintrop-Wilensky-2019_Block-to-text-transition.pdf` | T1 |
| 5 | **Schmucker, Xia, Azaria, Mitchell (2024), "Ruffle&Riley: … LLM-Based Conversational Tutoring System", AIED'24 (arXiv:2404.17460)** | P1.3 / C | Concrete LLM CTS: two-agent learning-by-teaching, ITS inner/outer-loop, auto-authored tutoring script (EMT), open-sourced. Closest existing design to what we're building. | `Schmucker-2024_Ruffle-Riley-AIED_arXiv-2404.17460.pdf` | T1 |
| 6 | **Kasneci & Kasneci (2026), "Sycophancy is an Educational Safety Risk: Why LLM Tutors Need Sycophancy Benchmarks", arXiv:2605.14604** | P1.3 / A | Operationalizes anti-sycophancy as a *safety* property: EduFrameTrap benchmark; "corrective friction"; authority + social-affective pressure attacks == Alice's social-engineering. Includes computer-science domain. | `Kasneci-2026_Sycophancy-educational-safety_arXiv-2605.14604.pdf` | T1 |
| 7 | **Chase, Chin, Oppezzo, Schwartz (2009), "Teachable Agents and the Protégé Effect", J. Science Education and Technology** | P2.7 | Foundational protégé-effect: learners work harder teaching an agent than for themselves; strongest for low achievers; grounds the reverse-tutoring / learning-by-explaining idea. | `Chase-2009_Protege-effect-teachable-agents.pdf` | T2 |
| 8 | **Munshi et al. (2022), "Analyzing Adaptive Scaffolds that Help Students Develop SRL Behaviors" (Betty's Brain), arXiv:2202.09698** | P2.5 / P2.7 / C | Betty's Brain adaptive SRL scaffolding in a middle-school OELE; detects cognitive/metacognitive inflection points -> mentor/agent feedback. Model for "diagnose state -> next didactic move" + fading. | `Munshi-2022_Bettys-Brain-adaptive-scaffolds_arXiv-2202.09698.pdf` | T2 |
| 9 | **Biswas, Leelawong et al. (2004), "Developing Learning by Teaching Environments that support SRL" (Betty's Brain / ITS'04)** | P2.5 / P2.7 | Earlier Betty's Brain: Zimmerman SRL framework operationalized (goal-setting, monitoring, self-eval) via teach-an-agent scaffolds. | `Biswas-2004_Bettys-Brain-SRL.pdf` | T2 |
| 10 | **SocraticLLM / Chang et al. (2024), "Boosting LLMs with Socratic Method for Conversational Mathematics Teaching", arXiv:2407.17349** | P1.3 | Socratic-prompt LLM tutor (review/heuristic/rectify/summarize); dataset SocraticMATH; explicit "guide, don't answer" + rectify-because-model-trusts-user (anti-sycophancy). | `SocraticLLM-2024_arXiv-2407.17349.pdf` | T2 |
| 11 | **Henkel et al. (2024), "Effective and scalable math support: … AI-tutor on math achievement in Ghana", arXiv:2402.09809** | P1.3 / B | Field evidence for answer-withholding tutor design at scale; complements the "crutch" finding (perf collapses when answer-giving AI removed). | `Henkel-2024_AI-tutor-math-Ghana_arXiv-2402.09809.pdf` | T2 |
| 12 | **Schmucker et al. (2023), "Ruffle&Riley: Towards the Automated Induction of Conversational Tutoring Systems", arXiv:2310.01420** | P1.3 / C | Fuller design/architecture detail for #5 (turn manager, agent prompts, EMT). Read alongside #5 for implementation specifics. | `Schmucker-2023_Ruffle-Riley-induction_arXiv-2310.01420.pdf` | T2 |
| 13 | **Kazemitabaar et al. (2022), "CodeStruct: … Intermediary Programming Environment for Novices to Transition from Scratch to Python", IDC'22** | P1.4 | Design supports for a *staged* block->text (Scratch->Python) transition; reduces syntax + data-type load. Concrete scaffolding ideas for Alice's MakeCode->CircuitPython jump. | `Kazemitabaar-2022_CodeStruct_Scratch-to-Python.pdf` | T2 |
| 14 | **"Hybrid LLM-Embedded Dialogue Agents for Learner Reflection" (CHI'26, arXiv:2602.20486)** | C / P2 | Rule-based state machine + LLM generator for reflective dialogue with **middle-schoolers doing robot-design** (our age + hardware-adjacent). Direct model for Q2 hybrid architecture + reflection phase. | `Hybrid-LLM-reflection-dialogue-2026_arXiv-2602.20486.pdf` | T2 |
| 15 | **Kapur, "Productive Failure" (overview, BOLD Science 2025 summary of Kapur 2008/2012/2014)** | P2.6 | Accessible overview of productive-failure design (explore-before-instruct); grounds "manageable uncertainty" mini-challenge calibration. Overview only — primary Kapur papers are gated (see § B). | `Kapur_Productive-Failure-overview_BOLD.pdf` | T3 |
| 16 | **Mayer & Moreno (2002), "Aids to computer-based multimedia learning", Learning & Instruction** | P3.9 | Cognitive-load + cognitive-theory-of-multimedia-learning primer (dual-channel, essential vs extraneous load). Relevant to the exemplars' heavy figure use + how much the tutor shows at once. | `MayerMoreno-2002_Multimedia-learning-cognitive-load.pdf` | T3 |
| 17 | **Sentance & Waite, "Teaching Programming with PRIMM" (Raspberry Pi practitioner summary)** | P1.4 | Practitioner-level PRIMM (Predict-Run-Investigate-Modify-Make): read-before-write, gradual ownership transfer, classroom-talk. Original peer-reviewed PRIMM papers are gated (see § B). | `Sentance-Waite_Teaching-with-PRIMM_RaspberryPi.pdf` | T3 |
| 18 | **Pal Chowdhury, Zouhar, Sachan (2024), "AutoTutor meets LLMs" / MWPTutor, arXiv:2402.09216** | P1.3 / C | Hybrid: LLM fills the state space of a hand-designed **finite-state transducer**; "handcraft the pedagogy, let the LLM fill it in"; live vs cached variants; beats free-form GPT-4; open-sourced (eth-lre/MWPTutor). Central Q2-architecture evidence. *(Was ranked-gated #3; arXiv mirror found + downloaded.)* | `PalChowdhury-2024_AutoTutor-meets-LLMs-MWPTutor_arXiv-2402.09216.pdf` | T1 |
| 19 | **"Towards SocratiCode: … GenAI Programming Tutor for K-12 Students, 4-Week Participatory Design Study" (2026, arXiv:2605.17857)** | P1.3 / P1.4 | **K-12 + programming + Socratic** — closest age+domain match after the gated Blocks-to-Text. Structural constraints, controlled pacing, misconception clarification, reflective pauses, hints-before-solutions; evolved from content-delivery toward guided inquiry. | `SocratiCode-2026_GenAI-programming-tutor-K12_arXiv-2605.17857.pdf` | T2 |
| 20 | **"Sakshm AI: … Socratic Tutoring and Comprehensive Feedback" (2025, arXiv:2503.12479)** | P1.3 | Large-scale (1170 users) Socratic coding tutor: context-aware hints, structured feedback, conversational memory, no direct code-gen. Engineering-undergrad population (older than Alice) — read for the guardrail/hint-tiering mechanics, discount the age-specific findings. | `SakshmAI-2025_Socratic-coding-tutor_arXiv-2503.12479.pdf` | T3 |

---

## B. Relevant-but-inaccessible — RANKED for Alex to fetch

Ranked by expected value to the tutor design. `[gated]` = paywall/library; `[unconfirmed]` = existence/citation not yet pinned.
When you obtain one, drop the PDF in `../materials/papers/` and I'll ingest it next iteration.

Update (2026-07-15, post arXiv-access pass): **MWPTutor is now downloaded** (arXiv mirror found — corpus #18); STAP has no arXiv
mirror but two open substitutes were downloaded (#19 SocratiCode-K12, #20 Sakshm). SSRN and the SAGE/Springer/Elsevier/Wiley
items below remain gated. Remaining ranked to-fetch:

1. **`[gated]` "From Blocks to Text: Bridging Programming Misconceptions" (Mladenović, Žanko & Zaharija, 2024), Journal of Educational Computing Research 62(5):1082-1106, DOI 10.1177/07356331241240047.** — TOP priority: quasi-experiment, **163 sixth-graders**, **MakeCode for micro:bit -> Python** mediated transfer (bridging method), reduces misconceptions in variables/sequencing/selection/loops. Our *exact* stack, transition, and age band. No open mirror found (SAGE-gated). *(Author correction 2026-08-14: Mladenović/Žanko/**Zaharija** — not Granić.)* **Same-lineage related** (also gated, lower priority, same team/finding): Mladenović, Žanko & Granić (2021) "Mediated transfer: From text to blocks and back", *Int. J. Child-Computer Interaction* 29:100279 (DOI 10.1016/j.ijcci.2021.100279); Žanko, Mladenović & Krpan (2023) "Mediated transfer: impact on programming misconceptions", *J. Computers in Education* 10(1):1-26 (DOI 10.1007/s40692-022-00225-z).
2. **`[unconfirmed]` Scheiter's specific LLM tutorial-dialogue-system paper.** — She says in the podcast "we tried to build a system that engages the learner in a tutorial dialog" (sycophancy suppression; endless-question-loop failure). NOT found in her Potsdam publication list (closest: cognitive-tutor/ITS work below). Candidates: a 2025/26 in-progress or workshop paper; a collaborator's system she speaks to; or the AutoTutor lineage via co-author Graesser. **Do you know the specific project/paper?** (Highest-value single lead per the agenda.)
3. **`[gated]` STAP: "A Socratic Tutor for Adaptive Programming with Pedagogical Scaffolding" (ISAIE 2025, DOI 10.1145/3775073.3775165).** — Socratic *programming* tutor; formalizes "answer leakage", "minimum viable hint", tiered Socratic hints, prompt-policy guardrails. Directly on our anti-gaming-for-code problem. No arXiv mirror (ACM-only). *Partial substitutes downloaded: #19, #20.*
4. **`[gated]` Sun, D., Zheng, Y., Xu, J. & Yang, Z. (2026), "When Generative AI Meets Socratic Method…", Journal of Computer Assisted Learning 42(2):e70210, DOI 10.1002/jcal.70210.** — **High value for Q7** (the understanding-vs-solution boundary): operationalizes "give the answer only once the student demonstrates clear understanding", defined as (1) correctly identifying the root cause (logic vs syntax vs conceptual e.g. variable scope) and (2) a coherent step-by-step solution path — an LLM-judgeable gate. Wiley-gated (abstract-level mechanism captured; full method/results need the PDF).
5. **`[gated]` Kapur (2008), "Productive Failure", Cognition and Instruction 26(3):379-424** + **Sinha & Kapur (2021), "When Problem Solving Followed by Instruction Works", Review of Educational Research 91(5).** — Primary + meta-analytic productive-failure evidence (we only have the practitioner overview locally).
6. **`[gated]` PRIMM originals: Sentance & Waite (2017), WiPSCE (DOI 10.1145/3137065.3137084)** + **Sentance, Waite & Kallia (2019), "Teaching computer programming with PRIMM: a sociocultural perspective", Computer Science Education.** — Peer-reviewed PRIMM (trial: 493 students / 13 schools). We hold only the practitioner PDF.
7. **`[gated]` Chi self-explanation set: Chi, Bassok, Lewis, Reimann, Glaser (1989), Cognitive Science 13; Chi (1994) "Eliciting self-explanations"; Chi & Wylie (2014) ICAP framework.** — Foundational for self-explanation + the ICAP active/constructive/interactive engagement ladder (backbone for measuring the 3 prime skills).
8. **`[gated]` "The Impact of LLMs on Students: A Randomised Study of Socratic vs. Non-Socratic AI…" (SSRN 5040921, 2024).** — RCT, **122 students aged 14-18**: Socratic AI raised engagement but not learning, and retention/transfer collapsed when AI removed. Age-matched cautionary evidence. SSRN returns 403 to non-browser clients (retried, still blocked) — needs a manual browser download.
9. **`[gated]` Sibley, L., Fabian, A., Plicht, C., Pagano, L., Ehrhardt, N., Wellert, L., Bohl, T. & Lachner, A. (2025), "Adaptive teaching with technology enhances lasting learning", Learning & Instruction 99:102141 (DOI 10.1016/j.learninstruc.2025.102141).** — Long-term (delayed) cognitive/metacognitive/motivational effects of tech-enhanced adaptive teaching; N=656, grades 7-12. *(Correction 2026-08-14: this is the Tübingen/Lachner group, **not** a Scheiter paper — earlier mislabeled.)*
10. **`[gated]` Kruger & Dunning (1999), "Unskilled and Unaware of It", JPSP 77(6):1121-1134.** — The overconfidence/calibration primary source (justifies not trusting Alice's self-reported understanding). Well-summarized secondhand; low urgency.
11. **`[gated]` Use-Modify-Create: Lee et al. (2011), "Computational thinking for youth in practice", ACM Inroads.** — The progression PRIMM builds on. Lower urgency (PRIMM sources cover it).
12. **`[gated]` Sweller, Ayres & Kalyuga (2011), *Cognitive Load Theory* (book); Mayer (2009), *Multimedia Learning* (book).** — Canonical CLT/multimedia texts. We hold the Mayer & Moreno article-level primer; books only if we go deep on load management.

---

## C. Secondary leads surfaced in the corpus (for the NEXT iteration)

Named inside the sources above; worth following once the T1/T2 set is digested:
- **Cognitive offloading**: Risko & Gilbert (2016) — the theoretical base under "metacognitive laziness".
- **Anthropic education report** (student AI-usage patterns; ~half of requests are direct-answer with minimal engagement) — cited in the metacog-laziness coverage.
- **Tracing-before-writing**: Lister et al. (multiple) — novices need ~50% trace accuracy before independent writing; the empirical base under PRIMM's "read before write".
- **Worked examples in CS**: Morrison, Margulieux & Guzdial (2015).
- **Productive-failure theory**: Loibl, Roll & Rummel (2017) "Towards a theory of when/how PS-then-instruction works".
- **SRL framework**: Zimmerman (self-regulation phases) — the scaffolding target for Betty's-Brain-style fading.
- **ICAP**: Chi & Wylie (2014) — engagement taxonomy usable as a skill-measurement rubric.
- **Recent AI-reliance corroborations** (open, not yet downloaded — grab if we deepen P3.10): Georgiou (2025) arXiv:2507.00181; "Thinking Less, Trusting More" arXiv:2601.22430.
- **Multi-turn sycophancy benchmark**: SYCON-Bench (Findings of EMNLP 2025) — measures "turn-of-flip" under pressure; a concrete anti-social-engineering eval instrument.

## D. Coverage check against the agenda (`04...md § E`)

| Cell | Covered by | Gap |
|------|-----------|-----|
| P1.1 Scheiter tutorial-dialogue | #1 (her synthesis) + Ruffle&Riley/Hybrid-reflection as analogues | The *specific* Scheiter system (§B.2) unconfirmed |
| P1.2 Your Brain on ChatGPT | #2 (primary, downloaded) | — closed |
| P1.3 ITS + LLM hybrids | #5,#6,#10,#11,#12,#14,#18(MWPTutor),#19,#20 | STAP gated (§B.3); JCAL Q7-gate paper gated (§B.4) |
| P1.4 programming pedagogy | #4,#13,#17,#19 + §B.1,6,11; secondary Lister/Morrison | Blocks-to-Text-Misconceptions + Croatian lineage gated (§B.1, TOP) |
| P2.5 SRL/metacognition | #8,#9 | Zimmerman primary (secondary list) |
| P2.6 desirable difficulty / productive failure | #15 + §B.5 | Kapur primaries gated |
| P2.7 self-explanation / teachable agents | #7,#8,#9 + §B.7 | Chi primaries gated |
| P2.8 overconfidence/calibration | §B.10 (well-summarized) | Kruger&Dunning primary gated (low urgency) |
| P3.9 cognitive load / multimedia | #16 + §B.12 | books only if deep |
| P3.10 metacognitive laziness / AI-reliance | #3 + secondary (Georgiou; Trusting-More) | — well covered |
| P3.11 delay-of-gratification | (deliberately deferred — light lens) | — |

## Cross-references
- Research agenda (source of the P-cells): `04_pre-design-considerations-and-research-agenda.md § E`
- Full attribution + licensing of every source here: `../REFERENCES.md`
- Open questions / next steps: `03_open-questions-todos.md`
- Scheiter digest (the seed source): `../digests/scheiter-they-talk-tech_digest.md`
