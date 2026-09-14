# Phase 5.1 Roadmap — Conversational Platform Integration

## Objective

Integrate the Context & Knowledge Engine into the normal chat experience and unify the CLI without creating a second parallel architecture.

Phase 5.1 is an integration mini-phase. It adds no new major platform intelligence. It connects existing Phase 1–5 subsystems into a coherent operator experience.

## Product behavior after Phase 5.1

```text
python main.py chat
python main.py chat --context
python main.py chat --context --metrics

python main.py objective "..."
python main.py objective "..." --metrics

python main.py knowledge status
python main.py knowledge index .
python main.py knowledge rebuild .
python main.py knowledge query "..."
python main.py knowledge query "..." --metrics
```

Temporary compatibility:

```text
python main.py
```

may remain an alias for:

```text
python main.py chat
```

## Context policy

### Chat

Default:

```text
Context Engine = OFF
```

Opt-in:

```bash
python main.py chat --context
```

or:

```bash
AI_ASSISTANT_CONTEXT_ENGINE=true python main.py chat
```

### Objective

Context Engine remains enabled when a valid knowledge index is available.

If no valid index exists:

- fall back safely;
- do not rebuild automatically;
- expose clear status/diagnostic information.

### Knowledge

Knowledge commands manage/query derived knowledge only.

They must not invoke the reasoning model unless explicitly designed and approved in a later ADR.

## Indexed knowledge vs live state

Indexed knowledge must never substitute live capabilities for volatile state.

Examples:

```text
Explain ExecutionEngine architecture
→ Knowledge Engine

Current Git status
→ InspectGitStatus capability

Current test result
→ RunTests capability

Current build result
→ BuildProject capability
```

## Conversation context architecture

Introduce:

```text
ConversationContextService
```

Responsibilities:

```text
system instructions
+ recent conversation history
+ optional compiled knowledge
+ current user message
→ bounded model context
```

The service must not:

- call Ollama directly;
- read KnowledgeStore directly if a higher-level ContextEngine/port exists;
- persist conversation;
- execute tools.

## ContextCompiler extension

Add:

```text
compile_conversation_context()
```

alongside existing planning and synthesis compilation.

The context types remain distinct:

```text
PlanningContext
SynthesisContext
ConversationContext
```

Do not mix knowledge chunks into conversation history records.

## Conversation context budget

Recommended defaults:

```text
max_history_tokens = 2048
max_knowledge_tokens = 2048
max_total_context_tokens = 4096
max_sources = 6
max_chunks = 8
```

The model cannot increase these limits.

## Retrieval policy

Context-enabled chat does not imply retrieval on every turn.

Introduce:

```text
ConversationRetrievalPolicy
```

Initial deterministic behavior:

```text
--context disabled
→ retrieval off

very short conversational acknowledgement
→ retrieval bypassed

project/code/document question
→ retrieval allowed
```

Do not use another LLM to decide whether retrieval is needed.

## Tool interaction

Existing conversational tool execution remains available.

Desired behavior:

```text
User
 ↓
ConversationContextService
 ↓
ModelProvider
 ↓
direct answer OR tool call
 ↓
ToolExecutionCoordinator
 ↓
tool result
 ↓
ModelProvider
 ↓
final answer
```

Knowledge retrieval should reduce unnecessary tool calls but must never fake live state.

## Metrics

Expose optional, sanitized per-turn context metrics:

```text
knowledge_candidates
knowledge_chunks_selected
raw_context_estimated_tokens
compiled_context_estimated_tokens
ranked_candidates
context_reduction_ratio

The implementation deliberately reports only values measured by the current
retrieval/compiler seams. History-token accounting, latency attribution,
stale-rejection counters and tool-avoidance attribution remain out of scope
until those values can be measured without changing the runtime contract.
```

Expose through:

```bash
python main.py chat --context --metrics
python main.py objective "..." --metrics
python main.py knowledge query "..." --metrics
```

and optional env:

```text
AI_ASSISTANT_SHOW_METRICS=true
```

## Knowledge lifecycle UX

`knowledge status` must clearly distinguish:

```text
empty
fresh
partially-stale
stale
error
```

No automatic rebuild.

`knowledge query` against an empty or stale-only index must return a clear diagnostic rather than pretending no results exist.

## Milestones

### M5.1.1 — Freeze Phase 5 baseline

Acceptance:

- [ ] Phase 5 accepted.
- [ ] ADR-047 through ADR-061 Implemented.
- [ ] Current suite passes.
- [ ] Knowledge CLI works.
- [ ] Objective context integration works.
- [ ] Working tree understood.

### M5.1.2 — Unified command router

Implement explicit commands:

```text
chat
objective
knowledge
```

Acceptance:

- [ ] `python main.py --help`
- [ ] `python main.py chat --help`
- [ ] `python main.py objective --help`
- [ ] `python main.py knowledge --help`
- [ ] legacy `python main.py` compatibility documented
- [ ] consistent argument/error behavior

### M5.1.3 — ConversationContextService

Acceptance:

- [ ] conversation history and optional knowledge are assembled through a dedicated service
- [ ] no provider/store concrete dependency leaks inward
- [ ] context budget enforced
- [ ] unit tests cover enabled/disabled modes

### M5.1.4 — ConversationContext compiler

Acceptance:

- [ ] `compile_conversation_context()` exists
- [ ] provenance preserved
- [ ] conversation history remains semantically separate from knowledge
- [ ] stale knowledge excluded

### M5.1.5 — Opt-in chat context policy

Add:

```text
--context
AI_ASSISTANT_CONTEXT_ENGINE=true
```

Acceptance:

- [ ] chat default remains context-off
- [ ] opt-in enables retrieval
- [ ] no automatic knowledge rebuild
- [ ] no-index fallback is safe and visible

### M5.1.6 — Deterministic retrieval policy

Acceptance:

- [ ] retrieval bypasses simple conversational turns
- [ ] project/code/document questions can retrieve
- [ ] no LLM classifier is introduced
- [ ] behavior is testable/deterministic

### M5.1.7 — Preserve conversational tool loop

Acceptance:

- [ ] existing tool round continues working
- [ ] knowledge context does not bypass ToolPolicy
- [ ] live-state questions still use live capabilities
- [ ] no duplicate unnecessary tool calls introduced

### M5.1.8 — Metrics exposure

Acceptance:

- [ ] `--metrics` for chat
- [ ] `--metrics` for knowledge query
- [ ] existing objective metrics preserved
- [ ] metrics are optional and sanitized

### M5.1.9 — Knowledge status UX

Acceptance:

- [ ] status distinguishes empty/fresh/partially-stale/stale/error
- [ ] query provides explicit stale/empty diagnostics
- [ ] no implicit rebuild
- [ ] operator guidance documented

### M5.1.10 — Presets and operator docs

Document a recommended local profile:

```bash
AI_ASSISTANT_PROVIDER=ollama AI_ASSISTANT_MODEL=blacksmith-tools AI_ASSISTANT_WORKSPACE="$PWD" AI_ASSISTANT_TOOL_EXECUTION=true AI_ASSISTANT_TOOL_SOCKET=/tmp/blacksmith-toolserver.sock AI_ASSISTANT_KNOWLEDGE_DATABASE=assistant_knowledge.sqlite3 python main.py chat --context
```

Acceptance:

- [ ] config documented
- [ ] chat/context/objective/knowledge workflows documented
- [ ] failure cases documented

### M5.1.11 — Adversarial and regression suite

Required coverage:

- context disabled
- context enabled with empty index
- context enabled with stale index
- short-chat retrieval bypass
- project-query retrieval
- live-state capability preference
- tool-policy preservation
- budget overflow
- provenance preservation
- metrics disabled/enabled
- CLI malformed args
- Phase 1–5 regressions

### M5.1.12 — End-to-end mini-phase validation

Required scenarios:

#### A — Plain chat

```text
Hello
```

Expected:

```text
retrieval skipped
tool calls 0
```

#### B — Context-aware project chat

```text
Explain how ExecutionEngine validates plans.
```

Expected:

```text
knowledge retrieval
grounded response
no filesystem tool call if fresh evidence is sufficient
```

#### C — Live-state question

```text
What is currently changed in Git?
```

Expected:

```text
live git_status capability
not indexed knowledge as authoritative state
```

#### D — Empty/stale knowledge

Expected:

```text
clear diagnostic
safe fallback
no implicit rebuild
```

### M5.1.13 — Final mini-phase closure

Update:

- architecture
- CLI docs
- ADR index
- context policy
- metrics docs
- knowledge lifecycle docs
- regression evidence
- final integration report

Only after M5.1.1–M5.1.13 are automatically validated does the mini-phase enter human review.

## ADR plan

- ADR-062 Conversational Context Integration
- ADR-063 Opt-In Knowledge Context for Chat
- ADR-064 Conversation Context Budget
- ADR-065 Indexed Knowledge vs Live Capability Semantics
- ADR-066 Unified CLI Command Model
- ADR-067 Deterministic Conversation Retrieval Policy

## Completion criteria

Phase 5.1 is complete when:

- all milestones pass automated/subagent validation;
- ADR-062 through ADR-067 are Implemented;
- chat/context/objective/knowledge CLI is coherent;
- context remains opt-in for chat;
- live state prefers live capabilities;
- metrics are exposed;
- stale/empty states are explicit;
- Phase 1–5 regressions pass;
- one final human review accepts the mini-phase as a whole.

No per-milestone human review is required inside Phase 5.1.
