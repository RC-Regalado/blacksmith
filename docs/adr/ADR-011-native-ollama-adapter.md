# ADR-011 — Native Ollama adapter

- Status: Implemented
- Date: 2026-07-29
- Deciders: Project owner
- Supersedes:
- Superseded by:

## Context

Initial real model tests use a local Ollama process.

## Options considered

Use OpenAI-compatible endpoint only; native Ollama API.

## Decision

Integrate Ollama using its native local HTTP API.

Create a dedicated Ollama adapter using `/api/chat`.

## Consequences

Ollama-specific mapping remains isolated; OpenAI-compatible provider stays separate.

## Agent constraint

Agents must not implement a contradictory change without a superseding proposed ADR and recorded human approval.
