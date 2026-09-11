# Session Log — circuitpython-exp16-planetx

Per-project session memory for **exp16** (BPI-Bit-S2 CircuitPython + PlanetX, LightTower PoC). Behavioral/process: `../../universal/`. Domain: `../../concepts/`. Roster: `../_INDEX.md`.

## Sessions

## 2026-09-11: Session 16 — [exp16] (round-1 device window opened; serial console live; sandbox device-I/O permission finding)

- Partition CSV tables distilled to `../../concepts/tooling-4mb-partitions.md`; live pointers retargeted off `ai-notes/esp32-4mb-circuitpy-vs-ota/`. Calibration: Exp16 is not confidential (dump-all deferred to that wrap-up).
- Reconciliation from Session 15 **resolved**: Alex confirmed unit **UID `0740D10F1BE9`** (already CP 10.3.0 per Session 14) is the board for round 1. PlanetX cable **not yet connected** — pending on his end.
- Alex reshaped round-1 sequencing (supersedes the Session-11/15 item-1–9 list): (1) confirm serial console still works, (2) minimal PlanetX-button PoC on the **existing** NeoPixel `code.py` (buttons drive the display-lib review process, not the other way round), (3) if buttons work: full CIRCUITPY backup into a new `ai-notes/` subfolder, (4) wipe old code + all libraries, fresh install of this project's `lib/`. Step 4 is the destructive-ops hard gate — not actioned, flagged for a dedicated confirmation when reached. `BRIGHTNESS` default changed **0.20 → 0.05** (Alex's call, overriding the `plan_v1.0.md` Fix-layer value).
- **Step 1 done.** Found the "own setup" Alex half-remembered: `.vscode/tasks.json` **Serial Monitor (miniterm)** task already exists in Exp14/Exp11/Exp15 (`pyserial-miniterm` from the pinned venv; `screen` fails "no PTY" in Cursor's terminal) — Exp16 never had it (P7 was never scaffolded here). Created `2026-09_Exp16_…/.vscode/tasks.json` (same two tasks, mirrored) for Alex's manual workflow. Created `2026-09_Exp16_…/scripts/read_serial_log.py` (git-tracked, one of the ≤5 agent scripts) as the non-interactive sibling for autonomous reads — VID-based port auto-detect, bounded duration, **never** calls `.write()`. Confirmed live: captured board's REPL/console output (`code.py`, CP 10.3.0, "Color snake" — the pre-existing NeoPixel sketch, not this project's library).
- **New tooling finding, persisted:** opening the raw serial device node (`/dev/cu.usbmodem*`) via `pyserial` through the Shell tool raised `PermissionError` under the default sandbox; `required_permissions:["all"]` fixed it. Enumeration (`ls /dev/cu.*`) and mounted-volume file reads (`boot_out.txt` on CIRCUITPY) did **not** need elevation — restriction is specifically on raw device *opens*. Recorded `universal/WORKING_STYLE.md § Workflow & Artifacts` (new row, sibling of the file-mutation-approval-gate row) + a cross-reference pointer in `concepts/tooling.md`. Scoped deliberately narrow (single board/tool/OS) per Alex's explicit ask not to over-generalize a sandbox work-around.
- **Task confirmation:** validated `.vscode/tasks.json` (JSONC-valid, port auto-detect finds `/dev/tty.usbmodem0740D10F1BE91`, `pyserial-miniterm` binary present) but could **not** fully exercise the interactive task from my own shell — `pyserial-miniterm` needs a real PTY (`termios.error`), which my backgrounded Shell-tool calls don't have but VS Code's integrated terminal does (same root cause as the pre-existing "screen fails, no PTY" task comment). `pkill -f pyserial-miniterm` (the disconnect task) also needs `required_permissions:["all"]` under the default sandbox (process-list introspection) — another instance of the device/process-access sandbox pattern; not force-retried since no orphan process existed to clean up. **Alex confirmed 2026-09-11**: ran `Serial Monitor (miniterm)` from VS Code's Run Task picker (folder `2026-09_Exp16_BPI-Bit-S2_CircuitPy_PlanetX`) — connects to `/dev/tty.usbmodem0740D10F1BE91` at 115200, streams live `code.py` output (`Color snake ..`). **Task fully confirmed working; gap closed.** Both disconnect paths confirmed by Alex too: `Ctrl+]` inside the terminal, and the `Serial Monitor: disconnect (kill miniterm)` task.
- **New `esptool` venv named (Alex, 2026-09-11):** `/Users/alex/Development/PythonVEs/MicroControllers` (hosts `esptool` 5.1.0). Recorded persona-wide (`universal/WORKING_STYLE.md`): use freely, but **installs need explicit approval each time** (unlike the `CircuitPython_3.13_VsCode` venv, which is blanket pre-authorized for installs) — and **esptool itself may probe (read-only) autonomously but must never write/erase/flash without per-instance explicit approval**, tool-specific carve-out under the Destructive-action hard gate.
- **PlanetX C/D physically connected (Alex, 2026-09-11):** Nezha Pro / Nezha v2 breakout on `J3` → BPI-Bit-S2. Cross-checked against `Notes/bpi_bit_v2_goldfinger.jpg` + LightTower reference figure (`ButtonSensor_on_J3_event.png`, MakeCode `MICROBIT_ID_IO_P13`/`P14` + `MICROBIT_PIN_EVT_FALL`): P13→GPIO36, P14→GPIO37 — matches the firmware `pins.c` mapping already on record (Session 4/5c), no new dispute. **K2 firmware-naming half already resolved; cable half now done too** — full discharge still needs the on-device press test (step 2 below). Same Nezha breakout family as `coding-tutor`'s target setup ("Nezha2") — noted in `crossref/BY_TOPIC.md`.
- **Next:** step 2 — minimal PlanetX-button PoC on the existing `code.py` (will ask before writing to the device).

## 2026-09-11: Session 15 — [exp16] (`ai-notes/` recovered from git history; round-1 coverage reconciliation flagged)

- Alex confirmed the Session 11 empty-`ai-notes/` flag was his own unintentional on-disk `rm -rf` ("my mistake"), not an agent action. Asked to (a) recover via git history, (b) re-persist current context.
- **Recovered**: all 34 files, byte-for-byte, from `ae8ac09^` (= `aaf38ea`, the last commit before the Session-10 untrack) via `git show <rev>:<path>` per file — pure blob reads, no index/tracking change; folder stays untracked/gitignored as intended.
- **Pitfall hit + documented**: `git ls-tree`/`git show <rev>:<path>` with a repo-root-relative pathspec while `cwd` is already inside the experiment subfolder silently returns empty (no error) — must run from the repo root. Detail: exp16 `ai-notes/learnings/2026-09-11_ai-notes-deletion-recovery.md`.
- Brought `ai-notes/INDEX.md`/`NOTES.md` current with Session 10/11 (flagged `design/student-api-portability.md` stale — superseded by committed `Notes/student-api-portability.md`) — **then discovered, while doing so, that Sessions 12–14 (this file, other chats, same day) already opened the device window**, something this chat's own scope (Session 11 handoff) had explicitly deferred. Added an addendum to `ai-notes/NOTES.md` folding in the Session 12–14 findings (unit `0740D10F1BE9`: CP 10.0.3 → 10.3.0 via TinyUF2 Path A, CIRCUITPY preserved; multiple physical units exist, not assumed to match).
- **Reconciliation flagged, not resolved silently:** in *this* chat's round-1 discussion, Alex answered "board still needs flashing" to a direct question — conflicting with the Session 14 record for `0740D10F1BE9`. Surfaced to Alex rather than guessing which unit round-1 targets. Round-1 coverage list from Session 11 (in `ai-notes/NOTES.md`) stays **proposed, not agreed**, pending that clarification.

## 2026-09-11: Session 14 — [exp16] (teach TinyUF2 + esptool 5 upgrade; no flash yet)

- Alex: walk through CP **10.3.0** + TinyUF2 upgrade with **esptool**, not do it for him. Current board: CP **10.0.3** `bpi_bit_s2`.
- Research: board page lists CP 10.3.0 + TinyUF2 **0.35.0**; 4MB Espressif needs TinyUF2 ≥ **0.33.0**. UF2 + combined.bin URLs HTTP 200. esptool **5.1.0**: hyphenated cmds, auto-verify, `--before no-reset` in ROM mode. BananaPi Bit-S2 docs that say `--chip esp32s3` are **wrong**.
- BPI TinyUF2 entry: tap RESET then BOOT (~1 s, purple) → `BITS2BOOT`. `combined.bin` @ 0x0 **wipes CIRCUITPY**.
- Seeded `concepts/tooling.md`. Did **not** erase/flash. Next: Alex runs the walkthrough; re-probe `boot_out.txt` after.
- Alex: **multiple** BPI-Bit-S2s — 10.0.3 was UID `0740D10F1BE9` only. Path A (CP `.uf2`) does **not** update TinyUF2; that is `update-tinyuf2-*.uf2` on `BITS2BOOT`, or Path B `combined.bin`.
- Path A **done** on UID `0740D10F1BE9`: `boot_out.txt` = CP **10.3.0** (2026-08-31 build). CIRCUITPY listing still `code.py`/`lib`/`sd`/`settings.toml`; Alex: prior LED-icon sketch still running. Same-layout UF2 copy preserved the filesystem. This unit is off the 10.3.0 flash lock.
- CIRCUITPY size on that unit: `diskutil` **983040 B**; `df` 941 KiB total / 197 KiB used / 745 KiB avail. TinyUF2 `Flash Size 0x002C0000` is firmware, not CIRCUITPY.
- **Correction (Alex):** pre-0.33 TinyUF2 does **not** yield a larger CIRCUITPY. Dual-OTA vs no-OTA: `ota_0` 1408K+1408K → 2816K; `ffat` stays 960K. Agent had conflated firmware growth with user-FS size. Tables: `../../concepts/tooling-4mb-partitions.md`.

## 2026-09-11: Session 13 — [exp16] (firmware ID: CircuitPython 10.0.3)

- Second USB cable → board enumerates. **CircuitPython**, not MicroPython.
- `boot_out.txt`: `Adafruit CircuitPython 10.0.3 on 2025-10-17; BPI-Bit-S2 with ESP32S2` / `Board ID:bpi_bit_s2` / UID `0740D10F1BE9` / MAC `70:04:1D:F0:B1:9E`.
- USB: `/dev/cu.usbmodem0740D10F1BE91` VID:PID=`303A:80E6` product `BPI-Bit-S2` mfr `BananaPi`. Volume `/Volumes/CIRCUITPY`.
- Drive already has user `code.py` (NeoPixel Hello World, `board.NEOPIXEL`, brightness 0.05), `lib/{neopixel.mpy,adafruit_pixelbuf.mpy,adafruit_led_animation/}`, empty `sd/`. **Behind Exp16 lock (CP 10.3.0).** No flash this turn.

## 2026-09-11: Session 12 — [exp16] (USB firmware ID attempt: board not enumerating)

- Alex asked what firmware is on the plugged-in BPI-Bit-S2 (CircuitPython vs MicroPython). USB window is open for **read-only** ID; no flash/erase.
- Host: `esptool` **5.1.0** present in `/Users/alex/Development/PythonVEs/MicroControllers` (confirmed `esptool` + `esptool.py`).
- Probe (this Mac): **no CIRCUITPY volume**; pyserial saw no USB VID/PID serial (only Bluetooth/Jabra/Jawbone/debug-console); IOUSB tree = hub + Logitech receiver + C920 + CMI LAN. No Espressif (`0x303A`) / Adafruit (`0x239A`) device.
- Cannot ID firmware until the board enumerates. Next: USB-C on the **board back** (not a micro:bit USB tray), data cable, then re-probe. If still dark: hold **BOOT**, tap **RESET** (ROM CDC) → `esptool chip-id` / REPL banner. ID rule: CIRCUITPY + “Adafruit CircuitPython” = CPy; CDC-only + “MicroPython” banner = MPy.

## 2026-09-09: Session 11 — [exp16] (handoff: first hands-on coverage discussion)

- **Next chat (discussion only):** first round of **human / on-device** tests — what they should cover. Not P1–P6 (host-green). Not P7 `.vscode/` / shared CircuitPythonSync. Do **not** USB-probe, flash, or deploy until Alex opens that window in that chat.
- Plan pointers: `ai-notes/plan/plan_v1.0.md` P8 + Known unknowns **K1** (bundle `asyncio`), **K2** (PlanetX C/D cable), **K5** (onboard A/B); cadence **P-device / P-human**. Locks: `ai-notes/NOTES.md` (flash 10.3.0 first; human testing rare/strategic).
- Deliverable of that chat: an agreed coverage list (and what is *out* of round 1). Implementation / `code.py` / flash only if Alex then asks.

## 2026-09-09: Session 10 — [exp16] (`ai-notes/` split + untrack)

- Grant `G-2026-09-08-1` (`untracking granted`). Lifted student-API guidelines to committed `Notes/student-api-portability.md`; checkpoint into README Status; emulation headlines into CONCLUSIONS (unverified). README no longer links into `ai-notes/`.
- `git rm -r --cached` on `ai-notes/` (34 files); working tree kept. Gitignore: experiment `.gitignore` + repo `**/ai-notes/`. Commit `ae8ac09`. History scrub was prepped + verified locally (`G-2026-09-09-1`) but **abandoned** — Alex clarified the ai-notes are noise, not confidential, and may remain in GitHub history. **Revised non-destructive plan:** fast-forward `git push origin alex/display-mvp_5x5` (publishes `ae8ac09`); master untouched; no force-push. Optional `rm -rf` on-disk `ai-notes/` (gitignored). Runbook: `/tmp/circuitpython-experiments-scrub-20260909-INSTRUCTIONS.md`.
- Local notes remain the plan/locks/cadence store (`INDEX.md`, `NOTES.md`, `plan/`).

## 2026-09-07: Session 9 — [exp16] (persona-less AI persist: emulation research)

- Alex asked a **persona-less** LLM (Exp16 folder only) to research and persist into `ai-notes/`. This chat analyzed the uncommitted writes, then applied agreed trims (no merge / no new folder / no persona copy).
- **Payload (kept):** `ai-notes/design/rp2350-emulation-macos.md` (hypothetical RP2350 switch) and `ai-notes/digests/local-mcu-emulation.md` (current `bpi_bit_s2` / pre-P8). Different chips; same shape of answer (no stock-CP emulation that discharges P8; host-pytest stays the oracle).
- **Trims applied:** dropped both README Further-reading rows; folded NOTES Pre-P8 heading into § Research pointers (not locks); load-only-if on INDEX rows, portability See-also, both research headers; RP2350 switch-table → links to portability/NOTES/Exp15; host inventory → re-run commands; reverted `plan_v1.0.md` See-also inline; `digests/INDEX.md` keeps P0 vs post-loop split. Cross-link between the two research files.
- **Not done:** move S2 digest into `design/` (would delete an untracked path; P0-vs-post-loop split already isolates it). No `concepts/tooling.md`. No persona CONCLUSIONS copy. `.kilo/` + workspace folder adds still unrelated noise.
- Headlines stay `unverified` (web self-descriptions) except `[local]` host *commands*.
- Commit `aaf38ea` + PR: https://github.com/AlexHentschel/circuitpython-experiments/pull/2 (base `master`). Left uncommitted: `.kilo/`, workspace folder adds.

## 2026-09-04: Session 8 — [exp16] (README interface JPEG)

- Alex added `Notes/bpi_bit_v2_interface_en.jpg` from BananaPi Hardware interface section. Same CC BY-SA footer as goldfinger.
- License file `Notes/bpi_bit_v2_interface_en.jpg.license` (unmodified collection item). README eye-catcher + caption attribution. JPEG not cropped/re-encoded.
- Alex: “Sidecar” in the README caption is jargon. Caption now says **License file:**. Keep “sidecar” in license/REUSE notes if useful.
- Caption wrapped in `<small>` (portable fine print; Markdown has no font-size). Stays under the figure, not a bottom-of-page footnote.
- GitHub: `<small>` is ~90% body (looks unchanged). Switched to documented `<sub>` (75%).
- Commit+push this batch on `alex/display-mvp_5x5` (icons, tests, README, interface JPEG, memory).

## 2026-09-04: Session 7 — [exp16] (MakeCode GHOST / LEFT_TRIANGLE)

- Alex: overnight `GHOST` and `LEFT_TRIANGLE` disagreed with MakeCode screenshots. `TRIANGLE` (isosceles, slot 32) was not in the attachments — left as Exp09.
- Cause: P2 ported Exp09 `Image.*` faithfully. Exp09 `GHOST` lights top corners; Exp09 `TRIANGLE_LEFT` drops the base row. Comments matched those wrong bytes.
- Fix: MakeCode grids. `GHOST` `0x1E,0x0D,0x1F,0x0D,0x1E`. `LEFT_TRIANGLE` `0x1F,0x12,0x14,0x18,0x10`.
- Tests: comment↔byte parse of all 40+8 blocks; independent MakeCode fixtures for the two names. Codec round-trip was invertibility only (shared-derivation). 149 pytest green.
- Later same session: cover/how docstrings on every test; root `README.md`; `<path-to-venv>` stub. Alex: say **experiment** not repo; host venv example is tangible only. Grep: no absolute host paths in `lib/` or `tests/*.py`. Notes: `ai-notes/learnings/host-venv-paths.md`.

## 2026-09-04: Session 6 — [exp16] (overnight P1–P6 executed; host-green)

- First action: `_constants.WIDTH = HEIGHT = 5`. LUT stage-2 = BPI-Bit-S2 `py + 20 - px*5` (rotation branches kept). Visual-fixture tests (not the wiring formula).
- Icons: Exp09 row-major → 5 column bytes. G4 names present. Arrows stay in `icons.py`.
- Font: DAL `pendolino3` MIT vendored (`lib/display/font_makecode_5/` + LICENSE). Table storage, not PCF. Pitchfork not used (no GPL case). `_glyph_columns` is a table lookup; Exp14 PCF algorithm untouched.
- `PIXEL_PIN=board.NEOPIXEL`, `BRIGHTNESS=0.20`. `_write_pattern_on_the_fly` wired as `render_pattern` hot path; `_iter_pattern_rows_fast` kept.
- Buttons: `lib/buttons.py`. Fake EventQueue FALL fires C/D. A/B names exist. No student `update()`.
- **P6:** 146 pytest green. Optional mpy-cross 10.3.0 → mpy v6.3 (`/tmp/exp16-mpy-smoke`, not in tree). Goldfinger JPEG was **already tracked** on `9806434` (handoff “uncommitted” was stale); this overnight did not touch it.
- Cadence: `ai-notes/learnings/p1-p6-overnight.md`. P7/P8 not started.

## 2026-09-04: Session 5i — [exp16] (P1–P6 overnight kickoff authorized)

- Alex: board stays unplugged overnight; do not USB-check until instructed. Ready for first autonomous plan section → `/handoff-exec-prompt`.
- **Cold-AI boot:** execute `plan_v1.0.md` P1–P6. First action `WIDTH=HEIGHT=5`. Stop at P6 host-pytest green. P7/P8 out of this executing chat. Coarse commits on `alex/display-mvp_5x5` authorized. Planning chat did **not** start implementation.

## 2026-09-04: Session 5h — [exp16] (stubs 10.3.0 + board-flash reminder)

- `circuitpython-stubs` 10.0.3 → **10.3.0** in scratch venv (PEP 561 `.pyi`; Blinka `keypad.py` still the runtime import). Types only.
- **Alex reminder:** flash BPI-Bit-S2 to CP 10.3.0 (board likely older). Pinned: NOTES banner, Open Questions, Cursor Goal, P8.

## 2026-09-04: Session 5g — [exp16] (host-venv vs MCU verification)

- Re-probed `/Users/alex/Development/PythonVEs/CircuitPython_3.13_VsCode`: **CPython 3.13.11 Miniconda**. Overnight-needed: pytest 9.1.1, pytest-asyncio 1.4.0 — present. Missing on purpose: `neopixel`, `adafruit_bitmap_font`. Blinka `keypad` present — **do not use in tests**. `import board` fails (`pkg_resources`) — keep it; that guards `display/__init__.py` off `core.py`. No `/Volumes/CIRCUITPY`. No `mpy-cross`.
- Firmware (not venv): CP **10.3.0** `bpi_bit_s2` support matrix + `pins.c` + `circuitpy_mpconfig.mk`. `keypad.Keys` + `_asyncio` compiled in; `neopixel` frozen; user `asyncio` = bundle. `board.IO13`/`IO14` = GPIO36/37.
- Overnight tests = Exp14 Tier-1 + fake EventQueue (CircuitPython `Event` shape, not Blinka) + pytest-asyncio on **CPython** asyncio. Cannot prove MCU interpreter without the board (or a unix port we do not have).
- **mpy-cross (Alex yes, 2026-09-04):** Adafruit CP **10.3.0** macOS arm64 binary in the scratch venv `bin/` (symlink `mpy-cross`). Emits **mpy v6.3**. Did **not** `pip install mpy-cross` (that wheel is MicroPython). Smoke-compiled a stub `.mpy`.
- Recorded: CONCLUSIONS (K1/K2), `concepts/circuitpython-runtime.md` asyncio split, plan K1/K2 + pins table.

## 2026-09-04: Session 5f — [exp16] (cleanup + three-runtime split)

- Alex deleted `__pycache__`, `.DS_Store`, `font_free_mono_8`. Confirmed gone.
- Correction: host venv = CPython 3.13 Miniconda, not CircuitPython. CircuitPython ≠ MicroPython; check CPy source. Blinka `keypad` in that venv is not K1 evidence.
- Recorded in `CODING_PRINCIPLES.md` (cross-runtime lift `[project]`→`[user]`) + `WORKING_STYLE.md` Domain-Specific.

## 2026-09-04: Session 5e — [exp16] (v1.0 accepted; wait to start)

- Alex: plan looks good. Will install pytest into the pinned venv himself; **do not start until he says so**. Overnight git: coarse commits on `alex/display-mvp_5x5`.
- Blocker confirmed: that venv has Python 3.13 + Blinka, **no pytest**. No board needed. No delete grant (FreeMono stays). No `.vscode` / CircuitPythonSync.

## 2026-09-04: Session 5d — [exp16] (license bar restated + Exp14 algorithm lock)

- Alex: restated font bar to **no copyleft combined into `lib/`** (not “no GPLv3 files anywhere”); case-by-case analysis; use license freedoms; don’t coarse-dismiss pitchfork.
- Plan: keep Exp14 reviewed algorithms (`_write_pattern_on_the_fly` et al.) with localized edits; comments stay; style SoT = Exp14 `lib/display/`. Host venv pinned: `/Users/alex/Development/PythonVEs/CircuitPython_3.13_VsCode`.
- Amended `plan_v1.0.md` in place (loop not reopened). Pitchfork is a candidate pending a written combination case; default P3 still DAL MIT.

## 2026-09-04: Session 5c — [exp16] (goldfinger JPEG CC BY-SA + C/D pin dispute)

- Alex: may we check unmodified `Notes/bpi_bit_v2_goldfinger.jpg` (from BananaPi Docs, CC BY-SA) into the public repo?
- Yes, as a collection item: attribution + license sidecar; ShareAlike does not infect the rest of the tree; do not relicense the JPEG. Site footer does not print a CC version. Sidecar: `Notes/bpi_bit_v2_goldfinger.jpg.license`. No git commit this turn.
- Same page contradicts Exp09 C/D = `IO13`/`IO14` (official P13/P14 = GPIO36/GPIO37). Recorded `disputed` in CONCLUSIONS; plan K2 updated; overnight still fake events. No silent winner.

## 2026-09-04: Session 5b — [exp16] (font license lock on public-repo PoC)

- Alex: PoC is in a public repo; font must allow personal hobby use **and** a copy into the repo **with license**. Glyph source still not locked.
- DAL `pendolino3` header is **MIT** (BBC/Lancaster), not Apache-2.0 — qualifies. Pitchfork GPLv3 treated as out at the time; **restated in Session 5d** (copyleft-into-`lib/` needs a written case, not a coarse ban). P3 vendors the MIT notice beside glyphs if DAL path.
- Amended `plan_v1.0.md` + `NOTES.md` + `risk-register.md` R2; loop not reopened.

## 2026-09-04: Session 5 — [exp16] (digests + plan_v1.0; PoC not started)

- P0: `ai-notes/digests/` (four files) + Exp14 `lib/display/` copied to Exp16 (new files; copy residue `__pycache__`/`.DS_Store` left — no delete grant).
- Font: recommend Lancaster DAL `pendolino3` (license header at P3); do not silently ship Exp09 pitchfork-5x5 (**GPLv3**). Source not locked.
- C/D pins remain hypothesis `board.IO13`/`IO14`.
- Plan-refinement: v0.0→v0.4 + confirm v0.5, cap 8 not hit, **converged**. Sign-off: `ai-notes/plan/plan_v1.0.md`. Risks: `ai-notes/plan/risk-register.md`. Extractor: [v0.0 gaps](296baf09-cc29-489d-8271-fd2d6e7d773f) → `ai-notes/returns/extract-plan-v0.0-gaps.md`.
- Criteria-revision: overnight host tests do **not** require importing `Display` on CPython; G7 stand-in = public names, not a Watch I sketch.
- Hard stop. No `.vscode/`, no 5×5/button implementation, no shared CircuitPythonSync, no git commit.

## 2026-09-04: Session 4 — [exp16] (handoff: execute digests + plan-refinement; this chat did not execute)

- Alex confirmed information is sufficient for (1) `ai-notes/digests/` + Exp14 `lib/display/` copy and (2) plan-refinement to `plan_v1.0.md`. Requested `/handoff-exec-prompt` for a **new** chat.
- **This session did not start execution.** Cold-AI boot surface: this bullet + `CONTEXT.md` Resumption point + `ai-notes/NOTES.md` + `ai-notes/plan/loop-setup.md`.
- Scope of the executing chat: steps 1–2 only. Hard stop at `plan_v1.0.md` presented to Alex. No `.vscode/` scaffolding, no 5×5/button implementation, no shared CircuitPythonSync edits, no git commit unless Alex asks in that chat.
- Remaining unknowns are in-scope for that chat to *research/recommend*, not escalate: MakeCode 5×5 font source; PlanetX C/D pin confirm (Exp09 `IO13`/`IO14` is the working hypothesis). On-device CP 10.3.0 `keypad`/asyncio stays a later human window.

## 2026-09-04: Session 3 — [exp16] (loop cap + approach locks; loop not started)

- Plan-refinement: cap **8** (`v0.8` max); autonomous start after digests; sub-agents authorized. Artefacts: `ai-notes/plan/loop-setup.md`. Courtesy defaults: `plan_vX.Y.md` + `notes_vX.Y.md` in `ai-notes/plan/`; briefs/returns under `ai-notes/`.
- Approach locks (AskQuestion): overnight = host tests + libs on disk; buttons API A/B/C/D, smoke C/D; font = research during digests; copy Exp14 `lib/display/` during digest collection.
- Explicit: this turn is **not** the loop start.

## 2026-09-04: Session 2b — [exp16] (standing §4 park confirmed)

- Alex asked to confirm a standing safe-location for Exp16 §4 moves. Recorded: `ai-notes/_parked/` (full path in `_parked/README.md`). Live notes stay in `ai-notes/` proper; parked payloads gitignored; `MANIFEST.md` tracked for cold-AI discoverability. Cleanup = ask after first-milestone PoC; deleting parked copies still §5-gated. This is **not** a delete grant.
- Follow-up: Alex explicitly happy with that exact path (`…/ai-notes/_parked`). Standing location is locked.

## 2026-09-04: Session 2 — [exp16] (destructive-ops banners; corpus now named)

- Alex updated the live corpus with `destructive-operations.md`. Prominently summarized the hard gate at the top of `ai-notes/INDEX.md` and `ai-notes/NOTES.md`; pointer in this project's CONTEXT. Persona-wide install is in central memory (stub + ledger + WORKING_STYLE banner) — see central `SESSION_LOG.md` 2026-09-04.
- Invalidates Session 1 note that destructive-ops "silence ≠ approval" was not named in the corpus.

## 2026-09-03: Session 1 — [exp16] (kickoff / alignment)

- Context: Alex pointed at `Notes/overall_goal.md` and asked to internalize persona + the Exp16 goal. Folder otherwise empty (`ai-notes/` exists, 0 files).
- Goal restated: CircuitPython stack on BPI-Bit-S2 that can run LightTower; first milestone = async 5×5 display lib (from Exp14) + async button lib; PoC quality with library-level upgrade path.
- Copy-paste in the goal note resolved (agent judgment, pending Alex confirm): **template + library source = Exp14**, not Exp16→Exp16. Exp09 supplies 5×5 LUT, orientation, and micro:bit pictogram bitmaps.
- Button-chat recommendation for **stock micro:bit v2** (no `keypad`, no asyncio → `digitalio`+debouncer+`update()`) **does not transfer**. BPI-Bit-S2 CircuitPython 10.0.3 support matrix includes `_asyncio`, `keypad.Keys`, frozen `neopixel`. Treat 10.3.0 as likely-same until on-device confirm. Goal's "Synchronous Button library" heading conflicts with "focus on asynchronous programming" — recommend async (`keypad` → event dispatch → asyncio pump).
- Workspace CircuitPythonSync still set to Exp14 board (`vcc_gnd_yd_rp2040`, CP 10.1.3). Per working-setup freeze: do not rewrite shared workspace settings; per-experiment `.vscode/` override when scaffolding is authorized.
- Corpus path in the goal (`/Users/alex/Git/rnd-ai-skills/generalized-agent-learnings`) is the live source; in-persona copies remain at `.cursor/rules/reference/`. Destructive-ops protocol **now named** in that corpus (`destructive-operations.md`) — 2026-09-03 "not named" flag **invalidated** 2026-09-04 (see Session 2).
- Memory: new roster row `circuitpython-exp16-planetx`; this folder created.
- Alex confirmed (AskQuestion 2026-09-03): overnight PoC = **full first milestone** (5×5 display with icons+font AND async buttons). Accepted all four defaults. Corrected typos in `Notes/overall_goal.md`: Exp14 as library source; heading now "An asynchronous Button library".
- Correction (same session): 8×8 switch-back is not just geometry/LUT/icons. **Also font and arrows**, via localized edits or file replacements. Exp14 `icons.py` already treats arrows as a separate named set (`ARROW_NAMES` / `ARROWS`) in the same file; font is `font_free_mono_8/` + `_FONT_PATH` in `core.py`. Shape of split (keep one file vs `arrows.py`) left open.
- Portability refinement (2026-09-04): **constructor parameters and config may change** in student code as well as library code. Stability target is student *operations* (handlers, state machine, display sequence), not a pin-free student file.
- Display hardware scope locked (2026-09-04): square **WS2812** matrices only, N≤8; 5×5 and 8×8 are the only realistic sizes. **Charlieplexed** (row/column multiplexed — stock micro:bit / Exp15) out of scope. A3 in `student-api-portability.md` promoted from assumption to lock.

## Open Questions

- **REMINDER: flash BPI-Bit-S2 to CircuitPython 10.3.0** — Alex: board disconnected; **not needed for overnight P1–P6**. Plug in at P8 / first human device window.
- On-device P8: `help("modules")` + `circup install asyncio` (firmware matrix already lists `keypad`/`_asyncio`; user `asyncio` is bundle).
- LightTower extras (servo, light sensor) — out of first milestone; capture when that phase starts.
- PlanetX C/D **cable** on P13/P14 (firmware names now known: `board.IO13`/`IO14`).
- Pitchfork-5x5 into `lib/` — not used overnight (DAL MIT taken). Written GPLv3 combination case only if that path is chosen later.
- **P7** `.vscode/` / **P8** on-device — log-only until Alex opens a human device window. Flash to 10.3.0 first.
