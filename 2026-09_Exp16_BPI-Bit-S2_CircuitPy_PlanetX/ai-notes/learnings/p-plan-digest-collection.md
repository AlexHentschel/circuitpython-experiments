# Learning — P-plan (digest collection, 2026-09-04)

## Extract 1

- **Claim:** Exp14 `build_lut` stage-2 (bottom-up progressive) must not be reused on BPI-Bit-S2; Exp09 formula `idx = row + 20 - column * 5` is the wiring.
- **Evidence:** Exp09 `lib/display_v0.py` docstring grid vs Exp14 `geometry.py`.
- **Status:** `evidence-supported` (code); on-device Exp16 still open.
- **Guideline touched:** G2 (LUT in swap files)
- **Action:** keep
- **Date:** 2026-09-04

## Extract 2

- **Claim:** Pitchfork-5x5 is GPLv3 (`evidence-supported`). Combining converted glyphs into `lib/` is likely a combined work — **not** a coarse ban; needs a written case. DAL `pendolino3` is **MIT** and is the low-friction default if the notice is vendored.
- **Evidence:** Exp09 `microbit.py` comment; DAL `MicroBitFont.cpp` header + repo LICENSE fetched 2026-09-04. Apache-2.0 hypothesis **invalidated**. Alex restated the bar 2026-09-04: copyleft-into-`lib/` after a case, not “GPLv3 files forbidden.”
- **Status:** MIT on DAL `evidence-supported`; GPLv3 on pitchfork `evidence-supported`; combination-into-`lib/` `unverified` until P3 case
- **Guideline touched:** none (product/license).
- **Action:** keep (P3 default DAL + MIT notice; pitchfork only after written case)
- **Date:** 2026-09-04 (restated same day)

## Extract 3

- **Claim:** ChatGPT micro:bit-v2 `digitalio`+debouncer+`update()` recommendation does not transfer; BPI-Bit-S2 should follow the same chat’s RP2350 `keypad.Keys` + asyncio pump, with 10.3.0 confirm deferred to P-device.
- **Evidence:** `Notes/Button_chat.md`; NOTES recommended backend; 10.0.3 support matrix (persona Session 1).
- **Status:** backend `unverified` on 10.3.0
- **Guideline touched:** G5 / sync-vs-async hazard
- **Action:** keep
- **Date:** 2026-09-04
