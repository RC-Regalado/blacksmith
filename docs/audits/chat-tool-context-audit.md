# Chat / Context / Tooling Deep Audit

## 1. Executive Summary

Estado general: REMEDIATION REQUIRED.

El sistema tiene integración real de Phase 5.1 entre chat, ConversationContextService, retrieval, KnowledgeStore y CLI, pero la integración es insuficiente para continuar ampliando la plataforma sin correcciones. La mayor falla funcional es el límite conversacional de una sola ronda de herramienta: el flujo legítimo `list_directory -> read_file -> respuesta final` queda bloqueado por diseño y aparece en logs reales como `tool_round_limit_reached`. Además, el adapter de Ollama no envía ni coordina `num_ctx`/`num_predict`, no expone `done_reason` ni contadores de tokens, y el runtime acepta respuestas no vacías sin detectar truncamiento. La observabilidad de tools es útil para eventos de herramienta, pero no permite reconstruir una interacción completa de modelo + contexto + tool loop.

Conteo de clasificaciones de esta auditoría:

| Status | Count |
| ------ | -----:|
| PASS | 8 |
| PARTIAL | 18 |
| FAIL | 8 |
| NOT VERIFIED | 4 |

Blockers:

- FINDING-001: el límite de una ronda impide flujos legítimos multi-step dentro de una misma respuesta.
- FINDING-002: Ollama puede truncar o terminar por límite sin que el adapter/runtime lo detecte.
- FINDING-003: no existe síntesis final útil cuando se agota el budget de tools; se devuelve un mensaje genérico.

Riesgos principales:

1. Correctness: el chat no puede completar preguntas simples que requieren descubrir un path y luego leerlo en el mismo turno.
2. Seguridad/semántica: el bypass de retrieval para estado vivo existe, pero la preferencia por capabilities en vivo queda delegada al modelo si las tools están habilitadas.
3. Observabilidad: los logs separan requests, ejecución, recovery y rejections, pero carecen de `interaction_id`, eventos de llamada al modelo, contexto compilado, causa de retrieval bypass y síntesis final.
4. Budgets: se mezclan presupuestos por caracteres, tokens aproximados por palabras y parámetros Ollama configurados externamente sin coordinación verificable.
5. Eficiencia: no hay métrica causal ni guard determinístico que pruebe que una tool fue evitada gracias al contexto.

Recomendación: corregir primero. No recomiendo continuar ampliando capacidades hasta rediseñar el tool loop conversacional, añadir metadata de terminación/tokenización en ModelProvider/Ollama y cerrar la trazabilidad end-to-end.

Evidencia de validación ejecutada durante esta auditoría:

- `git status --short && git branch --show-current` -> branch `develop`; modificados preexistentes: `Modelfile`, `ai_assistant/application/tool_calls.py`, `tests/test_tools.py`.
- Focused audit regression: `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest tests/test_agent_runtime.py tests/test_conversation_context.py tests/test_phase51_adversarial.py tests/test_tool_coordinator_recovery.py tests/test_tool_diagnostics.py tests/test_ollama_model.py -q -p no:cacheprovider` -> `54 passed in 0.40s`.
- `git diff --check` -> passed.
- No se ejecutó build compilante porque el mandato fue read-only y los builds Python habituales pueden escribir `__pycache__`/`.pyc`.

## 2. Architecture Conformance

| Area | Expected | Actual | Status | Evidence |
| ---- | -------- | ------ | ------ | -------- |
| Clean Architecture | `interfaces -> application -> domain`; infrastructure implements ports; bootstrap composes. | La separación principal existe. Runtime depende de puertos de memory/model/tools y de servicios application. Bootstrap conoce infrastructure. | PASS | `docs/architecture.md:168-184`, `ai_assistant/application/runtime.py:8-24`, `ai_assistant/bootstrap/container.py:51-95`. |
| ports/adapters | ModelProvider, stores y executors detrás de puertos. | `ModelProvider` es mínimo y no transporta metadata; executors/catalog/policy sí están portados. | PARTIAL | `ai_assistant/application/ports/models.py:8-11`, `ai_assistant/application/ports/tools.py:23-33`, `ai_assistant/bootstrap/container.py:74`. |
| store separation | ConversationStore, AuditStore, ExecutionStore y KnowledgeStore separados. | Config y bootstrap crean bases separadas; KnowledgeStore dedicado. | PASS | `ai_assistant/bootstrap/config.py:18-20,32`, `ai_assistant/bootstrap/container.py:61,73,142,172`. |
| provider separation | Ollama y OpenAI-compatible aislados detrás del ModelProvider. | Separación existe, pero Ollama pierde metadata crítica de terminación/tokens. | PARTIAL | `ai_assistant/infrastructure/models/adapter.py:55-78`, `ai_assistant/infrastructure/models/ollama.py:31-36,74-86`. |
| capability boundaries | Objective usa CapabilityRegistry para mapear capabilities a tools aprobadas. | Implementado para objective; chat no tiene router capability explícito, depende de tool-call JSON del modelo. | PARTIAL | `ai_assistant/platform/application/engine.py:198-205`, `ai_assistant/application/runtime.py:90-93`. |
| Context Engine boundaries | ConversationContextService no debe ejecutar tools, persistir ni llamar Ollama; KnowledgeStore sigue derivado. | Servicio cumple boundaries, pero usa `context_provider` sin puerto tipado y mezcla presupuestos con ContextBuilder. | PARTIAL | `docs/roadmap-phase-5.1.md:96-120`, `ai_assistant/application/conversation_context.py:10-86`. |
| tool execution boundaries | ToolCall -> policy -> path -> audit -> executor -> audit; recovery interno no debe saltarse policy/path. | Pipeline principal existe; recovery revalida PathPolicy. Falta guard de duplicados/progreso y multi-round budget. | PARTIAL | `docs/adr/ADR-016-safe-tool-execution-pipeline.md:30`, `ai_assistant/application/tool_coordinator.py:72-97,99-202`. |

## 3. Conversational Context Integration

| Behavior | Status | Evidence |
| -------- | ------ | -------- |
| chat sin contexto | PASS | `CliApplication.run` deja `include_knowledge_context` en default/env si no hay `--context`; runtime llama `build_with_retrieval(... include_knowledge=False)` y el servicio no recupera knowledge. `ai_assistant/interfaces/cli/app.py:43-55`, `ai_assistant/application/runtime.py:58-63`, `ai_assistant/application/conversation_context.py:52-55`. Test: `tests/test_phase51_e2e.py:29-42`. |
| chat con `--context` | PASS | CLI setea `include_knowledge_context=True`; bootstrap inyecta ConversationKnowledgeContextProvider + ConversationRetrievalPolicy. `ai_assistant/interfaces/cli/app.py:48-53`, `ai_assistant/bootstrap/container.py:67-72`. Test: `tests/test_phase51_e2e.py:45-60`. |
| `AI_ASSISTANT_CONTEXT_ENGINE=true` | PASS | Config lee env y runtime inicia con `include_knowledge_context=app_config.context_engine`. `ai_assistant/bootstrap/config.py:108-111`, `ai_assistant/bootstrap/container.py:82`. Test config: `tests/test_config.py:27-82`. |
| ConversationContextService | PARTIAL | Ensambla history + user + knowledge separada, pero no tiene puerto formal para `context_provider`/`retrieval_policy`; no registra causa de bypass ni tokens de history. `ai_assistant/application/conversation_context.py:10-86`. |
| ContextCompiler conversation | PASS | `compile_conversation_context()` existe y delega a `compile(ContextPurpose.CONVERSATION, ...)`; preserva provenance verificando hash/token_count/freshness. `ai_assistant/knowledge/compiler.py:20-43,45-60`. Tests: `tests/test_context_compiler.py:71-77`, `tests/test_phase51_adversarial.py:125-158`. |
| ConversationRetrievalPolicy | PARTIAL | Determinística y sin LLM classifier, pero heurística frágil por substrings: cualquier mensaje <=2 palabras se omite, y live-state detection requiere términos concretos. `ai_assistant/knowledge/retrieval_policy.py:30-43`. Tests: `tests/test_phase51_adversarial.py:81-87`. |
| ContextBudget | PARTIAL | `ContextBudget` usa token_count derivado de chunks; ContextBuilder usa caracteres; ConversationContextService usa `split()` para total. No existe `ConversationContextBudget` separado con history/knowledge/total. `ai_assistant/knowledge/domain.py:30-41`, `ai_assistant/application/context.py:24-36`, `ai_assistant/application/conversation_context.py:41,100-101`. |
| fallback sin índice | PASS | Si no hay evidence, inyecta diagnóstico visible y no rebuild. `ai_assistant/application/conversation_context.py:68-76`; `tests/test_phase51_e2e.py:96-119`. |
| índice stale | PASS | Store/retrieval/compiler excluyen stale; tests validan stale no aparece. `ai_assistant/infrastructure/storage/sqlite_knowledge.py:384-388`, `ai_assistant/knowledge/retrieval.py:83-91`, `ai_assistant/knowledge/compiler.py:53-60`; `tests/test_phase51_adversarial.py:58-79`. |
| provenance | PASS | Knowledge message incluye `source_uri#chunk_id`; compiler verifica content_hash y token_count. `ai_assistant/application/conversation_context.py:89-97`, `ai_assistant/knowledge/compiler.py:45-60`. |

Conclusión: el Context & Knowledge Engine sí está integrado en chat, pero la integración es opt-in, heurística y sin un presupuesto conversacional real separado. No hay prueba determinística de que el modelo evite tools por contexto salvo modelos fake/scripted.

## 4. Knowledge vs Live State

| Example | Expected | Actual | Status | Evidence |
| ------- | -------- | ------ | ------ | -------- |
| arquitectura del proyecto | Usar indexed knowledge si fresh y `--context`; evitar tool si evidencia suficiente. | El sistema inyecta chunks fresh y el test espera respuesta sin tool coordinator. La evitación depende del modelo, no de un guard del runtime. | PARTIAL | `tests/test_phase51_e2e.py:45-60`, `ai_assistant/application/runtime.py:90-93`. |
| contenido de README | Stable document content puede venir de index si fresh; si se solicita contenido actual exacto debería usar `read_file`. | Retrieval policy permite `readme`; no diferencia “explícame README indexado” vs “lee el README actual”. | PARTIAL | `ai_assistant/knowledge/retrieval_policy.py:4-17,43`, `docs/roadmap-phase-5.1.md:76-94`. |
| estado actual de Git | Debe usar capability vivo `git_status`, no knowledge. | Policy evita retrieval para “currently changed in Git”; el modelo scripted llama `git_status`. No hay enforcement si el modelo responde sin tool. | PARTIAL | `ai_assistant/knowledge/retrieval_policy.py:18-27,37-42`, `tests/test_phase51_e2e.py:63-94`, `tests/test_agent_runtime.py:303-336`. |
| resultado actual de tests | Debe usar `run_tests`. | Retrieval policy omite frases como `test result` y `tests passing`, pero no fuerza `run_tests`; depende del prompt/modelo. | PARTIAL | `ai_assistant/knowledge/retrieval_policy.py:23-25,41-42`, `Modelfile:85-87`, `ai_assistant/bootstrap/container.py:109`. |
| resultado actual de build | Debe usar `build_project`. | Igual: bypass para `build result`/`show build`, sin enforcement de capability viva. | PARTIAL | `ai_assistant/knowledge/retrieval_policy.py:25-27,41-42`, `Modelfile:88-89`, `ai_assistant/bootstrap/container.py:110`. |

Observación clave: Phase 5.1 documenta “live state prefers live capabilities” (`docs/roadmap-phase-5.1.md:76-94`), pero el código solo previene retrieval en algunos casos; no existe un dispatcher que convierta intención live-state en capability obligatoria.

## 5. Tool Loop Audit

Flujo implementado:

```text
model
→ assistant JSON tool_call
→ ToolCallDetector
→ ToolExecutionCoordinator.execute
→ tool result Message(role="tool")
→ model
→ final answer OR second tool request rejected
```

Evidencia exacta:

- Primer modelo: `AgentRuntime.respond()` llama `self.model.chat(context)` en `ai_assistant/application/runtime.py:90`.
- Detección: `self.tool_detector.detect(response)` en `ai_assistant/application/runtime.py:91`.
- Ejecución: `_respond_with_tool_round()` crea request y ejecuta coordinator en `ai_assistant/application/runtime.py:112-129`.
- Tool result: `Message(role="tool", ...)` en `ai_assistant/application/runtime.py:130-135`.
- Segundo modelo: `self.model.chat([*context, tool_request_message, tool_message])` en `ai_assistant/application/runtime.py:136`.
- Segunda tool request: rechazada con `tool_round_limit_reached` en `ai_assistant/application/runtime.py:137-156`.

| Control | Status | Evidence |
| ------- | ------ | -------- |
| max rounds | FAIL | Hardcoded a 1 executed round; second request is always rejected. `ai_assistant/application/runtime.py:137-156`. Tests: `tests/test_agent_runtime.py:338-365`. Logs reales: `logs/tools/log-blacksmith-tools-context-test-2b-2026-08-28.log:1-4`. |
| max requests | PARTIAL | Solo un tool call por message; `ToolCallInterpreter` toma un objeto `tool_call`, no lista. No hay `max_requests` configurable. `ai_assistant/application/tool_calls.py:16-22,35-47`. |
| executor operation budget | PARTIAL | Recovery registra counters internos, pero no hay budget object general ni enforcement multi-op. `ai_assistant/application/tool_coordinator.py:132-201`. |
| duplicate detection | FAIL | No hay guard por fingerprint de tool name + args; solo rechazo del segundo request por límite. Search no encontró implementación de duplicate guard fuera de tests de plan IDs. |
| no-progress detection | FAIL | No hay tracking semántico de progreso ni guard para requests equivalentes tras error. |
| failure handling | PARTIAL | Executor exceptions se normalizan; denial/error/timeouts se registran. Pero el modelo recibe un JSON de error y la siguiente tool request se rechaza por límite aunque sea alternativa legítima. `ai_assistant/application/tool_coordinator.py:260-272`, `ai_assistant/application/runtime.py:136-156`. |
| final synthesis when exhausted | FAIL | Devuelve literal “Tool round limit reached; no additional tool was executed.”, sin sintetizar con evidencia disponible. `ai_assistant/application/runtime.py:153-156`. |
| `list_directory -> read_file -> respuesta final` | FAIL | Log real `context-test-2b`: `list_directory` ejecutó en round 1; `read_file README.md` fue requested+rejected en round 2 por `tool_round_limit_reached`. `logs/tools/log-blacksmith-tools-context-test-2b-2026-08-28.log:1-4`. |

## 6. Path Recovery Audit

| Behavior | Status | Evidence |
| -------- | ------ | -------- |
| PATH_NOT_FOUND | PASS | `PathNotFoundError` es recoverable; missing path intenta recovery y falla con `path_not_found`. `ai_assistant/domain/errors.py`, `ai_assistant/application/path_policy.py:61-66`, `tests/test_tool_coordinator_recovery.py:80-94`. |
| case-insensitive exact recovery | PASS | Busca coincidencia exacta case-insensitive solo del basename; revalida PathPolicy. `ai_assistant/application/path_recovery.py:1-19,78-97`, `ai_assistant/application/tool_coordinator.py:169-202`. Test: `tests/test_tool_coordinator_recovery.py:45-65`. |
| ambiguity | PASS | Más de una coincidencia -> `AmbiguousPathError`, denied sin elegir. `ai_assistant/application/path_recovery.py:91-97`; `tests/test_tool_coordinator_recovery.py:96-110`. |
| traversal | PASS | `..` y absolutos se deniegan antes de recovery. `ai_assistant/application/path_policy.py:88-93`; `tests/test_tool_coordinator_recovery.py:112-124`. |
| sensitive paths | PASS | Hidden/sensitive se deniegan; candidatos sensibles no se ofrecen. `ai_assistant/application/path_recovery.py:33-45,111-118`, `ai_assistant/application/path_policy.py:103-110`; tests `tests/test_tool_coordinator_recovery.py:126-154`. |
| symlink escape | PASS | Revalidación de path resuelto impide escape; case variant de symlink externo falla tras retry. `ai_assistant/application/path_policy.py:61-70`, `tests/test_tool_coordinator_recovery.py:156-194`. |
| write exclusion | PASS | `_RECOVERABLE_TOOLS` solo incluye `read_file` y `file_metadata`; `write` no entra. `ai_assistant/application/tool_coordinator.py:39-43,117-124`; `tests/test_tool_coordinator_recovery.py:197-215`. |
| recovery retries | PASS | Una resolución y una revalidación; test valida cap a 1 operation. `ai_assistant/application/tool_coordinator.py:132-201`; `tests/test_tool_coordinator_recovery.py:239-249`. |
| recovery budgets | PARTIAL | Se reportan `model_tool_requests=1`, `executor_operations`, `recovery_operations`; no hay enforcement externo ni budget object dedicado. `ai_assistant/application/tool_diagnostics.py:92-121`. |
| toolserver C participation | PARTIAL | C repite validación de workspace/sensitive/symlink para ejecución productiva, pero recovery ocurre solo en Python antes del executor. `c_toolserver/src/actions.c:287-312,631-789,1182-1229`. |

## 7. Ollama / Generation Budget Audit

| Item | Status | Evidence |
| ---- | ------ | -------- |
| effective `num_ctx` | FAIL | El adapter no envía `options.num_ctx`; depende de Modelfile/server. Modelfile actual declara 8192, docs/ollama-local todavía recomienda 2048. `ai_assistant/infrastructure/models/ollama.py:38-43`, `Modelfile:7-13`, `docs/ollama-local.md:16-18,63-70`. |
| effective `num_predict` | FAIL | El adapter no envía `options.num_predict`; solo Modelfile actual lo fija en 2048. `ai_assistant/infrastructure/models/ollama.py:38-43`, `Modelfile:11-13`. |
| system prompt | PARTIAL | Bootstrap añade instrucciones de tools a `AI_ASSISTANT_SYSTEM_PROMPT`; Modelfile tiene otro SYSTEM. Puede haber dos capas de instrucciones no coordinadas. `ai_assistant/bootstrap/container.py:98-113`, `Modelfile:23-98`. |
| prompt/context size | PARTIAL | `AI_ASSISTANT_CONTEXT_LIMIT` controla caracteres de history; `ConversationContextService` usa palabra-split; no hay medición real del prompt enviado. `ai_assistant/application/context.py:24-36`, `ai_assistant/application/conversation_context.py:100-101`. |
| reserved generation space | FAIL | No existe reserva explícita que reste `num_predict` de `num_ctx`; `ContextBudget` puede llenar 4096 tokens estimados y Modelfile permitir 2048 output sin coordinación. |
| `done` | FAIL | No se lee ni se expone `done`. `ai_assistant/infrastructure/models/ollama.py:31-86`. |
| `done_reason` | FAIL | No se lee ni se expone; truncamiento por `length` sería invisible. `ai_assistant/infrastructure/models/ollama.py:74-86`. Test ausente: `tests/test_ollama_model.py` solo valida content/tool_calls/errors. |
| `prompt_eval_count` | FAIL | No se captura. |
| `eval_count` | FAIL | No se captura. |
| truncation handling | FAIL | Cualquier `message.content` no vacío se convierte en Message; no hay warning/error si Ollama cortó. `ai_assistant/infrastructure/models/ollama.py:74-86`. |

Determinación: sí existe riesgo de truncamiento silencioso. El puerto `ModelProvider.chat() -> Message` no tiene espacio para terminación, token counts ni metadata (`ai_assistant/application/ports/models.py:8-11`).

## 8. Tool Observability Audit

¿Puede reconstruirse una interacción completa? PARTIAL.

Lo que sí se puede reconstruir para tools:

| Field | Present | Evidence |
| ----- | ------- | -------- |
| timestamp | yes | `ToolCallLogEvent.timestamp`; JSONL payload. `ai_assistant/domain/tools.py:263-278`, `ai_assistant/infrastructure/tool_diagnostics.py:26-33`. |
| session_id | yes | `ToolCallLogEvent.session_id`. |
| interaction_id | no | No existe campo equivalente en `ToolCallLogEvent`. |
| tool_call_id | yes | `ToolCallLogEvent.tool_call_id`. |
| model/provider | yes | `provider`, `model`. |
| round | yes | `round_index`, `tool_call_count`. |
| tool name | yes | `tool_name`. |
| sanitized arguments | yes | JSONL usa `redact_sensitive`. `ai_assistant/infrastructure/tool_diagnostics.py:26-33`. |
| result/status/duration | yes | `result`, `status`, `duration_ms`. |
| model_tool_requests | only recovery events | `ToolLoopDiagnostics.recovery()` hardcodea `model_tool_requests: 1`. `ai_assistant/application/tool_diagnostics.py:112-118`. |
| executor_operations | only recovery events | same. |
| recovery_operations | only recovery events | same. |
| rejection reason | yes | `error.code`, e.g. `tool_round_limit_reached`. |
| duplicate calls | no | No duplicate guard/status. |
| tool-round exhaustion | yes | Runtime logs requested+rejected round 2. `tests/test_tool_diagnostics.py:122-139`. |

Lo que falta para reconstrucción completa:

- No hay log de cada llamada al modelo con session+interaction+round+prompt token estimate+completion metadata.
- No hay log de retrieval policy decision o context chunks seleccionados por interaction.
- No hay `interaction_id` común que una model call, context retrieval, tool requests, recovery y final response.
- Audit SQLite guarda eventos de coordinator, pero no registra recovery ni model tool requests como flujo conversacional completo. `ai_assistant/infrastructure/storage/sqlite_audit.py:33-54,99-150`.

Logs diagnósticos reales inspeccionados:

- `logs/tools/log-blacksmith-tools-context-test-2a-2026-08-28.log`: muestra `read_file` failed por `missing_socket`, luego `list_directory` round 2 rejected por budget.
- `logs/tools/log-blacksmith-tools-context-test-2b-2026-08-28.log`: muestra `list_directory` success y `read_file README.md` round 2 rejected.

## 9. Metrics Audit

| Metric | Current | Status | Evidence |
| ------ | ------- | ------ | -------- |
| knowledge candidates | Present | PASS | `ContextMetrics.knowledge_candidates`, `ai_assistant/knowledge/metrics.py:9-41`. |
| selected chunks | Present | PASS | `knowledge_chunks_selected`, same. |
| compiled tokens | Present as estimated chunk tokens | PARTIAL | `compiled_context_estimated_tokens=context.token_count`, `ai_assistant/knowledge/metrics.py:38-40`. |
| history tokens | Missing | FAIL | No field in `ContextMetrics`; roadmap explicitly left out in current seam. `docs/roadmap-phase-5.1.md:218-221`. |
| tool calls avoided | Missing | FAIL | No causal attribution; roadmap says out of scope. |
| retrieval latency | Missing | FAIL | No duration in `ConversationKnowledgeContextProvider.build`. `ai_assistant/knowledge/conversation.py:24-30`. |
| stale rejection | Missing as metric | PARTIAL | Stale excluded, but no counter. `ai_assistant/knowledge/retrieval.py:83-91`, `ai_assistant/knowledge/compiler.py:53-60`. |
| tool rounds | Present in diagnostics only | PARTIAL | `round_index` and `tool_call_count` in JSONL, not surfaced in `--metrics`. |
| executor operations | Recovery-only | PARTIAL | `executor_operations` only in recovery events. |
| recovery operations | Recovery-only | PARTIAL | `recovery_operations` only in recovery events. |
| model calls | Objective budget only | PARTIAL | `ExecutionEngine` records one model call for planning; chat metrics do not. `ai_assistant/platform/application/engine.py:105-108`. |
| output tokens | Missing | FAIL | Ollama eval_count not captured; no tokenizer. |

Las métricas de Phase 5/5.1 representan solo el comportamiento del retrieval/compiler, no el comportamiento completo del chat. La documentación del roadmap ya reconoce gaps (`docs/roadmap-phase-5.1.md:218-221`), pero para auditoría de plataforma esos gaps son materialmente importantes.

## 10. Test Coverage Audit

| Behavior | Unit | Integration | Adversarial | Status |
| -------- | ---- | ----------- | ----------- | ------ |
| chat default context-off | `tests/test_conversation_context.py:71-82` | `tests/test_phase51_e2e.py:29-42` | yes, `tests/test_phase51_adversarial.py:42-56` | PASS |
| chat `--context` retrieval | `tests/test_conversation_context.py:58-68` | `tests/test_phase51_e2e.py:45-60` | yes | PASS |
| env context enable | `tests/test_config.py:27-82` | CLI fake runtime only | no live end-to-end | PARTIAL |
| stale knowledge excluded | `tests/test_phase51_adversarial.py:58-79` | `tests/test_phase51_e2e.py:96-119` | yes | PASS |
| live-state retrieval bypass | `tests/test_phase51_adversarial.py:81-87` | `tests/test_phase51_e2e.py:63-94` | scripted model only | PARTIAL |
| tool policy preservation | `tests/test_agent_runtime.py:235-300` | coordinator tests | yes | PASS |
| multi-step conversational tools | only rejection tested | no success case | no | FAIL |
| duplicate tool guard | no | no | no | FAIL |
| no-progress guard | no | no | no | FAIL |
| path recovery | `tests/test_tool_coordinator_recovery.py:45-249` | runtime reproduction `:254-278` | yes | PASS |
| recovery does not consume LLM round | unit asserted | no real log assertion against model calls | partial | PASS |
| diagnostic JSONL logging | `tests/test_tool_diagnostics.py:28-160` | sample logs in repo | no duplicate/no-progress | PARTIAL |
| Ollama done/tokens | no | no | no | FAIL |
| context/generation budget coordination | `tests/test_config.py:92-95` only allows 8192 | no | no | FAIL |
| knowledge CLI lifecycle | `tests/test_knowledge_cli.py:14-153` | no real CLI process | yes path cases | PARTIAL |
| C toolserver audited flow | contract tests for actions | yes contract | path/symlink tests | PASS |

## 11. ADR Compliance

| ADR(s) | Subject | Conformance | Evidence |
| ------ | ------- | ----------- | -------- |
| ADR-001..007 | Ports/adapters, message, stores, config | PASS | ADR index implemented `docs/adr/README.md:24-32`; code boundaries as above. |
| ADR-011 | Native Ollama adapter | PARTIAL | Uses `/api/chat` and isolated adapter, but lacks termination/tokens metadata required for current budget audit. `ai_assistant/infrastructure/models/ollama.py:31-43,74-86`. |
| ADR-015 | Configurable model profiles | PARTIAL | Context limit configurable; Ollama `num_ctx`/`num_predict` not configured through runtime. `ai_assistant/bootstrap/config.py:67-70`; `Modelfile:9-13`. |
| ADR-016 | Safe tool execution pipeline | PARTIAL | Pipeline exists; recovery revalidates; observability/audit incomplete for full interaction. `ai_assistant/application/tool_coordinator.py:72-97`. |
| ADR-017 | Deny-by-default | PASS | Exact checks and stable reason codes. `ai_assistant/application/tool_policy.py:24-52`. |
| ADR-019/025 | Path confinement/sensitive deny | PASS | PathPolicy + recovery/C validation cover traversal, hidden, sensitive, symlink escape. `ai_assistant/application/path_policy.py:79-166`, `c_toolserver/src/actions.c:287-312`. |
| ADR-020/023/034 | Audit/redaction/retention | PARTIAL | Audit store and redaction exist; full interaction/recovery not in audit DB. `ai_assistant/infrastructure/storage/sqlite_audit.py:33-54`, `ai_assistant/infrastructure/tool_diagnostics.py:26-33`. |
| ADR-024 | Bounded single tool round | PASS to ADR, FAIL to current product need | Code implements single round. This now conflicts with legitimate Phase 5.1 chat flow expectations. `ai_assistant/application/runtime.py:137-156`; `docs/adr/ADR-024-bounded-single-tool-round-per-turn.md:21-45`. |
| ADR-028 | C toolserver primary executor | PASS | Bootstrap default `unix_socket`; C handles all current tools. `ai_assistant/bootstrap/config.py:34-35`, `ai_assistant/bootstrap/container.py:157-160`, `c_toolserver/src/actions.c:1182-1229`. |
| ADR-047..059 | Knowledge engine derived, retrieval, compiler, budgets, freshness, manual lifecycle | PASS/PARTIAL | Core implemented; budgets and metrics are approximate/incomplete. `ai_assistant/infrastructure/storage/sqlite_knowledge.py`, `ai_assistant/knowledge/compiler.py`, `ai_assistant/interfaces/cli/knowledge.py`. |
| ADR-060/061 | No semantic user memory / no automatic skills | PASS | No evidence of semantic long-term user memory or automatic skill generation in inspected paths. |
| ADR-062 | Conversation context integration | PARTIAL | Dedicated service exists; provider port untyped and metrics incomplete. `ai_assistant/application/conversation_context.py:10-86`. |
| ADR-063 | Opt-in chat context | PASS | CLI flag/env default off. `ai_assistant/interfaces/cli/app.py:43-53`, `ai_assistant/bootstrap/config.py:37,108-111`. |
| ADR-064 | Conversation context budget | PARTIAL | No distinct ConversationContextBudget; mixed char/word/token estimates. |
| ADR-065 | Indexed knowledge vs live capability semantics | PARTIAL | Retrieval bypass exists but live capability use is model-dependent. |
| ADR-066 | Unified CLI command model | PASS | `chat|objective|knowledge` router present. `ai_assistant/interfaces/cli/app.py:35-124`. |
| ADR-067 | Deterministic retrieval policy | PASS/PARTIAL | Deterministic, no LLM; heuristic gaps remain. `ai_assistant/knowledge/retrieval_policy.py:30-43`. |

## 12. Findings

### FINDING-001 — Conversational one-round tool limit blocks legitimate discovery-read flows

* Severity: BLOCKER
* Status: FAIL
* Component: AgentRuntime tool loop
* Expected: The tool loop should allow legitimate bounded flows such as `list_directory -> read_file -> respuesta final` without becoming unbounded.
* Actual: Runtime executes at most one tool request; any second tool request is rejected with `tool_round_limit_reached`.
* Evidence: `ai_assistant/application/runtime.py:137-156`; `tests/test_agent_runtime.py:338-365`; real log `logs/tools/log-blacksmith-tools-context-test-2b-2026-08-28.log:1-4` shows round 1 `list_directory` success followed by round 2 `read_file README.md` rejection.
* Risk: The assistant cannot complete common repository-inspection tasks in one turn; users receive generic budget exhaustion despite available safe path.
* Recommendation: Replace single executed round with a small platform-owned loop budget separating model rounds, tool requests and executor/recovery operations.
* Suggested tests: e2e test where model requests `list_directory`, then `read_file`, then final answer; assert two executed tools, no third tool, full diagnostic trace.

### FINDING-002 — Ollama termination metadata and token counts are discarded

* Severity: BLOCKER
* Status: FAIL
* Component: ModelProvider / Ollama adapter
* Expected: Adapter exposes `done`, `done_reason`, `prompt_eval_count`, `eval_count` and termination metadata so truncation and budget exhaustion are visible.
* Actual: `OllamaModelProvider.chat()` returns only `Message(role="assistant", content=...)` and ignores all response fields except `message.content` / first `tool_calls`.
* Evidence: `ai_assistant/application/ports/models.py:8-11`; `ai_assistant/infrastructure/models/ollama.py:31-36,74-86`; tests in `tests/test_ollama_model.py:26-170` do not cover `done_reason` or token counts.
* Risk: Silent truncation can look like a valid final answer or malformed JSON/tool call; budgets cannot be audited.
* Recommendation: Extend provider result contract or side-channel metadata before expanding context-heavy flows.
* Suggested tests: fake Ollama response with `done_reason="length"`, `prompt_eval_count`, `eval_count`; assert runtime surfaces/records truncation.

### FINDING-003 — Tool-round exhaustion does not synthesize a useful final answer

* Severity: BLOCKER
* Status: FAIL
* Component: AgentRuntime final response
* Expected: When tool budget is exhausted, final output should summarize what is known, what was executed, what was rejected and what the user can do next.
* Actual: Runtime replaces model output with fixed text: `Tool round limit reached; no additional tool was executed.`
* Evidence: `ai_assistant/application/runtime.py:153-156`; `tests/test_agent_runtime.py:338-365` encodes this fixed string.
* Risk: User loses useful partial evidence and cannot tell which request failed unless inspecting logs.
* Recommendation: Add a final synthesis path that includes sanitized executed tool evidence and explicit rejected request reason, without executing more tools.
* Suggested tests: budget exhaustion after successful first tool returns a final answer containing first result summary and rejected second tool name/code.

### FINDING-004 — No duplicate-call guard exists

* Severity: HIGH
* Status: FAIL
* Component: Tool loop policy
* Expected: Repeated identical tool requests in a turn should be detected and rejected separately from round exhaustion.
* Actual: No fingerprint/history guard exists; second request is rejected only because round limit is hit.
* Evidence: No duplicate implementation in `ai_assistant/application/runtime.py` or `tool_coordinator.py`; only unrelated duplicate plan tests found. Search results show no `duplicate` guard for tool calls.
* Risk: If rounds are increased, loops can repeat identical calls and waste budgets.
* Recommendation: Add per-interaction duplicate fingerprinting before increasing max rounds.
* Suggested tests: model repeats exact `read_file` request twice; assert `duplicate_tool_call` rejection and final synthesis.

### FINDING-005 — No no-progress guard exists

* Severity: HIGH
* Status: FAIL
* Component: Tool loop policy
* Expected: The loop should stop when successive calls do not add evidence or repeat failed strategy.
* Actual: No progress state is tracked; current safety relies on hard stop after one round.
* Evidence: `ai_assistant/application/runtime.py:112-167` has no progress accounting; `ToolLoopDiagnostics` has no progress status in `ai_assistant/domain/tools.py:88-99`.
* Risk: Increasing tool rounds without this guard can create loops; keeping one round blocks useful flows.
* Recommendation: Track result signatures/status deltas and require each new request to be non-duplicate and plausibly progress-making.
* Suggested tests: failed `read_file missing.md` followed by same failed path; changed path allowed; unrelated tool after failure rejected if no progress rationale is available.

### FINDING-006 — Live-state capability preference is not enforced

* Severity: HIGH
* Status: PARTIAL
* Component: ConversationRetrievalPolicy / chat runtime
* Expected: Current Git/tests/build queries must use live capabilities when tools are available and not rely on indexed knowledge.
* Actual: Retrieval is bypassed for several live-state patterns, but runtime still lets the model answer directly or choose tools; no deterministic router forces `git_status`, `run_tests` or `build_project`.
* Evidence: `ai_assistant/knowledge/retrieval_policy.py:18-27,37-42`; `ai_assistant/application/runtime.py:90-93`; tests use scripted model tool calls in `tests/test_phase51_e2e.py:63-94`.
* Risk: A model can answer stale/imagined live state if it ignores instructions.
* Recommendation: Add a live-state intent guard or capability hint/required-tool policy for volatile classes.
* Suggested tests: live-state prompt with model direct answer should be rejected or forced into capability path when tools enabled.

### FINDING-007 — Context budget semantics are inconsistent

* Severity: HIGH
* Status: PARTIAL
* Component: ContextBuilder / ConversationContextService / ContextBudget
* Expected: `num_ctx`, input prompt, history, knowledge and reserved generation space should be governed coherently.
* Actual: ContextBuilder uses character lengths; ContextCompiler uses chunk token_count; ConversationContextService uses whitespace word count; no generation reserve.
* Evidence: `ai_assistant/application/context.py:24-36`; `ai_assistant/knowledge/domain.py:30-41`; `ai_assistant/application/conversation_context.py:41,100-101`.
* Risk: Prompt can exceed Ollama context or crowd out response tokens while appearing in-budget.
* Recommendation: Define a ConversationContextBudget with history, knowledge, tool-result and output reserve estimates.
* Suggested tests: oversized history + knowledge + tool result near configured `num_ctx`; assert deterministic trimming and preserved output reserve.

### FINDING-008 — Runtime does not coordinate `AI_ASSISTANT_CONTEXT_LIMIT` with Ollama `num_ctx`/`num_predict`

* Severity: HIGH
* Status: FAIL
* Component: Bootstrap / Ollama adapter / Modelfile
* Expected: Effective Ollama context/generation limits should be known or explicitly configured by runtime.
* Actual: Config has `context_limit`, but Ollama payload has no `options`; Modelfile currently says `num_ctx 8192`, docs recommend server context 2048 and CLI context 2048/4096.
* Evidence: `ai_assistant/bootstrap/config.py:25,67-70`; `ai_assistant/infrastructure/models/ollama.py:38-43`; `Modelfile:9-13`; `docs/ollama-local.md:16-18,63-70,83-85`; `docs/model-profiles.md:7-22`.
* Risk: Operators may believe context is 4096/8192 while server/model effective window differs.
* Recommendation: Make context/generation options explicit and observable; avoid relying on divergent docs/Modelfile defaults.
* Suggested tests: payload includes expected `options` when configured; docs and Modelfile consistency guard.

### FINDING-009 — Tool observability lacks interaction-level correlation

* Severity: HIGH
* Status: PARTIAL
* Component: Tool diagnostics / logs
* Expected: Reconstruct complete interaction: context, model request, tool requests, executor/recovery ops, final response.
* Actual: JSONL logs tool events but no `interaction_id`, no model-call events, no retrieval decision, no final synthesis event.
* Evidence: `ai_assistant/domain/tools.py:263-278`; `ai_assistant/application/tool_diagnostics.py:123-153`; `ai_assistant/infrastructure/tool_diagnostics.py:26-33`; logs under `logs/tools/`.
* Risk: Incidents cannot be reconstructed without conversation DB + logs + inference from timestamps.
* Recommendation: Introduce per-turn `interaction_id` propagated through context, model calls, diagnostics and audit.
* Suggested tests: one chat turn produces correlated model/request/executor/recovery/final records sharing an ID.

### FINDING-010 — Metrics do not represent full chat behavior

* Severity: MEDIUM
* Status: PARTIAL
* Component: ContextMetrics / CLI metrics
* Expected: Metrics should represent retrieval, context, tool loop, model calls and output tokens for chat.
* Actual: Metrics only show candidates/ranked/selected/raw/compiled/reduction. Missing history tokens, tool calls avoided, retrieval latency, stale rejection, model calls and output tokens.
* Evidence: `ai_assistant/knowledge/metrics.py:9-41`; `ai_assistant/interfaces/cli/app.py:167-178`; roadmap notes exclusions at `docs/roadmap-phase-5.1.md:218-221`.
* Risk: Operators may overestimate efficiency and cannot diagnose why a chat turn used tools.
* Recommendation: Expand metrics after provider metadata and interaction IDs exist.
* Suggested tests: `chat --context --metrics` includes retrieval decision, model_calls, tool_rounds, selected chunks and output termination.

### FINDING-011 — Tool diagnostics and audit are split with different coverage

* Severity: MEDIUM
* Status: PARTIAL
* Component: SQLiteAuditRecorder / JsonlToolDiagnosticLogger
* Expected: Durable audit and diagnostic logs should have clear responsibilities and enough overlap for incident review.
* Actual: Audit DB records coordinator allow/result events; JSONL records model-requested and recovery events. Recovery is not durable in audit DB.
* Evidence: `ai_assistant/infrastructure/storage/sqlite_audit.py:33-54,99-150`; `ai_assistant/application/tool_coordinator.py:136-201`; `ai_assistant/application/tool_diagnostics.py:92-121`.
* Risk: If JSONL logs rotate/delete, recovery evidence disappears from durable audit.
* Recommendation: Either persist recovery summaries in audit or document JSONL as required diagnostic artifact with retention.
* Suggested tests: recovery success/failure has durable audit metadata and JSONL detail.

### FINDING-012 — ConversationContextService uses untyped provider/policy seams

* Severity: MEDIUM
* Status: PARTIAL
* Component: Application context service
* Expected: Application services should depend on explicit ports.
* Actual: Constructor accepts `context_provider=None`, `retrieval_policy=None` and calls duck-typed `.build()`/`.allow()`.
* Evidence: `ai_assistant/application/conversation_context.py:10-23,56-63,80-86`.
* Risk: Boundary drift and harder contract testing as context providers expand.
* Recommendation: Add explicit application/knowledge ports for conversation context provider and retrieval policy.
* Suggested tests: contract tests for provider exceptions, metrics shape and policy decisions.

### FINDING-013 — Knowledge can reduce tools only by prompt/model behavior, not by deterministic runtime guard

* Severity: MEDIUM
* Status: PARTIAL
* Component: Chat context/tool interaction
* Expected: The system should avoid tools when context is sufficient.
* Actual: Context is injected before model, but the runtime does not suppress tool calls when the compiled context already contains evidence. Tests prove scripted no-tool behavior, not enforcement.
* Evidence: `ai_assistant/application/runtime.py:90-93`; `tests/test_phase51_e2e.py:45-60`; `Modelfile:31-35,50-51`.
* Risk: Model may still call `read_file` unnecessarily, wasting rounds and hitting budget.
* Recommendation: Add diagnostics and possibly a soft/hard policy for stable-context sufficiency cases.
* Suggested tests: model requests `read_file README.md` after fresh README chunk injected; assert logged as unnecessary or allowed with explicit reason depending target design.

### FINDING-014 — Knowledge query CLI uses lexical_search only, not HybridRetriever/Ranker

* Severity: MEDIUM
* Status: PARTIAL
* Component: Knowledge CLI
* Expected: Knowledge query management interface should represent available retrieval behavior or clearly state lexical-only.
* Actual: `KnowledgeCli._query()` calls `store.lexical_search()` directly; conversation/objective providers use HybridRetriever + Ranker + Compiler.
* Evidence: `ai_assistant/interfaces/cli/knowledge.py:91-99`; `ai_assistant/knowledge/conversation.py:24-29`; `ai_assistant/knowledge/planning.py:30-35`.
* Risk: Operator query diagnostics differ from chat/objective retrieval behavior.
* Recommendation: Clarify CLI as lexical-only or route through the same retriever/ranker metrics seam.
* Suggested tests: symbol/semantic-only candidate appears in provider retrieval and documented CLI behavior matches.

### FINDING-015 — Docs and Modelfile disagree on Ollama context profile

* Severity: MEDIUM
* Status: FAIL
* Component: Operator docs / Modelfile
* Expected: Local profile docs, Modelfile and config examples should agree or explain precedence.
* Actual: `docs/ollama-local.md` says server/model context 2048; `Modelfile` now uses `num_ctx 8192` and `num_predict 2048`; README example uses `AI_ASSISTANT_CONTEXT_LIMIT=2048`.
* Evidence: `docs/ollama-local.md:16-18,63-70,83-85`; `Modelfile:9-13`; `README.md:95-103`.
* Risk: Operators may misdiagnose latency/truncation and context failures.
* Recommendation: Align documentation after deciding target context profile.
* Suggested tests: documentation guard asserting Modelfile parameters appear in runbook.

### FINDING-016 — Build result not verifiable under strict read-only audit

* Severity: LOW
* Status: NOT VERIFIED
* Component: Build validation
* Expected: Audit examples include current build result.
* Actual: Running `compileall`/build profile may write bytecode. This audit did not run it to honor read-only instruction.
* Evidence: Build profile documented as `python -m compileall -q ai_assistant main.py` in `README.md:172-179`; C/Python build commands can write artifacts.
* Risk: Current build status remains unknown in this audit.
* Recommendation: Provide a read-only build/check command or allow ephemeral artifact writes for validation.
* Suggested tests: add no-write static import/AST compile check if feasible.

### FINDING-017 — Tool execution direct user JSON bypasses model and returns raw tool JSON, not synthesized answer

* Severity: LOW
* Status: PARTIAL
* Component: AgentRuntime direct operator tool JSON path
* Expected: Direct operator tool calls are useful for deterministic testing, but chat UX should distinguish raw execution from assistant synthesis.
* Actual: If user input itself is `tool_call`, runtime executes and returns `_tool_result_content` directly without model synthesis or normal explanatory answer.
* Evidence: `ai_assistant/application/runtime.py:67-89`; `tests/test_agent_runtime.py:176-203`.
* Risk: Useful for testing, confusing for normal chat if user pasted JSON expecting integrated flow.
* Recommendation: Keep as operator/debug path and document as raw execution mode; do not count it as chat synthesis.
* Suggested tests: CLI/help documents direct JSON path and output shape.

### FINDING-018 — Recovery error differentiation is good internally but collapses model-facing result to `path_denied`

* Severity: LOW
* Status: PARTIAL
* Component: Path recovery / coordinator
* Expected: Recoverable and non-recoverable errors should be differentiated without leaking sensitive paths.
* Actual: Diagnostics preserve `path_not_found`, `ambiguous_path`, `path_outside_workspace`; final tool result often becomes generic `path_denied`.
* Evidence: `ai_assistant/application/tool_coordinator.py:147-158,181-192,229-242`; tests `tests/test_tool_coordinator_recovery.py:83-94,99-110,174-194`.
* Risk: Model/user may not know whether to retry with corrected case, ask user, or stop.
* Recommendation: Consider sanitized model-facing subcodes for recoverable miss vs ambiguity while preserving path secrecy.
* Suggested tests: ambiguous recovery returns safe actionable error message without candidate leakage.

## 13. Improvement Plan

### Immediate

1. Redesign conversational tool budget before increasing capabilities:
   - allow at least a bounded two-step discovery-read flow;
   - separate model tool rounds, tool requests, executor operations and recovery operations;
   - add duplicate and no-progress guards first.
2. Extend ModelProvider/Ollama result contract to include termination metadata: `done`, `done_reason`, `prompt_eval_count`, `eval_count`, provider raw duration if safe.
3. Add final synthesis on tool budget exhaustion using sanitized available evidence.
4. Add interaction-level correlation ID propagated through context, model calls, tool diagnostics and audit.

### Short term

1. Define `ConversationContextBudget` with explicit history, knowledge, tool-result, total and generation reserve fields.
2. Coordinate `AI_ASSISTANT_CONTEXT_LIMIT`, Ollama `num_ctx`, `num_predict` and Modelfile/server profile in docs and code.
3. Add live-state guard/capability routing for Git/tests/build prompts when tools are enabled.
4. Expand chat metrics to include retrieval decision, retrieval latency, context size, model calls, tool rounds and output termination.
5. Formalize ports for conversation context provider and retrieval policy.

### Later

1. Improve tool-avoidance attribution once interaction IDs and model metadata exist.
2. Unify or clearly separate `knowledge query` lexical behavior vs HybridRetriever behavior.
3. Add optional operator diagnostics for stale/empty index at chat startup without automatic rebuild.
4. Add richer but sanitized recovery messages for ambiguity/missing path cases.
5. Consider tokenization approximation compatible with target Ollama model, but keep it deterministic and local.

## 14. Recommended Tool Loop Design

### CURRENT

```text
1. Build conversation context.
2. Call model once.
3. If assistant response contains tool_call:
   a. log requested round=1;
   b. execute one ToolExecutionCoordinator request;
   c. log completed;
   d. append tool result message;
   e. call model second time.
4. If second model response contains tool_call:
   a. log requested round=2;
   b. reject with tool_round_limit_reached;
   c. return fixed exhaustion message.
```

Current counters:

- `round_index`: diagnostic only.
- `tool_call_count`: diagnostic only.
- `executor_operations`: only recovery event payload.
- `recovery_operations`: only recovery event payload.
- No duplicate fingerprint.
- No progress guard.

### RECOMMENDED

```text
Per interaction budget:
- model_tool_rounds_max: 3 small default for chat, configurable by platform not model
- tool_requests_max: 3-5 per interaction
- executor_operations_max: includes validation + execution + recovery retries
- recovery_operations_max: 1 per path-bearing tool request

Loop:
1. Create interaction_id.
2. Compile context and log retrieval decision/metrics.
3. Call model and log provider metadata.
4. For each tool request:
   a. validate against ToolPolicy/PathPolicy;
   b. reject duplicate fingerprint before executor;
   c. reject no-progress pattern before executor;
   d. execute/recover within executor/recovery budget;
   e. append sanitized result;
   f. continue only if budget remains and last result added evidence.
5. On budget exhaustion:
   a. do not execute more tools;
   b. run or construct final synthesis over available evidence;
   c. include rejected tool name/code and next safe operator action.
```

## 15. Recommended Context Flow

### CURRENT

```text
chat
→ ContextBuilder(system + recent history + user)
→ ModelProvider
→ optional one tool round

chat --context
→ ConversationRetrievalPolicy.allow(user_input)
→ if allowed: ConversationKnowledgeContextProvider(HybridRetriever + KnowledgeRanker + ContextCompiler)
→ ConversationContextService inserts system knowledge message
→ ModelProvider
→ optional one tool round

objective
→ ModelBackedPlanner receives compiled planning context in JSON payload
→ ExecutionEngine executes validated plan through capabilities/tools
→ SynthesisContextProvider appends context observations

knowledge
→ manual status/index/rebuild/query
→ query uses SQLite lexical_search directly
```

### RECOMMENDED

```text
chat
→ ConversationContextService always owns assembly
→ retrieval disabled by policy
→ model call metadata logged
→ bounded tool loop with final synthesis

chat --context
→ retrieval policy emits explicit decision: bypass/allow/live-state/no-index/stale
→ context provider compiles fresh derived evidence
→ ConversationContextBudget reserves output and tool-result space
→ model receives provenance + diagnostics
→ live-state guard overrides stale indexed knowledge for Git/tests/build
→ bounded tool loop with duplicate/progress guard

objective
→ keep capability registry authoritative
→ planning/synthesis context budgets coordinated with provider context limits
→ include provider termination metadata in objective metrics

knowledge
→ lifecycle management remains manual
→ query either documents lexical-only or uses same retriever/ranker path as chat/objective
→ status exposes empty/fresh/partially-stale/stale/error without rebuild
```

## 16. Final Verdict

REMEDIATION REQUIRED

El sistema cumple una parte importante de Phase 5.1: la integración opt-in del Context & Knowledge Engine en chat existe, el KnowledgeStore permanece derivado, el recovery de paths está bien acotado y las policies de tools siguen siendo autoritativas. Sin embargo, hay blockers antes de ampliar la plataforma:

1. El tool loop de una ronda no soporta flujos legítimos y ya falla en logs reales con `list_directory -> read_file`.
2. Ollama no expone metadata de terminación/tokens, por lo que no se puede auditar truncamiento ni coordinar budgets.
3. La síntesis al agotar budget no es útil.
4. La observabilidad no reconstruye una interacción completa.
5. Los budgets de contexto/generación no son coherentes entre código, Modelfile y docs.

La recomendación técnica es corregir estos puntos antes de seguir ampliando capacidades de chat, retrieval o tools.
