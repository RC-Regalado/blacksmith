# Context IA

Contexto completo: `context-ai.md`.

## Estado

Phase 1, Phase 2, Phase 3 y Phase 4 están implementadas y aceptadas.

Phase 4 finalizó con M4.18 aprobado por revisión humana.

La plataforma ya soporta:

- chat local-first;
- herramientas controladas;
- toolserver C;
- ejecución explícita de objetivos;
- planes estructurados;
- validación de DAG;
- scheduler secuencial;
- presupuestos;
- checkpoints lógicos;
- persistencia de ejecución separada;
- evaluación por evidencia;
- observabilidad metadata-only;
- pruebas adversariales y regresión Phase 1-3.

## Siguiente fase

Phase 5: Context & Knowledge Engine.

Objetivo:

> Reducir el trabajo que debe realizar el LLM principal transformando previamente datos locales en conocimiento indexado, recuperable, versionado y compilable en contexto de alta relevancia.

## Datos disponibles

- `ai_assistant/application/context.py`
- `ai_assistant/platform/`
- `ai_assistant/application/tool_coordinator.py`
- `ai_assistant/application/path_policy.py`
- `ai_assistant/infrastructure/storage/sqlite_execution.py`
- `ai_assistant/infrastructure/storage/sqlite_audit.py`
- `c_toolserver/`
- `ia_make-plan.log`
- `tests/test_platform_*`

## Decisiones pendientes

- ADRs de Phase 5.
- `KnowledgeStore` separado de ConversationStore, AuditStore y ExecutionStore.
- Estrategia de índice: lexical, SQLite FTS, embeddings o híbrida.
- Formato de documentos, chunks, metadata y versiones.
- Política de invalidación/reindexado.
- Presupuesto de recuperación y compilación de contexto.
- Redacción y control de contenido sensible.
- Cómo el Knowledge Engine usará capacidades existentes sin saltarse políticas.
