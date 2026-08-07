---
name: gate-agent-delivery
description: Review or design an AI agent, agent workflow, MCP capability, tool-using assistant, or automation for accountable pilot delivery. Use when choosing workflow versus agent architecture, writing an agent contract, checking data and decision rights, defining tools and approvals, planning evals and tracing, reviewing pilot readiness, or deciding pass/revise/stop before real organisational use.
---

# Gate Agent Delivery

Require evidence that a proposed agent is useful, bounded, testable, and operable. Do not equate a successful demo with readiness.

## Read the actual artifacts

Inspect code, schemas, prompts, tools, state, tests, data flow, deployment plan, and product evidence. Do not score intentions when an implementation exists.

Use `assets/AGENT-DELIVERY-CHECKLIST.md` when producing a formal readiness review or pilot pack.

## Challenge the architecture

Classify each component as:

- deterministic query/function;
- fixed workflow;
- one typed model call;
- tool loop or agent;
- human decision;
- durable job/service;
- API/MCP capability.

Require a named reason the next simpler design fails. More agents do not count as a capability gain.

## Verify the contracts

Check:

1. **Purpose:** named user, moment, job, benefit, non-goals.
2. **Evidence:** definition, source, scope, freshness, caveats, conflicts.
3. **Data:** classification, minimum fields, model/trace/log/queue boundaries.
4. **Decision rights:** retrieve, interpret, recommend, approve, act.
5. **Tools:** narrow schema, server-side authorization, side effect, error semantics.
6. **Autonomy:** allowed actions, approval boundary, turn/call/retry/cost limits.
7. **State:** durable ownership, idempotency, resume, stale work, human edits.
8. **Evaluation:** critical cases, trajectory, abstention, model comparison, regression rule.
9. **Operations:** owner, monitoring, support, rollback, kill switch, expiry.

Treat identity, tenant, permission, SQL, filesystem path, and approval as server-controlled values. Do not accept them merely because a model supplied them.

## Inspect consequence

Separate read tools from write tools. For each consequential call require:

- exact preview;
- authenticated and authorised reviewer;
- approve and reject paths;
- durable pause/resume when the wait can outlive a process;
- idempotency or replay protection;
- audit metadata without unnecessary payload duplication;
- recovery or compensation plan.

“Human in the loop” fails if the person cannot inspect evidence, edit, reject, or safely delay.

## Inspect evaluation integrity

Require bottom-up gates:

- deterministic facts and state invariants;
- schemas and forbidden fields;
- tool selection/arguments/stopping;
- grounded output and appropriate abstention;
- real pilot outcome and harm measures.

Keep hard gates separate. Never average a privacy, authorization, or serious factual failure away with high style scores. Select model and reasoning effort from frozen representative cases.

## Rule

Use one of three rulings:

- **Pass:** every hard gate has evidence; remaining issues are bounded and owned.
- **Revise:** useful pilot hypothesis, but named gates lack evidence or implementation.
- **Stop:** purpose, authority, data use, or consequence is unacceptable at the proposed scope.

Do not inherit an old ruling after a material change. Reverify affected gates.

## Deliver

Produce:

1. Ruling and one-sentence reason.
2. Intended user/job and product boundary.
3. Architecture decomposition and simplification opportunities.
4. Critical findings with concrete failure scenarios and evidence.
5. Missing agent/tool/data/operational contract fields.
6. Required eval cases and drills.
7. Minimum changes for a bounded pilot.
8. Owners, decisions needed, and expiry/review trigger.

State measured facts, inferences, and unknowns separately.

