# Bounded pilot runbook

## Pilot control

- Product/version:
- Pilot owner:
- Technical operator:
- Privacy/security contacts:
- Domain/data owner:
- Eligible users:
- Start/end:
- Approved purpose/data/actions:
- Explicit exclusions:

## Go-live gates

- [ ] Purpose, data, tool, agent, and operational contracts approved.
- [ ] Synthetic demonstration completed before approved-data connection.
- [ ] Critical offline and model evals pass.
- [ ] Authorization and approval drills pass.
- [ ] Trace/log payload configuration verified.
- [ ] Backup, restore, rollback, and kill switch tested.
- [ ] Users know limitations, exception routes, and support contact.
- [ ] Success, serious-error, and stop thresholds are recorded.

## Start procedure

1. Confirm deployed version and configuration digest.
2. Confirm source freshness and least-privilege identity.
3. Run smoke cases, including one exception and one rejected approval.
4. Enable only pilot users and tools.
5. Record start decision and operator.

## Operating view

Monitor:

- job states and stale work;
- tool error codes and authorization failures;
- exception/abstention rate;
- critical eval regressions;
- latency, tokens, and cost;
- human rejection/edit rate;
- support burden and user workaround behaviour;
- data freshness and definition changes.

## Incident procedure

1. Protect people and data; stop consequential tools if needed.
2. Preserve metadata, version, and references without spreading payloads.
3. Identify affected users/artifacts and decision owner.
4. Roll back, disable, or constrain the capability.
5. Communicate known facts, unknowns, and next update time.
6. Add a regression case or drill before re-enable.

## Stop/rollback

- Kill command or control:
- Person authorised to use it:
- Safe degraded mode:
- Rollback version:
- Pending-job treatment:
- User communication:
- Data/output correction process:

## Pilot close

- Results against predeclared gates:
- Serious errors/near misses:
- User behaviour observed:
- Support and operating cost:
- Privacy/security findings:
- Decision: stop / revise / extend bounded pilot / seek production review
- Owner and expiry date:

