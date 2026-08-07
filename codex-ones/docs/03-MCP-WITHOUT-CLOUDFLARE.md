# MCP without Cloudflare

Cloudflare is one way to expose an HTTP service. It is not part of MCP and it is not required to build, test, demonstrate, or internally operate an MCP server.

MCP answers: “How does a host discover and call tools, resources, and prompts?” Hosting answers: “Where does the process run, how is it reached, and who secures it?” Keep those decisions separate.

## Choose the smallest deployment

| Option | Network listener | Best for | Main boundary |
|---|---:|---|---|
| In-process test client | No | Automated server tests | Test process |
| Local stdio | No | Codex/desktop prototype, one user | Logged-in OS user and child process |
| Loopback Streamable HTTP | Local only | Multiple local clients and integration tests | Machine account + local port |
| Internal workstation/VM service | Internal | Small team pilot where IT permits a managed host | Institutional network + service identity |
| Internal container/Kubernetes/OpenShift | Internal | Governed multi-user service | Platform identity, ingress, namespace, database role |
| Approved public-cloud app/container service | Configurable | Managed production service when institution standardises on a cloud | Cloud tenant, private networking, IdP, platform controls |
| External managed MCP host | External | Only after procurement/security/privacy approval | Vendor contract and identity integration |

For your university demonstration, start with stdio. It proves tool discovery, schemas, invocation, and agent use without creating an inbound endpoint. If colleagues need a shared pilot, ask which managed runtime and identity pattern are already approved rather than introducing a new edge provider.

## The recommended path

```text
in-memory test
    -> local stdio with synthetic data
    -> loopback HTTP integration test
    -> security/privacy architecture review
    -> approved internal runtime with approved aggregate view
    -> bounded pilot
```

Do not move right merely to make the demo look more “real.” Move when a new user or operating requirement demands it.

## What the sample server exposes

`mcp-server` has four read-only tools:

- `list_reporting_periods`
- `get_application_snapshot`
- `get_data_quality`
- `compare_application_periods`

It also exposes a methodology resource. It does not expose raw rows, SQL, arbitrary file reads, publication, or admission decisions.

That shape is intentional. MCP tool descriptions are visible to a model; the server must still authenticate, authorize, validate, and constrain every call.

## Stdio: the zero-cloud route

The MCP host launches the server as a child process and speaks over stdin/stdout. Benefits:

- no open port;
- no DNS or TLS setup;
- no cloud account;
- easy use from Codex;
- the server can call local approved tools under the user's existing permissions.

Constraints:

- it is primarily per-user;
- environment variables and absolute paths must be configured in the host;
- deployment and updates must reach each workstation;
- local permissions can still be too broad.

Never `print()` diagnostics from a stdio server. Stdout is the protocol wire; use standard logging, which writes to stderr.

## Streamable HTTP: shared capability

Use Streamable HTTP for a URL-addressable service. New work should not use the legacy SSE transport.

For local development, bind to `127.0.0.1`. For a real hostname:

- terminate TLS through approved infrastructure;
- use OAuth 2.1 / institutional identity rather than a hard-coded shared secret;
- validate token issuer, audience, expiry, scopes, and caller;
- perform per-tool and per-resource authorization;
- allowlist the exact Host and Origin values;
- propagate an authenticated subject or service identity through server-controlled context;
- use a least-privilege database identity;
- rate-limit by identity and tool;
- include timeouts, health checks, monitoring, and incident ownership.

The current MCP Python SDK enables DNS-rebinding protection for localhost by default. A deployment behind a real hostname can return HTTP 421 until the hostname is explicitly allowed. That is a security gate, not a random client failure.

## University-friendly hosting alternatives

Ask infrastructure colleagues which of these the organisation already supports:

1. **An internal Windows or Linux VM/service.** Run the ASGI app as a managed service behind the existing reverse proxy and identity layer.
2. **An internal container platform.** Deploy the supplied Dockerfile to Kubernetes, OpenShift, or another organisational platform; use secrets management and workload identity.
3. **The institution's approved cloud tenant.** A generic container can run on Azure Container Apps, Azure App Service for Containers, AWS ECS/App Runner, Google Cloud Run, or an equivalent—but choose the provider the institution already governs.
4. **An existing internal API platform.** Mount MCP beside an approved FastAPI/Starlette service or expose the same deterministic domain functions through both REST and MCP.
5. **No shared hosting.** Keep stdio for the prototype and demonstrate it locally. This is a legitimate answer when network approval is not yet available.

The repository gives you a container, not a recommendation to bypass architecture review.

If the university's approved path is Azure, Container Apps is a plausible conversation starter because it can run a generic container with internal ingress, HTTPS, revisions, secrets, and Microsoft Entra authentication. Its platform authentication can reject unauthenticated traffic, but your service must still enforce fine-grained tool and data authorization from validated identity claims. App Service for Containers is another managed container route. Treat these as options for the university's architects to select, not as a personal deployment shortcut. See [Azure Container Apps overview](https://learn.microsoft.com/en-us/azure/container-apps/overview), [Container Apps authentication](https://learn.microsoft.com/en-us/azure/container-apps/authentication), and [containerized Python on App Service](https://learn.microsoft.com/en-us/azure/developer/python/tutorial-containerize-simple-web-app-for-app-service).

## MCP or ordinary API?

Use an ordinary API when fixed application code calls fixed operations. Add MCP when model-driven clients benefit from standardized discovery and typed capabilities. It is often useful to expose one domain service through both:

```text
approved database/view
        |
deterministic domain service
        |------------------|
REST endpoint          MCP tools/resources
fixed app clients      approved agent hosts
```

Keep the rules in the domain service so REST and MCP cannot disagree.

## Current Python compatibility seam

On 7 August 2026, PyPI reports:

- `openai 2.53.0`;
- `openai-agents 0.19.4`, requiring `mcp>=1.19,<2`;
- `mcp 2.0.0` as the current stable MCP SDK.

The sample therefore uses:

```text
.venv       OpenAI client + Agents SDK + MCP v1 client dependency
.venv-mcp   MCP v2 server + deterministic codex_ones package
```

The server supports current and legacy protocol clients. Separate environments are a sound service boundary, not a workaround to hide.

## Production questions before a URL

- What exact user job does each tool serve?
- Who owns every returned definition?
- Which identity is the caller, and where is it established?
- Which tools can that identity discover and call?
- Does a model ever supply identity, tenant, scope, SQL, or filesystem paths?
- Which calls have side effects, and where is approval enforced?
- What enters logs, traces, caches, queues, and serialized state?
- What is the response when data is stale, conflicting, or unavailable?
- Who monitors the service and can turn it off?
- How are clients and schemas versioned?

If those answers are not written, hosting is premature.

Official references: [MCP Python SDK](https://py.sdk.modelcontextprotocol.io/), [connect to a real host](https://py.sdk.modelcontextprotocol.io/get-started/real-host/), [deploy and scale](https://py.sdk.modelcontextprotocol.io/run/deploy/), [authorization](https://py.sdk.modelcontextprotocol.io/authorization/), [Agents SDK MCP clients](https://openai.github.io/openai-agents-python/mcp/), and [Codex MCP](https://developers.openai.com/codex/mcp).
