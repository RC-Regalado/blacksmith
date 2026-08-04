# ADR-035 — Process Output, Timeout and Environment Limits

- Status: Accepted
- Date: 2026-08-03
- Deciders: Project owner
- Supersedes:
- Superseded by:

## Context

`run_tests` and `build_project` execute approved local processes. Even fixed profiles can hang, flood output or inherit unsafe environment values.

## Decision drivers

- Bound runtime and memory pressure.
- Avoid leaking secrets through inherited environment.
- Return useful failure information without raw tracebacks or secrets.
- Clean up timed-out process groups.

## Options considered

Inherit full environment; no output caps; fixed timeouts and sanitized environment.

## Decision

Process profiles must define:

- fixed argv;
- workspace-confined working directory;
- timeout;
- stdout and stderr byte limits;
- explicit environment allowlist.

Defaults and hard maximums follow the Phase 3 roadmap:

| Limit | Default | Hard maximum |
|---|---:|---:|
| Test timeout | 120 s | 900 s |
| Build timeout | 180 s | 1200 s |
| Process stdout | 128 KiB | 2 MiB |
| Process stderr | 128 KiB | 2 MiB |

Processes run without shell. Timeouts terminate the process tree where supported. Results include status, exit code, duration, truncated stdout/stderr summaries and sanitized error code.

## Consequences

- Positive: project execution is bounded and auditable.
- Negative: long builds may need explicitly approved profile limits.
- Risk: process cleanup differs by platform; contract tests must exercise timeout behavior.

## Compatibility and migration

No Phase 2 behavior changes.

## Validation

Tests must cover output flood, timeout cleanup, environment injection, shell metacharacters and sanitized result shape.

## Review trigger

Changing hard limits, inheriting broad environment, using shell or allowing network/package-install profiles requires human approval.
