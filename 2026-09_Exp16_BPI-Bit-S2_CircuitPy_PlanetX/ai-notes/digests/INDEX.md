# Digests — cold-AI knowledge pack (Exp16 first milestone)

**Status:** live 2026-09-04. **Purpose:** one-hop extracts so a cold AI can adapt Exp14’s display lib + write an async PlanetX button lib without re-scanning the source trees.
**How to check:** every row below has a file; if a digest is missing, collection is incomplete and the plan-refinement loop must not start.

Working-notes root: `/Users/alex/Development/VsCode/CircuitPython/2026-09_Exp16_BPI-Bit-S2_CircuitPy_PlanetX/ai-notes/`
Locks: `../NOTES.md`. Spec: `../../Notes/overall_goal.md`.

| File | Source (read, do not copy wholesale) | What a cold AI needs from it |
|------|--------------------------------------|------------------------------|
| `exp14-display-lib.md` | Exp14 `lib/display/` (now also copied at `../../lib/display/`) | Two-tier API, swap units, hooks in `core.py`, host-test split |
| `exp09-lut-icons.md` | Exp09 `lib/display_v0.py`, `lib/microbit.py`, PlanetX `button.py` | 5×5 LUT formula, orientation, `Image.*` names, C/D pin hypothesis |
| `lighttower-student-ops.md` | Isana LightTower `2026-05-15_lighthouse-keeper_requirements_v1.0.md` + tutorial `…_v1.0.md` | Watch I student operations the PoC must offer |
| `button-research.md` | `Notes/Button_chat.md` + `CodingTutor/mini-project-scatches/button-library.md` | Public API shape vs backend; why micro:bit-v2 ChatGPT rec does **not** transfer |

Font recommendation (source not locked): lands in the execution plan after these digests; facts that constrain it live in `exp14-display-lib.md` (FreeMono-at-8px fails) + `exp09-lut-icons.md` (MakeCode 5×5 / Exp09 `generate_font.py`) + persona `concepts/fonts.md`.
