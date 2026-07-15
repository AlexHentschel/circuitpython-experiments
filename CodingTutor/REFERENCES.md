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

## 2. Primary academic works to locate (research-agenda leads)

These are the P1 leads from `notes-learnings-insights_for_building_tutor/04_pre-design-considerations-and-research-agenda.md § E`.
Citations to be completed once located; gated PDFs go to `materials/papers/` (git-ignored).

### [Scheiter-tutorial-dialogue] — highest-value lead `[to locate]`
- Katharina Scheiter and colleagues' work on **LLM-based tutorial-dialogue systems** (referenced in the podcast: "we tried
  to build a system that engages the learner in a tutorial dialog"; suppressing sycophancy; the endless-question-loop
  failure mode). Locate via her Univ. Potsdam / Leibniz-IWM Tübingen publication list, ORCID, or Google Scholar.
- **Access**: likely mix of `open`/`gated`. **Redistribution**: `TBD` per paper.

### [Scheiter-profile] — author background `[to locate]`
- Katharina Scheiter: educational + cognitive psychology, learning with digital media, multimedia learning, eye-tracking,
  adaptive / intelligent tutoring systems. Formerly Leibniz-Institut für Wissensmedien (IWM), Tübingen; honorary professor,
  School of Education, University of Nottingham. Pull her key review/framework papers (cognitive load, multimedia,
  self-regulated learning with media).

### [YourBrainOnChatGPT-2025] — the EEG essay study `[to verify]`
- Referenced in the episode ("Your Brain on ChatGPT", small-n EEG, essay writing, brain-first vs AI-first reversal).
  **Best-known details (UNVERIFIED — confirm before citing)**: Kosmyna, N., et al. (2025), MIT Media Lab, arXiv preprint,
  title approx. "Your Brain on ChatGPT: Accumulation of Cognitive Debt when Using an AI Assistant for Essay Writing Task."
- **Access**: likely `open` (arXiv). **Redistribution**: `TBD` (arXiv preprints are usually redistributable under their
  posted license — confirm the specific license line).

### Further research-agenda topics (see `04_...md § E` for the full P1–P3 list)
Intelligent Tutoring Systems / cognitive tutors + LLM hybrids; programming-education pedagogy for novices with prior
experience (PRIMM, Use-Modify-Create, worked-examples-with-fading, block→text transition); self-regulated learning &
metacognition (monitoring/regulation); desirable difficulties (Bjork) & productive failure (Kapur); self-explanation
(Chi) & learning-by-teaching / teachable agents (Betty's Brain); novice overconfidence / calibration (Kruger & Dunning);
cognitive load theory & multimedia learning (Sweller; Mayer); "metacognitive laziness" / AI-reliance literature.
→ add full citations here as each is located.

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
| [Scheiter-tutorial-dialogue] | paper(s) | TBD | TBD per paper | no | `materials/papers/…` when downloaded |
| [YourBrainOnChatGPT-2025] | preprint | open? | TBD (confirm arXiv license) | no | `materials/papers/…` |
| Hardware wiki/GitHub refs (§3) | web | open | n/a (link-only) | n/a | — |
| Exemplar tutorials (§4) | prior work | internal | Alex's own | external | Isana folders |

### Recommended actions (Alex's decision)
1. **Untrack the transcript + translation** (keeps local copies; removes from future commits):
   `git rm --cached "materials/They Talk Tech transcript.txt" "materials/They Talk Tech transcript_EN.txt"`
   then uncomment the matching lines in `.gitignore`. If the repo was already pushed, scrub them from history separately.
2. Before committing any file under `materials/papers/`, confirm a permissive license and record it above.
3. Confirm the publication scope of the `circuitpython-experiments` repo (see `README.md` § Publication scope caution).
