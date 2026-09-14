# Phase 5.2 Roadmap — Runtime Hardening & Audit Remediation

## Objective
Remediate the blocking and high-severity findings from `docs/audits/chat-tool-context-audit.md` before expanding platform capabilities.

## Baseline targets
- FINDING-001 one-round conversational tool limit
- FINDING-002 discarded Ollama termination/token metadata
- FINDING-003 no useful final synthesis on tool budget exhaustion
- FINDING-004 no duplicate-call guard
- FINDING-005 no no-progress guard
- FINDING-007 inconsistent context budget semantics
- FINDING-008 runtime/Ollama context-generation mismatch
- FINDING-009 missing interaction-level correlation

## Core rule
Do not solve FINDING-001 only by increasing a numeric limit. Duplicate/progress guards, explicit budgets, final synthesis and tracing must exist first.

## Target architecture
ConversationContextService
→ ModelProvider
→ ModelResponse
→ ToolLoopController
   ├── ToolLoopBudget
   ├── DuplicateCallGuard
   ├── ProgressGuard
   └── FinalSynthesisPolicy
→ ToolExecutionCoordinator
→ ModelProvider
→ Final response

## ModelResponse
Suggested provider-neutral fields:
- message
- finish_reason
- prompt_tokens
- output_tokens
- duration_ms
- truncated
- metadata

Finish reasons:
- STOP
- LENGTH
- TOOL_CALL
- ERROR
- UNKNOWN

## Tool loop budget
Initial chat defaults:
- max_model_tool_rounds = 3
- max_tool_requests = 5
- max_executor_operations = 8
- max_recovery_operations_per_request = 1

## Conversation/generation budget
Suggested:
- provider_context_window = 8192
- reserved_output_tokens = 2048
- max_input_tokens = 6144

Runtime must explicitly configure/observe Ollama `num_ctx` and `num_predict` when supported.

## Milestones

### M5.2.1 — Freeze remediation baseline
- audit file present
- baseline tests pass
- blockers reproduced/verified
- current PASS security/path-recovery behavior recorded

### M5.2.2 — Approve ADR-068..071
- provider response contract
- bounded multi-round loop
- interaction correlation
- context/generation budget
- ADR-024 supersession path documented

### M5.2.3 — Implement provider-neutral ModelResponse
- all providers adapted
- DummyModel remains deterministic
- no provider-specific leakage

### M5.2.4 — Ollama termination metadata
- map done/done_reason
- capture prompt_eval_count/eval_count
- explicit truncation
- STOP/LENGTH tests

### M5.2.5 — Ollama context/generation configuration
- explicit num_ctx
- explicit num_predict
- observable effective values
- docs/Modelfile/config aligned

### M5.2.6 — ConversationContextBudget
- coherent history/knowledge/tool-result/input/output-reserve accounting
- no mixed char/word/token semantics for enforcement

### M5.2.7 — interaction_id
- one per user turn
- propagated through context/model/tools/recovery/final completion

### M5.2.8 — ToolLoopBudget and controller
- separate model rounds/tool requests/executor ops/recovery ops
- no hardcoded loop logic in AgentRuntime

### M5.2.9 — Duplicate-call guard
- normalized fingerprint
- successful duplicate not re-executed
- unchanged failed duplicate rejected

### M5.2.10 — Deterministic progress guard
- repeated no-progress strategy stops safely
- changed strategy remains allowed
- no LLM progress judge

### M5.2.11 — Bounded multi-round chat
- `list_directory -> read_file -> final answer` succeeds
- bounded 3-round default
- guards active before enabling rounds
- recovery does not consume model round

### M5.2.12 — Final synthesis on exhaustion
- no further tool execution
- useful answer from available evidence
- sanitized rejected request/reason included

### M5.2.13 — End-to-end observability
Correlated events for:
- context/retrieval
- model request/response
- tool request/result
- recovery
- budgets
- final synthesis
- interaction completion

### M5.2.14 — Expanded metrics
Expose optionally:
- model_calls
- prompt/output tokens
- finish_reason
- tool rounds
- tool requests
- executor operations
- recovery operations
- retrieval decision
- selected knowledge chunks

### M5.2.15 — Adversarial/regression suite
Required:
- two-tool discovery/read success
- bounded three-round flow
- excess round rejection
- duplicate success/failure
- changed strategy after failure
- no-progress case
- path recovery
- budget exhaustion synthesis
- Ollama STOP/LENGTH
- truncation surfaced
- context reserve
- interaction correlation
- Phase 1–5.1 regressions

### M5.2.16 — Repeat deep audit and close
Repeat `docs/audits/chat-tool-context-audit.md` as an independent audit.

Targets:
- FINDING-001 PASS
- FINDING-002 PASS
- FINDING-003 PASS
- FINDING-004 PASS
- FINDING-005 PASS
- FINDING-007 PASS or justified non-risk PARTIAL
- FINDING-008 PASS
- FINDING-009 PASS

No previously PASS path/security finding may regress.

Acceptable final verdict:
- READY TO CONTINUE
- READY WITH MINOR REMEDIATION

Unacceptable:
- REMEDIATION REQUIRED
- ARCHITECTURAL BLOCKER

## Exclusions
- new tool families
- MCP
- network retrieval
- semantic long-term memory
- automatic skills
- external vector DB
- parallel chat tool execution
- LLM duplicate/progress judges

## Completion
Phase closes only after ADR-068..071 are Implemented, required findings pass, regressions pass, repeated independent audit is acceptable, and final human review accepts closure.
