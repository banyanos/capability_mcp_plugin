# Capability MCP Plugin Development Plan

Status: planning baseline
Last updated: 2026-09-10

## Goal

`capability_mcp_plugin` owns the Banyanos capability-facing MCP management layer.
It should present Provider, MCP Server, Tool, and Invocation GraphQL contracts to
Banyanos callers while delegating durable catalog storage and runtime execution
to `mcp_protocol_plugin`.

This plugin is a compatibility and product-domain layer. It should not implement
an MCP runtime or duplicate daemon persistence tables.

## Source Analysis

Source project: `C:\Users\bibo7\gitrepo\silvaengine\mcp_daemon_engine`

The existing capability work is embedded in the MCP daemon under:

- `types/capability_mcp.py`
- `queries/capability_mcp.py`
- `mutations/capability_mcp.py`
- `handlers/capability_mcp.py`
- `handlers/capability_mcp_invoke.py`

The old plan in `mcp_daemon_engine/docs/CAPABILITY_ENGINE_MCP_INTEGRATION_PLAN.md`
shows that read compatibility, registration mutations, invocation adapter,
unified registration, and unregister behavior were already designed around
MCP daemon primitives.

## Target Ownership

Keep in this plugin:

| Area | Target modules |
| --- | --- |
| Capability GraphQL schema | `CapabilityMcpProvider`, `CapabilityMcpTool`, `CapabilityMcpInvocation`, payload and connection types. |
| Compatibility queries | Provider/server/tool/invocation list/detail views shaped for Banyanos clients. |
| Compatibility mutations | Remote/custom/Git/unified registration, refresh/check, invocation/test, and unregister. |
| Banyanos metadata mapping | Display names, descriptions, legacy IDs, transport labels, status labels, trace/agent metadata. |
| Policy integration hooks | Places to call Banyanos authorization, rate limit, circuit breaker, and audit systems when those are migrated. |

Delegate to `mcp_protocol_plugin`:

- MCP catalog entities and persistence.
- External MCP sync, S3/Base64 package processing, Git install/refresh/check.
- Tool/resource/prompt runtime execution and `MCPFunctionCall` audit writes.
- MCP configuration cache refresh/clear.

Consume from `silvaengine_daemon` only through the same shared helpers used by
`mcp_protocol_plugin`: partition context, GraphQL execution helpers, base config,
serialization, plugin module YAML routing, and repository contracts where direct
repository reads are used.

## Proposed Package Shape

```text
capability_mcp_plugin/
|-- capability_mcp_plugin/
|   |-- __init__.py
|   |-- main.py
|   |-- schema.py
|   |-- service.py              # adapter over mcp_protocol_plugin services
|   |-- handlers/
|   |   |-- capability_mcp.py
|   |   `-- invoke.py
|   |-- queries/
|   |   `-- capability_mcp.py
|   |-- mutations/
|   |   `-- capability_mcp.py
|   |-- types/
|   |   `-- capability_mcp.py
|   `-- tests/
|-- docs/
|   `-- DEVELOPMENT_PLAN.md
|-- pyproject.toml
`-- README.md
```

## Compatibility Contract

Read fields should preserve the existing compatibility names:

- `capabilityMcpProvider`, `capabilityMcpProviderList`
- `capabilityMcpServer`, `capabilityMcpServerTools`
- `capabilityMcpTool`, `capabilityMcpToolList`
- `capabilityMcpInvocationList`

Mutation fields should preserve:

- `registerCapabilityRemoteMcp`
- `generateCapabilityCustomMcpUploadUrl`
- `registerCapabilityCustomMcpPackage`
- `registerCapabilityCustomMcpPackageBase64`
- `registerCapabilityCustomMcpGitPackage`
- `refreshCapabilityCustomMcpGitPackage`
- `checkCapabilityCustomMcpGitPackageVersion`
- `registerCapabilityMcp`
- `invokeCapabilityMcpTool`
- `testCapabilityMcpTool`
- `unregisterCapabilityMcp`

Transport mapping remains:

| Capability transport | MCP plugin source |
| --- | --- |
| `REMOTE` | `MCPModule.source == "external"` |
| `CUSTOM` | S3, Base64, Git, or locally installed custom module |
| `BUILTIN` | Deployment-configured module name, not a storage marker |

## Migration Phases

### Phase 1: Bootstrap Package

- Create packaging metadata and package folders.
- Declare `silvaengine_daemon` as the shared daemon substrate dependency.
- Add the capability MCP plugin module YAML descriptor required by
  `silvaengine_daemon` internal plugin routing.
- Copy capability-specific GraphQL types, queries, mutations, and handlers from
  `mcp_daemon_engine` with imports renamed.
- Add a service adapter boundary instead of importing old daemon internals
  directly.

### Phase 2: Define MCP Service Adapter

- In `service.py`, wrap `mcp_protocol_plugin` operations needed by capability
  flows: module lookup/list, function lookup/list, function-call list, remote
  sync, package upload/process, Git install/refresh/check, tool invocation,
  module unregister, and cache clear.
- Keep adapter return values daemon-native internally; convert to capability
  shapes only in query/mutation resolvers.
- Preserve header keys verbatim in provider config views.

### Phase 3: Rebuild Registration and Invocation

- Port specific and unified registration mutations with the same validation and
  feature-flag behavior from the old compatibility layer.
- Port unregister behavior with `expectedTransport` safety guard and orphaned
  setting cleanup.
- Port invocation/test mutations so `_capability_context` carries `traceId` and
  `agentId` into the underlying `MCPFunctionCall` audit record.

### Phase 4: Banyanos Cutover

- Rewire Banyanos callers from capability-engine MCP tables/transports to this
  plugin's GraphQL surface.
- Keep legacy `tenant_capability_mcp_server`, `tenant_capability_mcp_tool`, and
  `tenant_capability_tool_invocation` tables read-only during the transition.
- Verify provider counts, tool counts, transport labels, and invocation records
  against the old views for representative tenants.

### Phase 5: Policy and Cleanup

- Decide which Banyanos policy concerns belong in this plugin: authorization,
  rate limits, circuit breakers, dashboard metadata, and historical audit reads.
- Remove legacy capability-engine MCP transport/runtime code only after traffic
  proves the plugin path is authoritative.
- Add historical-read bridging only if product dashboards require old invocation
  records in the new view.

## Acceptance Criteria

- Banyanos clients can manage MCP providers, servers, tools, and invocations
  through this plugin without calling `mcp_daemon_engine` directly.
- Shared daemon behavior is imported from `silvaengine_daemon`, not the retired
  planning package.
- Capability MCP routes are registered through `silvaengine_daemon` internal
  plugin routing YAML and the capability MCP plugin module YAML.
- Outside traffic flows through `silvaengine_gateway` first, then
  `silvaengine_daemon`, then this plugin.
- The plugin stores no duplicate MCP catalog tables; source of truth remains
  `mcp_protocol_plugin` catalog storage.
- Provider/tool/invocation shapes match the compatibility contract from the old
  integration plan.
- Remote, custom S3/Base64, custom Git, built-in classification, invoke/test,
  and unregister paths have unit tests with mocked MCP service adapter calls.
- A cutover validation report reconciles old Banyanos MCP rows with new plugin
  views for at least one tenant partition.

## Risks

| Risk | Mitigation |
| --- | --- |
| Banyanos clients depend on legacy UUIDs. | Store `legacy_ids` in capability metadata or maintain a small alias map if required. |
| Policy behavior changes during cutover. | Keep authorization/rate/circuit behavior in Banyanos until deliberately migrated. |
| Capability plugin reimplements MCP runtime. | Enforce service-adapter delegation and dependency-boundary tests. |
| Built-in classification drifts by environment. | Treat built-ins as deployment config and include it in release manifests. |
