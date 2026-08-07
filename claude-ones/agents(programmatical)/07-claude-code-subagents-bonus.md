# Bonus: Claude Code's own subagent system (`.claude/agents/*.md`)

Everything in `01`–`05` is **portable** — plain Python, runs anywhere. This file
is the opposite: it's **specific to Claude Code**, the tool you're using right
now to read this. Worth knowing since you work in this repo daily, but don't
confuse it with the SDK material above — a `.claude/agents/*.md` file only means
something inside Claude Code; it is not code you could hand to a company running
their own infrastructure. Verified against Claude Code's own docs on 2026-08-07;
version numbers below (`v2.1.x`) may have moved on by the time you read this.

## The frontmatter schema

```markdown
---
name: my-agent-name
description: Use this agent when the user asks about X — phrase it as a trigger condition, not a label
tools: Read, Grep, Glob, Bash
model: sonnet
---

The markdown body below the frontmatter is the agent's system prompt,
verbatim. No templating, no variable injection.
```

| Field | What it does | Notes |
|---|---|---|
| `name` | Required. Lowercase + hyphens only. | `:` is reserved for plugin scopes and errors if used |
| `description` | Required. **This is not documentation — it's read by the orchestrating model to decide when to auto-delegate to this agent.** | Phrase it as "Use this agent when..." — that phrasing measurably improves whether it actually gets invoked automatically |
| `tools` | Comma-separated string or YAML list; allowlist | Omit to inherit all available tools. Supports `mcp__servername` and `mcp__*` patterns |
| `disallowedTools` | Same syntax; denylist, applied before `tools` | |
| `model` | `sonnet` / `opus` / `haiku` / `fable` / a full model ID / `inherit` | Defaults to `inherit` (the parent session's model) |
| `permissionMode` | `default` / `acceptEdits` / `bypassPermissions` / `plan` / etc. | Inherits from parent if omitted |
| `maxTurns` | A positive integer cap on agentic turns | No cap by default |
| `isolation` | `worktree` | Runs the agent in a temporary git worktree branched from default |
| `mcpServers` | Named references or inline server definitions | Inline ones are scoped to just this subagent |
| `hooks` | `PreToolUse` / `PostToolUse` / `Stop` only | `Stop` becomes `SubagentStop` at runtime |
| `color` | A display color in the transcript UI | Cosmetic only |

**Precedence when the same agent name exists in multiple places** (highest wins):
org-managed settings → the `--agents` CLI flag → project `.claude/agents/` →
user `~/.claude/agents/` → a plugin's bundled agents.

**Managing them:** as of recent versions, `/agents` no longer opens an interactive
wizard — it just tells you to ask Claude to create the file, or edit
`.claude/agents/` directly. The file watcher picks up edits to *existing* agent
files within a few seconds; creating the *first* agent file in a brand-new
`agents/` directory needs a restart to be picked up.

## Two worked examples

**A narrow, read-only reviewer** (the "critic" idea from Lesson 3, as a Claude
Code agent instead of a Python script):

```markdown
---
name: spec-compliance-reviewer
description: Use this agent when code has just been changed and you want an independent check that it matches the written spec/plan, not a general code review. Only invoke when a spec or plan document exists to check against.
tools: Read, Grep, Glob
model: sonnet
---

You review changed code against a specific spec or plan document — nothing
else. You do not evaluate code style, performance, or general quality. For
each requirement in the spec, state whether the code satisfies it, with a
file:line citation, or state plainly that it does not. Do not soften a real
gap to be agreeable.
```

**A safety-railed mechanical runner** (the exact pattern used earlier in this
session to babysit a long benchmark):

```markdown
---
name: benchmark-runner
description: Use this agent to launch and babysit a long-running benchmark or test script. Not for interpreting results or making judgment calls — those stay with the caller.
tools: Bash
model: sonnet
---

You launch one specified command with run_in_background and wait for it to
complete, then report the raw output verbatim. Read-only repo: never run git,
never edit files. If the command errors or hangs, report the exact output —
do not retry with changed flags or attempt to fix it yourself.
```

The second one is a direct, durable version of the throwaway prompt used earlier
in this session to run the checkpointed-Whisper benchmark — the difference
between a one-off prompt and a saved `.md` file is exactly the difference
between using a pattern once and being able to reuse it every time this kind
of task comes up.

## Open questions the research couldn't fully verify

- Whether there's an official best-practices guide for writing `description`
  beyond "phrase it as a trigger" — the phrasing advice is solid, but there's
  no canonical tuning document as of this check.
- The exact interaction between `Agent(name)` spawn restrictions and
  plugin-scoped agent names wasn't fully documented.
- Version-numbered behavior (default nesting depth, background-by-default,
  etc.) changes across releases — treat specific version numbers above as a
  snapshot, not a guarantee, and re-verify against current docs before relying
  on them for something load-bearing.
