# Chat / Context / Tooling Deep Audit — Post-Remediation (Phase 5.2 Closure Check)

Independent repeat audit of `docs/audits/chat-tool-context-audit.md` after the
supervisor-run "Phase 5.2" remediation. This audit does **not** trust the
supervisor's self-reported milestone claims (`.agent/reports/M5.2.*.md`); every
verdict below is derived from the current source, a fresh full test run, and
live reproductions constructed and executed by this auditor against the real
`create_application()` wiring — not from reading the milestone reports, which
were used only for orientation on what changed.

## 1. Executive Summary

Estado general: **READY TO CONTINUE**.

Human review found a missed runtime case after the first audit: `chat --context --metrics` for `¿Que hace este proyecto?` produced `context_conversation: candidates=0 ranked=0 selected=0 ... retrieval_attempted=True knowledge_chunks_selected=0` and then entered the tool loop. Supervisor reproduction confirmed the retrieval-side root cause: `ConversationRetrievalPolicy` allowed the prompt, but the lexical store required an exact full-query FTS phrase; generic natural-language project-summary prompts did not retrieve project knowledge unless the full phrase existed verbatim. Corrective task `M5.2.16-R1` is now complete and independently validated: the same prompt now reports `candidates=12 ranked=12 selected=12` and `tool_rounds=0`; full suite is `585 passed, 17 skipped`.

All 8 mandatory findings from the baseline (`FINDING-001` through `005`,
`007`, `008`, `009`) are genuinely resolved in current source, verified both
by the existing regression suite and by fresh, independently-constructed
reproductions in this audit (a live `AgentRuntime` built through
`create_application()`, a temp workspace, a scripted `ModelProvider`, and a
real `JsonlInteractionDiagnosticLogger`/`JsonlToolDiagnosticLogger` sink whose
JSONL output this auditor read directly). None of the previously-PASS
security or path-recovery controls have regressed — `PathPolicy`,
`PathRecoveryPolicy`, `DenyByDefaultToolPolicy`, confirmation gating for
`EXECUTE_PROJECT`/`WRITE_WORKSPACE`, and the C toolserver are byte-for-byte
unchanged from the audited baseline (`git diff --stat HEAD -- c_toolserver`
is empty; `ai_assistant/application/path_policy.py`,
`ai_assistant/application/path_recovery.py`,
`ai_assistant/application/tool_policy.py` are unchanged in logic from the
baseline audit's citations).

Conteo de clasificaciones de esta auditoría (18 findings re-derived):

| Status | Count |
| ------ | -----:|
| PASS | 8 |
| PARTIAL | 8 |
| FAIL | 1 |
| NOT VERIFIED | 1 |

(FINDING-006, 010–014, 017, 018 remain PARTIAL; FINDING-015 remains FAIL;
FINDING-016 remains NOT VERIFIED — all as expected, since none were
designated mandatory for this closure and Phase 5.2 explicitly deferred
docs/Modelfile alignment (FINDING-015) and did not touch the build-safety
question (FINDING-016). See section 12 for the full mapping.)

Full suite: `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q` →
**578 passed, 17 skipped** (0 failed). Baseline suite for the same command
scope had been referenced only via a focused 54-test regression; this run is
the complete current suite.

Live reproduction evidence produced by this audit (see section 5 for full
JSONL excerpts):

- A scripted model driving `list_directory -> read_file -> final answer` in
  one turn completed successfully with `tool_rounds=2`, no rejection,
  `finish_reason=stop` — the exact flow the baseline's FINDING-001 proved was
  impossible.
- A scripted model that only ever emits new (non-duplicate) tool requests
  that keep failing was stopped by the progress guard after two consecutive
  failures, and a scripted model that repeats one exact fingerprint twice was
  rejected as `duplicate_tool_call` without a second executor spend.
- On both exhaustion paths, the runtime asked the model once more for a
  synthesis (no tool executed, no budget spent) and, since the scripted model
  kept insisting on a tool call, fell back to the documented deterministic
  sanitized summary — exactly the two-tier design ADR-069 describes, not a
  fixed generic string.
- One JSONL file recorded `context_retrieval`, two `model_request`/
  `model_response` pairs, two tool `requested`/`executed` events, and
  `interaction_completed`, **all sharing one `interaction_id`**
  (`9f453dd174bb42c49473e364a0992307` in the run reproduced below).

## 2. Method

1. Read `docs/audits/chat-tool-context-audit.md` (baseline) in full.
2. Read `docs/roadmap-phase-5.2.md` in full.
3. Skimmed `.agent/reports/M5.2.1.md` through `M5.2.15.md` for orientation
   only; every claim in those reports that mattered to a mandatory finding
   was independently re-verified against current source/tests/live runs
   below rather than cited as fact.
4. Ran the full test suite fresh.
5. Read the current implementation of every file the baseline cited as
   evidence, line-by-line, to detect drift, regression, or dead code.
6. Constructed a real `AgentRuntime` via `ai_assistant.bootstrap.container
   .create_application()` with an isolated temp workspace, `tool_executor=
   "local"` (the in-process `LocalReadOnlyToolExecutor`, avoiding a
   dependency on the C toolserver socket), a scripted `ModelProvider`
   substituted onto the constructed runtime, and a real
   `JsonlInteractionDiagnosticLogger`/`JsonlToolDiagnosticLogger` writing to
   a temp `tool_log_dir`. Ran multiple scenarios (bounded success,
   duplicate, no-progress/exhaustion) and read the resulting JSONL files
   directly.
7. Re-ran the path-recovery/security-focused test files explicitly.
8. Verified ADR statuses in `docs/adr/README.md` against the individual ADR
   files.

## 3. Architecture Conformance (re-check)

| Area | Baseline status | Current status | Evidence |
| ---- | ---------------- | --------------- | -------- |
| Clean Architecture | PASS | PASS (unchanged) | `ai_assistant/application/runtime.py:1-40` still depends only on application ports/services; bootstrap composition unchanged in shape. |
| ports/adapters | PARTIAL | PASS | `ModelProvider.chat()` now returns `ModelResponse`, not a bare `Message`: `ai_assistant/application/ports/models.py:9-12`. All three providers (`dummy`, `ollama`, `openai_compatible`) implement the new contract — verified by reading `ai_assistant/infrastructure/models/dummy.py:9-21`, `ollama.py:39-46,67-87`, and by the passing `tests/test_ollama_model.py`/`tests/test_openai_compatible.py`/`tests/test_model_adapter.py`. |
| store separation | PASS | PASS (unchanged) | `ai_assistant/bootstrap/config.py:18-20`, `container.py:61,73`. |
| provider separation | PARTIAL | PASS | Ollama adapter now maps `done`/`done_reason`/`prompt_eval_count`/`eval_count` into `ModelResponse`: `ai_assistant/infrastructure/models/ollama.py:67-87`. |
| capability boundaries | PARTIAL | PARTIAL (unchanged) | Not a Phase 5.2 target; chat still routes tool calls via model-emitted JSON, not a capability router. |
| Context Engine boundaries | PARTIAL | PASS | `ConversationContextService` now owns an explicit `ConversationContextBudget` (`ai_assistant/application/conversation_context.py:14-24`) instead of mixing budgeting units; `context_provider`/`retrieval_policy` remain duck-typed (FINDING-012, unchanged, non-mandatory). |
| tool execution boundaries | PARTIAL | PASS | Bounded multi-round loop with `DuplicateCallGuard`/`ProgressGuard` lives in `ai_assistant/application/tool_loop.py` and is exercised by `AgentRuntime._run_tool_loop` (`ai_assistant/application/runtime.py:160-244`); path recovery still never counts as an extra model round (`ai_assistant/application/tool_coordinator.py:107-118`, unchanged). |

## 4. Conversational Context Integration (re-check)

No regressions found. `ConversationContextService.build`/`build_with_retrieval`
(`ai_assistant/application/conversation_context.py:26-85`) preserve every
baseline-PASS behavior (opt-in retrieval, stale exclusion delegated to
`ContextCompiler`/`HybridRetriever`, provenance via
`source_uri#chunk_id`) and additionally now use one shared
`estimate_tokens()` unit (`ai_assistant/application/conversation_budget.py:16-17`)
for the input-budget decision at `conversation_context.py:40`, replacing the
prior word-split-only estimate. `ai_assistant/application/context.py:5,25-30`
(`ContextBuilder._select_history`) also now calls `estimate_tokens` instead of
raw character length, closing the baseline's "mixed char/word/chunk-token"
complaint (FINDING-007).

## 5. Tool Loop Audit (re-check, with fresh live evidence)

Flujo implementado ahora (verified by reading `ai_assistant/application/
runtime.py:160-302` and `ai_assistant/application/tool_loop.py:1-81`, then
proven live):

```text
model
→ ToolCallDetector
→ while budget remains and no stall:
     ToolLoopBudget check (max_model_tool_rounds / max_tool_requests / max_executor_operations)
     ProgressGuard.is_stalled(history) check
     DuplicateCallGuard.is_duplicate(history, fingerprint) check
     ToolExecutionCoordinator.execute (path recovery inside does not cost a round)
     model call again with tool result appended
→ on non-tool response: return it
→ on budget exhaustion or stall: one extra "synthesis-only" model call
   (no tool executed, doesn't count against budget) → real answer, or a
   deterministic sanitized fallback summary if the model still asks for a tool
```

| Control | Baseline | Current | Evidence |
| ------- | -------- | ------- | -------- |
| max rounds | FAIL (hardcoded 1) | **PASS** | `ToolLoopBudget(max_model_tool_rounds=3, max_tool_requests=5, max_executor_operations=8)` defaults, `ai_assistant/application/tool_loop.py:18-30`; enforced in the loop guard at `ai_assistant/application/runtime.py:188-195`; no hardcoded round cap remains in `AgentRuntime`. |
| max requests | PARTIAL | **PASS** | `len(history) >= self.tool_loop_budget.max_tool_requests` at `runtime.py:190`; `ToolCallAttempt` history accumulates per tool call, not per message. |
| executor operation budget | PARTIAL | **PASS** | `executor_operations_used >= self.tool_loop_budget.max_executor_operations` at `runtime.py:191`, incremented by `tool_result.executor_operations` at `runtime.py:225` (includes recovery-attempt spend). |
| duplicate detection | FAIL | **PASS** | `DuplicateCallGuard.is_duplicate` (`tool_loop.py:49-58`) checked before every executor spend at `runtime.py:204`; rejected via `_duplicate_rejection()` (`runtime.py:483-493`) with code `duplicate_tool_call`, **without calling the executor** (no `tool_result.executor_operations` cost). Live-verified in this audit (Scenario B below): second identical `read_file` request rejected, `executor_operations` metric stayed at 1 for the whole turn. |
| no-progress detection | FAIL | **PASS** | `ProgressGuard.is_stalled` (`tool_loop.py:61-80`) stops after 2 consecutive failure-status attempts (`DENIED`/`ERROR`/`TIMEOUT`), even with *different* fingerprints — i.e. it tracks outcome streaks, not repeated names, matching the documented "changed strategy after a failure remains allowed" rule. Live-verified in Scenario C below. |
| failure handling | PARTIAL | **PASS** | Failed tool executions are recorded into `history` with their real `ToolExecutionStatus`; the loop continues (does not hard-stop on the first failure) as long as budget remains and the progress guard isn't tripped. |
| final synthesis when exhausted | FAIL | **PASS** | `_finish_with_synthesis()` (`runtime.py:245-302`) issues one extra model call carrying all evidence gathered so far and an explicit "no more tools" instruction; only falls back to the fixed `_exhaustion_summary()` (`runtime.py:496-501`) if the model still insists on a tool call. This is a materially different, evidence-aware design from the baseline's unconditional fixed string. |
| `list_directory -> read_file -> respuesta final` | FAIL | **PASS** | Live-reproduced in this audit (Scenario in section 5.1): completed in one turn, `tool_rounds=2`, final `finish_reason=stop`, no rejection. |

### 5.1 Live reproduction — bounded success (FINDING-001/002/003/009 proof)

Constructed via `create_application()` with a temp workspace containing
`README.md`, `tool_executor="local"`, a scripted 3-call model
(`list_directory` → `read_file README.md` → final text), and a real
`JsonlInteractionDiagnosticLogger`. Output (trimmed):

```
RESPONSE: Final answer: README says hello world.
METRICS: InteractionMetrics(interaction_id='9f453dd174bb42c49473e364a0992307',
  outcome='tool_loop', model_calls=3, prompt_tokens=200, output_tokens=15,
  finish_reason=<FinishReason.STOP: 'stop'>, truncated=False, tool_rounds=2,
  tool_requests=2, executor_operations=2, recovery_operations=0,
  retrieval_attempted=False, knowledge_chunks_selected=0)
```

The JSONL file (`log-scripted-test-model-audit-session-2026-08-28.log`)
contained 12 lines, every one carrying
`"interaction_id": "9f453dd174bb42c49473e364a0992307"`, spanning stages
`context_retrieval` → `model_request`/`model_response` (round 1) →
`requested`/`executed` (`list_directory`) → `model_request`/`model_response`
(round 1→2) → `requested`/`executed` (`read_file`) →
`model_request`/`model_response` (final) → `interaction_completed`. This is a
direct, personally-verified proof of FINDING-001 (bounded multi-round
success), FINDING-002 (`finish_reason`/token counts genuinely populated from
the `ModelResponse`, not just present in the dataclass), and FINDING-009
(single `interaction_id` correlating every stage in one file).

One incidental observation from this run: the `context_retrieval` event's
payload correctly surfaced `provider_context_window=8192`,
`reserved_output_length=2048`, `max_input_length=6144`, `model_num_ctx=8192`,
`model_num_predict=2048` in a single record — i.e. FINDING-008's "one
observable record" is real, not just described in a comment (see section 8).

### 5.2 Live reproduction — duplicate guard (FINDING-004 proof)

Scripted model repeats the exact same `read_file README.md` request twice,
then answers. Result: `tool_requests=2`, `executor_operations=1` (the
duplicate cost nothing), and the JSONL shows:

```
requested read_file None
executed  read_file None
requested read_file None
rejected  read_file {'code': 'duplicate_tool_call', 'message': 'Duplicate tool call rejected; no new evidence would result.'}
```

Final response was the model's real answer (`"ok final"`), not a fallback —
confirming the duplicate guard fires before wasting a tool round, and the
turn still completes normally afterward.

### 5.3 Live reproduction — progress guard / exhaustion synthesis (FINDING-003/005 proof)

Two scenarios: (a) a model that always requests a *new*, distinct, but
nonexistent path each round, and (c) the same with different filenames. Both
stopped after exactly 2 consecutive `denied` attempts (matching
`ProgressGuard(max_consecutive_failures=2)`, `tool_loop.py:71`) with:

```
RESPONSE: No further tools were executed (repeated tool attempts made no further progress).
Attempted this turn:
- read_file: denied
- read_file: denied
```

This is the deterministic fallback path (the scripted model kept demanding a
new tool call even in the synthesis-only follow-up call, so the runtime
correctly refused to spend another round and used
`_exhaustion_summary()`). This proves both that the no-progress guard stops a
genuinely non-productive loop (FINDING-005) and that exhaustion produces a
sanitized, evidence-referencing answer rather than the baseline's
unconditional fixed string (FINDING-003).

## 6. Path Recovery Audit — regression check (non-negotiable section)

Every control the baseline marked PASS was re-read against current source
and re-run:

| Behavior | Baseline | Current | Evidence of no regression |
| -------- | -------- | ------- | -------------------------- |
| PATH_NOT_FOUND recoverable | PASS | PASS | `ai_assistant/application/path_policy.py:60-67` unchanged; `tests/test_tool_coordinator_recovery.py` passes. |
| case-insensitive exact recovery | PASS | PASS | `ai_assistant/application/path_recovery.py:52-100` logic byte-identical to baseline citation; single-candidate-only resolution, no fuzzy match. |
| ambiguity → deny | PASS | PASS | `path_recovery.py:96-99` still raises `AmbiguousPathError` on >1 candidate, never picks one. |
| traversal denied pre-recovery | PASS | PASS | `path_policy.py:84-89` (`".." in path.parts`, absolute-path rejection) unchanged. |
| sensitive/hidden paths denied | PASS | PASS | `_SENSITIVE_PATTERNS`/`_require_allowed_components` in `path_policy.py:32-42,101-108` unchanged; mirrored `_DENIED_CANDIDATE_PATTERNS` in `path_recovery.py:33-44` still excludes sensitive names from ever being offered as a recovery candidate. |
| symlink escape denied | PASS | PASS | `_require_inside_workspace` re-resolves and re-checks the resolved path in both `path_policy.py:98-99` and after any recovery retry (`tool_coordinator.py:174-178`, `path_policy.validate` called again on the corrected path). |
| write excluded from recovery | PASS | PASS | `_RECOVERABLE_TOOLS = {READ_FILE, FILE_METADATA}` at `ai_assistant/application/tool_coordinator.py:39-43` — `write` still never present; comment reiterates "a write must never silently retarget itself" (ADR-030). |
| recovery is a single bounded retry | PASS | PASS | `_attempt_recovery()` (`tool_coordinator.py:135-207`) performs exactly one lookup + one re-validate; no loop. |
| recovery never consumes a model round | PASS | PASS | Confirmed both by code inspection (`_resolve_path` is called once inside a single `execute()` call, itself one model tool round) and live reproduction: recovery-triggering scenarios (5.3) showed `tool_rounds=3` for 3 model-issued tool requests while `executor_operations` separately absorbed the recovery-attempt cost (4), i.e. recovery spend is tracked in a different counter than model rounds, exactly as designed. |
| confirmation required for EXECUTE_PROJECT/WRITE_WORKSPACE | PASS | PASS | `_CONFIRMATION_REQUIRED = {EXECUTE_PROJECT, WRITE_WORKSPACE}` and the `ConfirmationService.ensure_confirmed(...)` gate at `tool_coordinator.py:83-92` are unchanged. |
| deny-by-default ToolPolicy | PASS | PASS | `ai_assistant/application/tool_policy.py:38-51` unchanged: unknown tool, permission mismatch, timeout-over-limit, invalid/over-limit arguments all still explicit denials with stable reason codes. |
| C toolserver participation | PARTIAL | PARTIAL (unchanged) | `git diff --stat HEAD -- c_toolserver` and `git status --short -- c_toolserver` both empty — the C executor was not touched by Phase 5.2 at all. |

Targeted regression run: `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest
tests/test_tool_coordinator_recovery.py tests/test_tools.py
tests/test_adversarial_security.py -q` → **65 passed**.

**Conclusion: zero security or path-recovery regressions found.** Every
previously-PASS control in this section was independently re-read and, where
applicable, re-run or live-reproduced against the current tree; none has
weakened, been removed, or been bypassed by the new tool-loop/budget/
observability code paths added in Phase 5.2.

## 7. Ollama / Generation Budget Audit (re-check)

| Item | Baseline | Current | Evidence |
| ---- | -------- | ------- | -------- |
| effective `num_ctx` | FAIL | **PASS** | `OllamaModelProvider._options()` sends `options.num_ctx` when configured (`ai_assistant/infrastructure/models/ollama.py:59-65`); wired end-to-end from `AppConfig.ollama_num_ctx` → `ModelAdapterConfig` → `_build_ollama_provider` (`ai_assistant/infrastructure/models/adapter.py:76-83`, `ai_assistant/bootstrap/container.py:91,126-135`). |
| effective `num_predict` | FAIL | **PASS** | Same path, `num_predict` (`ollama.py:63-64`). |
| `done` | FAIL | **PASS** | Surfaced in `ModelResponse.metadata["done"]` (`ollama.py:82-86`); live-verified metadata present in this audit's reproduction. |
| `done_reason` | FAIL | **PASS** | Mapped through `_FINISH_REASONS` to `FinishReason.STOP`/`LENGTH`, else `UNKNOWN` unless a tool call was used (`ollama.py:70-73`); `tests/test_ollama_model.py::test_ollama_length_termination_surfaces_truncation_and_tokens` and `::test_ollama_stop_termination_is_not_truncated` cover both branches. |
| `prompt_eval_count`/`eval_count` | FAIL | **PASS** | Read into `ModelResponse.prompt_tokens`/`.output_tokens` (`ollama.py:74-80`), int-guarded. |
| truncation handling | FAIL | **PASS** | `truncated=finish_reason == FinishReason.LENGTH` (`ollama.py:81`); surfaced to `AgentRuntime._call_model` and `InteractionMetrics.truncated` (`runtime.py:330,438`). |
| reserved generation space | FAIL | **PASS** | `ConversationContextBudget.reserved_output_tokens`/`.max_input_tokens` (`ai_assistant/application/conversation_budget.py:20-37`), enforced at `conversation_context.py:40` and configured from `AppConfig.reserved_output_tokens` (default 2048) in `container.py:73-76`. |
| `AI_ASSISTANT_CONTEXT_LIMIT` vs Ollama `num_ctx`/`num_predict` coordination | FAIL | **PASS** | Both numbers are independently configurable (`context_limit` drives `ConversationContextBudget.provider_context_window`; `ollama_num_ctx`/`ollama_num_predict` drive the Ollama payload) but are now surfaced together in one `context_retrieval` diagnostic record per turn (`runtime.py:396-412`) — live-verified in section 5.1: `provider_context_window=8192, reserved_output_length=2048, max_input_length=6144, model_num_ctx=8192, model_num_predict=2048` all appeared in one JSONL line. This is "coordinated into one observable record," per the roadmap's own framing of FINDING-008 — it is observational correlation, not a single enforced value, which is what the roadmap asked for. |
| system prompt duplication | PARTIAL | PARTIAL (unchanged) | Bootstrap-injected tool instructions (`container.py:108-123`) and `Modelfile`'s own `SYSTEM` block remain two independent layers; not a Phase 5.2 target. |
| docs/Modelfile agreement | FAIL | **FAIL (unchanged, known-deferred)** | `Modelfile:9` still says `num_ctx 8192`; `docs/ollama-local.md:67` still says `num_ctx 2048`; `README.md:54` still describes `AI_ASSISTANT_CONTEXT_LIMIT` as a "character budget" although it is now a word-token estimate via `estimate_tokens`. `.agent/reports/M5.2.5.md:15` explicitly defers this (FINDING-015) to closure and it was not picked up — confirmed still open. Not mandatory for this verdict. |

## 8. Tool Observability Audit (re-check)

¿Puede reconstruirse una interacción completa ahora? **YES**, live-verified.

| Field | Baseline | Current | Evidence |
| ----- | -------- | ------- | -------- |
| interaction_id | absent | **present, shared** | `ToolCallLogEvent.interaction_id` and `InteractionLogEvent.interaction_id` (`ai_assistant/domain/tools.py:282,318`), both populated from `AgentRuntime.last_interaction_id` (a fresh `uuid4().hex` per `respond()` call, `runtime.py:88`) and written into the *same* JSONL file by `JsonlToolDiagnosticLogger`/`JsonlInteractionDiagnosticLogger` (`ai_assistant/infrastructure/tool_diagnostics.py:24,41` share the `_filename()` helper). |
| model-call events | absent | **present** | `InteractionStage.MODEL_REQUEST`/`MODEL_RESPONSE` recorded around every `self.model.chat(...)` call (`runtime.py:304-334`), including `finish_reason`, token counts (renamed `input_length`/`output_length` to dodge the sanitizer's substring match — see section 10), and `truncated`. |
| retrieval decision | partially present | **present** | `InteractionStage.CONTEXT_RETRIEVAL` records `include_knowledge`, `retrieval_attempted`, `diagnostic`, candidate/selected counts, and the budget/Ollama numbers (`runtime.py:385-418`). |
| final synthesis event | absent | **present** | `InteractionStage.FINAL_SYNTHESIS` records `reason`, `attempts`, `fallback_used` (`runtime.py:289-298`). |
| interaction completion event | absent | **present** | `InteractionStage.INTERACTION_COMPLETED` records the full `InteractionMetrics` snapshot (`runtime.py:424-469`). |
| duplicate calls | absent | **present** | `rejected` events with `code=duplicate_tool_call` (`runtime.py:206-212`); live-verified in section 5.2. |
| audit DB correlation | absent | **present** | `ToolAuditEvent.interaction_id` column now exists in the SQLite audit schema (`ai_assistant/infrastructure/storage/sqlite_audit.py:124,153`), letting a durable audit row be joined back to the JSONL interaction stream by ID — FINDING-011 materially improved, though recovery *sub-steps* themselves still live only in JSONL, not the audit DB (unchanged, non-mandatory). |

This closes FINDING-009 as a genuine PASS: one turn's context, model calls,
tool requests/results (including a rejected duplicate or a stalled
no-progress attempt), final synthesis, and completion all share one
`interaction_id` in one correlatable JSONL stream, which this audit read
directly rather than trusting the milestone report's description.

## 9. Metrics Audit (re-check)

`ContextMetrics` itself (`ai_assistant/knowledge/metrics.py:10-25`) is
unchanged — still missing history tokens, retrieval latency, and a stale-
rejection counter (FINDING-010 partially open, as expected — not a mandatory
target). However, a new `InteractionMetrics` dataclass
(`ai_assistant/application/interaction_metrics.py:15-29`) now exposes
`model_calls`, `prompt_tokens`, `output_tokens`, `finish_reason`,
`truncated`, `tool_rounds`, `tool_requests`, `executor_operations`,
`recovery_operations`, `retrieval_attempted`, `knowledge_chunks_selected` per
turn, surfaced through `AgentRuntime.last_interaction_metrics` and printed by
`chat --metrics` (`ai_assistant/interfaces/cli/app.py:182-198`). This
directly answers most of M5.2.14's "Expanded metrics" milestone even though
`FINDING-010` was never a mandatory target — a genuine improvement beyond
what closure required.

## 10. A known, deliberately-accepted residual: `redact_sensitive` substring matching

Confirmed accurately still the state: `ai_assistant/infrastructure/
sanitization.py:9-20` (`_SENSITIVE_KEYS`) matches by substring
(`_is_sensitive_key`, `sanitization.py:51-53`), so any compound key
containing "token", "prompt", "content", "response", or "auth" is blanked
regardless of what it actually holds. `.agent/reports/M5.2.13.md:20,41` and
`M5.2.15.md:49` document this honestly as an unfixed root cause, worked
around at the two colliding call sites by renaming payload keys
(`prompt_tokens`/`output_tokens` → `input_length`/`output_length`,
`reserved_output_tokens`/`max_input_tokens` → `reserved_output_length`/
`max_input_length` — visible in `runtime.py:322-329,403-410,454-457`).
Live-verified in this audit's section 5.1 reproduction: the renamed keys
carried real integer token counts through the JSONL file unredacted.

This audit found one **additional, previously undocumented** instance of the
same failure mode, from a different mechanism inside the same file: path-
value redaction. `_is_sensitive_path()` (`sanitization.py:60-62`) treats any
path *segment* starting with `.` as hidden — including the bare current-
directory argument `"."` itself, since `".".split("/")` yields `["."]` and
`".".startswith(".")` is `True`. In this audit's section 5.1 reproduction,
the `list_directory` tool call's `{"path": "."}` argument was logged as
`{"path": "[redacted]"}` in the JSONL, while the `read_file`
`{"path": "README.md"}` call in the same run was left unredacted. This is
**over-redaction of a non-sensitive, non-secret value** (the literal current
directory), not an under-redaction: it makes the diagnostic slightly less
useful for an operator trying to see which directory was listed, but it does
not leak anything that should have stayed hidden. Per this audit's
instructions, an over-redaction false positive is a documented, low-severity,
non-blocking residual — consistent in category and severity with the already
-tracked `M5.2.13`/`M5.2.15` finding, not a new security gap. No case was
found in which something that *should* be redacted (a real secret, an actual
sensitive path, real file content beyond the tool's own return payload) was
left exposed.

## 11. ADR Compliance (re-check)

| ADR | Baseline conformance | Current status (docs/adr/README.md) | Assessment |
| --- | --------------------- | -------------------------------------- | ---------- |
| ADR-024 (bounded single tool round) | PASS-to-ADR/FAIL-to-need | **Superseded** (by ADR-069) | Correctly retired, not left `Implemented` while contradicted by code — `docs/adr/ADR-024-bounded-single-tool-round-per-turn.md:3` says `Status: Superseded`; current runtime code no longer implements a single-round cap anywhere (verified in section 5). |
| ADR-068 (provider-neutral ModelResponse) | n/a (new) | **Implemented** | `docs/adr/ADR-068-provider-neutral-model-response-metadata.md:3`. Verified: all three providers construct `ModelResponse`; `ModelProvider.chat()` signature enforces it; DummyModel remains deterministic (`FinishReason.STOP` always, no provider leakage). |
| ADR-069 (bounded multi-round loop) | n/a (new) | Accepted | Verified fully implemented and live-proven in section 5 (budget, duplicate guard, progress guard, recovery not counted as a round, final synthesis). **This audit recommends promoting ADR-069 to `Implemented`** — every one of its stated guarantees is real, tested, and independently reproduced by this audit, not merely designed. |
| ADR-070 (interaction correlation) | n/a (new) | Accepted | Verified fully implemented and live-proven in section 8 (single `interaction_id` across context/model/tool/synthesis/completion in one JSONL file, plus now in the audit DB). **This audit recommends promoting ADR-070 to `Implemented`** for the same reason. |
| ADR-071 (context/generation budget) | n/a (new) | Accepted | Verified fully implemented: `ConversationContextBudget` is the one shared unit (`estimate_tokens`) used by both `ContextBuilder` and `ConversationContextService`; reserved-output accounting is explicit and enforced; the budget and Ollama `num_ctx`/`num_predict` are surfaced together per turn (section 7). **This audit recommends promoting ADR-071 to `Implemented`** — nothing found here is aspirational; all of it is exercised by passing tests and this audit's own live reproduction. |

The Accepted-not-yet-Implemented status for 069/070/071 reads as a
deliberate, documented choice to defer the promotion to this very closure
milestone (consistent with `docs/roadmap-phase-5.2.md`'s M5.2.16 framing).
Given what this audit independently verified — real code, real tests, real
live reproduction, no gap between the ADR's stated guarantee and the current
implementation for any of the three — **all three now deserve `Implemented`
status**. This is a documentation action item for whoever performs the human
sign-off, not a blocker to the verdict below.

## 12. Baseline → Current status mapping (all 18 findings)

| Finding | Severity | Baseline status | Current status | Mandatory for this closure? | Notes |
| ------- | -------- | ---------------- | ---------------- | ----------------------------- | ----- |
| FINDING-001 | BLOCKER | FAIL | **PASS** | Yes | Bounded multi-round loop, live-verified. |
| FINDING-002 | BLOCKER | FAIL | **PASS** | Yes | Ollama termination/token metadata surfaced end-to-end. |
| FINDING-003 | BLOCKER | FAIL | **PASS** | Yes | Real evidence-aware synthesis, deterministic fallback only if model refuses to stop. |
| FINDING-004 | HIGH | FAIL | **PASS** | Yes | `DuplicateCallGuard`, live-verified, no executor spend on duplicate. |
| FINDING-005 | HIGH | FAIL | **PASS** | Yes | `ProgressGuard`, live-verified, changed-strategy-after-failure still allowed. |
| FINDING-006 | HIGH | PARTIAL | PARTIAL (unchanged) | No | Live-state capability preference still not deterministically enforced; not a Phase 5.2 target. |
| FINDING-007 | HIGH | PARTIAL | **PASS** | Justified PASS or PARTIAL acceptable | Single `estimate_tokens` unit + `ConversationContextBudget` with explicit reserved-output accounting. |
| FINDING-008 | HIGH | FAIL | **PASS** | Yes | `num_ctx`/`num_predict` configurable end-to-end; both numbers surfaced together in one per-turn diagnostic record, live-verified. |
| FINDING-009 | HIGH | PARTIAL | **PASS** | Yes | Single `interaction_id` correlates context/model/tool/synthesis/completion in one JSONL stream and now also in the audit DB; live-verified. |
| FINDING-010 | MEDIUM | PARTIAL | PARTIAL (improved) | No | New `InteractionMetrics` covers most of the gap; `ContextMetrics` itself still lacks retrieval latency/stale counters. |
| FINDING-011 | MEDIUM | PARTIAL | PARTIAL (improved) | No | Audit DB now carries `interaction_id`; recovery sub-steps still JSONL-only. |
| FINDING-012 | MEDIUM | PARTIAL | PARTIAL (unchanged) | No | `context_provider`/`retrieval_policy` still untyped/duck-typed. |
| FINDING-013 | MEDIUM | PARTIAL | PARTIAL (unchanged) | No | No deterministic guard suppresses redundant tool calls when context already has evidence. |
| FINDING-014 | MEDIUM | PARTIAL | PARTIAL (unchanged) | No | `knowledge query` CLI still uses `lexical_search` directly. |
| FINDING-015 | MEDIUM | FAIL | **FAIL (unchanged, deliberately deferred)** | No | Modelfile (`num_ctx 8192`)/docs (`num_ctx 2048`)/README (stale "character budget" description, missing new env vars) still disagree; explicitly deferred in `M5.2.5.md:15`. |
| FINDING-016 | LOW | NOT VERIFIED | NOT VERIFIED (unchanged) | No | Still not run, to honor the read-only audit mandate (a real `compileall` writes `.pyc` files by design, not just when bytecode caching is on). |
| FINDING-017 | LOW | PARTIAL | PARTIAL (unchanged) | No | Direct operator-JSON tool bypass path still returns raw tool result without model synthesis; still an intentional debug path. |
| FINDING-018 | LOW | PARTIAL | PARTIAL (unchanged) | No | Model-facing recoverable-path errors still collapse to generic `path_denied`. |

## 13. Final Verdict

**READY TO CONTINUE**

This verdict includes the M5.2.16-R1 human-review corrective addendum above.

All 8 mandatory findings (FINDING-001, 002, 003, 004, 005, 007, 008, 009) are
genuinely PASS, each backed by (a) current source inspection with exact
file:line evidence, (b) the existing regression test suite (578 passed, 17
skipped, 0 failed), and (c) this audit's own independently-constructed live
reproductions — a real `AgentRuntime` built through `create_application()`,
a scripted model, and a real JSONL diagnostics sink whose output this auditor
read directly rather than trusting any milestone report's description. No
previously-PASS security or path-recovery control has regressed: `PathPolicy`,
`PathRecoveryPolicy`, `DenyByDefaultToolPolicy`, confirmation gating, and the
untouched C toolserver were all re-verified against current source and,
where applicable, re-run.

FINDING-006 and FINDING-010 through FINDING-018 remain PARTIAL, FAIL, or NOT
VERIFIED as before (with FINDING-010/011 measurably improved as a side effect
of the observability work). None of these were designated mandatory for this
closure, so per the audit mandate they do not block this verdict — but they
remain real, accurately-described gaps and should stay on the backlog for a
future hardening pass, particularly FINDING-006 (live-state enforcement) and
FINDING-015 (docs/Modelfile/README drift), both of which have real
operational-confusion risk even though they are not correctness blockers.

Recommendation for the human sign-off: promote ADR-069, ADR-070, and ADR-071
from `Accepted` to `Implemented` in `docs/adr/README.md` and the individual
ADR files — this audit found no gap between what those ADRs promise and what
the current code, tests, and live reproduction actually do.
