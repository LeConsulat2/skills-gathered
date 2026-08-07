# Learning: Building Real Agents

You already know how to design *plans* and *skills* (see the Fable skill family in
`.claude/skills/` in the main repo) — reusable instructions that guide a model inside
Claude Code. That's real skill, but it's bound to one product's config format.

What's in this folder is the next layer down: **actual Python code that builds an
agent from the Anthropic API directly.** No Claude Code, no `.claude/agents/*.md`
files — just the `anthropic` SDK, called from a script you write and own. This is
what you'd actually hand a university department or a company client, because it
runs anywhere Python runs: a server, a cron job, a notebook, their own CI pipeline.

## Read/run in this order

| File | Teaches |
|---|---|
| `01_single_tool_agent.py` | The minimum viable "agent": a model that can call a tool, with the loop handled for you (Tool Runner) |
| `02_manual_agent_loop.py` | The exact same agent, but with the loop written by hand — so you see the mechanism the Tool Runner was hiding |
| `03_generator_critic_pipeline.py` | Two models with different jobs, one checking the other's work — your first *multi*-agent system |
| `04_supervisor_parallel_workers.py` | One smart model decomposing a task into pieces, cheap models running them in parallel, the smart model combining the results — the pattern that actually scales and controls cost |
| `05_managed_agent_hosted.py` | Handing the whole loop off to Anthropic's own infrastructure (Managed Agents) — for when a script on your laptop isn't good enough and a client needs something hosted, persistent, and schedulable |
| `06-consulting-playbook.md` | How to turn any of the above into an actual client/university deliverable — the scoping questions, the security checklist, and the tier-selection table |
| `07-claude-code-subagents-bonus.md` | Bonus: Claude Code's own `.claude/agents/*.md` system, verified against current docs — NOT portable like `01`–`05`, but useful since you work in this repo daily |
| `08-real-agents-built-in-this-repo.md` | Four real, working subagents built from `07`'s schema, now live in `.claude/agents/` — a tri-phase reviewer (user-reality + domain-lens + Antigravity style) plus its orchestrator |
| `09_tri_phase_review_pipeline.py` | The SAME tri-phase idea as `08`, rebuilt as portable Python (parallel lenses + a synthesizer that isn't allowed to soften findings) — no Claude Code dependency at all |

## Before running anything

```bash
pip install anthropic
```

Auth: either set `ANTHROPIC_API_KEY` as an environment variable, or run `ant auth login`
(the Anthropic CLI) once and the SDK picks up the credential automatically — see
`06-consulting-playbook.md` for why the second option is usually better for anything
beyond a one-off script.

## The one-sentence version of the whole progression

A **prompt** is one request with no memory. An **agent** is a prompt given tools and
a loop, so it can act and re-act until the task is done. A **multi-agent system** is
several agents with different jobs and different prompts, coordinated by code you
write. **Managed Agents** is the same multi-agent idea, except Anthropic runs the
loop and the sandbox for you instead of your own script. Everything in this folder
is a worked example of one rung on that ladder — read them in order and you'll have
built one of each.
