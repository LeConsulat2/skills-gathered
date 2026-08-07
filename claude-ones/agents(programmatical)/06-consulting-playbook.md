# Turning This Into a Client/University Deliverable

You now have five working patterns (files `01`–`05`). This file is about the part
that's actually your job as a consultant: picking the right one, scoping it
correctly, and not shipping something that quietly does the wrong thing.

## 1. Which tier does the job actually need?

Don't default to "build an agent" — it's the most expensive, hardest-to-verify
option, and most requests don't need it. Work down this list and stop at the
first row that fits:

| What the client actually needs | Reach for | Why |
|---|---|---|
| Classify / extract / summarize / answer one thing | A single API call | One request, one response — no loop needed |
| A fixed multi-step process YOU control ("parse this, then check it, then format it") | A **workflow** — code-controlled steps, each maybe an API call | You own the control flow; the model doesn't decide what happens next |
| The model needs to decide its own next step, using tools, until a task is done | An **agent** (Lessons 1–4) | Open-ended, tool-using, model-driven |
| The agent needs to run for a long time, need a real sandboxed workspace, or run on a schedule with nobody watching | **Managed Agents** (Lesson 5) | Hosted loop + hosted container, not your laptop/server |

If you can answer "no" to any of these about the task, don't build an agent for it
— stay at a simpler tier:
- Is it genuinely multi-step and hard to fully specify in advance?
- Does the outcome justify the extra cost and latency of an agent loop?
- Is the model actually capable at this kind of task?
- Can a wrong answer be caught and fixed (tests, a review step, a rollback)?

## 2. Scoping questions to ask before writing any code

- **What does "done" look like, concretely?** Not "a good report" — "a CSV with a
  numeric `price` column for every SKU." If you can't state the success
  condition precisely, you can't build a critic (Lesson 3) or an outcome check
  for it.
- **What data does it touch, and what's the sensitivity?** Client names, health
  records, financial data, anything under NDA — this determines whether you can
  even send it to an API at all, and whether Managed Agents' hosted sandbox is
  appropriate or a self-hosted sandbox is required (see `shared/managed-agents-self-hosted-sandboxes.md`
  in the `claude-api` skill for that variant).
- **What's the blast radius if the agent does the wrong thing?** A tool that
  reads files is low-risk. A tool that sends emails, moves money, or deletes
  data needs a human-approval gate before it fires — every pattern in this
  folder can be adapted to pause and wait for a yes/no before a risky tool call
  actually executes.
- **Who's the human in the loop, and where exactly do they sit?** Reviewing
  every output (safe, slow)? Reviewing only what a critic flagged (Lesson 3)?
  Reviewing nothing, with monitoring/alerting instead (only for low-stakes,
  well-tested workflows)?
- **Does this need to run once, on a schedule, or on an external trigger** (a
  webhook, a new file landing somewhere)? That answer picks between "a script
  someone runs" and "a Managed Agents deployment" (Lesson 5).

## 3. A cost/security checklist, before you hand anything off

- [ ] Every tool with side effects (send, delete, pay, publish) is gated behind
      an explicit approval step, not auto-executed.
- [ ] Cheap models are used wherever the job is mechanical (Lesson 4's workers);
      the expensive model's tokens are spent only where judgment is actually
      needed.
- [ ] There's a hard cap on loop iterations / retries / spend — an agent with no
      exit condition is a production incident (infinite cost, infinite latency),
      not a feature. `Lesson 3`'s `MAX_ROUNDS` and Managed Agents' `budget`
      parameter are both this same idea.
- [ ] Secrets (API keys, tokens) never go through the model as plain text in a
      prompt — they're injected by the harness/host, never typed into a system
      prompt or user message (Managed Agents' vault credentials, or your own
      equivalent, exist specifically for this).
- [ ] You've told the client, in writing, what happens when the agent is wrong
      — because it will be, eventually. "What's the failure mode, and who
      notices" is a real deliverable, not an afterthought.

## 4. A worked case study, from earlier in this actual session

While this folder was being written, a ~1.5 hour benchmark run needed launching
and babysitting. Instead of the expensive model (me) sitting there waiting on
it, a cheaper model was dispatched with a **self-contained** prompt carrying:
the exact command to run, explicit safety rails (read-only repo, no git, never
read/quote content that might be sensitive — only report the safe numeric
summary), and instructions for what to do on failure (report verbatim, don't
improvise a fix). That's Lesson 4's pattern (supervisor delegates the
mechanical part to a cheaper worker) applied to a real engineering task, not
just customer feedback classification. The pattern is genuinely general —
"design and interpret with the expensive model, execute the mechanical part
with a cheap one" is a cost story you can put directly into a client proposal.

## 5. Making it portable across a company's own stack

Everything in `01`–`04` is plain Python + the `anthropic` package — no framework,
no vendor lock beyond the API calls themselves. If a client's stack uses a
different provider, the *code* changes but the *shape* doesn't: the loop in
Lesson 2, the generator/critic split in Lesson 3, and the supervisor/parallel-
workers split in Lesson 4 are all provider-agnostic design patterns. What
changes moving to another provider's SDK is exactly four things: how you
authenticate, the exact tool-schema field names, the exact response field
names (`stop_reason` vs. whatever that provider calls it), and pricing/model
names. The mechanism — send, check, execute, append, repeat — is universal.
That's the actual skill you're selling: not "I can call the Anthropic API," but
"I know how to design the loop, the roles, and the guardrails," which transfers
anywhere.
