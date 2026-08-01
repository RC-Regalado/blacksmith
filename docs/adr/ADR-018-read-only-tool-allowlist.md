# ADR-018 — Read-Only Tool Allowlist

- Status: Implemented
- Date: 2026-07-30
- Deciders: Project owner
- Supersedes:
- Superseded by:

## Context

Phase 2 scope permits only workspace inspection.

## Decision drivers

- Keep the execution surface small.
- Avoid dynamic tool registration.
- Make tool definitions reviewable.

## Options considered

Dynamic tools; include C server prototype tools; exact static allowlist.

## Decision

Productive Phase 2 allowlist contains exactly:

- `list_directory`
- `read_file`

`noop` may exist only in tests. Historical `echo` and `list_tools` actions are not productive assistant tools unless a later ADR approves them.

## Consequences

- Positive: minimal review surface.
- Negative: no general command execution or writes.
- Risk: future useful tools require explicit roadmap work.

## Compatibility and migration

Existing declarative tool parsing remains unchanged; unknown names are denied by policy.

## Validation

Catalog tests must verify exact-name lookup and rejection of unknown, shell-like and case-variant names.

## Review trigger

Any new productive tool requires a new approval gate or ADR update.
