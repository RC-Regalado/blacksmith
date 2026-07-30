# Phase 2 Readiness Report

## Status

ready-with-approval-gates

## Phase 1 Validation

Phase 1 is accepted by human review and current automated validation passes.

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -q
```

Result: 75 passed.

## Existing Data Available For Phase 2

| Area | Available data | Evidence |
|---|---|---|
| Tool call representation | `ToolDefinition`, `ToolCall`, `ToolCallPlan` | `ai_assistant/domain/tools.py` |
| Tool call interpretation | JSON `tool_call` parser without execution | `ai_assistant/application/tool_calls.py` |
| Runtime handoff point | Runtime stores `last_tool_plan` after model response | `ai_assistant/application/runtime.py` |
| Permission vocabulary | Protobuf `PermissionLevel` enum exists | `proto/toolserver.proto` |
| Result vocabulary | Protobuf `ToolStatus` and `ToolResponse` exist | `proto/toolserver.proto` |
| Transport primitive | Unix socket protobuf client exists | `ai_assistant/tools/unix_socket_client.py` |
| C tool server prototype | `noop`, `echo`, `list_tools` documented | `c_toolserver/README.md` |
| Safety baseline | Phase 1 forbids tool execution and shell execution | `docs/architecture.md`, ADR-008 |
| Test categories | Unit, integration, contract, smoke and ollama markers exist | `pytest.ini` |

## Data Missing Before Implementation

These are required before enabling any real tool execution path.

| Missing data | Why it matters | Recommended owner |
|---|---|---|
| Initial allowed tools | Prevents generic execution surface. Start with `noop`, `echo`, `list_tools` only if approved. | Product owner |
| Tool permission policy | Maps each tool to max permission level and denial behavior. | Architect/security reviewer |
| Confirmation rule | Defines when CLI must ask the user before running a tool. | Product owner |
| Audit record schema | Phase 2 requires audit; define request ID, session, tool name, permission, dry-run flag, status, timestamps and sanitized error. | Persistence implementer |
| Timeout defaults | Existing proto supports timeout; no project default or per-tool override is approved. | Architect |
| Workspace boundary | Required before any filesystem-writing tool exists. | Product owner/security reviewer |
| Error redaction policy | Prevents leaking secrets or raw model/provider content into logs. | Security reviewer |
| New ADR for tool execution | ADR-008 only covers Phase 1 no-execution; Phase 2 needs an accepted execution policy ADR. | Architect |

## Approval Gates

- `PHASE2-G1`: approve exact tool execution safety policy.
- `PHASE2-G2`: approve initial tool scope and permission mapping.
- `PHASE2-G3`: approve audit persistence target and retention.

## Recommended First Phase 2 Milestone

Do not connect model output to tool execution yet.

Small first milestone:

1. Create a proposed ADR for tool execution policy.
2. Add application ports for `ToolCatalog`, `ToolPolicy`, `ToolExecutor` without concrete side effects.
3. Add a dry-run-only executor fake for tests.
4. Add CLI confirmation shape as a documented contract, not broad UI work.
5. Validate denial-by-default behavior.

## Readiness Decision

The repository is technically ready to plan Phase 2, but not ready to execute model-requested tools until the three approval gates are closed.
