# ADR-034 — Audit Retention and Manual Purge

- Status: Accepted
- Date: 2026-08-03
- Deciders: Project owner
- Supersedes:
- Superseded by:

## Context

Phase 2 audit retention is indefinite. Phase 3 adds more events, including writes and process execution.

## Decision drivers

- Avoid unbounded audit growth.
- Preserve high-risk events long enough for review.
- Keep purge unavailable to model tools.
- Avoid accidental deletion of audit evidence.

## Options considered

Indefinite retention only; automatic purge by default; manual purge with retention policy.

## Decision

Add `AuditRetentionPolicy` with retention classes:

| Event | Retention |
|---|---:|
| Metadata/search | 30 days |
| Git inspection | 90 days |
| Tests/builds | 90 days |
| Write | 365 days |
| Security denial | 365 days |
| Critical error | 365 days |

Automatic purge is disabled by default:

```text
AI_ASSISTANT_AUDIT_AUTO_PURGE=false
```

Manual purge must support dry-run, report count and date range, require human confirmation, respect minimum retention and audit the purge itself. Purge is not exposed as a model tool.

## Consequences

- Positive: local audit growth becomes manageable without losing recent evidence.
- Negative: retention implementation requires schema/query care.
- Risk: purge bugs can destroy useful audit records.

## Compatibility and migration

Existing audit rows remain valid. Retention must not require destructive migration.

## Validation

Tests must cover dry-run, confirmation requirement, minimum retention, purge audit event and model-inaccessibility.

## Review trigger

Enabling automatic purge by default, reducing retention materially or exposing purge to the model requires human approval.
