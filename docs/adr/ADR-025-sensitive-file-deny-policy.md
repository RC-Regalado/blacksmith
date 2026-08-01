# ADR-025 — Sensitive File Deny Policy

- Status: Implemented
- Date: 2026-07-30
- Deciders: Project owner
- Supersedes:
- Superseded by:

## Context

Local workspaces often contain secrets. Read-only access can still disclose them.

## Decision drivers

- Hidden files are sensitive by default in Phase 2.
- The model cannot override sensitive file policy.
- Policy needs a minimum denylist.

## Options considered

Allow hidden files; deny only `.env`; deny hidden paths and a minimum sensitive pattern set.

## Decision

Deny hidden paths and at least these sensitive patterns:

```text
.env
.env.*
*.pem
*.key
*.p12
*.pfx
id_rsa
id_ed25519
credentials.json
secrets.*
*.kubeconfig
```

Denial applies to path components and target names before file open. External symlinks are denied separately by ADR-019.

## Consequences

- Positive: common secrets are blocked.
- Negative: users cannot inspect dotfiles in Phase 2.
- Risk: denylist is incomplete; hidden-path denial mitigates common cases.

## Compatibility and migration

No Phase 1 behavior changes.

## Validation

Tests must cover hidden files, hidden directories and every minimum sensitive pattern.

## Review trigger

Reconsider when user-managed allow exceptions are designed.
