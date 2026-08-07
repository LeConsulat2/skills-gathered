# Evals and evidence: make domain judgment executable

The most valuable thing you can do with deep domain knowledge is not put more of it in a prompt. It is turn the difficult cases into durable tests.

## Five layers of evaluation

| Layer | What it checks | Should require a model? | Example |
|---|---|---:|---|
| 0. Code invariant | Exact calculation and state rules | No | Duplicate IDs do not inflate counts |
| 1. Contract | Shape, required evidence, forbidden fields | Usually no | Every brief has caveats and review status |
| 2. Agent trajectory | Tool choice, arguments, stopping, approvals | Sometimes | Agent uses aggregate tool, not publication tool |
| 3. Output quality | Correctness, groundedness, usefulness, tone | Yes/human | Analyst can verify each claim quickly |
| 4. Pilot outcome | Real work and harm measures | No single grader | Less reconciliation time without serious errors |

A fluent answer can pass layer 3 style while failing layer 0 truth. Test from the bottom up.

## Case design

Each eval case should contain:

- stable ID;
- behaviour being protected;
- input or evidence reference;
- expected result or rubric;
- severity if it fails;
- reason the case exists;
- source or domain owner;
- date added;
- whether it contains sensitive content;
- model/runtime version when applicable.

The committed `data/eval_cases.jsonl` deliberately tests facts and boundaries without an API call. Run it with:

```powershell
python examples\09_local_evals.py
```

## Build cases from work, not imagination alone

Good sources are:

- real reconciliation disputes rewritten with synthetic values;
- queries new analysts misunderstand;
- unknown or stale data that used to be silently ignored;
- last-minute requests from senior users;
- user edits to generated reports;
- near misses and incidents;
- attempts to make the system act outside its mandate;
- a weaker model's failures;
- production latency, timeout, and retry problems.

Never copy confidential examples into a personal repository. Preserve the structural difficulty while replacing all identifying and institutional values.

## Grade evidence before prose

For an analyst brief, score in this order:

1. Required facts are correct.
2. Every important claim maps to supplied evidence.
3. Unknowns, conflicts, and freshness remain visible.
4. Observation and interpretation are distinct.
5. No forbidden inference or decision appears.
6. Required next checks are actionable.
7. Language is useful to the intended professional.

If the first five fail, polished wording is not a rescue.

## Agent trajectory rubric

Record more than the final answer:

- tools exposed versus tools called;
- call order and arguments;
- invalid or repeated calls;
- number of turns;
- approval requested, approved, rejected, and resumed;
- exception/abstention behaviour;
- final structured output;
- tokens, latency, and cost;
- runtime and model identifiers.

A correct answer reached through an unauthorized tool path is a failed run.

## Model selection experiment

Run the same frozen cases against candidate model/effort pairs. Predeclare gates such as:

```text
serious factual error rate = 0 on critical cases
grounded claim rate >= 98%
appropriate abstention >= 95%
p95 latency <= agreed threshold
median cost <= agreed threshold
```

Then select the cheapest/fastest configuration that clears every hard gate. Do not average a privacy failure away with good tone scores.

## Regression rule

Every material defect should produce one of:

- a deterministic unit test;
- a contract validation case;
- a model eval case;
- a recovery drill;
- a monitoring alert.

If an incident only produces a prompt paragraph, it is likely to recur.

## Current OpenAI platform note

As of 7 August 2026, OpenAI documents the Evals platform as a legacy API: it is scheduled to become read-only for existing users on 31 October 2026 and shut down on 30 November 2026, with Datasets suggested for new evaluation work. That is why this repository's durable source of truth is local JSONL plus ordinary tests. A vendor UI can be a useful analysis surface, but it should not be the only copy of your cases.

Official references: [OpenAI eval guidance and deprecation notice](https://developers.openai.com/api/docs/guides/evals), [Agents SDK tracing](https://openai.github.io/openai-agents-python/tracing/), and [OpenAI model guidance](https://developers.openai.com/api/docs/guides/latest-model).

