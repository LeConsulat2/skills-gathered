# Start here: from capable maker to accountable agent engineer

You already know how to make software with Python, TypeScript, React, SQL, and AI assistance. The next level is not learning one more framework. It is learning to turn domain judgment into a system that another person can inspect, challenge, operate, and safely reuse.

That requires five separations:

1. Facts from language.
2. Evidence from inference.
3. Recommendation from decision.
4. Read capability from write capability.
5. A successful demo from a supported service.

The lessons use synthetic application data. They do **not** model admission decisions, rank applicants, or make eligibility determinations. They teach evidence delivery, data-quality surfacing, report drafting, and controlled publication.

## The surprising part

An agent is rarely the first architecture you need.

```text
stable calculation -> deterministic function
fixed multi-step path -> workflow
uncertain selection among safe tools -> agent
consequential action -> agent + explicit approval
long-running work -> durable application state
live organisational capability -> governed API or MCP server
```

Adding more agents before contracts, eval cases, and recovery paths usually adds ambiguity rather than intelligence.

## Setup A: offline core

```powershell
cd codex-ones
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python examples\01_deterministic_evidence.py
python examples\09_local_evals.py
```

## Setup B: OpenAI API lessons

```powershell
python -m pip install -e ".[learn,dev]"
Copy-Item .env.example .env
```

Add `OPENAI_API_KEY` to `.env`. The default product model is `gpt-5.6-terra`, not because it is always best, but because a balanced default is a better starting hypothesis than “use the largest model everywhere.” Keep `gpt-5.6-sol` for work whose evals justify the extra capability; test `gpt-5.6-luna` for high-volume narrow work. Model selection is an empirical product decision.

## The ten lessons

### 1. Deterministic evidence

Run `examples/01_deterministic_evidence.py`.

Learn to calculate counts, freshness, duplicates, unknown values, and caveats before a model sees anything. This is the foundation. If a SQL query or Python function can produce the fact, do that.

### 2. Structured output

Run `examples/02_structured_brief.py` with an API key.

The model receives an aggregate evidence packet, not raw applicant rows, and must return a typed draft. Learn that a schema constrains shape, not truth. Every claim still needs evidence.

### 3. One read-only tool

Run `examples/03_single_tool_agent.py`.

Give one agent one narrow capability. Observe what the runtime manages, and what remains your responsibility: tool correctness, authorization, data boundary, prompt, audit, and evaluation.

### 4. Own the loop

Run `examples/04_manual_responses_loop.py`.

Implement the function-calling loop yourself. This removes the magic: model proposes a call, application validates and executes it, application returns the result, model continues. Learn this before relying on an agent framework.

### 5. Parallel review without consensus theatre

Run `examples/05_parallel_review.py`.

Data-quality, domain-grounding, and decision-rights reviewers inspect the same frozen evidence packet concurrently. Their findings stay separate. A supervisor is not allowed to silently soften disagreement; a person reconciles the ledger.

### 6. Human approval and resumable state

Run `examples/06_human_approval.py`.

A publication tool pauses before writing. The run state can be stored and resumed. This teaches a crucial boundary: “the model asked for it” is not authorization.

### 7. Auditable local output

Run `examples/07_audited_report.py`.

Create a draft plus a payload-free audit event. Audit structure and decisions, but do not casually duplicate sensitive content into logs.

### 8. Durable jobs

Run `examples/08_durable_job.py`.

Use SQLite to model queued, running, succeeded, and failed work. Background API execution and application durability are different problems. Users should be able to leave, return, and understand what happened.

### 9. Local evals

Run `examples/09_local_evals.py`.

Turn domain expectations into executable JSONL cases. This repo uses a local harness because eval assets should survive provider or product changes, and because deterministic invariants should not need a paid model call.

### 10. MCP without Cloudflare

Follow `mcp-server/README.md`, then run `examples/10_mcp_client_agent.py`.

Start with stdio: the host launches a local process, no port or cloud account required. Then try localhost Streamable HTTP. Only after the capability and governance are sound should you put the same protocol service on approved internal infrastructure.

## Three Codex-native skills

The `.agents/skills` directory contains reusable judgment, not copied Claude personas:

- `$frame-real-product` converts an idea into a narrow picture, wedge, boundary, and falsifiable pilot.
- `$audit-human-workflow` cross-examines interruption, recovery, overrides, and durable state.
- `$gate-agent-delivery` decides whether a proposed agent is ready for a pilot and produces an agent contract.

Skills encode repeatable ways of thinking. MCP supplies live tools and data. `AGENTS.md` supplies durable repository rules. Programmatic agents are ordinary application code. Treating those as four distinct layers prevents a great deal of accidental complexity.

## What “ready for work” means

A prototype is not ready because the output looks intelligent. It is ready for a bounded pilot when:

- its user, moment, and job are specific;
- the source of every important fact is visible;
- unknown and conflicting records become exceptions;
- model inputs are explicitly allowed to leave their trust boundary;
- write actions are separately authorized and approved;
- a human can edit, reject, and recover;
- the system has offline invariants and representative model evals;
- cost, latency, failure, and ownership are measured;
- there is an operator runbook and a kill switch;
- the pilot has a falsifiable success and stop condition.

## Your likely highest-leverage projects

For university work, begin with evidence delivery rather than decision automation:

- a definitions-aware application/enrolment metric explainer;
- a data-quality exception queue with owners and freshness;
- a report-draft assistant that cites the exact aggregate tables used;
- a “how do I get this data?” guide backed by approved metadata;
- a reconciliation workflow that shows why two reports disagree.

For counselling or golf, reuse the architecture but re-establish the domain boundary from first principles. Do not transfer risk assumptions just because the code transfers.

Continue with [Architecture Ladder](docs/01-ARCHITECTURE-LADDER.md), then [Safety and Governance](docs/02-UNIVERSITY-SAFETY-AND-GOVERNANCE.md).

