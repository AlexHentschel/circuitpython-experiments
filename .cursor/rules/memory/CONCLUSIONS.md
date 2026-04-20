# Conclusions

Last updated: 2026-04-17 (initial cold-start; no entries yet)

Status tiers: `verified` · `evidence-supported` · `unverified` · `disputed` · `invalidated`. Only the human elevates a finding to `verified`. Tag every conclusion with experiment scope: `[expNN]`, `[tooling]`, `[cross-experiment]`, or `[universal]`.

## Validated

| Finding | Scope | Evidence | Confirmed by | Date |
|---------|-------|----------|--------------|------|

## Evidence-Supported (awaiting confirmation)

| Finding | Scope | Evidence | Date raised |
|---------|-------|----------|-------------|
| Tier 1 pytest suite (78 tests) passes on CPython after package restructure; covers all 48 authored bitmaps (round-trip) plus negative paths for `bitmap_codec`. | `[exp14]` | `pytest tests/` → `78 passed in 0.03s`, run from `.venv`. Pending human elevation to `verified`. | 2026-04-17 |

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
