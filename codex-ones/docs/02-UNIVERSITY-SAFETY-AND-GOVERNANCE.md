# University safety and governance: build decision support, not shadow authority

This guide is a design aid, not University of Auckland policy or legal advice. Real work must use the university's approved privacy, information-security, records, procurement, data-governance, and model-use processes.

## Start with purpose, not data access

Write one sentence:

> For **named users**, during **a named work moment**, the system may **perform a bounded job** so they can **make a named human decision**, while it must never **cross a named boundary**.

Example:

> For student-insights analysts preparing a weekly intake briefing, the system may assemble approved aggregate counts, definitions, freshness, and data-quality exceptions so an analyst can draft the briefing; it must never rank applicants, infer eligibility, or publish without review.

If that sentence is vague, more tooling will make the risk harder to see.

## Assign four rights separately

| Right | Question | Typical owner |
|---|---|---|
| Data access | Who may retrieve which fields and aggregates? | Data owner / delegated access process |
| Interpretation | Who may explain what a measure means? | Domain steward / analyst |
| Recommendation | Who may propose an action? | Named professional role |
| Decision/action | Who may approve or execute it? | Formally authorised person or system |

Never let “the agent can call the tool” collapse these rights into one.

## A practical data boundary

Classify both stored data and every outbound model payload. At minimum distinguish:

- public or deliberately synthetic;
- internal aggregate;
- confidential row-level;
- highly sensitive or restricted;
- credentials and security material.

For each class, record:

- approved storage locations;
- approved model/provider and region, if any;
- retention and deletion rule;
- whether prompts, traces, tool outputs, and human comments may contain it;
- the exact fields or transformation allowed to cross each boundary.

Do not use a regex PII detector as the authorization control. Use allowlisted fields, purpose-specific views, database permissions, and explicit classification. Detection can be a warning layer, never the only gate.

## Evidence packet before narrative

A decision-support artifact should carry:

- metric definition and version;
- source system or approved view;
- query/report identifier;
- scope and filters;
- data-as-of time;
- measured value;
- known quality exceptions;
- assumptions and transformations;
- human review state;
- a stable artifact or evidence digest.

The model should receive the smallest approved packet required for the task. If it receives only an aggregate, it cannot accidentally repeat a name it never saw.

## Exception queues are a feature

Use explicit outcomes such as:

```text
answerable
needs_definition_owner
needs_data_correction
needs_authorised_access
conflicting_sources
stale_data
out_of_scope
```

Forcing every request into an answer hides organisational work. A useful exception queue names the issue, source, owner, age, next action, and whether downstream reports are blocked.

## Agent and tool threat model

Treat user text, retrieved documents, web pages, database text, and MCP tool outputs as untrusted content. They may contain instructions that conflict with system policy.

Controls should include:

- narrow, verb-specific tools;
- server-side authorization derived from authenticated identity, never a model-supplied user ID;
- read-only identities for read tools;
- fixed output directories and allowlisted resource identifiers;
- strict argument schemas and bounded sizes;
- tool timeouts, call limits, and retry limits;
- approval for writes, messages, publication, deletion, or scope expansion;
- previews that show the exact action and material payload;
- idempotency for retried writes;
- a kill switch outside the model;
- adversarial eval cases containing prompt injection in otherwise valid data.

A tool named `run_sql(query)` is usually too broad for a governed product. Prefer purpose-shaped tools such as `get_application_snapshot(reporting_period)` backed by an approved view and parameterized query.

## Human control must be real

“Human in the loop” is not a confirmation button after the system has made the important choice. The reviewer needs:

- enough evidence and time to disagree;
- an editable draft;
- visible uncertainty and exceptions;
- the ability to reject without losing work;
- no penalty for choosing the safe path;
- a record of what was reviewed and what changed;
- clear accountability after approval.

Protect human-authored edits from later regeneration. Store source, model draft, and reviewed final as distinct versions.

## Traces and logs are data stores

The Agents SDK traces model generations and tool calls by default, and sensitive payload capture is enabled by default unless configured otherwise. These examples set `OPENAI_AGENTS_TRACE_INCLUDE_SENSITIVE_DATA=0` before importing the SDK.

For real work, decide separately whether to:

- disable tracing;
- retain structural traces without inputs/outputs;
- use an approved internal trace processor;
- log only event metadata and stable references.

Do not assume an observability product is outside privacy and records obligations. Do not put secrets in serialized `RunState`; the state is designed to travel and persist.

## Guardrails are layered, not magical

Input and output guardrails can catch known patterns, but capability design is stronger:

- keep restricted data out of model context;
- do calculations in deterministic code;
- hide tools the caller cannot use;
- authorize again inside the service;
- require approval for consequence;
- validate final artifacts before release.

In the Agents SDK, input guardrails apply at the entry agent, output guardrails at the final agent, while function-tool guardrails run around each function tool. Multi-agent designs therefore need explicit coverage at every boundary, not one ceremonial guardrail at the top.

## Domain transfer rule

Architecture may transfer; risk assumptions do not.

- A golf practice assistant may safely suggest a drill, but should distinguish measured launch-monitor data from visual inference.
- A counselling note assistant deals with deeply sensitive information, practitioner accountability, clinical safety, crisis pathways, and professional standards. It must not be treated as a renamed university demo.
- An application insights tool may describe aggregates, but automated eligibility or selection requires a fundamentally different governance process.

Re-run purpose, data, harm, decision-rights, and eval design for every domain and every major feature expansion.

Official technical references: [Agents SDK tracing](https://openai.github.io/openai-agents-python/tracing/), [human-in-the-loop](https://openai.github.io/openai-agents-python/human_in_the_loop/), and [OpenAI safety best practices](https://developers.openai.com/api/docs/guides/safety-best-practices).

