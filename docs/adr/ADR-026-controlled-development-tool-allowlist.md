# ADR-026 — Controlled Development Tool Allowlist

- Status: Accepted
- Date: 2026-08-03
- Deciders: Project owner
- Supersedes:
- Superseded by:

## Context

Phase 3 expands from read-only file inspection to controlled development tools. Each new tool increases local data exposure or side-effect risk.

## Decision drivers

- Preserve deny-by-default behavior.
- Keep the productive surface reviewable.
- Prevent model-selected or dynamically registered tools.
- Preserve the Phase 2 one-tool-round execution boundary.

## Options considered

Dynamic tool registration; broad filesystem/process tools; exact static allowlist.

## Decision

Phase 3 productive tools are exactly:

- `file_metadata`
- `search_text`
- `git_status`
- `git_diff`
- `run_tests`
- `build_project`
- `write`

No other productive tool may be registered, advertised or executed in Phase 3.

Tool definitions remain static and reviewed in the application catalog. Unknown tool names, aliases, case variants, shell-like names and model-invented tools are denied before executor invocation.

## Consequences

- Positive: small and auditable execution surface.
- Negative: common operations such as delete, move, rename, copy, mkdir and append remain unavailable.
- Risk: users may ask for unsupported operations; the assistant must explain limitation instead of broadening scope.

## Compatibility and migration

Phase 2 tools remain valid. `list_directory` and `read_file` continue to work unless replaced by compatible catalog entries in a later accepted ADR.

## Validation

Catalog and adversarial tests must verify the exact allowlist and deny unknown or shell-like names.

## Review trigger

Any additional productive tool requires a new approval gate or superseding ADR.
