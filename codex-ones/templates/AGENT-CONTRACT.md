# Agent contract

## Identity and control

- Agent/workflow name:
- Business owner:
- Technical owner:
- Domain/data owner:
- Version:
- Review/expiry date:
- Status: synthetic prototype / review / bounded pilot / production / suspended / retired

## Purpose

- Named users:
- Triggering moment:
- Bounded job:
- Human decision supported:
- Measurable benefit:
- Non-goals:

## Autonomy boundary

- May answer/review:
- May call without approval:
- Must ask before:
- Must never:
- Stop/abstain when:
- Maximum turns:
- Maximum tool calls:
- Maximum retries:
- Time/cost budget:

## Data boundary

| Data class | Fields/artifact | Source | May enter model? | May enter trace/log? | Retention |
|---|---|---|---:|---:|---|
| | | | | | |

## Evidence contract

- Required provenance:
- Required freshness:
- Required definitions:
- Required caveats:
- Conflict handling:
- Exception taxonomy:
- “No evidence” behaviour:

## Tool inventory

| Tool | Read/write | Identity/authorization | Side effect | Approval | Timeout/retry | Idempotency | Audit |
|---|---|---|---|---|---|---|---|
| | | | | | | | |

## Model/runtime hypothesis

- Baseline model and effort:
- Why this role needs a model:
- Candidate alternatives:
- Structured output schema:
- State strategy:
- Tracing configuration:
- Version pin/update policy:

## Human control

- Preview shown:
- Approver role:
- Approve/reject/edit flow:
- Persist/resume mechanism:
- Human edit preservation:
- Escalation path:

## Evaluation gates

| Gate | Dataset/case IDs | Threshold | Severity | Owner | Current result |
|---|---|---|---|---|---|
| Factual correctness | | | | | |
| Grounded claims | | | | | |
| Appropriate abstention | | | | | |
| Tool trajectory | | | | | |
| Approval enforcement | | | | | |
| Privacy/security | | | | | |
| Latency/cost | | | | | |
| User outcome | | | | | |

## Operations

- Durable job states:
- Monitoring and alerts:
- Operator/support owner:
- Incident classification:
- Kill switch:
- Rollback:
- Data/model/provider failure mode:
- Change review triggers:
- Retirement/export plan:

## Approval record

| Role | Name | Decision | Conditions | Date |
|---|---|---|---|---|
| | | | | |

