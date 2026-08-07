# Agent delivery checklist

Copy this into a pilot review pack and replace every placeholder with evidence.

## Purpose

- [ ] Named user and work moment
- [ ] Narrow recurring job
- [ ] Observable benefit
- [ ] Explicit non-goals and refusal boundary
- [ ] Pilot expiry and kill criteria

## Architecture

- [ ] Deterministic facts remain in code/query
- [ ] Reason simpler architecture fails is recorded
- [ ] Agent roles have distinct contracts and eval value
- [ ] Shared business logic is not copied across clients

## Data and authority

- [ ] Purpose-specific minimum data view
- [ ] Field-level model/trace/log boundary
- [ ] Retrieve, interpret, recommend, approve, and act rights assigned
- [ ] Unknown/conflicting data enters an exception path
- [ ] Identity and tenant are established outside model arguments

## Tools and approval

- [ ] Read and write capabilities separated
- [ ] Strict bounded schemas
- [ ] Server-side authorization and least privilege
- [ ] Timeouts, retries, idempotency, and error codes
- [ ] Exact preview plus approve/reject/resume for consequence

## State and humans

- [ ] Wander, Parallel, Switch, and Vanish tested
- [ ] Durable state owner
- [ ] Human edits preserved separately from source/model draft
- [ ] Stale work and crash recovery tested
- [ ] Support can reconstruct status without reading sensitive payloads

## Evals and operations

- [ ] Critical deterministic and model cases pass
- [ ] Tool trajectory and injection cases pass
- [ ] Appropriate abstention threshold passes
- [ ] Model/effort selected by evidence
- [ ] Cost and latency gates pass
- [ ] Monitoring, owner, rollback, and kill switch tested
- [ ] Change triggers and next review date recorded

## Ruling

- Decision: pass / revise / stop
- Blocking findings:
- Evidence references:
- Owners and dates:
- Conditions for re-review:

