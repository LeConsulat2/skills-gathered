# Repository Guidelines

## Purpose

This workspace collects reusable agent definitions, skills, and worked agent examples.
It is a reference/porting repository, not a single deployable application.

## Layout

- `claude-ones/skills/`: Claude-oriented skills. Each skill lives in its own folder
  and is defined by a `SKILL.md` file.
- `claude-ones/agents/`: Claude Code subagent definitions in Markdown with YAML
  frontmatter.
- `claude-ones/agents(programmatical)/`: Standalone Anthropic SDK examples and their
  learning notes. Read `00-START-HERE.md` before changing these examples.
- `codex-ones/`: Destination for Codex-native adaptations. Keep adaptations here
  rather than overwriting the Claude originals unless the task explicitly requests
  a source update.

## Editing Conventions

- Preserve the distinction between app-specific skills and `-portable` variants.
  Portable variants must remain self-contained and must not depend on private project
  files, history, or product names.
- Keep skill metadata at the top of `SKILL.md` in valid YAML frontmatter. Make trigger
  descriptions concrete enough that an agent can decide when to activate the skill.
- Keep agent definitions declarative: YAML frontmatter first, followed by focused role
  instructions, required inputs, review criteria, and an explicit output contract.
- Treat examples and source-specific references as intentional historical material.
  Do not silently rewrite model names, API patterns, or missing external file references;
  verify current provider documentation and state the migration scope first.
- Prefer small, reviewable changes. When porting, preserve the original alongside the
  adaptation and document any semantic differences.
- Never add real API keys, tokens, credentials, private user data, or generated outputs.

## Validation

- For Python-only edits, run:
  `python -m compileall -q "claude-ones/agents(programmatical)"`
- Inspect changed Markdown frontmatter and confirm every opening `---` has a matching
  closing delimiter before the document body.
- Search portable skills for accidental repository-specific references after editing.
- Do not execute the Anthropic examples as a validation step unless the user explicitly
  requests it: they require credentials, may make paid network calls, and some examples
  expose local tools to the model.
- Remove generated `__pycache__` directories before handing off changes.

## Documentation

- Update the nearest guide when adding a new example or changing its intended reading
  order.
- Write instructions in plain Markdown and use repository-relative paths in prose.
- Call out prerequisites, provider dependencies, and whether an artifact is portable or
  tied to a specific codebase.
