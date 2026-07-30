# ADR-020 — Tool Execution Audit and Retention

- Status: Accepted
- Date: 2026-07-30
- Deciders: Project owner
- Supersedes:
- Superseded by:

## Context

Tool execution needs traceability without storing sensitive contents.

## Decision drivers

- Deny, allow, success and failure must be explainable.
- Conversation history is not an audit log.
- File contents and prompts must not be persisted in audit.

## Options considered

No audit; append to conversation history; separate SQLite audit store.

## Decision

Use a separate append-oriented SQLite audit store configured by `AI_ASSISTANT_AUDIT_DATABASE`.

Record sanitized metadata:

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

Do not record prompts, full model responses, secret values, file contents, auth headers or raw tracebacks.

Initial retention is indefinite local retention. Automatic deletion is out of scope until approved.

## Consequences

- Positive: audit is queryable and separate from conversation data.
- Negative: local audit DB can grow.
- Risk: argument summaries must remain sanitized.

## Compatibility and migration

No existing conversation schema changes are required.

## Validation

Tests must prove file contents and sensitive values are not persisted.

## Review trigger

Reconsider when retention, export or user deletion features are required.
