# notes_v0.3 — merge extractor (`returns/extract-plan-v0.0-gaps.md`)

**Date:** 2026-09-04. **From:** `plan_v0.2.md`. Extractor scored **v0.0**; several rows already fixed in v0.1–v0.2.

## Observe

Extractor: 10 lock-miss, 13 digest-miss, 1 soft contradiction, 1 over-committed-shape, 4 undecoded. Dispatch complete vs brief (structured inventory, no decisions). **Verdict:** composer-class extract was complete enough to merge; no re-run.

## R1 — apply / drop

| Extract | Disposition |
|---------|-------------|
| G1 Exp14 as project **template** | Apply — Fix; executing chat copies template bits, not this planning chat |
| G2 encoding cap 8; no 4×4/6×6/7×7 | Apply — Fix |
| G3 Exp09 = LUT/orientation/pictograms only | Apply — Fix |
| G4 arrows independently replaceable; `core`/`bitmap_codec` geometry-agnostic except hooks | Apply — Fix |
| G5 sub-agents authorized | Apply — one loop line (already in loop-setup) |
| G6 max 5 agent scripts | Apply — Fix |
| G7 firmware in Fix | Already in v0.1 |
| G8 human testing rare/strategic | Apply — Fix |
| G9 pictogram port | Covered by G3 |
| G10 motor/light deferred | Apply — Fix (G6) |
| G11–G13 pause / letters / A–D names | Mostly in v0.2; tighten: all four `on_*_pressed` **names** exist; overnight fire-test C/D only |
| G14 release handlers as P6 gate | **Drop** — overnight is press=FALL; keep release as optional API (provisional). Adding as gate expands criteria |
| G15 trace shape as required sequence test | **Drop as overnight gate** — G7 stand-in stays names-only (v0.1 criteria-revision). Mention as what a later sketch will do |
| G16 four compass arrows | Apply — names N/S/E/W exist (bitmaps), not “one arrow” |
| G17 `overall_goal.md` | Apply — header spec pointer |
| G18 digest-complete gate | Historical; P0 done. Skip in execution plan |
| G19 reject Exp09 `Button` student API | Apply — P5 |
| G20 re-open A1–A4 at P-phase | Apply |
| G21 full LightTower sketch overnight | **Drop** — would expand overnight target; stand-in remains |
| G22 library must not own `LighthouseMode` | Apply — Fix |
| G23 full copy path | Already in v0.1 |
| G24 digits 0–2 vs 0–9 | Keep 0–9 (superset of digest 0–2). Not a target change |
| G25 visual-fixture rationale | Apply — one phrase, still not a named helper |
| G27–G29 decode LUT / codec / dispatcher / visual fixture | Apply — glosses |
| G30 loop-setup | Header already |

**Criteria still right?** Yes. Did not add release-handlers or Watch I sketch as overnight gates (would be scope expansion → escalate; we decline).

## R2 / R3

Decode LUT = Look-Up Table, codec = `bitmap_codec` ASCII↔column-major, dispatcher = key-index→A/B/C/D, visual fixture = hand-constructed expected indices not derived from the same formula. Trim: do not paste extractor table into the plan.

## Change-magnitude

- **Breadth:** Fix (several locks), P5, success criteria (compass arrows + handler names), header spec, glosses.
- **Depth:** T2 (constraints added; criteria not expanded except G16 names).
- **Unknowns discharged:** 0.
- **Trend:** filling lock holes. **Verdict:** `converging`.
- **Reflection:** one confirm pass (v0.4). If ≤T1 and no new lock-miss, promote `plan_v1.0.md` + risk scan.

## Learning

Nothing new beyond digest-collection extracts. Extractor confirmed v0.0 under-specified Fix layer — **record:** lock-misses belong in Fix, not only in phases.
