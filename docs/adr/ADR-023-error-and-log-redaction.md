# ADR-023 — Error and Log Redaction

- Status: Accepted
- Date: 2026-07-30
- Deciders: Project owner
- Supersedes:
- Superseded by:

## Context

Tool failures may involve file paths, sensitive names or partial contents. Logs and user errors must not leak secrets.

## Decision drivers

- Prompts, responses and file contents are sensitive by default.
- Operators still need actionable failure reason codes.
- Audit data must be sanitized.

## Options considered

Log raw exceptions; redact only obvious secrets; use structured sanitized errors.

## Decision

Use typed tool errors with stable codes and sanitized messages.

Do not log:

- full prompts;
- full model responses;
- file contents;
- secret values;
- auth headers;
- raw tracebacks in user-facing messages.

Logs may include stable error code, tool name, session ID, request ID, duration and sanitized relative path category.

## Consequences

- Positive: useful diagnostics without content leakage.
- Negative: debugging some failures requires local reproduction.
- Risk: redaction tests must include realistic secret-like values.

## Compatibility and migration

Extends the existing typed error and safe logging approach.

## Validation

Tests must assert logs and audit records omit file contents and sensitive values.

## Review trigger

Reconsider before adding external telemetry.
