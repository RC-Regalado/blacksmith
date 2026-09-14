# Knowledge Engine Operator Guide

## Purpose

The Knowledge Engine reduces primary model work by compiling local derived knowledge into bounded objective context.

The store is derived and rebuildable. It is not a canonical source of truth.

## Recommended Local Chat Profile

```bash
AI_ASSISTANT_PROVIDER=ollama \
AI_ASSISTANT_MODEL=blacksmith-tools \
AI_ASSISTANT_WORKSPACE="$PWD" \
AI_ASSISTANT_TOOL_EXECUTION=true \
AI_ASSISTANT_TOOL_SOCKET=/tmp/blacksmith-toolserver.sock \
AI_ASSISTANT_KNOWLEDGE_DATABASE=assistant_knowledge.sqlite3 \
python main.py chat --context
```

Use `python main.py chat` for normal chat without indexed knowledge. Use `python main.py chat --context --metrics` when you want opt-in knowledge context plus per-turn context metrics.

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

Status reports one lifecycle value: `empty`, `fresh`, `partially-stale`, `stale`, or `error`.
Empty and stale indexes are never rebuilt automatically; run `knowledge index PATH` or `knowledge rebuild PATH` explicitly.

Query lexical knowledge:

```bash
AI_ASSISTANT_WORKSPACE="$PWD" python main.py knowledge query "ExecutionEngine"
AI_ASSISTANT_WORKSPACE="$PWD" python main.py knowledge query "ExecutionEngine" --metrics
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

## Failure Cases

- `status=empty`: index a path with `python main.py knowledge index PATH` or rebuild a known-good root.
- `status=stale`: run `python main.py knowledge rebuild PATH`; query will not use stale-only knowledge.
- `status=partially-stale`: fresh records can still match, but stale records are excluded.
- `status=error`: fix the store/configuration error before relying on knowledge context.
- Empty and stale-only query diagnostics never trigger indexing or rebuilds.

## Safety Rules

- Hidden and sensitive files are denied.
- Oversized and non-UTF-8 files fail explicitly.
- Stale knowledge is excluded from retrieval and compiled context.
- Context budgets are platform-controlled.
- Metrics expose counts, tokens, ratios and duration only.

## Exclusions

Phase 5.1 does not implement semantic user memory, automatic skills, MCP, network retrieval, external vector databases or background watchers.
