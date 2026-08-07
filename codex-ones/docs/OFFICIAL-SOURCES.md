# Official source snapshot

These links and versions were checked on 7 August 2026. APIs, model names, package constraints, and deprecation dates are time-sensitive; re-check them before a production decision.

## OpenAI API and models

- [Current model guidance](https://developers.openai.com/api/docs/guides/latest-model)
- [GPT-5.6 prompt guidance](https://developers.openai.com/api/docs/guides/prompt-guidance-gpt-5p6)
- [Function calling](https://developers.openai.com/api/docs/guides/function-calling)
- [Structured outputs](https://developers.openai.com/api/docs/guides/structured-outputs)
- [Responses API migration and concepts](https://developers.openai.com/api/docs/guides/migrate-to-responses)
- [MCP and connectors](https://developers.openai.com/api/docs/guides/tools-connectors-mcp)
- [Background mode](https://developers.openai.com/api/docs/guides/background)
- [Safety best practices](https://developers.openai.com/api/docs/guides/safety-best-practices)
- [Evals guidance and transition notice](https://developers.openai.com/api/docs/guides/evals)

The current model resolver identifies `gpt-5.6-sol` as the frontier model. OpenAI's guidance describes Terra as the balanced capability/cost option and Luna as the high-volume option. The repo therefore makes the model configurable and defaults product examples to Terra.

## OpenAI Agents SDK

- [Agents SDK overview](https://openai.github.io/openai-agents-python/)
- [Tools and agents-as-tools](https://openai.github.io/openai-agents-python/tools/)
- [Agent orchestration](https://openai.github.io/openai-agents-python/multi_agent/)
- [Human-in-the-loop](https://openai.github.io/openai-agents-python/human_in_the_loop/)
- [MCP clients](https://openai.github.io/openai-agents-python/mcp/)
- [Guardrails](https://openai.github.io/openai-agents-python/guardrails/)
- [Tracing and sensitive-data controls](https://openai.github.io/openai-agents-python/tracing/)

## Codex

- [AGENTS.md](https://developers.openai.com/codex/guides/agents-md)
- [Skills](https://developers.openai.com/codex/skills)
- [MCP](https://developers.openai.com/codex/mcp)
- [Codex SDK](https://developers.openai.com/codex/sdk)
- [Codex as an MCP server](https://developers.openai.com/codex/mcp-server)

Codex repository skills live under `.agents/skills`; user skills live under `$HOME/.agents/skills`. A skill encodes a reusable workflow. MCP supplies live context/actions. `AGENTS.md` supplies repository instructions.

## Model Context Protocol

- [MCP Python SDK v2](https://py.sdk.modelcontextprotocol.io/)
- [Connect to a real host](https://py.sdk.modelcontextprotocol.io/get-started/real-host/)
- [Server construction](https://py.sdk.modelcontextprotocol.io/server/)
- [Deploy and scale](https://py.sdk.modelcontextprotocol.io/run/deploy/)
- [Authorization](https://py.sdk.modelcontextprotocol.io/authorization/)
- [MCP authorization security](https://modelcontextprotocol.io/docs/tutorials/security/authorization)

The current SDK documentation calls v2 the stable line and recommends Streamable HTTP for shared deployment. Stdio remains the direct local transport. Legacy SSE is superseded for new work.

## Package snapshot

PyPI metadata checked on the snapshot date:

| Package | Version | Python | Important constraint |
|---|---:|---|---|
| `openai` | 2.53.0 | >=3.10 | Responses client |
| `openai-agents` | 0.19.4 | >=3.10 | Requires `mcp>=1.19,<2` |
| `mcp` | 2.0.0 | >=3.10 | Current stable server SDK |

Re-check with PyPI or your approved internal package mirror before updating pins. Upgrade one environment at a time and rerun offline tests, MCP in-memory tests, tool-trajectory evals, and approval/resume drills.
