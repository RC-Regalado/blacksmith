# ADR-030 — Controlled Workspace Write Semantics

- Status: Accepted
- Date: 2026-08-03
- Deciders: Project owner
- Supersedes:
- Superseded by:

## Context

Phase 3 introduces bounded file writes. Writes can destroy user work if scope and modes are too broad.

## Decision drivers

- Preserve workspace confinement.
- Avoid destructive operations beyond the approved need.
- Keep audit useful without storing contents.
- Require confirmation for side effects.

## Options considered

Unrestricted write; append/edit/delete/move operations; create and replace only.

## Decision

Phase 3 supports only `write` with modes:

```text
create
replace
```

Rules:

- target must be a relative workspace path;
- hidden and sensitive targets are denied;
- external symlinks are denied;
- target must be a regular file when replacing;
- content must be UTF-8 text;
- content size is bounded;
- first use requires `WRITE_WORKSPACE` confirmation;
- audit records metadata and hashes, never full content.

Append, delete, move, rename, copy, mkdir and unrestricted write are out of scope.

## Consequences

- Positive: useful file creation/replacement with narrow destructive surface.
- Negative: patch-style edits are initially represented as full replacements.
- Risk: replace mode still overwrites user work unless optimistic concurrency is used.

## Compatibility and migration

No Phase 2 behavior changes. Existing read-only path policy remains the minimum baseline.

## Validation

Tests must prove denied writes never reach the executor and hidden, sensitive, symlink, traversal and oversized targets are rejected.

## Review trigger

Any new write mode or broader filesystem mutation requires human approval.
