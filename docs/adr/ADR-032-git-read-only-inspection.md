# ADR-032 — Git Read-Only Inspection

- Status: Implemented
- Date: 2026-08-03
- Deciders: Project owner
- Supersedes:
- Superseded by:

## Context

Phase 3 needs repository inspection through `git_status` and `git_diff` without allowing arbitrary Git commands or mutation.

## Decision drivers

- Preserve read-only behavior.
- Avoid hooks, pagers and external diff tools.
- Bound output size.
- Keep repository access inside workspace.

## Options considered

Arbitrary `git` subcommand tool; parse `.git` files manually; fixed read-only Git inspection actions.

## Decision

Provide only:

- `git_status`: structured read-only repository status.
- `git_diff`: bounded diff for `staged` or `worktree` scopes only.

The repository root must be inside the configured workspace. Commands, if used, must be fixed argv with pager, hooks and external tools disabled by environment/config flags. The model cannot choose revisions, subcommands or flags in Phase 3.

Sensitive paths or contents must be denied or redacted before being returned or audited.

## Consequences

- Positive: common development context is available without general Git control.
- Negative: no arbitrary revision comparison initially.
- Risk: Git output can contain sensitive content; truncation and redaction need tests.

## Compatibility and migration

No Phase 2 behavior changes.

## Validation

Tests must cover repo-outside-workspace denial, no pager, no external diff, staged/worktree-only scope and bounded output.

## Review trigger

Adding mutation, arbitrary revisions or model-controlled Git flags requires human approval.
