# Phase 5 Functional Evaluation

## Goal

Validate that derived knowledge reduces objective execution work while keeping provenance, budgets and read-only execution intact.

## Preparation

Start the toolserver and index the repository:

```bash
AI_ASSISTANT_WORKSPACE="$PWD" python main.py knowledge rebuild .
```

Run objectives with metrics:

```bash
AI_ASSISTANT_PROVIDER=ollama \
AI_ASSISTANT_MODEL=blacksmith-tools \
AI_ASSISTANT_WORKSPACE="$PWD" \
AI_ASSISTANT_TOOL_EXECUTION=true \
AI_ASSISTANT_TOOL_SOCKET=/tmp/blacksmith-toolserver.sock \
AI_ASSISTANT_REQUEST_TIMEOUT=240 \
python main.py objective --metrics "Explain why ExecutionEngine cannot write files"
```

## Scenario A

Objective:

```text
Explain why ExecutionEngine cannot write files
```

Expected behavior:

- The plan uses read-only capabilities such as `SearchText` or `ReadFile`.
- The summary cites code/config evidence, not model-only claims.
- The answer explains that write execution is blocked by platform budget/policy/capability boundaries.
- `Budget` shows model and tool calls.
- `Metrics` shows duration and compiled context tokens.

## Scenario B

Objective:

```text
Diagnose a scheduler test failure
```

Expected behavior:

- The plan inspects scheduler-related tests/source.
- The summary identifies relevant files and likely failure surface.
- Evidence remains tool-derived.
- `Metrics` shows duration, model calls, tool calls and context token counts.

## Metrics To Record

For each scenario record:

- `Budget.model_calls`
- `Budget.tool_calls`
- `Metrics.duration_seconds`
- `context_planning.compiled_tokens`
- `context_synthesis.compiled_tokens`
- `context_* reduction_ratio`

No target threshold is enforced in M5.20. The purpose is to make these values visible for manual comparison before Phase 5 final review.
