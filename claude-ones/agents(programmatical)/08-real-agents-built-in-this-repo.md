# What just got built, for real, in `.claude/agents/`

Files `01`–`05` were teaching material you run yourself. These four are different:
they're **live, working Claude Code subagents**, sitting in this repo's
`.claude/agents/` right now, using the exact frontmatter schema verified in
`07-claude-code-subagents-bonus.md`. You can invoke `tri-phase-orchestrator` today.

| File | Role | Phase |
|---|---|---|
| `.claude/agents/ux-reality-checker.md` | Applies the `fable-user-reality` skill's Four Fates + guardrail taxonomy to a feature/diff | 1 |
| `.claude/agents/domain-lens-checker.md` | Applies `fable-domain-lens-portable` — checks whether decisions trace to dated behavior facts or are untested assumptions | 2 |
| `.claude/agents/antigravity-style-checker.md` | Checks UI code against the Antigravity glassmorphism spec (`antigravity.md`, cross-checked against the newer `.claude/commands/Design.md`) | 3 |
| `.claude/agents/tri-phase-orchestrator.md` | Runs all three in sequence on the same target, then writes one consolidated ship/don't-ship verdict | orchestrator |

## The design choices worth noticing (they're reusable, not one-off tricks)

- **The two checker agents don't repeat their skill's content in the system
  prompt.** They declare `skills: [fable-user-reality]` / `skills: [fable-domain-lens-portable]`
  in frontmatter and the skill is preloaded automatically. The agent's own body
  only says *how to apply* the skill to a review task, not *what the skill says*
  — so if the skill file is ever updated, the agent doesn't drift out of sync
  with a stale copy-paste.
- **Each specialist is read-only** (`Read, Grep, Glob`, no `Bash`/`Write`/`Edit`).
  A review agent that can also edit the code it's reviewing is a different, more
  dangerous tool — keep the two roles separate even when it'd be "more efficient"
  to let the reviewer just fix what it finds.
- **The orchestrator's `tools:` field names exactly which three agents it may
  spawn** (`Agent(ux-reality-checker, domain-lens-checker, antigravity-style-checker)`),
  not a bare `Agent` that could spawn anything. This is the Claude Code
  equivalent of Lesson 4's principle: give a coordinator the narrowest tool
  surface that still lets it do its job.
- **The orchestrator is explicitly told not to soften findings.** A synthesis
  step is exactly where a real problem quietly becomes "mostly fine" if nobody
  guards against it — the same failure mode Lesson 3's critic prompt was
  written to resist ("do not soften real problems to be polite").

## Try it

```
Use the tri-phase-orchestrator agent to review [some recent feature/PR/plan] before I ship it.
```

Same idea as Lesson 3 and Lesson 4, just running as native Claude Code subagents
instead of a Python script you wrote yourself — two different implementations of
the identical underlying idea: specialist roles, narrow tools, and a synthesis
step that isn't allowed to lie.
