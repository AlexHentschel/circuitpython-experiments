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

## TODOs: student tooling stack (editor, linter, checks)
Added 2026-10-02 (Alex). Not started.

- **T1 — Investigate a linter rule that flags an un-awaited `async def` result.** Wanted rule: the value returned by calling an `async def` function or method must be (a) preceded by `await`, or (b) passed to `asyncio.run(...)` / `asyncio.create_task(...)` / `gather(...)`, or (c) assigned to a variable (and then used). A bare call statement is the error. Motivation: S1 below, the forgotten `await` is silent on the board. Questions for the investigation:
  1. Pyright's `reportUnusedCoroutine` already flags a *call statement* whose coroutine result is unused (docs: default `"error"` in basic/standard mode, source `microsoft/pyright` `docs/configuration.md`, fetched 2026-10-02). Does it cover our case in Cursor/VS Code with the CircuitPython stubs (the `async def` methods of `display` must resolve to real coroutine types)? Does it miss "assigned but never used" (`x = display.show_string(...)`)?
  2. Which other tools have a rule (Ruff, flake8-async, Pylint)? Can a custom rule be written, and how hard is a small AST check (`Expr(Call)` statement whose callee resolves to an `async def`)?
  3. Is the diagnostic visible to a 12-year-old: wording, severity (error squiggle vs hint), and does it run in the editor the student uses without setup?
  4. False positives: fire-and-forget `create_task(...)` returns a Task (not a coroutine), so it is not flagged; `lambda: display.show_string(...)` passed to `forever` must not be flagged.
  5. Where does the config live (per-experiment `pyrightconfig.json` or workspace settings; note VS Code does not merge arrays across settings layers)?
  Outcome wanted: a recommendation plus, if viable, the config or rule file shipped with the student project template. Related: persona concept `concepts/tooling.md` (stub completion, Pyright) and exp16 `ai-notes/`.

## Tutor screening items (watch-list for Alice's code)
Items the tutor persona should screen for when reviewing Alice's programs or error reports. Added by the assisting persona. Each is a Python/CircuitPython *language* fact, so the tutor may explain it directly under the tutoring contract. The algorithmic fix stays Alice's.

### S1 — Forgotten `await` (added 2026-10-02): silent failure, no error message
- **Symptom Alice reports**: "the display does nothing", "the text never shows", "my delay is ignored", "the program just ends". No traceback.
- **Cause**: calling an `async def` function without `await` (or without `asyncio.run(...)` / `asyncio.create_task(...)` at the top level) only *creates* a coroutine object. Its body never starts. Desktop Python prints a "coroutine ... was never awaited" warning. The board is expected to print nothing (`unverified` on the board; see Exp16 persona memory `concepts/circuitpython-runtime.md`).
- **Where it bites in the Exp16 library**: every Tier 2 display call (`show_string`, `show_icon`, `show_number`, `scroll_image`, `pause`, ...) and `display.forever(cb)` (being made `async`). Each needs `await` inside a coroutine, or `asyncio.run(...)` at top level. Sync Tier 1 calls (`render_icon`, `set_pixel`, ...) must *not* be awaited. Likewise `asyncio.sleep(1)` with no `await` gives no delay, and the button `run()` methods need `await` / `gather` / `create_task`.
- **Screen for**:
  1. a bare `display.show_...(...)` or `asyncio.sleep(...)` statement inside a coroutine with no `await`;
  2. `async def` handlers that are registered but never reached;
  3. a script whose last line calls an async function directly instead of `asyncio.run(main())`;
  4. the opposite error, `await` on a sync call (this one does raise a `TypeError`).
- **Suggested tutor move (to be checked against the anti-gaming rules)**: do not just patch the line. Name the symptom ("nothing happened, and no error"). Ask Alice what she expects a function call to do. Let her find the missing `await` herself with a one-line experiment: `print(display.show_string("Hi"))` shows `<coroutine object ...>`. Reflection question: "what is the difference between *calling* a function and *running* it?" (prime goal (i): precise program steps).
- **Status**: mechanism `evidence-supported` for CPython; "silent on CircuitPython" is `unverified` until observed on the board.
- **Tooling counterpart**: TODO T1 above (a lint rule would catch this before Alice runs the code).
