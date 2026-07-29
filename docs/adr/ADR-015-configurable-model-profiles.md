# ADR-015 — Configurable model profiles

- Status: Accepted
- Date: 2026-07-29
- Deciders: Project owner
- Supersedes:
- Superseded by:

## Context

Hardware is sufficient for local models but limited for large models and long contexts.

## Options considered

Hard-code one model; auto-detect; configurable profiles.

## Decision

Keep model and context configurable for 6 GB VRAM and 64 GB RAM.

Use environment-selected model with development, validation and evaluation recommendations.

## Consequences

Architecture is not coupled to Gemma or a size; performance depends on operator configuration.

## Agent constraint

Agents must not implement a contradictory change without a superseding proposed ADR and recorded human approval.
