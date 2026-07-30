# Phase 2 Preparation Report

## Status

prepared-blocked-on-policy-approval

## Inputs Read

- `AGENTS-phase-2.md`
- `docs/roadmap-phase-2.md`
- Phase 1 state in `.agent/roadmap-state.md`
- Human gates in `.agent/human-review.md`
- Existing tool-call, protobuf, Unix socket and C toolserver files

## Phase 2 Scope

Only these productive tools are allowed:

- `list_directory`
- `read_file`

Explicitly out of scope:

- shell or process execution;
- writes, deletes, copies, moves or directory creation;
- network access;
- Git execution;
- dynamic tools;
- unrestricted recursion;
- access outside `AI_ASSISTANT_WORKSPACE`;
- hidden or sensitive file reads.

## Milestone Sequence

1. `M2.1`: approve Phase 2 security decisions.
2. `M2.2`: add execution domain models.
3. `M2.3`: add application ports.
4. `M2.4`: implement static tool catalog.
5. `M2.5`: implement workspace and path policy.
6. `M2.6`: implement deny-by-default tool policy.
7. `M2.7`: add fake and dry-run executors.
8. `M2.8`: implement audit persistence.
9. `M2.9`: implement local read-only executor.
10. `M2.10`: implement execution coordinator.
11. `M2.11`: integrate one bounded tool round into runtime.
12. `M2.12`: add configuration and CLI support.
13. `M2.13`: extend protobuf and C tool service.
14. `M2.14`: implement Unix socket executor.
15. `M2.15`: add adversarial security tests.
16. `M2.16`: final documentation and manual review.

## Configured Subagents

Added Phase 2 prompt files:

- `.agent/prompts/phase2-architect.md`
- `.agent/prompts/tool-policy-engineer.md`
- `.agent/prompts/filesystem-security-engineer.md`
- `.agent/prompts/python-executor-engineer.md`
- `.agent/prompts/audit-engineer.md`
- `.agent/prompts/runtime-integration-engineer.md`
- `.agent/prompts/c-toolserver-engineer.md`

Existing Phase 1 prompts remain available for documentation, tests, security and integration validation.

## Next Eligible Work

`M2.1` should start with ADR proposals, not code execution.

Required ADRs:

- ADR-016 Safe Tool Execution Pipeline
- ADR-017 Deny-by-Default Tool Policy
- ADR-018 Read-Only Tool Allowlist
- ADR-019 Workspace Confinement and Path Resolution
- ADR-020 Tool Execution Audit and Retention
- ADR-021 Tool Timeouts and Resource Limits
- ADR-022 Unix Socket Tool Executor
- ADR-023 Error and Log Redaction
- ADR-024 Bounded Single Tool Round per Turn
- ADR-025 Sensitive File Deny Policy

## Open Gates

- `PHASE2-G1`: approve exact tool execution safety policy.
- `PHASE2-G2`: approve initial tool scope and permission levels.
- `PHASE2-G3`: approve audit persistence target and retention.
- `PHASE2-G4`: approve ADR-016 through ADR-025 after proposal.

## Baseline Validation

```bash
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q
```

Result after preparation: 74 passed, 1 skipped.

`PYTHONDONTWRITEBYTECODE=1 python -m pytest -q` could not run in the active shell because the non-venv interpreter does not have `pytest` installed.

## Readiness

The environment is ready to begin M2.1 planning and ADR drafting. Productive tool execution remains blocked until the ADR package and open gates are approved by the user.
