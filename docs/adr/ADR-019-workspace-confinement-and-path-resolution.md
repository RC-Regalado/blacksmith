# ADR-019 — Workspace Confinement and Path Resolution

- Status: Accepted
- Date: 2026-07-30
- Deciders: Project owner
- Supersedes:
- Superseded by:

## Context

Phase 2 tools read local paths. Path traversal and symlink escape are primary risks.

## Decision drivers

- All model-supplied paths are hostile.
- Workspace must be operator-configured.
- Python and C executors must validate independently.

## Options considered

Trust normalized strings; allow absolute paths under workspace; require relative paths resolved against a canonical workspace.

## Decision

All tool paths must be relative to `AI_ASSISTANT_WORKSPACE`.

Path policy must:

- canonicalize the workspace;
- reject missing workspace;
- reject absolute tool paths;
- reject `..` traversal and canonical escapes;
- reject external symlinks;
- reject hidden paths;
- reject sensitive paths;
- reject path strings above hard length;
- validate expected file type before executor access.

Concrete executors must repeat validation immediately before access.

## Consequences

- Positive: bounded workspace reads.
- Negative: hidden files are unavailable in Phase 2.
- Risk: symlink handling must be tested carefully.

## Compatibility and migration

No Phase 1 behavior depends on workspace configuration.

## Validation

Adversarial tests must cover traversal, absolute paths, external symlinks, hidden paths, sensitive paths and special files.

## Review trigger

Reconsider if Phase 3 needs controlled access outside the workspace.
