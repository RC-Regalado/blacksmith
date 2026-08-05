# ADR-033 — Search Text Limits and Redaction

- Status: Implemented
- Date: 2026-08-03
- Deciders: Project owner
- Supersedes:
- Superseded by:

## Context

`search_text` exposes workspace content in previews and can become expensive on large trees.

## Decision drivers

- Bound CPU, I/O and response size.
- Avoid binary, hidden and sensitive files.
- Keep implementation simple and deterministic.
- Avoid regex complexity initially.

## Options considered

Regex search; delegate to arbitrary `grep`; fixed `ripgrep` interface with
bounded literal search.

## Decision

`search_text` performs bounded literal text search through an internal search
profile designed for `rg` (`ripgrep`).

The model supplies only query and bounded search arguments. It cannot supply
the executable, argv, flags, shell fragments or environment. The implementation
uses fixed argv for `rg` with literal search mode and explicit limits. `grep`
is not an approved fallback because behavior, defaults and performance differ
across platforms. If `rg` is unavailable, the tool returns a typed
`search_backend_unavailable` error.

Rules:

- query must be non-empty text;
- no regex in Phase 3;
- `rg` is the preferred and only approved external search backend;
- no fallback to `grep`;
- workspace-confined traversal;
- hidden, sensitive, binary and special files excluded;
- bounded total files, bytes per file, matches and preview length;
- truncation is explicit;
- returned previews are bounded and redacted for sensitive-looking values where practical.

## Consequences

- Positive: useful search with deterministic limits and a consistent backend.
- Negative: no regex or advanced ignore semantics initially.
- Risk: `rg` must be installed for the productive search profile; redaction heuristics cannot catch every secret, so hidden/sensitive denial remains primary defense.

## Compatibility and migration

No Phase 2 behavior changes.

## Validation

Tests must cover binary files, hidden paths, sensitive patterns, resource
exhaustion, truncation, no-regex rejection, fixed `rg` argv construction and
typed failure when `rg` is unavailable.

## Review trigger

Adding regex, model-controlled flags, `grep` fallback or another search backend
requires human approval.
