# Knowledge Engine Operator Guide

## Purpose

The Knowledge Engine reduces primary model work by compiling local derived knowledge into bounded objective context.

The store is derived and rebuildable. It is not a canonical source of truth.

## Stores

Keep these databases separate:

- `AI_ASSISTANT_DATABASE`: conversation history.
- `AI_ASSISTANT_AUDIT_DATABASE`: tool audit events.
- `AI_ASSISTANT_EXECUTION_DATABASE`: objectives, plans, executions and checkpoints.
- `AI_ASSISTANT_KNOWLEDGE_DATABASE`: derived indexed knowledge.

## Manual Lifecycle

Index a workspace:

```bash
AI_ASSISTANT_WORKSPACE="$PWD" python main.py knowledge rebuild .
```

Check status:

```bash
AI_ASSISTANT_WORKSPACE="$PWD" python main.py knowledge status
```

Query lexical knowledge:

```bash
AI_ASSISTANT_WORKSPACE="$PWD" python main.py knowledge query "ExecutionEngine"
```

Indexing is manual. There is no watcher daemon.

## Objective Integration

Run an objective with tools and context metrics:

```bash
AI_ASSISTANT_PROVIDER=ollama \
AI_ASSISTANT_MODEL=blacksmith-tools \
AI_ASSISTANT_WORKSPACE="$PWD" \
AI_ASSISTANT_TOOL_EXECUTION=true \
AI_ASSISTANT_TOOL_SOCKET=/tmp/blacksmith-toolserver.sock \
AI_ASSISTANT_REQUEST_TIMEOUT=240 \
python main.py objective --metrics "Explain why ExecutionEngine cannot write files"
```

Planner and synthesis context are compiled from fresh, verifiable knowledge only.

## Safety Rules

- Hidden and sensitive files are denied.
- Oversized and non-UTF-8 files fail explicitly.
- Stale knowledge is excluded from retrieval and compiled context.
- Context budgets are platform-controlled.
- Metrics expose counts, tokens, ratios and duration only.

## Exclusions

Phase 5 does not implement semantic user memory, automatic skills, MCP, network retrieval, external vector databases or background watchers.
