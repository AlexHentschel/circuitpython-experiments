# Permitted Destructive-Actions Ledger (master)

Authority checked **before** any non-trivially-reversible action.
**Absence of a matching active entry = no permission** (fail-closed).

Protocol: `/Users/alex/Git/rnd-ai-skills/generalized-agent-learnings/destructive-operations.md` §6 (schema) and §5 (how a grant is obtained). Durable copy: `../../reference/destructive-operations.md`. Always-on stub: `../../06-destructive-operations.mdc`.

Grants are **per exact file/folder/operation**, single-use unless `expiry` says standing. Conversation "yes" is not a ledger entry until recorded here after a §5 round.

## Confirmed park locations (not grants)

A confirmed §4 destination is **not** permission to delete. Deleting a parked copy still needs an Active grant below.

| workstream | path | confirmed | notes |
|---|---|---|---|
| Exp16 (`circuitpython-exp16-planetx`) | `/Users/alex/Development/VsCode/CircuitPython/2026-09_Exp16_BPI-Bit-S2_CircuitPy_PlanetX/ai-notes/_parked/` | 2026-09-04 Alex | Policy + MANIFEST in that folder. Exp16 only. Path endorsed ("happy with") same day. |

## Active grants

_None._

## Spent / historical grants

| id | date | granted-by | scope | exact-request | trigger-word | covered-set | status | expiry |
|---|---|---|---|---|---|---|---|---|
