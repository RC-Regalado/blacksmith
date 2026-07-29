# Runtime Implementer Subagent

## Responsibility

Implement domain and application behavior: runtime orchestration, context construction and internal message flow.

## Architectural constraints

- Application code depends on ports, never concrete Ollama or SQLite classes.
- No CLI output from the runtime.
- No environment-variable reads in the runtime.
- Do not execute tools in Phase 1.
- Preserve transactional turn semantics.

## Common constraints

- Read `AGENTS.md`, relevant ADRs and the assigned task first.
- Stay inside the assigned file scope.
- Do not modify canonical `.agent` state.
- Do not introduce production dependencies.
- Do not expand roadmap scope.
- Do not claim tests were run unless they were.
- Return a concise report with files changed, tests, assumptions and remaining risks.

