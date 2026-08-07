# What carries forward from `claude-ones`, and what changes

The source collection has a clear, valuable centre: build from a real human moment; narrow the wedge; make boundaries explicit; model interruption and recovery; preserve user agency; distinguish measured fact from assumption; and verify the weakest tier, not only the best demo.

Those principles are stronger than any one SDK. They carry forward directly.

## What is already unusually good

- **Picture before feature.** The work begins with a recognisable person under pressure.
- **Behaviour over opinion.** The ledgers make product claims falsifiable.
- **State outlives the screen.** Wander, Parallel, Switch, and Vanish reveal real product failures.
- **Allow, Absorb, Guard, Disable.** This creates deliberate recovery instead of blanket disabling.
- **Trust is product work.** Provenance, human edits, local data, and visible state are not footnotes.
- **One fact, many copies.** The fact census and sibling-writer checks are strong engineering instincts.
- **Domain and UX cross-examination.** Separate lenses find failures that code review alone misses.
- **Concrete design taste.** Serious, calm, practitioner-oriented interfaces resist generic AI decoration.
- **Evidence before confidence.** The mode and benchmark material distinguishes measured from assumed.

## What was experimental or one-off

That is not a criticism; it is the normal shape of learning. Several programmatic examples are tied to Anthropic beta helpers, hosted agent surfaces, or Claude-specific agent frontmatter. Some documents act as prompts, some as skills, some as project decisions, some as domain references, and some as release runbooks. That mixture helped ideas emerge, but makes portability and automated validation harder.

The main gaps for the next stage were:

- no single package with shared deterministic business logic;
- few offline tests connecting principles to executable invariants;
- prompt-level reviewer roles without a durable output/eval contract;
- insufficient separation between model orchestration and application job state;
- skills, agents, repository rules, and live capabilities sometimes occupying the same conceptual layer;
- examples that demonstrate patterns but do not yet form one supported pilot path;
- provider-specific MCP/deployment knowledge where protocol and hosting should be separate.

## The Codex translation

| Source pattern | Codex Ones equivalent | Why |
|---|---|---|
| Portable reasoning skill | `.agents/skills/<name>/SKILL.md` | Codex-native discovery and progressive disclosure |
| Claude agent persona/frontmatter | Python `Agent` with typed output, or a focused Codex skill | The runtime contract should be explicit rather than imitated |
| Tool Runner example | Responses function calling / Agents function tool | Current OpenAI API surfaces |
| Manual tool loop | `responses_loop.py` | Makes dispatch, limits, and state visible |
| Generator/critic | Frozen evidence plus explicit reviewer contract | Avoids unbounded self-revision and evidence drift |
| Supervisor + parallel workers | `asyncio.gather` plus an unsoftened review ledger | Parallel where independent; human reconciles disagreement |
| Long-running UI command | SQLite application job state | A model request is not the durable source of truth |
| Command/checklist | Template, test, script, or `AGENTS.md` rule | Match the artifact to how repeatable and enforceable it is |
| Live data integration | MCP or ordinary API | Separate governed capability from reasoning workflow |

## Three Codex layers to keep distinct

1. **`AGENTS.md`** holds durable instructions for work in a repository.
2. **Skills** hold reusable procedures and domain judgment that should trigger for a kind of task.
3. **MCP servers** expose live context and actions with identity and authorization.

Programmatic agents are application code. They can use skills conceptually and MCP technically, but are not replacements for either.

## The next evolution

The highest-leverage upgrade is to turn your domain knowledge into five assets:

1. A definition/evidence contract that a colleague can verify.
2. A deliberately difficult synthetic eval set.
3. An exception taxonomy with owners and recovery paths.
4. An approval and decision-rights map.
5. An operational artifact: job state, audit metadata, runbook, and kill switch.

This is more transferable than a very long prompt. It also makes you less dependent on any one model, SDK, or cloud platform.

## A useful new unit of work: the evidence service

Many organisations do not initially need an autonomous agent. They need a trustworthy evidence service that:

- gives non-technical people the right definition and approved number;
- shows freshness and filters;
- explains discrepancies;
- routes unknowns to an owner;
- produces a reviewable artifact;
- exposes the same capability to a dashboard, an analyst notebook, and an agent.

That can become an ordinary API plus MCP, with an agent as one client. It is a stronger organisational foundation than building a chat interface first.

