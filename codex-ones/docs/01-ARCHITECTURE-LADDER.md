# Architecture ladder: earn autonomy one boundary at a time

The question is not “How many agents can this use?” It is “What is the least autonomous architecture that reliably does the job?”

## The ladder

| Level | Shape | Use when | Evidence required before promotion |
|---|---|---|---|
| 0 | Pure function or query | Inputs, rules, and outputs are stable | Unit tests and reconciled definitions |
| 1 | Deterministic workflow | The path is known but has several steps | State-transition and recovery tests |
| 2 | One model call with typed output | Language judgment is useful; no tool choice is needed | Schema pass rate plus human rubric |
| 3 | Handwritten tool loop | You want explicit control over dispatch and state | Tool-selection and stopping evals |
| 4 | Single agent runtime | Safe tool choice or iteration is genuinely uncertain | Bounded-turn success, cost, and failure evidence |
| 5 | Parallel specialist review | Independent lenses can find different defects | Each lens beats one combined review on held-out cases |
| 6 | Agent plus approval | A proposed action has consequence outside the run | Preview, reject, resume, audit, and replay drills |
| 7 | Durable service | Work outlives a request, browser, or worker | Crash recovery, idempotency, ownership, and support drills |
| 8 | MCP/API capability | Multiple approved clients need the same governed capability | Auth, per-tool authorization, versioning, monitoring, and kill switch |

MCP is not automatically “more advanced” than an agent. A tiny deterministic read tool can be an excellent MCP service. A complex agent can still be a fragile local script.

## The reference flow

```text
user intent
    |
    v
purpose + data boundary -----> reject / exception queue
    |
    v
deterministic evidence ------> provenance + freshness + caveats
    |
    v
bounded model judgment ------> typed draft + unresolved questions
    |
    v
human review ----------------> edit / reject / approve
    |
    v
authorised write ------------> durable state + audit metadata
```

Every arrow is a contract. “The model is smart” is not a contract.

## Direct Responses API or Agents SDK?

Use the Responses API directly when you want to own:

- conversation and tool-loop state;
- exact tool dispatch and retry behaviour;
- a small number of steps;
- a provider boundary that stays easy to replace.

Use the Agents SDK when the runtime meaningfully helps with:

- function-tool schemas;
- turn management;
- handoffs or agents-as-tools;
- guardrails;
- tracing;
- human-in-the-loop interruptions and serializable run state.

The SDK manages orchestration mechanics. It does not take ownership of privacy, authorization, tool correctness, data definitions, human decision rights, or production support.

## Workflow or agent?

Choose a workflow when you can draw the route before the input arrives. Choose an agent when the input determines which safe route is appropriate and that choice cannot be captured more reliably in ordinary code.

Examples:

- “Run these five validation checks and build a report” is a workflow.
- “Choose which of twelve read-only evidence tools resolves this analyst question” may justify an agent.
- “Calculate an enrolment count” is a query, not an agent.
- “Publish whatever report seems best” is an authorization failure, not an agent design.

## One agent before many

Add a specialist only if all four are true:

1. It has a distinct input contract or evaluation rubric.
2. It produces an independently useful artifact.
3. It can operate without hidden shared conversation state.
4. Held-out evals show it finds defects the simpler design misses.

Parallel reviewers should receive the same frozen evidence packet. Preserve their separate reports. A synthesizer can help organise disagreement, but must not erase minority findings or decide whether a stop condition is acceptable.

## Model choice is a measured role assignment

As of 7 August 2026, OpenAI positions `gpt-5.6-sol` for frontier capability, `gpt-5.6-terra` for a balance of capability and cost, and `gpt-5.6-luna` for efficient high-volume work. This repository starts product examples on Terra and treats Sol or Luna as candidates to test on the same eval set.

A useful routing experiment is:

| Work | Baseline candidate | Promotion question |
|---|---|---|
| Deterministic metric | No model | Why is a model involved at all? |
| Narrow extraction/classification | Luna | Does it meet the error and exception threshold? |
| Analyst draft from clean evidence | Terra | Does Sol materially improve correctness or only prose? |
| Difficult cross-source reconciliation | Sol | Does higher reasoning beat a smaller model plus better evidence? |

Do not route only on perceived task prestige. Record task success, serious-error rate, abstention quality, latency, tokens, and cost.

## State belongs to the application

Conversation memory is not a job database. A background model request is not a durable workflow. A browser spinner is not status.

Model at least these states explicitly:

```text
queued -> running -> succeeded
                  -> failed -> retryable or terminal
queued/running -> cancelled
running too long -> stale -> queued or human review
```

Store references to governed inputs and outputs instead of copying payloads everywhere. Use idempotency keys for external writes. Make retry ownership and maximum attempts explicit.

## The four production contracts

Before implementation, write:

1. **Evidence contract** — definitions, sources, freshness, scopes, caveats, exceptions.
2. **Tool contract** — caller, arguments, result, authorization, side effects, failure semantics.
3. **Agent contract** — purpose, autonomy, limits, approvals, stop conditions, evals.
4. **Operational contract** — owner, state lifecycle, monitoring, support, rollback, retirement.

The templates directory contains starting artifacts. The `$gate-agent-delivery` skill checks whether they are substantive.

## Promotion rule

Move up one level only when the simpler level fails a named eval and the more autonomous level passes it without violating the cost, latency, privacy, or human-control gates. That turns architecture into evidence rather than fashion.

Official basis: [OpenAI model guidance](https://developers.openai.com/api/docs/guides/latest-model), [Agents SDK](https://openai.github.io/openai-agents-python/), and [function calling](https://developers.openai.com/api/docs/guides/function-calling).

