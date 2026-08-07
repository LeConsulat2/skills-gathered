---
name: audit-human-workflow
description: Audit a user flow, async workflow, UI state model, background job, upload, draft, editor, handoff, or approval experience against real interruption and recovery behaviour. Use when reviewing UX logic, specifying state transitions, diagnosing navigation or stale-state bugs, validating long-running work, or checking whether a workflow respects human edits and last-minute users.
---

# Audit Human Workflow

Cross-examine the workflow as a real person uses it under pressure. Produce concrete failure scenarios and state obligations, not general UX advice.

## Reconstruct the workflow

Inspect the implementation and product artifacts. Identify:

- user goal and triggering moment;
- source of truth for each important state;
- reads, writes, silent writes, derived copies, and caches;
- async boundaries and ownership;
- visible progress, completion, failure, and recovery;
- human-authored state that must survive regeneration.

When diagnosing, report before changing unless implementation was requested.

## Run the Four Fates

At every critical state, test:

- **Wander:** navigate elsewhere and return.
- **Parallel:** start or inspect another task.
- **Switch:** change record, project, tab, device, or account.
- **Vanish:** refresh, close, lose network, crash, restart, or redeploy.

For each fate choose deliberately:

- **Allow** when state is safe and durable.
- **Absorb** when the system can continue without disruption.
- **Guard** when the user must confirm or understand consequence.
- **Disable** only when no safe recovery design exists.

Call out blanket disabling that protects implementation convenience rather than the user.

## Test the awkward moments

Include at least these scenarios when relevant:

- empty and first-run state;
- duplicate click or retry;
- stale tab or out-of-order response;
- partial completion;
- user edit followed by regeneration;
- conflicting server and local state;
- work completed after the user leaves;
- approval rejected, delayed, or resumed elsewhere;
- last-minute user who has no time to learn the interface;
- support person reconstructing what happened.

Use one concrete person/time/failure sentence for every material finding.

## Protect state and authorship

Require:

- long-running work to outlive the initiating screen;
- stable identifiers rather than positional selection;
- idempotent writes and retries;
- model/source/human versions to remain distinguishable;
- human edits to be sticky;
- current-file or current-record rereads before consequential writes;
- errors to state what happened, whether work is safe, and what to do next.

## Deliver

Lead with a ruling: `pass`, `revise`, or `stop`.

Then provide:

1. User and pressure moment.
2. State-owner map.
3. Four Fates matrix with Allow/Absorb/Guard/Disable decisions.
4. Findings ordered by severity, each with a failure scenario and evidence.
5. Required behaviour changes.
6. Falsifiable tests and recovery drills.
7. Unknowns that require user or production evidence.

Do not bury a data-loss or authority problem under visual polish.

