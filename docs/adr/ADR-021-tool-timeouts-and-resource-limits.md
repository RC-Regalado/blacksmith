# ADR-021 — Tool Timeouts and Resource Limits

- Status: Implemented
- Date: 2026-07-30
- Deciders: Project owner
- Supersedes:
- Superseded by:

## Context

Read-only filesystem operations can still exhaust resources through large files, large directories or deep traversal.

## Decision drivers

- Limits must be deterministic.
- Defaults must be useful and conservative.
- Hard maximums cannot be overridden by the model.

## Options considered

No limits; model-provided limits; configured defaults with hard maximums.

## Decision

Use configured defaults capped by hard maximums:

| Limit | Default | Hard maximum |
|---|---:|---:|
| Tool timeout | 5 s | 30 s |
| Read bytes | 16 KiB | 64 KiB |
| Directory entries | 200 | 1,000 |
| Recursive depth | 0 | 3 |
| Path length | 1,024 chars | 4,096 chars |
| Request payload | 64 KiB | 256 KiB |
| Response payload | 128 KiB | 1 MiB |

Overrides above hard maximums are denied before executor invocation.

## Consequences

- Positive: bounded latency and memory use.
- Negative: large files may require explicit user follow-up in later phases.
- Risk: character encoding can affect byte-to-text presentation.

## Compatibility and migration

Adds new Phase 2 config without changing Phase 1 defaults.

## Validation

Tests must cover oversized reads, excessive entries, excessive depth and response-limit truncation or denial.

## Review trigger

Reconsider after measuring real workspace usage.
