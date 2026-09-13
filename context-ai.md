# Contexto del Proyecto AI Assistant

## Fin del proyecto

Construir un asistente de IA local-first, modular, seguro y extensible que evoluciona hacia una plataforma de ejecución de agentes.

El core Python coordina runtime conversacional, modelos, memoria, configuración, CLI, herramientas controladas y ejecución de objetivos. Todo sistema externo debe vivir detrás de puertos/adaptadores. Las herramientas productivas pasan por política determinística, validación de workspace, límites, auditoría y errores sanitizados.

## Estado actual (2026-09-01)

Phase 1, Phase 2, Phase 3, Phase 4 y Phase 5 están implementadas y aceptadas.

Phase 5.1 (Unified CLI + Conversational Context Integration) está implementada; su paquete de cierre quedó como `implemented-awaiting-final-human-review` y el trabajo de Phase 5.2 avanzó sobre ella, pero la fila de `.agent/human-review.md` para Phase 5.1 nunca se actualizó a `approved` — es una inconsistencia de tracking conocida, no una duda funcional (`docs/adr/README.md` ya marca ADR-062..067 como `Implemented`).

**Phase 5.2 (Runtime Hardening & Audit Remediation) está implementada pero NO aceptada.** Estado: `implemented-awaiting-final-human-review`, re-encolada tras un rework correctivo (M5.2.16-R1) pedido por el dueño del producto durante la revisión final. **No debe iniciarse Phase 5.3 ni ningún trabajo nuevo de Phase 5.2 hasta aprobación humana explícita.**

**Hay cambios sin commitear en el working tree** que corresponden a Phase 5.2 completa (incluyendo M5.2.16-R1) — el último commit en el historial (`2cf53c5`) es anterior a todo el trabajo de Phase 5.2. Antes de aceptar la fase formalmente, esos cambios deben revisarse y comitearse.

## Phase 1 — Python Core

Implementado:

- CLI con `python main.py`.
- Runtime framework-agnostic.
- `Message` neutral al proveedor.
- Context builder con presupuesto simple.
- Puertos para modelo y memoria.
- Providers `dummy`, Ollama nativo y OpenAI-compatible.
- Persistencia SQLite transaccional.
- Sesiones explícitas.
- Configuración centralizada.
- Logging básico.
- Errores tipados.
- Tool calls declarativos.
- Pytest y CI separado.
- Arquitectura por capas.

## Phase 2 — Read-Only Tools

Implementado:

- Allowlist productivo: `list_directory`, `read_file`.
- Política deny-by-default.
- Validación de workspace y paths relativos.
- Bloqueo de traversal, paths absolutos externos, symlinks externos, ocultos, sensibles y archivos especiales.
- Límites de timeout, bytes, entradas, profundidad, payload y respuesta.
- Auditoría SQLite sanitizada.
- `LocalReadOnlyToolExecutor`.
- `UnixSocketToolExecutor`.
- Toolserver C con acciones read-only.
- Tests adversariales.

Nota: el límite de "un solo tool round por turno" de esta fase (ADR-024) fue **superado** en Phase 5.2 por ADR-069 (ver más abajo); ya no aplica.

## Phase 3 — Controlled Development Tools

Implementado:

- Allowlist productivo: `file_metadata`, `search_text`, `git_status`, `git_diff`, `run_tests`, `build_project`, `write`.
- C toolserver como executor productivo primario.
- Permisos `READ_METADATA`, `READ_CONTENT`, `READ_REPOSITORY`, `EXECUTE_PROJECT`, `WRITE_WORKSPACE`.
- Confirmación de primer uso para ejecución de proyecto y escritura, scoped por sesión, workspace y permiso.
- Perfiles fijos para tests/builds; sin shell ni comandos definidos por el modelo.
- Búsqueda literal con `rg`, límites y redacción.
- Git status/diff read-only.
- Escritura UTF-8 acotada con create/replace, rename atómico y `expected_sha256` opcional.
- Retención y purga manual confirmada de auditoría.
- Cobertura adversarial Phase 3.

## Phase 4 — Agent Execution Engine

Implementado:

- CLI explícito de objetivos: `python main.py objective "..."`.
- Modelos provider-neutral: `Objective`, `Plan`, `PlatformTask`, `ExecutionRecord`, `ExecutionBudget`, `BudgetUsage`, `Checkpoint`, `ExecutionResult`, `EvaluationResult`.
- `ModelBackedPlanner` usando `ModelProvider` existente.
- Parser tolerante para modelos locales: JSON puro, fenced JSON, JSON con texto alrededor, `action/input/parameters` como aliases controlados.
- `CapabilityRegistry` que mapea capacidades abstractas a herramientas aprobadas.
- Capacidades autónomas read-only: `InspectDirectory`, `ReadFile`, `InspectFileMetadata`, `SearchText`, `InspectGitStatus`, `InspectGitDiff`, `RunTests`, `BuildProject`.
- Exclusión de `write` en ejecución autónoma.
- `PlanValidator` para schema, IDs, dependencias, ciclos, capacidades, argumentos y límites.
- `ExecutionGraph` inmutable con selección determinística de tareas listas.
- `TaskScheduler` secuencial: un worker, una tarea a la vez, sin retry, replanning, paralelismo ni subagentes.
- `BudgetManager` con límites platform-owned: `max_writes=0`, `max_replans=0`.
- `SQLiteExecutionStore` dedicado, separado de conversación y auditoría.
- Checkpoints lógicos de metadata; sin snapshots ni rollback de filesystem.
- `ObjectiveEvaluator` basado en evidencia; texto del modelo no puede convertir fallos en éxito.
- Observabilidad metadata-only.
- Resumen CLI determinístico y sanitizado para objetivos.
- Cobertura adversarial y regresión Phase 1-3.

## Phase 5 — Context & Knowledge Engine

Implementado:

- `KnowledgeStore` SQLite dedicado, derivado y reconstruible.
- CLI manual: `python main.py knowledge status|index|rebuild|query`.
- Hashing SHA-256, frescura, invalidación incremental y rebuild.
- Normalización, chunking, metadata y símbolos derivados.
- SQLite FTS5 para búsqueda léxica local.
- `EmbeddingProvider` separado de `ModelProvider`; `DummyEmbeddingProvider` CPU-only determinista.
- Persistencia local de embeddings y similitud coseno bounded en CPU.
- `HybridRetriever` (FTS5 + símbolos + búsqueda semántica) y `KnowledgeRanker` determinista inspectable.
- `ContextCompiler` con provenance, frescura y `ContextBudget`.
- Integración de contexto en planner y síntesis de objetivos (`objective --metrics`).
- Suite adversarial de seguridad, frescura, presupuesto, provenance y regresiones Phase 1-4.

## Phase 5.1 — Unified CLI & Conversational Context Integration

Implementado (M5.1.1–M5.1.13, `automatically-accepted`):

- Router de comandos unificado (`chat`, `knowledge`, `objective`) en `ai_assistant/interfaces/cli/app.py`.
- `ConversationContextService`, separada de la ruta de `objective`, con política opt-in (`chat --context`).
- Compilador de contexto conversacional reutilizando `ContextCompiler`/`KnowledgeRanker` de Phase 5.
- Política de recuperación determinística: prompts de estado en vivo (p. ej. git status) hacen *bypass* del índice de conocimiento antes de invocar el provider — nunca mezcla conocimiento indexado con estado vivo.
- Bucle conversacional de herramientas preservado end-to-end junto con el contexto opt-in.
- Métricas de contexto expuestas en `chat --metrics`.
- UX de `knowledge status` mejorada y presets/documentación operativa.
- Suite adversarial/regresión y validación end-to-end de mini-fase.
- ADR-062 a ADR-067: `Implemented`.

## Phase 5.2 — Runtime Hardening & Audit Remediation

Origen: auditoría profunda `docs/audits/chat-tool-context-audit.md` (veredicto inicial: **REMEDIATION REQUIRED**, 3 BLOCKER: FINDING-001/002/003).

Implementado (M5.2.1–M5.2.16 + rework M5.2.16-R1):

- **ADR-068 — `ModelResponse` provider-neutral** (`Implemented`): `finish_reason`, `prompt_tokens`, `output_tokens`, `truncated` poblados desde metadata real de Ollama (`done`/`done_reason`/`prompt_eval_count`/`eval_count`).
- **ADR-069 — Bucle de herramientas conversacional multi-ronda acotado** (`Implemented`, sustituye a ADR-024): `ToolLoopBudget`, `DuplicateCallGuard` (huellas exactas repetidas → rechazo sin gasto de executor), `ProgressGuard` (N fallos consecutivos sin cambio de estrategia → detiene), y `_finish_with_synthesis` (una llamada extra al modelo con la evidencia acumulada al agotar el presupuesto, en vez de devolver un rechazo crudo).
- **ADR-070 — Correlación de interacción y observabilidad end-to-end** (`Implemented`): `interaction_id` único por turno; `InteractionStage`/`InteractionLogEvent` (dominio), puerto `InteractionDiagnosticLogger`, `JsonlInteractionDiagnosticLogger` escribe en el **mismo archivo físico** que el diagnóstico de tools existente, permitiendo reconstruir un turno completo (contexto → modelo → tools → síntesis → cierre) filtrando por un solo `interaction_id`.
- **ADR-071 — Presupuesto conjunto de contexto y generación** (`Implemented`): `ConversationContextBudget` coordina la ventana de contexto del provider con la generación reservada; `InteractionMetrics` agrega por turno `model_calls`, tokens, `finish_reason`, `truncated`, `tool_rounds`, `tool_requests`, `executor_operations`, `recovery_operations`, retrieval y chunks seleccionados; `chat --metrics` imprime una línea `interaction: ...`.
- **ADR-024** (single-round por turno): `Superseded (by ADR-069)`.
- Rediseño de configuración de presupuesto (sin ADR nuevo, es config/bootstrap, no arquitectura de dominio): `context_limit`/`reserved_output_tokens`/`ollama_num_ctx`/`ollama_num_predict` reemplazados por `model_context_window`, `model_max_output_tokens`, `model_context_safety_margin` (provider-neutral; Ollama los traduce a `num_ctx`/`num_predict`). Soporte de archivo `.env` en `load_app_config` con precedencia `entorno de proceso > .env > defaults`. Ver `.env.example` (nuevo, sin commitear) y variables actualizadas en `README.md`/`docs/architecture.md`/`docs/model-profiles.md`/`docs/ollama-local.md`.
- **M5.2.16-R1 (rework post-cierre, pedido por el dueño del producto)**: la revisión humana final reprodujo un caso real fallido — `chat --context --metrics "¿Que hace este proyecto?"` obtenía `candidates=0 selected=0` y caía al tool loop en vez de responder directo. Causa raíz: coincidencia de frase completa exacta en FTS para prompts genéricos de resumen de proyecto en lenguaje natural. Corrección (TDD): `SQLiteKnowledgeStore` tokeniza/normaliza las consultas FTS locales en términos no-stopword entre comillas; `ConversationKnowledgeContextProvider` agrega expansión determinística y local de la consulta para prompts genéricos de resumen de proyecto (nunca para prompts de estado en vivo, que siguen haciendo bypass antes de invocar el provider). Revalidado: `candidates=12 ranked=12 selected=12`, `tool_rounds=0`.
- Dos bugs reales de redacción descubiertos y corregidos durante la fase (solo detectables con humo real, no con fakes en memoria): `redact_sensitive()` en `ai_assistant/infrastructure/sanitization.py` hace *substring matching* sobre palabras clave sensibles (`token`, `prompt`, etc.), así que claves legítimas como `prompt_tokens`/`output_tokens`/`reserved_output_tokens`/`max_input_tokens` se redactaban a `"[redacted]"`. Se corrigió renombrando solo las claves del payload JSONL en los puntos de colisión (`input_length`/`output_length`, `reserved_output_length`/`max_input_length`), nunca los campos del dataclass ni las etiquetas de CLI. El diseño raíz de *substring matching* del sanitizador **queda sin corregir intencionalmente** (ver Decisiones faltantes) — es sobre-redacción únicamente (nunca fuga de datos), y una auditoría independiente encontró un tercer caso similar (el path literal `"."` se trata como oculto).
- Auditoría independiente de cierre: `docs/audits/chat-tool-context-audit-post-remediation.md` — veredicto **READY TO CONTINUE**; FINDING-001 a 005, 007, 008 y 009 confirmados `PASS` con reproducción en vivo; cero regresiones de seguridad/path-recovery (C toolserver sin diff en toda la fase).
- Reporte de cierre: `.agent/reports/phase-5.2-final.md` (nota: este archivo se escribió **antes** del rework M5.2.16-R1 y no lo refleja; el estado autoritativo post-rework está en `.agent/roadmap-state.md` y `.agent/roadmap-state-phase-5.2.md`).

**Findings no obligatorios que siguen abiertos** (no bloquean el cierre, según la propia auditoría): FINDING-006 (aplicación de capacidades de estado-en-vivo), FINDING-010/011/012/013/014/016/017/018 (PARTIAL/NOT VERIFIED), FINDING-015 (desacuerdo docs/Modelfile/README sobre el perfil de contexto de Ollama, FAIL, diferido como backlog).

## Estructura actual

```text
ai_assistant/
|-- domain/
|-- application/
|-- platform/
|-- knowledge/
|-- capabilities/
|-- infrastructure/
|   |-- models/
|   |-- storage/
|   `-- tools/
|-- interfaces/
|-- bootstrap/
|-- agent/      # compatibility exports
|-- cli/        # compatibility exports
|-- storage/    # compatibility exports
|-- tools/      # framing/socket helpers
|-- gateway/
`-- main.py
```

## Ejecución

Chat normal:

```bash
python main.py
```

Chat con contexto conversacional (Phase 5.1/5.2):

```bash
AI_ASSISTANT_WORKSPACE="$PWD" python main.py chat --context --metrics
```

Objetivo Phase 4:

```bash
AI_ASSISTANT_PROVIDER=ollama \
AI_ASSISTANT_MODEL=blacksmith-tools \
AI_ASSISTANT_WORKSPACE="$PWD" \
AI_ASSISTANT_TOOL_EXECUTION=true \
AI_ASSISTANT_TOOL_SOCKET=/tmp/blacksmith-toolserver.sock \
AI_ASSISTANT_REQUEST_TIMEOUT=240 \
python main.py objective --verbose "Inspect repository status"
```

Knowledge Engine Phase 5:

```bash
AI_ASSISTANT_WORKSPACE="$PWD" python main.py knowledge rebuild .
AI_ASSISTANT_WORKSPACE="$PWD" python main.py knowledge query "ExecutionEngine"
python main.py objective --metrics "Explain why ExecutionEngine cannot write files"
```

## Configuración de presupuesto de contexto/generación (Phase 5.2, sin commitear)

Variables actuales (reemplazan `AI_ASSISTANT_CONTEXT_LIMIT`/`AI_ASSISTANT_RESERVED_OUTPUT_TOKENS`/`AI_ASSISTANT_OLLAMA_NUM_CTX`/`AI_ASSISTANT_OLLAMA_NUM_PREDICT`):

| Variable | Default | Propósito |
|---|---|---|
| `AI_ASSISTANT_MODEL_CONTEXT_WINDOW` | `4096` | Ventana de contexto del modelo, provider-neutral |
| `AI_ASSISTANT_MODEL_MAX_OUTPUT_TOKENS` | `2048` | Reserva de generación; Ollama la mapea a `num_predict` |
| `AI_ASSISTANT_MODEL_CONTEXT_SAFETY_MARGIN` | `0` | Margen extra restado del presupuesto de entrada compilado |

`load_app_config` ahora también acepta un archivo `.env` (precedencia: entorno de proceso > `.env` > defaults). Ver `.env.example`.

## Persistencia local

Stores separados:

- Conversación: `AI_ASSISTANT_DATABASE`, default `assistant.sqlite3`.
- Auditoría: `AI_ASSISTANT_AUDIT_DATABASE`, default `assistant_audit.sqlite3`.
- Ejecución: `AI_ASSISTANT_EXECUTION_DATABASE`, default `assistant_execution.sqlite3`.
- Conocimiento derivado: `AI_ASSISTANT_KNOWLEDGE_DATABASE`, default `assistant_knowledge.sqlite3`.

No mezclar estos stores sin ADR nuevo y aprobación humana.

## Validación

Suite completa:

```bash
PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -q
```

Última evidencia (2026-09-01, working tree actual, incluye M5.2.16-R1 sin commitear):

```text
600 passed, 17 skipped
```

`git diff --check`: limpio.

Evidencia manual Phase 4: `ia_make-plan.log`.

## ADRs

- ADR-001 a ADR-015: Phase 1 implementada.
- ADR-016 a ADR-023, ADR-025: Phase 2 implementada. ADR-024: `Superseded (by ADR-069)`.
- ADR-026 a ADR-035: Phase 3 implementada.
- ADR-036 a ADR-046: Phase 4 implementada.
- ADR-047 a ADR-061: Phase 5 implementada.
- ADR-062 a ADR-067: Phase 5.1 implementada.
- ADR-068 a ADR-071: Phase 5.2 implementada (`Implemented`, promovidas al cierre de M5.2.16 tras el veredicto favorable de la auditoría independiente).

71 archivos de ADR en `docs/adr/` (más `README.md` general y `README-phase-*.md` por fase).

## Estado de gates y revisión humana

- Phase 1 a Phase 5: aceptadas.
- Phase 5.1: implementada; fila de `.agent/human-review.md` sigue en `awaiting-review` (gap de tracking, no bloqueante funcionalmente — Phase 5.2 ya se construyó sobre ella).
- **Phase 5.2: `implemented-awaiting-final-human-review`, re-encolada tras M5.2.16-R1. Requiere aprobación explícita del dueño del producto antes de iniciar Phase 5.3 o cualquier otro trabajo nuevo.**
- Paquete de revisión pendiente: `.agent/reports/phase-5.2-final.md` (desactualizado respecto al rework — no lo menciona), `docs/audits/chat-tool-context-audit-post-remediation.md`, y la fila correspondiente en `.agent/human-review.md` (línea ~109) que sí documenta el rework M5.2.16-R1.
- Cambios de Phase 5.2 completos están sin commitear en el working tree; deben revisarse/comitearse como parte del cierre formal.

## Datos disponibles tras Phase 5.2

| Área | Disponible |
|---|---|
| Runtime conversacional (bucle multi-ronda, observabilidad, métricas) | `ai_assistant/application/runtime.py` |
| Bucle acotado de herramientas | `ai_assistant/application/tool_loop.py` |
| Context builder / presupuesto conversacional | `ai_assistant/application/conversation_context.py`, `conversation_budget.py` |
| Diagnóstico de interacción/tools | `ai_assistant/application/tool_diagnostics.py`, `application/interaction_metrics.py` |
| Model providers | `ai_assistant/infrastructure/models/` |
| Tool catalog y policy | `ai_assistant/application/tool_catalog.py`, `tool_policy.py` |
| Workspace path policy | `ai_assistant/application/path_policy.py` |
| Tool coordinator | `ai_assistant/application/tool_coordinator.py` |
| Audit store | `ai_assistant/infrastructure/storage/sqlite_audit.py` |
| Diagnóstico JSONL (tools + interacción, mismo archivo) | `ai_assistant/infrastructure/tool_diagnostics.py` |
| Sanitización (bug de sobre-redacción conocido, ver Decisiones faltantes) | `ai_assistant/infrastructure/sanitization.py` |
| Execution platform | `ai_assistant/platform/` |
| Execution store | `ai_assistant/infrastructure/storage/sqlite_execution.py` |
| Knowledge domain | `ai_assistant/knowledge/` |
| Knowledge store (FTS tokenizado tras M5.2.16-R1) | `ai_assistant/infrastructure/storage/sqlite_knowledge.py` |
| Knowledge CLI | `ai_assistant/interfaces/cli/knowledge.py` |
| Embeddings locales | `ai_assistant/infrastructure/embeddings/` |
| C toolserver (sin cambios en Phase 5.2) | `c_toolserver/` |
| Auditorías | `docs/audits/chat-tool-context-audit.md`, `docs/audits/chat-tool-context-audit-post-remediation.md` |
| Manual objective evidence | `ia_make-plan.log` |
| Adversarial tests | `tests/test_adversarial_security.py`, `tests/test_platform_*`, `tests/test_knowledge_adversarial.py`, `tests/test_agent_runtime.py`, `tests/test_interaction_diagnostics.py` |

## Decisiones faltantes

- **Aprobación humana final de Phase 5.2** (bloqueante para Phase 5.3).
- Comitear los cambios de Phase 5.2 al historial de git (actualmente solo en working tree).
- Actualizar `.agent/reports/phase-5.2-final.md` para reflejar el rework M5.2.16-R1 (o dejarlo como está y confiar en `.agent/roadmap-state.md` como fuente de verdad — decidir cuál).
- Corregir formalmente el gap de tracking de aprobación de Phase 5.1 en `.agent/human-review.md`.
- Decidir si se corrige el diseño raíz de *substring matching* de `redact_sensitive()` (backlog, no bloqueante; solo causa sobre-redacción confirmada, nunca fuga).
- Decidir la siguiente fase del producto (Phase 5.3+) una vez aprobada Phase 5.2.
- Decidir si se agregan embeddings productivos reales; hoy el provider incluido para pruebas es dummy CPU-only.
- FINDING-006, 010-018 de la auditoría: decidir si se abordan como trabajo futuro o se cierran explícitamente como aceptados tal cual.
- Mantener excluidos sin ADR nuevo: memoria semántica de usuario, automatic skills, MCP, network retrieval, watcher daemon y vector DB externo.

## Recomendaciones

- No iniciar Phase 5.3 hasta que el dueño del producto apruebe explícitamente el cierre de Phase 5.2.
- Revisar y comitear los cambios de Phase 5.2 antes de considerar la fase realmente cerrada.
- Mantener `KnowledgeStore` como estado derivado y reconstruible.
- Indexar manualmente antes de pruebas con objetivos o chat con contexto.
- Usar `chat --context --metrics` y `objective --metrics` para comparar duración, llamadas, tokens y rondas de herramientas.
- Cualquier cambio futuro a `redact_sensitive()` debe tratarse como una revisión de seguridad dedicada, no como un fold-in de otra tarea.
