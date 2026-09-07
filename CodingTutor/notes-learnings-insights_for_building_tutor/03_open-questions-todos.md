# Open questions & TODOs — CodingTutor

Living list. Resolved items move to the session log / picture; new ones append here.

## Next steps
1. **DONE (2026-07-15)**: ingested `materials/They Talk Tech transcript.txt` → English translation
   (`..._EN.txt`) + detailed digest (`digests/scheiter-they-talk-tech_digest.md`) + high-level overview
   (`04_pre-design-considerations-and-research-agenda.md`). Short summary mirrored into persona memory.
2. **DONE (2026-07-15) — research loop iteration 1**: assembled + downloaded a 17-source corpus across all agenda cells
   (Scheiter's own AI-effects synthesis, Your Brain on ChatGPT, LLM tutoring systems, programming-ed pedagogy, SRL/teachable
   agents, productive failure, cognitive load, metacognitive laziness). Catalog + triage + ranked can't-access list:
   `05_research-corpus_iteration-1.md`. Local PDFs in `../materials/papers/`. **Scheiter's *specific* tutorial-dialogue paper
   remains unconfirmed** (not in her Potsdam list) — flagged for Alex (`05...md § B.2`).
3. **NEXT — iteration 2 (deep read)**: digest the T1/T2 set (`05...md § A`), starting with Bauer/Scheiter-2025, Kosmyna-2025,
   Ruffle&Riley, Kasneci-2026-sycophancy, Weintrop-2019, Fan-2024. Produce per-source digests + fold concrete learnings into `04...`.
4. **Awaiting Alex — obtaining sources**:
   - **Email SENT to Prof. Scheiter (2026-08-14)**: friendly German outreach referencing the podcast; asked for **non-paper
     resources** — specifically a public **GitHub repository / prompts / materials / open-source system** for the
     tutorial-dialogue system she mentioned, plus pointers to further work. Awaiting reply. Capture whatever she sends into
     `materials/` + `REFERENCES.md`; if she names/points to the specific system, that closes `05...md § B.2` (the top
     unconfirmed lead).
   - **Alex to fetch** the ranked gated *publications* (`MISSING-REFERENCES.md`; also `05...md § B` / `REFERENCES.md § 2b`) —
     esp. #1 Blocks-to-Text-Misconceptions (our exact micro:bit->Python transition).
5. **Then**: compile a detailed, research-grounded tutor-design guidelines list; survey remaining secondary leads (`05...md § C`).

Only after the research: begin designing the tutor.

## Open questions (need Alex input or later resolution)
| # | Question | Why it matters | Status |
|---|---|---|---|
| Q1 | What is the current state of Alex's **CircuitPython Nezha2/PlanetX** support (API surface, motor + sensor coverage, event/interrupt model)? | Tutor content referencing concrete APIs can't be finalized without it; determines how close exemplar block-logic maps to real code. | open |
| Q2 | **Deployment model** of the tutor: its own Cursor persona / `.cursor/rules` set? A prompt template? A separate workspace? How is it invoked so it stays inactive here? | Shapes the whole build; also the mechanism that keeps Tutor ≠ assisting-persona. | open |
| Q3 | How should the tutor **measure & track the three prime skills** over time (i translate, ii critique, iii transfer)? What are the observable signals per skill? | The prompt says "track continuously" — needs a concrete, non-hand-wavy mechanism. | open |
| Q4 | How is **Alice simulated** during tutor development/testing (to validate anti-gaming behavior)? Real child, Alex role-play, or an AI Alice? | Determines how we can test the social-engineering-resistance. | open |
| Q5 | **Image generation**: can the tutor generate figures in its runtime, or must it emit prompts for Alex (as the exemplar prompts assumed for Copilot Chat)? | Exemplars lean heavily on figures; affects tutorial delivery. | open |
| Q6 | Where are the **tutorials/tasks authored and stored** for the CircuitPython era — new versions of feeder/lighthouse, or new problems? | Defines the problem corpus the tutor works from. | open |
| Q7 | How to **operationally classify an Alice-turn** as "understanding the problem" (help freely) vs "seeking the solution" (withhold)? | This boundary is exactly where social-engineering attacks land. Raised by the Scheiter digest. | open |
| Q8 | Which CircuitPython/hardware concepts are **must-internalize** vs **fine-to-look-up**? | Scheiter: can't reason without base knowledge in-head; needs Q1 (the actual API). | open (depends on Q1) |

## Notes to self (assisting persona)
- Keep the anti-gaming discipline (picture §3) front-of-mind in *every* future design decision — it is the single most
  emphasized, easiest-to-violate requirement.
- Ground pedagogy claims in cited research before elevating them to design guidelines (Alex is not the domain authority
  here; use the evidence-status discipline).
