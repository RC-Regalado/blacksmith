# ADR-029 — Preconfigured Test and Build Profiles

- Status: Implemented
- Date: 2026-08-03
- Deciders: Project owner
- Supersedes:
- Superseded by:

## Context

`run_tests` and `build_project` need controlled process execution. Arbitrary shell or argv from the model is not acceptable.

## Decision drivers

- Prevent command injection.
- Keep allowed commands reviewable.
- Avoid package installation and network side effects.
- Return useful bounded process results.

## Options considered

Model-supplied command strings; model-supplied argv arrays; preconfigured profile IDs.

## Decision

Use a `ToolProfileRegistry` that maps approved profile IDs to fixed argv arrays, working directory rules, timeout and sanitized environment.

The model may select only a profile ID and optional safe parameters explicitly defined by that profile. The model cannot supply argv, shell fragments, environment variables or executable paths.

Profiles must use `subprocess`-style argv execution without shell. Package installation profiles are prohibited in Phase 3.

## Consequences

- Positive: process execution is useful without becoming a shell.
- Negative: new projects may need explicit profile additions.
- Risk: overly broad profiles can still run expensive or mutating project scripts; profiles need review.

## Compatibility and migration

No Phase 2 behavior changes. Initial profiles should be minimal and project-local.

## Validation

Tests must deny unknown profiles, shell metacharacters, argv injection, environment injection and package installation attempts.

## Review trigger

Adding a profile that installs packages, uses network, changes system state or broadens command scope requires human approval.
