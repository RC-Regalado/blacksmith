# ADR-027 — Permission Levels and Confirmation Grants

- Status: Accepted
- Date: 2026-08-03
- Deciders: Project owner
- Supersedes:
- Superseded by:

## Context

Phase 3 tools have different risk levels. Read-only metadata is lower risk than running project commands or writing files.

## Decision drivers

- Model output cannot authorize permissions.
- Riskier operations require explicit operator consent.
- Grants must be local, scoped and easy to revoke.
- Default behavior must deny when confirmation is unavailable.

## Options considered

Single read/write permission; persistent global approvals; scoped in-memory grants.

## Decision

Use these permission levels:

```text
READ_METADATA
READ_CONTENT
READ_REPOSITORY
EXECUTE_PROJECT
WRITE_WORKSPACE
```

Tool mapping:

| Tool | Permission | Confirmation |
|---|---|---|
| `file_metadata` | `READ_METADATA` | No |
| `search_text` | `READ_CONTENT` | No |
| `git_status` | `READ_REPOSITORY` | No |
| `git_diff` | `READ_REPOSITORY` | No |
| `run_tests` | `EXECUTE_PROJECT` | First use |
| `build_project` | `EXECUTE_PROJECT` | First use |
| `write` | `WRITE_WORKSPACE` | First use |

Confirmation grants are in-memory only and scoped to:

```text
session_id + workspace_id + permission_level
```

Grants expire on process restart, session change, workspace change, policy change, explicit revocation or risk escalation. EOF, timeout, invalid input or unrecognized answers deny the request.

## Consequences

- Positive: read-only workflows remain low-friction while side effects require consent.
- Negative: CLI users may see first-use prompts.
- Risk: confirmation UX must be clear without leaking prompts or file contents into logs.

## Compatibility and migration

Existing Phase 2 `READ_ONLY` maps only to read-only behavior during migration. M3.3 must introduce the new domain values without allowing permission escalation.

## Validation

Tests must prove grant reuse only inside the exact scope, denial prevents executor invocation and confirmation decisions are audited.

## Review trigger

Changing grant scope, persistence or default-deny behavior requires human approval.
