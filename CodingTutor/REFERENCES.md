# References & attribution

Single consolidated source of attribution for the CodingTutor project. Every external source we read, cite, digest, or
build on is listed here with a full citation and its licensing / redistribution status. Referenced from `README.md`.

**Attribution is a hard requirement for this project.** Anything that informs the tutor's design should be traceable to a
source here. Our own writing (notes, digests, code) cites sources by the short key in the leftmost column or by a
descriptive phrase (per the "scoped IDs need source context" convention — never leave a bare key undecodable).

Status legend:
- **Access**: `open` (freely available) · `gated` (paywall / library) · `internal` (Alex-owned / prior work).
- **Redistribution**: `no` (copyrighted, do not commit) · `yes:<license>` (permissive, may commit) · `n/a` (link-only,
  nothing stored) · `TBD` (must confirm before committing the artifact).
- Stored artifacts that are copyrighted live git-ignored under `materials/papers/` (see that folder's README).

---

## 1. Learning-science & pedagogy sources (ingested / in progress)

### [Scheiter-TTT-2026] — primary ingested source
- **Podcast**: *They Talk Tech* (c't / heise), live episode from the University:Future Festival 2026:
  "Live mit Katharina Scheiter: KI und Bildung – Verlernen wir gerade, wie man denkt?"
- **Guest**: Prof. Dr. Katharina Scheiter (Professor of teaching-and-learning research / digital education, University of
  Potsdam). **Host**: c't *They Talk Tech* (normally co-hosted with Svea Eckert; she is absent in this live episode).
- **Festival session**: https://festival.hfd.digital/de/sessions-2026/?id=1191986
- **Related interview** (t3n): https://t3n.de/news/hirnforscher-warnen-chatgpt-1712547
- **MIT Technology Review 07/2025** (German ed., referenced in the episode): https://shop.t3n.de/collections/mit-technology-review/products/mit-technology-review-07-2025
- **Local artifacts**: `materials/They Talk Tech transcript.txt` (German original), `materials/They Talk Tech transcript_EN.txt`
  (our English translation). **Digest**: `digests/scheiter-they-talk-tech_digest.md`.
- **Access**: `open` (podcast). **Redistribution**: `no` — the transcript + translation are derivative of copyrighted
  audio. Our digest/notes (our own writing) are fine to commit; the transcript files should be untracked (see § Licensing).

## 2. Learning-science, tutoring & programming-education corpus (research iteration 1, 2026-07-15)

Assembled by the first autonomous research loop. Full triage + agenda-mapping + read-priority: `notes-learnings-insights_for_building_tutor/05_research-corpus_iteration-1.md`. Local PDFs live in `materials/papers/` (git-ignored). All are third-party copyrighted unless a specific redistribution license is noted; **none are committed** (see § Licensing).

### 2a. Downloaded (local copies in `materials/papers/`)

| Key | Citation | Local file | Access |
|---|---|---|---|
| [Bauer-2025-hype] | Bauer, E., Greiff, S., Graesser, A.C., Scheiter, K., Sailer, M. (2025). Looking beyond the hype: understanding the effects of AI on learning. *Educational Psychology Review* 37, 45. DOI 10.1007/s10648-025-10020-8. | `Bauer-Scheiter-2025_Looking-beyond-the-hype_EPR.pdf` | open (**CC-BY 4.0**) |
| [Kosmyna-2025] | Kosmyna, N., Hauptmann, E., Yuan, Y.T., Situ, J., Liao, X.-H., Beresnitzky, A.V., Braunstein, I., Maes, P. (2025). Your Brain on ChatGPT: Accumulation of Cognitive Debt… *arXiv:2506.08872*. | `Kosmyna-2025_Your-Brain-on-ChatGPT_arXiv-2506.08872.pdf` | open (arXiv) |
| [Fan-2024-laziness] | Fan, Y., Tang, L., Le, H., Shen, K., Tan, S., Zhao, Y., et al. (2024). Beware of metacognitive laziness… *British Journal of Educational Technology* 56, 489-530 (arXiv:2412.09315). | `Fan-2024_Metacognitive-laziness_arXiv-2412.09315.pdf` | open (arXiv preprint) |
| [Weintrop-2019] | Weintrop, D., Wilensky, U. (2019). Transitioning from introductory block-based and text-based environments to professional programming languages… *Computers & Education*. | `Weintrop-Wilensky-2019_Block-to-text-transition.pdf` | open (author copy) |
| [RuffleRiley-2024] | Schmucker, R., Xia, M., Azaria, A., Mitchell, T. (2024). Ruffle&Riley: Insights from Designing and Evaluating an LLM-Based Conversational Tutoring System. *AIED'24*, 75-90 (arXiv:2404.17460). DOI 10.1007/978-3-031-64302-6_6. | `Schmucker-2024_Ruffle-Riley-AIED_arXiv-2404.17460.pdf` | open (arXiv) |
| [RuffleRiley-2023] | Schmucker, R., et al. (2023). Ruffle&Riley: Towards the Automated Induction of Conversational Tutoring Systems. *arXiv:2310.01420*. | `Schmucker-2023_Ruffle-Riley-induction_arXiv-2310.01420.pdf` | open (arXiv) |
| [Kasneci-2026-syco] | Kasneci, E., Kasneci, G. (2026). Sycophancy is an Educational Safety Risk: Why LLM Tutors Need Sycophancy Benchmarks. *arXiv:2605.14604*. | `Kasneci-2026_Sycophancy-educational-safety_arXiv-2605.14604.pdf` | open (arXiv) |
| [SocraticLLM-2024] | (SocraticLLM) Boosting Large Language Models with Socratic Method for Conversational Mathematics Teaching (2024). *arXiv:2407.17349*. | `SocraticLLM-2024_arXiv-2407.17349.pdf` | open (arXiv) |
| [Henkel-2024-Ghana] | Henkel, O., Horne-Robinson, H., Kozhakhmetova, N., Lee, A. (2024). Effective and scalable math support: … AI-tutor on math achievement in Ghana. *arXiv:2402.09809*. | `Henkel-2024_AI-tutor-math-Ghana_arXiv-2402.09809.pdf` | open (arXiv) |
| [Chase-2009-protege] | Chase, C.C., Chin, D.B., Oppezzo, M.A., Schwartz, D.L. (2009). Teachable Agents and the Protégé Effect. *J. Science Education and Technology* 18. DOI 10.1007/s10956-009-9180-4. | `Chase-2009_Protege-effect-teachable-agents.pdf` | open (author copy, Stanford AAALab) |
| [Munshi-2022-betty] | Munshi, A., Biswas, G., et al. (2022). Analyzing Adaptive Scaffolds that Help Students Develop SRL Behaviors (Betty's Brain). *arXiv:2202.09698*. | `Munshi-2022_Bettys-Brain-adaptive-scaffolds_arXiv-2202.09698.pdf` | open (arXiv) |
| [Biswas-2004-betty] | Biswas, G., Leelawong, K., et al. (2004). Developing Learning by Teaching Environments that support Self-Regulated Learning (Betty's Brain). *ITS'04*. | `Biswas-2004_Bettys-Brain-SRL.pdf` | open (author copy) |
| [Kazemitabaar-2022] | Kazemitabaar, M., Weintrop, D., et al. (2022). CodeStruct: … Intermediary Programming Environment for Novices to Transition from Scratch to Python. *IDC'22*. | `Kazemitabaar-2022_CodeStruct_Scratch-to-Python.pdf` | open (author copy) |
| [HybridReflect-2026] | Hybrid LLM-Embedded Dialogue Agents for Learner Reflection: Designing Responsive and Theory-Driven Interactions (2026). *CHI'26* (arXiv:2602.20486). DOI 10.1145/3772318.3791582. | `Hybrid-LLM-reflection-dialogue-2026_arXiv-2602.20486.pdf` | open (arXiv) |
| [Kapur-PF-overview] | Kapur, M. — Productive Failure (overview, BOLD Science 2025 summarizing Kapur 2008/2012/2014). | `Kapur_Productive-Failure-overview_BOLD.pdf` | open (summary) |
| [MayerMoreno-2002] | Mayer, R.E., Moreno, R. (2002). Aids to computer-based multimedia learning. *Learning and Instruction*. | `MayerMoreno-2002_Multimedia-learning-cognitive-load.pdf` | open (author copy) |
| [PRIMM-practitioner] | Sentance, S., Waite, J. — Teaching Programming with PRIMM (Raspberry Pi Foundation practitioner summary). | `Sentance-Waite_Teaching-with-PRIMM_RaspberryPi.pdf` | open (RPi) |
| [AutoTutor-LLM-2024] | Pal Chowdhury, S., Zouhar, V., Sachan, M. (2024). AutoTutor meets Large Language Models: A Language Model Tutor with Rich Pedagogy and Guardrails (MWPTutor). *Learning@Scale'24*, DOI 10.1145/3657604.3662041 (arXiv:2402.09216). Code: github.com/eth-lre/MWPTutor. | `PalChowdhury-2024_AutoTutor-meets-LLMs-MWPTutor_arXiv-2402.09216.pdf` | open (arXiv mirror of gated ACM paper) |
| [SocratiCode-2026] | Towards SocratiCode: Designing a Generative AI-Based Programming Tutor for K-12 Students through a 4-Week Participatory Design Study (2026). *arXiv:2605.17857*. | `SocratiCode-2026_GenAI-programming-tutor-K12_arXiv-2605.17857.pdf` | open (arXiv) |
| [SakshmAI-2025] | Sakshm AI: Advancing AI-Assisted Coding Education … Through Socratic Tutoring and Comprehensive Feedback (2025). *arXiv:2503.12479*. | `SakshmAI-2025_Socratic-coding-tutor_arXiv-2503.12479.pdf` | open (arXiv) |

### 2b. Relevant-but-inaccessible — RANKED to fetch (Alex)

Full ranked rationale: `notes-learnings-insights_for_building_tutor/05_research-corpus_iteration-1.md § B`. **Update 2026-07-15**: former #3 [AutoTutor-LLM-2024] now downloaded via arXiv mirror (moved to §2a); STAP has no arXiv but two open substitutes downloaded (§2a [SocratiCode-2026], [SakshmAI-2025]). Remaining:

1. [BlocksToText-Misconceptions-2024] — "From Blocks to Text: Bridging Programming Misconceptions" (Mladenović, Žanko & Zaharija, 2024), *J. Educational Computing Research* 62(5):1082-1106, DOI 10.1177/07356331241240047. **Top lead** (micro:bit MakeCode->Python, 163 sixth-graders). `gated`, no open mirror. Same-lineage related (also gated, lower priority): [MladenovicZankoGranic-2021] Mladenović, Žanko & Granić, IJCCI 29:100279, DOI 10.1016/j.ijcci.2021.100279 "…text to blocks and back"; [ZankoMladenovicKrpan-2023] Žanko, Mladenović & Krpan, *J. Computers in Education* 10(1):1-26, DOI 10.1007/s40692-022-00225-z "…impact on programming misconceptions".
2. [Scheiter-tutorial-dialogue] — the *specific* Scheiter LLM tutorial-dialogue system from the podcast. **`[unconfirmed]`** — not in her Potsdam list; candidates in the corpus doc. Needs Alex/author knowledge.
3. [STAP-2025] — Socratic Tutor for Adaptive Programming, *ISAIE'25*, DOI 10.1145/3775073.3775165. `gated` (no arXiv mirror).
4. [WhenGenAIMeetsSocratic-2026] — Sun, D., Zheng, Y., Xu, J. & Yang, Z. (2026). "When Generative AI Meets Socratic Method…", *J. Computer Assisted Learning* 42(2):e70210, DOI 10.1002/jcal.70210. **High value for Q7** — operationalizes the give-answer-only-after-understanding gate (identify root cause + coherent solution path). `gated` (Wiley).
5. [Kapur-2008] / [SinhaKapur-2021] — Productive Failure primaries (Cognition & Instruction 26(3); Review of Educational Research 91(5)). `gated`.
6. [PRIMM-2017] / [PRIMM-2019] — Sentance & Waite (2017, WiPSCE, DOI 10.1145/3137065.3137084); Sentance, Waite, Kallia (2019, Computer Science Education). `gated`.
7. [Chi-selfexplanation] — Chi et al. (1989, Cognitive Science 13); Chi (1994); Chi & Wylie (2014, ICAP). `gated`.
8. [SocraticRCT-2024] — Socratic vs Non-Socratic AI RCT, 122 students aged 14-18, *SSRN 5040921*. `gated` (403 to non-browser clients; retried — needs manual browser download).
9. [Sibley-adaptive-2025] — Sibley, L., Fabian, A., Plicht, C., Pagano, L., Ehrhardt, N., Wellert, L., Bohl, T. & Lachner, A. (2025). Adaptive teaching with technology enhances lasting learning, *Learning & Instruction* 99:102141, DOI 10.1016/j.learninstruc.2025.102141. `gated`. **(Correction 2026-08-14: NOT a Scheiter paper — Tübingen/Lachner group; earlier mislabeled `[Scheiter-adaptive-2025]`.)**
10. [KrugerDunning-1999] — Unskilled and Unaware of It, *JPSP* 77(6):1121-1134. `gated` (low urgency).
11. [UseModifyCreate-2011] — Lee et al., ACM Inroads. `gated` (low urgency).
12. [Sweller-CLT-2011] / [Mayer-2009] — CLT & Multimedia Learning books. `gated` (only if we go deep).

## 3. Hardware & platform references (from the exemplar tutorials)

Link-only unless noted; nothing stored locally. Access `open`, redistribution `n/a` (we link, not copy).

| Key | What | URL |
|---|---|---|
| [EF-Nezha2] | Elecfreaks Nezha Pro / Nezha2 breakout board wiki | https://wiki.elecfreaks.com/en/microbit/expansion-board/nezha-v2/ |
| [EF-Crash] | PlanetX Crash Sensor (EF05008) | https://wiki.elecfreaks.com/en/microbit/sensor/planet-x-sensors/Plant_X_EF05008/ |
| [EF-Motor] | PlanetX Smart Brick Motor (EF05071) | https://wiki.elecfreaks.com/en/microbit/sensor/planet-x-sensors/Plant_X_EF05071 |
| [EF-Button] | PlanetX Button (EF05017) | https://wiki.elecfreaks.com/en/microbit/sensor/planet-x-sensors/Plant_X_EF05017 |
| [EF-Analog] | PlanetX analog input module (EF05018) | https://wiki.elecfreaks.com/en/microbit/sensor/planet-x-sensors/Plant_X_EF05018 |
| [EF-Feeder] | Hackster "micro:bit remote feeder" build (feeder exemplar basis) | https://www.hackster.io/EFELECFREAKS/how-to-build-a-micro-bit-remote-feeder-with-kidsiot-7470c4 |
| [EF-Lighthouse] | Elecfreaks Nezha Pro Ocean Kit case 07 "lighthouse" (LightTower basis) | https://wiki.elecfreaks.com/en/microbit/building-blocks/nezha-pro-ocean-kit/case-07-lighthouse |
| [pxt-nezha2] | MakeCode extension source (Nezha2) | https://github.com/elecfreaks/pxt-nezha2 |
| [pxt-planetx] | MakeCode extension source (PlanetX) | https://github.com/elecfreaks/pxt-planetx |
| [mc-reactive] | MakeCode micro:bit reactivity / event model reference | https://makecode.microbit.org/device/reactive |

## 4. Internal / prior-work sources

| Key | What | Location | Owner |
|---|---|---|---|
| [Exemplar-Feeder] | "The Gate Guardian" feeder tutorial (MakeCode era) | `/Users/alex/Development/Isana/Crash-Sensor_Mini-Challenge/` | Alex + earlier AI persona |
| [Exemplar-Lighthouse] | "Lighthouse Keeper Mode" transfer-learning tutorial | `/Users/alex/Development/Isana/LightTower-challenge/` | Alex + earlier AI persona |

Access `internal`, redistribution: Alex's own work (his call whether/how to publish). Digest: `digests/exemplar-tutorials_pedagogy-and-stack_digest.md`.

---

## Licensing & redistribution status (commit-decision table)

| Source | Type | Access | Redistribution | Committed? | Local path |
|---|---|---|---|---|---|
| [Scheiter-TTT-2026] transcript (DE) | media transcript | open | **no** (copyrighted audio) | **yes — should untrack** | `materials/They Talk Tech transcript.txt` |
| [Scheiter-TTT-2026] translation (EN) | derivative transcript | open | **no** | **yes — should untrack** | `materials/They Talk Tech transcript_EN.txt` |
| [Scheiter-TTT-2026] our digest | our writing | — | yes (ours) | yes | `digests/scheiter-they-talk-tech_digest.md` |
| [Kosmyna-2025] Your Brain on ChatGPT | preprint | open (arXiv) | TBD (confirm arXiv license line before committing) | no | `materials/papers/Kosmyna-2025_…pdf` |
| [Bauer-2025-hype] Looking beyond the hype | journal article | open | **yes — CC-BY 4.0** (may be force-added if desired) | no (kept ignored by default) | `materials/papers/Bauer-Scheiter-2025_…pdf` |
| Research iteration-1 arXiv/author-copy corpus (§2a, 18 further PDFs) | preprints / author copies | open | TBD per item (arXiv non-exclusive licenses vary; author copies are publisher-copyright) | no | `materials/papers/*` (git-ignored) |
| Hardware wiki/GitHub refs (§3) | web | open | n/a (link-only) | n/a | — |
| Exemplar tutorials (§4) | prior work | internal | Alex's own | external | Isana folders |

### Recommended actions (Alex's decision)
1. **Untrack the transcript + translation** (keeps local copies; removes from future commits):
   `git rm --cached "materials/They Talk Tech transcript.txt" "materials/They Talk Tech transcript_EN.txt"`
   then uncomment the matching lines in `.gitignore`. If the repo was already pushed, scrub them from history separately.
2. Before committing any file under `materials/papers/`, confirm a permissive license and record it above.
3. Confirm the publication scope of the `circuitpython-experiments` repo (see `README.md` § Publication scope caution).
