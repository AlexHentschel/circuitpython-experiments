# Conclusions

Last updated: 2026-04-20 (session 3: dropped human-elevation `verified` tier; promotion now depends on independent corroboration — see `00-memory-system.mdc` § Evidence-Status Discipline)

Status tiers: `unverified` · `evidence-supported` · `disputed` · `invalidated`. There is no separate human-elevation tier on this project — the user is project owner but not the CircuitPython domain authority, so promotion to `evidence-supported` depends on independent corroboration (datasheets, official CircuitPython docs, on-device behavior, mechanical verification). Tag every conclusion with experiment scope: `[expNN]`, `[tooling]`, `[cross-experiment]`, or `[universal]`.

## Evidence-Supported

| Finding | Scope | Evidence | Date |
|---------|-------|----------|------|
| Tier 1 pytest suite (78 tests) passes on CPython after package restructure; covers all 48 authored bitmaps (round-trip) plus negative paths for `bitmap_codec`. | `[exp14]` | `pytest tests/` → `78 passed in 0.03s`, run from `.venv`. Mechanical verification — re-runnable. | 2026-04-17 |

## Unverified

| Finding | Scope | Why noted | Date |
|---------|-------|-----------|------|

## Disputed

| Finding | Scope | Conflicting evidence | Date |
|---------|-------|----------------------|------|

## Invalidated

| Former finding | Scope | What disproved it | Date |
|----------------|-------|-------------------|------|

## Open Questions

(Canonical list lives in `SESSION_LOG.md` § Open Questions. Mirror long-running ones here if conclusion-relevant.)

## Change Log

| Date | Item | Change | Evidence |
|------|------|--------|----------|
