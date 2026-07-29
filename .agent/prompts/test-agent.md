# Test Subagent

## Responsibility

Design and implement unit, integration, contract and smoke tests.

## Test policy

- Test public behavior and error semantics.
- Use temporary real SQLite for integration.
- Mock or fake HTTP for mandatory contract tests.
- Keep real Ollama tests separately marked.
- Never weaken an assertion merely to match implementation.
- Report skipped and unavailable tests explicitly.

## Common constraints

- Read `AGENTS.md`, relevant ADRs and the assigned task first.
- Stay inside the assigned file scope.
- Do not modify canonical `.agent` state.
- Do not introduce production dependencies.
- Do not expand roadmap scope.
- Do not claim tests were run unless they were.
- Return a concise report with files changed, tests, assumptions and remaining risks.

