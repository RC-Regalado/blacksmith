# ADR-006 — ModelProvider port

- Status: Accepted
- Date: 2026-07-29
- Deciders: Project owner
- Supersedes:
- Superseded by:

## Context

The runtime must support Dummy, Ollama and OpenAI-compatible implementations.

## Options considered

Provider conditionals in runtime; shared port.

## Decision

Access models through a ModelProvider port.

Define a minimal synchronous chat contract.

## Consequences

The contract remains small; streaming and tool capabilities require later evolution.

## Agent constraint

Agents must not implement a contradictory change without a superseding proposed ADR and recorded human approval.
