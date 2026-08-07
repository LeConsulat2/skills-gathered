# Tool card

## Control

- Tool name:
- Owner:
- Version:
- Purpose:
- Intended callers:
- Read or write:

## Contract

- Input schema:
- Output schema:
- Units and definitions:
- Maximum input/output size:
- Timeout:
- Retry policy:
- Idempotency key:
- Cache/freshness rule:

## Identity and authorization

- Authenticated subject/service:
- Required role/scope:
- Tenant/scope source (must not be model-generated):
- Underlying database/service identity:
- Per-record or per-field restrictions:

## Consequence

- Side effects:
- Reversibility:
- Approval rule:
- Exact preview shown to reviewer:
- Audit event (metadata only):

## Failure semantics

| Condition | Machine code | Safe model-visible message | Retryable? | Owner |
|---|---|---|---:|---|
| Invalid argument | | | | |
| Not authorised | | | | |
| Missing/stale data | | | | |
| Conflict | | | | |
| Upstream unavailable | | | | |

## Misuse cases

- Prompt injection in an argument or retrieved value:
- Attempt to expand scope:
- Repeated/replayed write:
- Oversized request:
- Model-supplied path, SQL, identity, or credential:

## Examples

### Valid call/result

```json
{}
```

### Safe exception

```json
{}
```

