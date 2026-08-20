# Contexto del Proyecto AI Assistant

## Fin del proyecto

Construir un asistente de IA local-first, modular, seguro y extensible que evoluciona hacia una plataforma de ejecución de agentes.

El core Python coordina runtime conversacional, modelos, memoria, configuración, CLI, herramientas controladas y ejecución de objetivos. Todo sistema externo debe vivir detrás de puertos/adaptadores. Las herramientas productivas pasan por política determinística, validación de workspace, límites, auditoría y errores sanitizados.

## Estado actual

Phase 1, Phase 2, Phase 3 y Phase 4 están implementadas y aceptadas.

Phase 4 quedó aceptada tras revisión humana final de M4.18.

Phase 5 está implementada y aceptada tras revisión humana final.

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
- Un solo tool round por turno conversacional.
- Tests adversariales.

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
- Observabilidad metadata-only: objetivo, plan, ejecución, transiciones, presupuesto, checkpoints y estado final sin prompts ni contenido de archivos.
- Resumen CLI determinístico y sanitizado para objetivos, derivado solo de resultados de herramientas ejecutadas; incluye guías simples para Makefile y CMake cuando hay evidencia.
- Cobertura adversarial y regresión Phase 1-3.

## Phase 5 — Context & Knowledge Engine

Implementado:

- `KnowledgeStore` SQLite dedicado, derivado y reconstruible.
- CLI manual: `python main.py knowledge status|index|rebuild|query`.
- Hashing SHA-256, frescura, invalidación incremental y rebuild.
- Normalización, chunking, metadata y símbolos derivados.
- SQLite FTS5 para búsqueda léxica local.
- `EmbeddingProvider` separado de `ModelProvider`.
- `DummyEmbeddingProvider` CPU-only y determinista.
- Persistencia local de embeddings y similitud coseno bounded en CPU.
- `HybridRetriever` que combina FTS5, símbolos y búsqueda semántica.
- `KnowledgeRanker` determinista con componentes inspectables.
- `ContextCompiler` con provenance, frescura y `ContextBudget`.
- Integración de contexto en planner y síntesis de objetivos.
- Métricas de contexto y `python main.py objective --metrics "..."`.
- Suite adversarial de seguridad, frescura, presupuesto, provenance y regresiones Phase 1-4.
- Guías operativas: `docs/knowledge-engine.md` y `docs/phase5-functional-evaluation.md`.

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

## Persistencia local

Stores separados:

- Conversación: `AI_ASSISTANT_DATABASE`, default `assistant.sqlite3`.
- Auditoría: `AI_ASSISTANT_AUDIT_DATABASE`, default `assistant_audit.sqlite3`.
- Ejecución: `AI_ASSISTANT_EXECUTION_DATABASE`, default `assistant_execution.sqlite3`.
- Conocimiento derivado: `AI_ASSISTANT_KNOWLEDGE_DATABASE`, default `assistant_knowledge.sqlite3`.

No mezclar estos stores sin ADR nuevo y aprobación humana.

## Validación

Suite completa en entorno con `protobuf-c`:

```bash
PKG_CONFIG_PATH=/home/rc-regalado/.local/lib/pkgconfig \
LD_LIBRARY_PATH=/home/rc-regalado/.local/lib \
PYTHONDONTWRITEBYTECODE=1 python -m pytest -q
```

Última evidencia M5.20:

```text
475 passed, 1 skipped
```

Evidencia manual Phase 4:

- `ia_make-plan.log`: objetivo ejecutado con plan de 3 tareas, checkpoints, presupuesto, evaluación `passed`.

## ADRs

- ADR-001 a ADR-015: Phase 1 implementada.
- ADR-016 a ADR-025: Phase 2 implementada.
- ADR-026 a ADR-035: Phase 3 implementada.
- ADR-036 a ADR-046: Phase 4 implementada.
- ADR-047 a ADR-061: Phase 5 implementada.

## Estado Phase 5

Objetivo:

> Reducir el trabajo que debe realizar el LLM principal transformando previamente datos locales en conocimiento indexado, recuperable, versionado y compilable en contexto de alta relevancia.

Estado:

- M5.1 a M5.21 aceptados por revisión humana.
- Phase 5 cerrada y aceptada.
- No hay siguiente fase activa todavía.

## Datos disponibles tras Phase 5

| Área | Disponible |
|---|---|
| Runtime conversacional | `ai_assistant/application/runtime.py` |
| Context builder | `ai_assistant/application/context.py` |
| Model providers | `ai_assistant/infrastructure/models/` |
| Tool catalog y policy | `ai_assistant/application/tool_catalog.py`, `tool_policy.py` |
| Workspace path policy | `ai_assistant/application/path_policy.py` |
| Tool coordinator | `ai_assistant/application/tool_coordinator.py` |
| Audit store | `ai_assistant/infrastructure/storage/sqlite_audit.py` |
| Execution platform | `ai_assistant/platform/` |
| Execution store | `ai_assistant/infrastructure/storage/sqlite_execution.py` |
| Knowledge domain | `ai_assistant/knowledge/` |
| Knowledge store | `ai_assistant/infrastructure/storage/sqlite_knowledge.py` |
| Knowledge CLI | `ai_assistant/interfaces/cli/knowledge.py` |
| Embeddings locales | `ai_assistant/infrastructure/embeddings/` |
| C toolserver | `c_toolserver/` |
| Manual objective evidence | `ia_make-plan.log` |
| Adversarial tests | `tests/test_adversarial_security.py`, `tests/test_platform_*`, `tests/test_knowledge_adversarial.py` |

## Decisiones faltantes

- Decidir la siguiente fase del producto.
- Decidir si el chat conversacional normal debe usar contexto indexado; hoy solo `objective` lo consume.
- Decidir si se agregan embeddings productivos reales; hoy el provider incluido para pruebas es dummy CPU-only.
- Decidir umbrales de evaluación funcional si se quiere comparar reducción de llamadas/tokens entre versiones.
- Mantener excluidos sin ADR nuevo: memoria semántica de usuario, automatic skills, MCP, network retrieval, watcher daemon y vector DB externo.

## Recomendaciones

- Validar manualmente `docs/phase5-functional-evaluation.md` antes de aceptar Phase 5.
- Mantener `KnowledgeStore` como estado derivado y reconstruible.
- Indexar manualmente antes de pruebas con objetivos.
- Usar `objective --metrics` para comparar duración, llamadas y tokens compilados.
- No activar contexto indexado en chat normal sin una decisión explícita.
