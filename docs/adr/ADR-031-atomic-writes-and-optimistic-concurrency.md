# ADR-031 — Atomic Writes and Optimistic Concurrency

- Status: Implemented
- Date: 2026-08-03
- Deciders: Project owner
- Supersedes:
- Superseded by:

## Context

Replacing files must not leave partial contents or accidentally overwrite concurrent user edits.

## Decision drivers

- Prevent partial writes.
- Detect stale model context when possible.
- Keep write audit content-free.
- Repeat critical validation in C.

## Options considered

Direct overwrite; temp file then rename; temp file with optional expected hash.

## Decision

The C `write` action must use this sequence:

```text
validate target
verify expected_sha256 when supplied
create temp file in target directory
write bounded UTF-8
fsync temp file
atomic rename
fsync directory where supported
return before/after hashes
```

`expected_sha256` is optional but, when supplied, mismatch denies replacement safely. Temporary files are cleaned on failure where possible.

Audit records mode, path metadata, byte count, before hash, after hash, status and error code, but not full content.

## Consequences

- Positive: file replacement is robust against partial failure and stale writes.
- Negative: implementation is more complex in C than direct write.
- Risk: filesystem-specific fsync behavior may vary.

## Compatibility and migration

Only applies to Phase 3 `write`.

## Validation

Tests must cover hash mismatch, interrupted write, temp cleanup, no external symlink write and content-free audit.

## Review trigger

Changing atomicity, removing hash support or storing content in audit requires human approval.
