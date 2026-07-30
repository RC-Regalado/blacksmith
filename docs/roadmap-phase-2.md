# Phase 2 Roadmap — Read-Only Workspace Tools

## Objective

Enable the assistant to inspect one authorized local workspace safely through two structured tools:

- `list_directory`
- `read_file`

The model may request a tool, but it never authorizes execution. Authorization belongs to deterministic application policy.

## Inherited baseline

Phase 1 is complete and approved with 75 passing tests. The repository already contains a provider-neutral `Message`, framework-agnostic runtime, model and memory ports, sessions, transactional SQLite persistence, typed errors, declarative tool calls, a Unix-socket protobuf client and a prototype C tool service.

## Target flow

```text
User request
    ↓
Model response
    ↓
ToolCallInterpreter
    ↓
ToolCallPlan
    ↓
ToolCatalog
    ↓
ToolPolicy
    ↓
PathPolicy
    ↓
ToolExecutionCoordinator
    ↓
AuditRecorder
    ↓
ToolExecutor
    ↓
Tool result message
    ↓
Second model call
    ↓
Final assistant response
```

## Completion statement

Phase 2 is complete when the assistant can answer questions such as:

```text
What files are in this project?
```

and:

```text
Explain what ai_assistant/application/runtime.py does.
```

using only approved read-only tools while remaining unable to:

- read outside the configured workspace;
- write, delete, rename, copy or create files;
- execute shell commands or processes;
- follow symlinks outside the workspace;
- read blocked secrets;
- bypass resource limits;
- execute unknown tools;
- omit audit records.

---

# Architectural principles

## Deny by default

Any tool, path, argument, permission or limit not explicitly allowed is denied.

## Model intent is not authorization

The model proposes a `ToolCall`; policy decides whether it may run.

## Read-only workspace

Phase 2 exposes no write, process, shell, network or Git capability.

## Workspace confinement

All filesystem operations are relative to:

```text
AI_ASSISTANT_WORKSPACE
```

## Double validation

Paths and limits are validated independently in Python and in the concrete executor or C tool service.

## Bounded resources

Every operation has hard limits for timeout, bytes, entry count, depth, path length, request size and response size.

## Complete audit

Allow, deny, success, timeout and failure outcomes are recorded with sanitized metadata.

---

# Initial tool contracts

## `list_directory`

### Request

```json
{
  "path": "ai_assistant",
  "recursive": false,
  "include_hidden": false,
  "max_entries": 200
}
```

### Response

```json
{
  "path": "ai_assistant",
  "entries": [
    {
      "name": "application",
      "type": "directory",
      "size": null
    }
  ],
  "truncated": false
}
```

### Required restrictions

- Path resolves inside the workspace.
- Hidden entries are excluded.
- Recursion is disabled by default.
- Depth and entry limits are enforced.
- Special files are not opened.
- External symlinks are denied.

## `read_file`

### Request

```json
{
  "path": "ai_assistant/application/runtime.py",
  "offset": 0,
  "max_bytes": 16384
}
```

### Response

```json
{
  "path": "ai_assistant/application/runtime.py",
  "content": "...",
  "bytes_read": 16384,
  "truncated": true
}
```

### Required restrictions

- Path resolves inside the workspace.
- Only regular files are readable.
- Byte count and offset are validated.
- Sensitive and hidden files are denied.
- External symlinks are denied.
- No automatic full-file retry after truncation.

---

# Default limits

| Limit | Default | Hard maximum |
|---|---:|---:|
| Tool timeout | 5 s | 30 s |
| Read bytes | 16 KiB | 64 KiB |
| Directory entries | 200 | 1,000 |
| Recursive depth | 0 | 3 |
| Path length | 1,024 chars | 4,096 chars |
| Request payload | 64 KiB | 256 KiB |
| Response payload | 128 KiB | 1 MiB |

Overrides beyond a hard maximum are denied.

# Sensitive path policy

Deny at minimum:

```text
.env
.env.*
*.pem
*.key
*.p12
*.pfx
id_rsa
id_ed25519
credentials.json
secrets.*
*.kubeconfig
```

Hidden paths are denied in Phase 2. The model cannot override this policy.

---

# Required application ports

## `ToolCatalog`

Resolves only approved tool definitions by exact name.

## `ToolPolicy`

Returns one of:

```text
allow
deny
require_confirmation
```

For Phase 2, the two approved tools require no interactive confirmation when every policy check passes.

## `PathPolicy`

Normalizes paths, confines them to the workspace, enforces symlink and sensitive-file rules, and validates expected file types.

## `ToolExecutor`

Executes only an already-authorized request. It never decides authorization.

Planned implementations:

- `FakeToolExecutor`
- `DryRunToolExecutor`
- `LocalReadOnlyToolExecutor`
- `UnixSocketToolExecutor`

## `AuditRecorder`

Stores sanitized execution events independently of conversation history.

## `ToolExecutionCoordinator`

Coordinates catalog lookup, validation, policy, audit, execution and normalized tool-result creation.

---

# Audit requirements

Record:

- request ID;
- session ID;
- tool name;
- permission level;
- sanitized workspace identifier;
- sanitized argument summary;
- policy decision and denial reason;
- dry-run flag;
- start/end timestamps;
- duration;
- status;
- timeout;
- sanitized error code;
- artifact identifiers, if any.

Do not record by default:

- complete prompts;
- complete model responses;
- secret values;
- complete file contents;
- authentication headers;
- raw internal tracebacks exposed to users.

Recommended persistence: local SQLite, append-oriented, initially without automatic deletion.

---

# Error model

Add or refine:

```text
ToolNotFoundError
ToolPolicyDeniedError
ToolArgumentError
WorkspaceNotConfiguredError
PathOutsideWorkspaceError
SensitivePathError
UnsupportedFileTypeError
ToolTimeoutError
ToolTransportError
ToolProtocolError
ToolResponseTooLargeError
ToolAuditError
```

---

# Milestones

## M2.1 — Approve Phase 2 security decisions

**Size:** M

### Objective

Formalize policy before productive filesystem execution.

### Tasks

1. Create ADR-016 through ADR-025 as Proposed.
2. Approve the allowlist, workspace policy, limits, audit schema, symlink behavior and single-round runtime policy.
3. Resolve Phase 2 gates in `.agent/human-review.md`.
4. Update architecture documentation.

### Acceptance criteria

- [ ] `list_directory` and `read_file` are the only productive tools.
- [ ] Deny-by-default is binding.
- [ ] Workspace and symlink rules are explicit.
- [ ] Sensitive paths are explicit.
- [ ] Audit and redaction rules are explicit.
- [ ] Default and hard limits are explicit.
- [ ] No implementation task remains blocked by an unresolved policy decision.

### Suggested commit

```text
docs(adr): define phase 2 read-only tool policy
```

## M2.2 — Add tool execution domain models

**Size:** M

### Scope

Add provider-neutral models for execution request, policy decision, execution context, normalized result, audit event and sanitized error.

### Acceptance criteria

- [ ] No infrastructure dependency leaks into domain.
- [ ] Request ID and session ID are explicit.
- [ ] Policy decisions are explicit tagged values.
- [ ] Results include truncation metadata.
- [ ] Invalid construction is tested.

### Suggested commit

```text
feat(tools): add execution domain models
```

## M2.3 — Add application ports

**Size:** M

### Scope

Add `ToolCatalog`, `ToolPolicy`, `PathPolicy`, `ToolExecutor` and `AuditRecorder`.

### Acceptance criteria

- [ ] Application imports no concrete infrastructure adapters.
- [ ] Executor cannot authorize.
- [ ] Policy performs no external effects.
- [ ] Fakes can implement every port.

### Suggested commit

```text
feat(tools): define execution application ports
```

## M2.4 — Implement the static tool catalog

**Size:** S

### Scope

Register only:

```text
list_directory
read_file
```

`noop` may remain test-only.

### Acceptance criteria

- [ ] Exact-name lookup only.
- [ ] Unknown names are rejected.
- [ ] Limits and permission metadata are immutable from model input.

### Suggested commit

```text
feat(tools): add static read-only tool catalog
```

## M2.5 — Implement workspace and path policy

**Size:** L

### Scope

- workspace configuration;
- canonical path resolution;
- traversal rejection;
- external symlink rejection;
- hidden and sensitive path denial;
- expected file-type checks;
- path-length limits.

### Acceptance criteria

- [ ] `../` escape is denied.
- [ ] External absolute path is denied.
- [ ] Internal valid path is allowed.
- [ ] External symlink is denied.
- [ ] Hidden and sensitive paths are denied.
- [ ] devices, sockets, FIFOs and other special files are denied.
- [ ] missing workspace produces a typed error.

### Suggested commit

```text
feat(security): enforce workspace path policy
```

## M2.6 — Implement deny-by-default tool policy

**Size:** M

### Scope

Validate tool name, permission, arguments, timeout, byte limits, depth, entry count and path-policy result.

### Acceptance criteria

- [ ] Unknown tools are denied.
- [ ] Malformed arguments are denied.
- [ ] Values above hard maximum are denied.
- [ ] Denied requests never invoke an executor.
- [ ] Every denial has a stable reason code.

### Suggested commit

```text
feat(security): add deny-by-default tool policy
```

## M2.7 — Add fake and dry-run executors

**Size:** M

### Objective

Validate orchestration without filesystem effects.

### Acceptance criteria

- [ ] Allowed requests reach the fake executor.
- [ ] Denied requests do not.
- [ ] Success, timeout and failure are reproducible.
- [ ] Dry-run produces no external effect.

### Suggested commit

```text
test(tools): add fake and dry-run executors
```

## M2.8 — Implement audit persistence

**Size:** L

### Scope

Add sanitized audit events and a SQLite implementation separate from `ConversationStore` semantics.

### Acceptance criteria

- [ ] Allow, deny, success, timeout and failure are recorded.
- [ ] File contents are never persisted.
- [ ] Sensitive values are redacted.
- [ ] Audit failure behavior is explicit.
- [ ] Integration tests use temporary SQLite.

### Suggested commit

```text
feat(audit): persist sanitized tool execution events
```

## M2.9 — Implement `LocalReadOnlyToolExecutor`

**Size:** L

### Scope

Provide secure Python implementations of bounded directory listing and file reading.

### Acceptance criteria

- [ ] Structured directory entries are returned.
- [ ] File reads are bounded and indicate truncation.
- [ ] Path validation is repeated immediately before access.
- [ ] Binary-file behavior is documented and tested.
- [ ] Response limits are enforced independently.

### Suggested commit

```text
feat(tools): add local read-only executor
```

## M2.10 — Implement `ToolExecutionCoordinator`

**Size:** L

### Acceptance criteria

- [ ] Execution order is deterministic.
- [ ] Every outcome is audited.
- [ ] Denied requests never reach the executor.
- [ ] Executor errors become normalized typed results.
- [ ] Unit tests use fake ports.
- [ ] Integration tests use the local executor and SQLite audit.

### Suggested commit

```text
feat(tools): orchestrate authorized execution
```

## M2.11 — Integrate one bounded tool round into runtime

**Size:** L

### Target behavior

```text
user message
→ model tool request
→ policy and execution
→ tool-result message
→ second model call
→ final assistant response
```

### Limits

- At most one execution round per user turn.
- No automatic retry after denial.
- A second tool request terminates safely.
- Existing no-tool behavior remains unchanged.

### Acceptance criteria

- [ ] Final answers can use tool results.
- [ ] No-tool Phase 1 behavior is preserved.
- [ ] Loop bound is enforced.
- [ ] Conversation persistence remains transactional.
- [ ] Regression tests cover Phase 1 behavior.

### Suggested commit

```text
feat(runtime): add bounded read-only tool round trip
```

## M2.12 — Add configuration and CLI support

**Size:** M

### Variables

```text
AI_ASSISTANT_WORKSPACE
AI_ASSISTANT_TOOL_EXECUTION
AI_ASSISTANT_TOOL_TIMEOUT
AI_ASSISTANT_MAX_READ_BYTES
AI_ASSISTANT_MAX_DIRECTORY_ENTRIES
AI_ASSISTANT_MAX_DIRECTORY_DEPTH
AI_ASSISTANT_AUDIT_DATABASE
```

### Rules

- Execution is opt-in.
- Missing workspace means tools are unavailable.
- User errors are sanitized.
- Prompts and file contents are not logged.

### Suggested commit

```text
feat(config): add read-only tool settings
```

## M2.13 — Extend protobuf and C tool service

**Size:** L

### Scope

Implement `list_directory` and `read_file` in C with independent workspace validation and bounded responses.

### Acceptance criteria

- [ ] Only allowlisted actions exist.
- [ ] C rejects traversal and external symlinks.
- [ ] C enforces response limits.
- [ ] Malformed protobuf fails safely.
- [ ] Python/C contract tests pass.
- [ ] No shell process is spawned.

### Suggested commit

```text
feat(toolserver): add read-only filesystem actions
```

## M2.14 — Implement `UnixSocketToolExecutor`

**Size:** L

### Scope

Map authorized execution requests to the C service using the existing protobuf framing.

### Acceptance criteria

- [ ] Only authorized requests are transmitted.
- [ ] Missing socket and timeout become typed errors.
- [ ] Malformed and oversized responses are rejected.
- [ ] Request and response IDs correlate.
- [ ] Contract and integration tests pass.

### Suggested commit

```text
feat(tools): add unix socket read-only executor
```

## M2.15 — Add adversarial security tests

**Size:** L

### Mandatory cases

- unknown tool;
- shell-like name;
- traversal;
- external absolute path;
- external symlink;
- hidden file;
- sensitive file;
- special file;
- oversized read;
- excessive entries or depth;
- malformed arguments;
- malformed protobuf;
- timeout;
- socket disconnect;
- binary file;
- audit failure;
- executor invocation after denial;
- second tool round;
- audit redaction;
- Phase 1 regression.

### Acceptance criteria

- [ ] Every case has an automated test.
- [ ] Every denial has a stable reason code.
- [ ] Logs contain no sensitive content.
- [ ] Core CI requires neither Ollama nor the C service.

### Suggested commit

```text
test(security): cover read-only tool boundary
```

## M2.16 — Documentation and final manual review

**Size:** M

### Scope

Update architecture, tool contracts, configuration, threat model, tests, operator guidance, ADR status and Phase 3 boundary.

### Final validation

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -q
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit -q
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m integration -q
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m contract -q
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m smoke -q
```

Environment-specific:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m ollama -q
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m toolserver -q
```

### Acceptance criteria

- [ ] All Phase 2 ADRs are Implemented.
- [ ] Architecture matches code.
- [ ] Every roadmap criterion has evidence.
- [ ] Security review has no blocker.
- [ ] Manual review is recorded.
- [ ] Phase status becomes Accepted.

### Suggested commit

```text
docs(phase2): finalize read-only workspace tools
```

---

# ADR plan

| ADR | Decision |
|---|---|
| ADR-016 | Safe Tool Execution Pipeline |
| ADR-017 | Deny-by-Default Tool Policy |
| ADR-018 | Read-Only Tool Allowlist |
| ADR-019 | Workspace Confinement and Path Resolution |
| ADR-020 | Tool Execution Audit and Retention |
| ADR-021 | Tool Timeouts and Resource Limits |
| ADR-022 | Unix Socket Tool Executor |
| ADR-023 | Error and Log Redaction |
| ADR-024 | Bounded Single Tool Round per Turn |
| ADR-025 | Sensitive File Deny Policy |

# Explicit exclusions

The following belong to Phase 3 or later:

- file writes, deletion, copy, move and directory creation;
- recursive text search;
- shell and process execution;
- Git commands;
- HTTP requests and downloads;
- dynamic plugins;
- model-defined tools;
- persistent blanket approvals;
- multi-step autonomous tool chains;
- embeddings, RAG and semantic memory;
- streaming;
- TUI and web interfaces.

# Phase 3 handoff

Phase 3 should build a Secure Tool Platform using the catalog, policy, audit and executor abstractions proven here. Each new tool family requires its own allowlist, permissions, audit policy and human approval gate.
