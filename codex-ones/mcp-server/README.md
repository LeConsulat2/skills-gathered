# Synthetic University Insights MCP

This is a read-only MCP server over invented aggregate data. It requires no Cloudflare account and supports two useful transports:

- **stdio** for a local proof, Codex, or one-user desktop workflow;
- **Streamable HTTP** for localhost, an internal service, or an approved container platform.

Do not start a new build on legacy SSE transport.

## Why this has a separate Python environment

As checked on 7 August 2026:

- `mcp` current stable is `2.0.0`;
- `openai-agents` current is `0.19.4` and still requires `mcp>=1.19,<2`.

Installing both into one environment forces one side onto the wrong SDK line. The clean design is two processes with two environments. MCP is the contract between them.

## Create the MCP v2 environment

From `codex-ones`:

```powershell
python -m venv .venv-mcp
.\.venv-mcp\Scripts\python.exe -m pip install -e .
.\.venv-mcp\Scripts\python.exe -m pip install -e ".\mcp-server[dev]"
.\.venv-mcp\Scripts\python.exe -m pytest .\mcp-server\tests -q
```

The first editable install provides the shared deterministic analytics package. It does not install the Agents SDK. The second install provides MCP v2.

## Option 1: local stdio

Sanity-check the launch command:

```powershell
.\.venv-mcp\Scripts\python.exe -m university_insights_mcp.server --transport stdio
```

Silence is success: stdout belongs to the MCP protocol and the process is waiting for a host. Press `Ctrl+C`.

Register it with Codex using absolute paths:

```powershell
codex mcp add university-insights --env CODEX_ONES_SYNTHETIC_ONLY=1 -- C:\absolute\path\codex-ones\.venv-mcp\Scripts\python.exe -m university_insights_mcp.server --transport stdio
codex mcp list
```

This is the best starting point inside an organisation: no listener, DNS, TLS, cloud account, or exposed endpoint. The host and server share the logged-in user's operating-system permissions, so that permission boundary still matters.

To use the same server from `examples/10_mcp_client_agent.py`, run the client from the **main** `.venv` and point it at the MCP environment:

```powershell
$env:MCP_SERVER_PYTHON = (Resolve-Path .\.venv-mcp\Scripts\python.exe)
python scripts\check_mcp_bridge.py
python examples\10_mcp_client_agent.py
```

The bridge check lists tools through MCP without making a model/API request.

## Option 2: localhost Streamable HTTP

Terminal 1, in the MCP environment:

```powershell
.\.venv-mcp\Scripts\python.exe -m university_insights_mcp.server --transport http
```

Terminal 2, in the main learning environment:

```powershell
$env:MCP_SERVER_URL = "http://127.0.0.1:8000/mcp"
python examples\10_mcp_client_agent.py
```

Or register the URL directly:

```powershell
codex mcp add university-insights-http --url http://127.0.0.1:8000/mcp
```

Local HTTP is useful for testing multiple clients. It is not production merely because it uses HTTP.

## Option 3: a portable container

Build from the `codex-ones` directory so the image can include the shared package and synthetic data:

```powershell
docker build -f mcp-server\Dockerfile -t university-insights-mcp:local .
docker run --rm -p 127.0.0.1:8000:8000 university-insights-mcp:local
```

The image is not tied to a cloud provider. It can run on a developer machine, an internal container host, Kubernetes/OpenShift, Azure Container Apps, Azure App Service for Containers, or another platform your organisation already governs.

## Before any real organisational deployment

This sample intentionally does not pretend that a hard-coded API key is enterprise security. For a real Streamable HTTP service:

- integrate the organisation's OAuth 2.1 / identity provider and validate token audience and scope;
- serve only through HTTPS;
- define per-tool authorization, not merely “can connect to the server”;
- allowlist the real `Host` and browser `Origin` values with `MCP_ALLOWED_HOSTS` and `MCP_ALLOWED_ORIGINS`;
- use a read-only database identity for these read-only tools;
- keep tenant/user identity out of model-generated parameters;
- emit metadata and decision audit events without copying sensitive payloads;
- add rate limits, timeouts, health checks, release ownership, and a kill switch;
- re-run privacy, security, and records-management review when the data or purpose changes.

See [MCP without Cloudflare](../docs/03-MCP-WITHOUT-CLOUDFLARE.md) for the deployment decision tree.
