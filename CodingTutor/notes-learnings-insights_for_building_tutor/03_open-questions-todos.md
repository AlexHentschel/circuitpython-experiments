# Open questions & TODOs — CodingTutor

Living list. Resolved items move to the session log / picture; new ones append here.

## Next steps (explicitly queued by Alex — do NOT start until directed)
1. **Ingest `materials/They Talk Tech transcript.txt`**: translate to English → create a detailed digest in
   `digests/` (focus: concrete recommendations for helping children/people learn) → distill a very short
   domain-coverage summary into persona memory (`ai-persona` `memory/projects/coding-tutor/CONTEXT.md`).
2. **Research the professor** featured in that transcript: study their work in detail, extract concrete learnings,
   fold into the knowledge base.
3. **Compile a detailed guidelines list** for designing the tutor (grounded in the research above).
4. Broader: survey **recent research on learning/tutoring of early-high-school children**, esp. teaching software
   engineering to kids with prior coding experience.

Only after the above: begin designing the tutor.

## Open questions (need Alex input or later resolution)
| # | Question | Why it matters | Status |
|---|---|---|---|
| Q1 | What is the current state of Alex's **CircuitPython Nezha2/PlanetX** support (API surface, motor + sensor coverage, event/interrupt model)? | Tutor content referencing concrete APIs can't be finalized without it; determines how close exemplar block-logic maps to real code. | open |
| Q2 | **Deployment model** of the tutor: its own Cursor persona / `.cursor/rules` set? A prompt template? A separate workspace? How is it invoked so it stays inactive here? | Shapes the whole build; also the mechanism that keeps Tutor ≠ assisting-persona. | open |
| Q3 | How should the tutor **measure & track the three prime skills** over time (i translate, ii critique, iii transfer)? What are the observable signals per skill? | The prompt says "track continuously" — needs a concrete, non-hand-wavy mechanism. | open |
| Q4 | How is **Alice simulated** during tutor development/testing (to validate anti-gaming behavior)? Real child, Alex role-play, or an AI Alice? | Determines how we can test the social-engineering-resistance. | open |
| Q5 | **Image generation**: can the tutor generate figures in its runtime, or must it emit prompts for Alex (as the exemplar prompts assumed for Copilot Chat)? | Exemplars lean heavily on figures; affects tutorial delivery. | open |
| Q6 | Where are the **tutorials/tasks authored and stored** for the CircuitPython era — new versions of feeder/lighthouse, or new problems? | Defines the problem corpus the tutor works from. | open |

## Notes to self (assisting persona)
- Keep the anti-gaming discipline (picture §3) front-of-mind in *every* future design decision — it is the single most
  emphasized, easiest-to-violate requirement.
- Ground pedagogy claims in cited research before elevating them to design guidelines (Alex is not the domain authority
  here; use the evidence-status discipline).
