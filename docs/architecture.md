# Architecture

## 1. Propósito del documento

Este documento define la arquitectura del proyecto **AI Assistant**, un asistente de IA local-first, modular, extensible y desacoplado.

La arquitectura está diseñada para mantener independientes:

- El runtime del agente.
- Los proveedores de modelos.
- La memoria conversacional.
- Las interfaces de usuario.
- La persistencia.
- Las futuras herramientas.
- Los futuros servicios de alto rendimiento escritos en C.

El documento distingue explícitamente entre:

- **Implemented**: ya existe en el repositorio.
- **Planned in Phase 1**: debe completarse durante la fase actual.
- **Future**: pertenece a fases posteriores y no debe condicionar innecesariamente el diseño actual.

---

## 2. Estado actual

### 2.1 Fase actual

**Phase 4: Agent Execution Engine**

Phase 1, Phase 2, Phase 3 y Phase 4 están implementadas. El producto ya funciona como asistente local-first y como plataforma de ejecución de objetivos read-only.

El núcleo funcional en Python incluye:

- Gateway delgado.
- Runtime de agente framework-agnostic.
- Abstracción de mensajes.
- Constructor de contexto.
- Adaptadores de modelo.
- Modelo dummy.
- Adaptador OpenAI-compatible.
- Adaptador Ollama nativo.
- Memoria en memoria.
- Persistencia SQLite.
- CLI mínima.
- Sesión predeterminada persistente.
- Logging básico.
- Configuración mediante variables de entorno.
- Pruebas con `pytest`.
- Herramientas locales controladas.
- Toolserver C como ejecutor productivo primario.
- Objetivos, planes, tareas, grafo de ejecución, scheduler secuencial, presupuestos, checkpoints lógicos, evaluación por evidencia y CLI de objetivos.

### 2.2 Fuera de alcance actual

No forman parte de Phase 4:

- UI web.
- TUI avanzada.
- Integraciones con Telegram u otras plataformas.
- Embeddings.
- RAG.
- Memoria semántica.
- Multiagente.
- Streaming.
- Plugins dinámicos.
- Sincronización entre dispositivos.
- Escritura autónoma.
- Reintentos, replanning, paralelismo y subagentes en ejecución autónoma.

La siguiente fase prevista es **Context & Knowledge Engine**. Su objetivo será reducir el trabajo del LLM principal transformando datos locales en conocimiento indexado, recuperable, versionado y compilable en contexto de alta relevancia.

---

## 3. Restricciones y supuestos

### 3.1 Plataforma

- Sistema operativo principal: Arch Linux.
- Python: 3.12 o superior.
- Ollama: proceso local.
- Transporte: HTTP local.
- Base URL predeterminada: `http://localhost:11434`.
- Persistencia inicial: SQLite.

### 3.2 Hardware de referencia

- VRAM: 6 GB.
- RAM: 64 GB.

Este hardware permite ejecutar modelos locales pequeños e intermedios, pero obliga a controlar:

- Tamaño del modelo.
- Cuantización.
- Ventana de contexto.
- Consumo de KV cache.
- Latencia.
- Descarga parcial de capas a RAM.

### 3.3 Perfiles de modelo

| Perfil | Modelo recomendado | Uso |
|---|---|---|
| development | Gemma 4 E2B Q4 | Desarrollo diario, smoke tests y validación rápida |
| validation | Gemma 4 E4B Q4 | Evaluación funcional y comportamiento |
| evaluation | Gemma 4 12B Q4 | Evaluación manual de calidad con descarga parcial a RAM |

El modelo exacto nunca debe estar codificado dentro del runtime.

Debe configurarse mediante:

```text
AI_ASSISTANT_MODEL
```

La guía operativa de perfiles vive en `docs/model-profiles.md`.

---

## 4. Principios arquitectónicos

### 4.1 Dependency Inversion

El runtime depende de abstracciones internas, no de implementaciones externas.

Ejemplo:

```text
AgentRuntime
    |
    v
ModelProvider
    ^
    |
OllamaModelProvider
OpenAICompatibleModelProvider
DummyModelProvider
```

### 4.2 Ports & Adapters

Los componentes externos se integran mediante adaptadores.

Adaptadores primarios:

- CLI.
- Futuras TUI.
- Futuras API HTTP.
- Futuros WebSockets.

Adaptadores secundarios:

- Ollama.
- OpenAI-compatible.
- SQLite.
- Memoria en memoria.
- Futuros ejecutores de herramientas.

### 4.3 Clean Architecture

La dirección de dependencias siempre apunta hacia el núcleo:

```text
interfaces -> application -> domain
infrastructure -> application ports
infrastructure -> domain
```

Nunca:

```text
domain -> sqlite
application -> ollama
application -> cli
```

### 4.4 Single Responsibility

Cada componente tiene una responsabilidad principal:

- Runtime: orquestar.
- ContextBuilder: construir contexto.
- ModelProvider: responder mediante un modelo.
- ConversationStore: persistir historial.
- CLI: recibir y mostrar datos.
- ToolCallInterpreter: interpretar tool calls.
- Bootstrap: ensamblar dependencias.

### 4.5 Framework Agnostic

El núcleo no depende de:

- LangChain.
- LangGraph.
- Semantic Kernel.
- SDK oficial de OpenAI.
- SDK oficial de Ollama.

La adopción futura de cualquiera de estas herramientas deberá realizarse mediante adaptadores.

### 4.6 Local-first

El sistema debe funcionar con:

- Modelo local.
- Persistencia local.
- Configuración local.
- CLI local.
- Sin servicios externos obligatorios.

---

## 5. Vista de contexto

```mermaid
flowchart LR
    User[Usuario] --> CLI[CLI]
    CLI --> Runtime[Agent Runtime]
    Runtime --> Memory[Conversation Store]
    Runtime --> Context[Context Builder]
    Runtime --> Model[Model Provider]
    Model --> Ollama[Ollama local]
    Memory --> SQLite[(SQLite)]
```

---

## 6. Arquitectura de alto nivel

```mermaid
flowchart TB
    subgraph Interfaces
        CLI[CLI Adapter]
        TUI[Future TUI]
        API[Future HTTP API]
    end

    subgraph Application
        Runtime[AgentRuntime / RespondToMessage]
        Engine[ExecutionEngine]
        Planner[ModelBackedPlanner]
        Validator[PlanValidator]
        Scheduler[TaskScheduler]
        Evaluator[ObjectiveEvaluator]
        ContextBuilder[ContextBuilder]
        ToolInterpreter[ToolCallInterpreter]
        Ports[Application Ports]
    end

    subgraph Domain
        Message[Message]
        SessionId[SessionId]
        ToolDefinition[ToolDefinition]
        ToolCall[ToolCall]
        Errors[Domain Errors]
    end

    subgraph Infrastructure
        SQLiteStore[SQLiteConversationStore]
        InMemoryStore[InMemoryConversationStore]
        DummyModel[DummyModelProvider]
        OllamaModel[OllamaModelProvider]
        OpenAIModel[OpenAICompatibleModelProvider]
        EnvConfig[Environment Config]
    end

    CLI --> Runtime
    TUI --> Runtime
    API --> Runtime

    Runtime --> ContextBuilder
    Runtime --> Ports
    Runtime --> ToolInterpreter
    Runtime --> Message
    Runtime --> SessionId
    CLI --> Engine
    Engine --> Planner
    Engine --> Validator
    Engine --> Scheduler
    Engine --> Evaluator
    Engine --> Ports

    SQLiteStore -. implements .-> Ports
    InMemoryStore -. implements .-> Ports
    DummyModel -. implements .-> Ports
    OllamaModel -. implements .-> Ports
    OpenAIModel -. implements .-> Ports

    EnvConfig --> Runtime
```

---

## 7. Capas

## 7.1 Domain

Contiene conceptos independientes de proveedores y persistencia.

### Responsabilidades

- Representar mensajes.
- Representar sesiones.
- Representar definiciones declarativas de herramientas.
- Representar tool calls tipados.
- Mantener invariantes.
- Definir errores del dominio.

### Dependencias permitidas

- Biblioteca estándar de Python.
- Otros módulos del dominio.

### Dependencias prohibidas

- SQLite.
- HTTP.
- Variables de entorno.
- CLI.
- Ollama.
- OpenAI.
- Logging de infraestructura.

---

## 7.2 Application

Contiene casos de uso y puertos.

### Responsabilidades

- Orquestar una petición.
- Leer historial.
- Construir contexto.
- Invocar el modelo.
- Interpretar tool calls.
- Persistir turnos completos.
- Devolver respuestas normalizadas.

### Dependencias permitidas

- Domain.
- Puertos definidos dentro de Application.

### Dependencias prohibidas

- Adaptadores concretos.
- SQLite.
- Ollama.
- `os.environ`.
- Impresión directa a consola.

---

## 7.3 Infrastructure

Implementa puertos.

### Responsabilidades

- Persistencia SQLite.
- Persistencia en memoria.
- Transporte HTTP.
- Adaptador Ollama nativo.
- Adaptador OpenAI-compatible.
- Configuración mediante variables de entorno.
- Logging técnico.

### Dependencias permitidas

- Domain.
- Puertos de Application.
- Biblioteca estándar.
- Dependencias externas mínimas y justificadas.

---

## 7.4 Interfaces

Contiene adaptadores de entrada.

### Responsabilidades

- Capturar entrada.
- Invocar casos de uso.
- Mostrar salida.
- Traducir errores internos a mensajes legibles.
- Manejar EOF, `exit`, `quit` y `Ctrl+C`.

### Dependencias permitidas

- Application.
- Domain.

### Dependencias prohibidas

- SQL directo.
- Construcción manual de requests de Ollama.
- Lectura directa del historial.
- Detección de tool calls.

---

## 7.5 Bootstrap

Es el composition root.

### Responsabilidades

- Cargar configuración.
- Construir adaptadores.
- Resolver proveedor.
- Construir runtime.
- Inyectar dependencias.
- Crear la aplicación CLI.

Bootstrap es el único módulo autorizado para conocer simultáneamente:

- Interfaces.
- Application.
- Domain.
- Infrastructure.

---

## 8. Módulos principales

## 8.1 `Message`

Dataclass inmutable.

Campos actuales o esperados:

```text
role
content
session_id optional
tool_name optional
tool_call_id optional
```

Responsabilidades:

- Validar contenido no vacío.
- Representar mensajes internos.
- Evitar formatos específicos de proveedores.

No debe:

- Serializar directamente requests de Ollama.
- Ejecutar herramientas.
- Consultar SQLite.

---

## 8.2 `SessionId`

Representa una sesión conversacional.

En Phase 1:

```text
type: string
default: "default"
persistent across executions: yes
interactive management: no
```

El sistema debe aceptar una sesión predeterminada configurable mediante:

```text
AI_ASSISTANT_SESSION
```

---

## 8.3 `ContextBuilder`

Orden de contexto:

1. Prompt de sistema.
2. Historial seleccionado.
3. Input actual.

Responsabilidades:

- Validar input.
- Construir la secuencia final.
- Aplicar una política simple de presupuesto de contexto.

Política inicial:

```text
1. Conservar system prompt.
2. Conservar mensaje actual.
3. Recorrer historial desde el más reciente.
4. Detenerse al alcanzar el límite configurado.
```

No debe:

- Consultar SQLite.
- Ejecutar resúmenes.
- Calcular embeddings.
- Depender de un proveedor.

---

## 8.4 `AgentRuntime`

Caso de uso principal.

Firma conceptual:

```text
respond(session_id, user_input) -> AgentResponse
```

Responsabilidades:

1. Validar solicitud.
2. Obtener historial.
3. Construir contexto.
4. Invocar modelo.
5. Interpretar respuesta.
6. Persistir turno.
7. Devolver resultado.

No debe:

- Construir SQL.
- Leer variables de entorno.
- Imprimir.
- Ejecutar herramientas.
- Interpretar JSON específico de Ollama.

---

## 8.5 `ModelProvider`

Puerto interno.

Contrato mínimo de Phase 1:

```text
chat(messages) -> Message
```

Implementaciones:

- `DummyModelProvider`.
- `OllamaModelProvider`.
- `OpenAICompatibleModelProvider`.

Extensiones futuras:

- Streaming.
- Structured output.
- Tool calling nativo.
- Multimodalidad.
- Métricas de uso.

Estas extensiones no deben incorporarse al contrato actual hasta que exista una necesidad concreta.

---

## 8.6 `ConversationStore`

Puerto interno.

Contrato recomendado:

```text
get_history(session_id) -> list[Message]
append(session_id, message) -> None
append_many(session_id, messages) -> None
clear(session_id) -> None
```

`append_many` debe ser transaccional.

---

## 8.7 `ToolDefinition`

Estructura declarativa:

```text
name
description
input_schema
```

Phase 1 no ejecuta herramientas.

---

## 8.8 `ToolCallInterpreter`

Responsabilidades:

- Detectar estructura explícita.
- Traducirla a `ToolCall`.
- Devolver un resultado tipado.
- No ejecutar.

---

## 8.9 `OllamaModelProvider`

Usa la API nativa de Ollama.

Endpoint principal:

```text
POST /api/chat
```

Request mínimo:

```json
{
  "model": "<configurable>",
  "messages": [],
  "stream": false
}
```

Responsabilidades:

- Traducir `Message` a formato Ollama.
- Realizar HTTP.
- Validar status.
- Parsear JSON.
- Traducir respuesta a `Message`.
- Normalizar errores.

No debe:

- Leer historial.
- Persistir.
- Imprimir.
- Decidir session ID.

---

## 8.10 `OpenAICompatibleModelProvider`

Debe permanecer separado del adaptador Ollama.

Ambos implementan el mismo puerto, pero usan contratos externos diferentes.

---

## 8.11 `ModelProviderFactory`

Responsabilidad:

- Seleccionar proveedor según configuración.

Valores esperados:

```text
dummy
ollama
openai-compatible
```

No debe imprimir el proveedor.

Debe generar un error de configuración ante valores desconocidos.

---

## 8.12 `ExecutionEngine`

Caso de uso principal de Phase 4.

Flujo:

```text
Objective -> Planner -> PlanValidator -> ExecutionGraph -> Scheduler -> ToolExecutionCoordinator -> Evaluator
```

Responsabilidades:

- Persistir objetivo, plan, ejecución, estados de tarea y checkpoints mediante `ExecutionStore`.
- Ejecutar una tarea lista a la vez.
- Enforzar presupuestos controlados por la plataforma.
- Usar `CapabilityRegistry` para mapear capacidades abstractas a herramientas aprobadas.
- Evaluar resultado con evidencia objetiva.
- Emitir logs metadata-only.

No debe:

- Importar adaptadores concretos de Ollama, SQLite, protobuf o toolserver C.
- Exponer `write`.
- Hacer retry, replanning, paralelismo o subagentes.
- Registrar prompts ni contenido de archivos.

---

## 8.13 Platform Domain

Modelos implementados:

- `Objective`
- `Plan`
- `PlatformTask`
- `ExecutionRecord`
- `ExecutionBudget`
- `BudgetUsage`
- `Checkpoint`
- `ExecutionResult`
- `EvaluationResult`

Los modelos validan transiciones e invariantes sin depender de SQLite, Ollama, CLI ni toolserver.

---

## 8.14 CapabilityRegistry

Mapea capacidades abstractas a herramientas aprobadas:

```text
InspectDirectory -> list_directory
ReadFile -> read_file
InspectFileMetadata -> file_metadata
SearchText -> search_text
InspectGitStatus -> git_status
InspectGitDiff -> git_diff
RunTests -> run_tests
BuildProject -> build_project
```

`write` queda excluida de ejecución autónoma. La ruta de escritura controlada de Phase 3 sigue disponible fuera de `ExecutionEngine`.

---

## 8.15 ExecutionStore

`SQLiteExecutionStore` persiste objetivos, planes, tareas, ejecuciones y checkpoints en una base dedicada:

```text
AI_ASSISTANT_EXECUTION_DATABASE=assistant_execution.sqlite3
```

Debe permanecer separado de:

- `ConversationStore`
- `AuditStore`

---

## 8.16 Context & Knowledge Engine

Phase 5 transforma datos locales en conocimiento derivado, indexado, recuperable, versionado y compilable en contexto de alta relevancia.

Debe respetar los límites existentes:

- No mezclar KnowledgeStore con ConversationStore, AuditStore o ExecutionStore.
- No ejecutar herramientas desde el motor de conocimiento sin pasar por políticas existentes.
- Mantener `EmbeddingProvider` separado de `ModelProvider`.
- Compilar contexto como entrada de alta señal para el LLM principal, no como sustituto de validación/evidencia.

M5.3 introduce únicamente modelos de dominio en `ai_assistant/knowledge/`:

- `KnowledgeDocument`
- `KnowledgeChunk`
- `KnowledgeSymbol`
- `KnowledgeQuery`
- `RetrievalCandidate`
- `ContextEvidence`
- `CompiledContext`
- `ContextBudget`

Estos modelos son inmutables, no dependen de infraestructura y validan frescura, provenance y presupuestos de contexto.

M5.4 agrega puertos abstractos en `ai_assistant/knowledge/ports.py`:

- `KnowledgeSource`
- `FileKnowledgeSource`
- `AdrKnowledgeSource`
- `ExecutionKnowledgeSource`
- `ConversationKnowledgeSource`

Estos puertos definen el contrato para listar documentos, cargar documentos, obtener chunks y obtener símbolos. No implementan adaptadores concretos ni acceden a stores canónicos.

M5.5 agrega `SQLiteKnowledgeStore` como base SQLite dedicada para estado derivado:

- Tabla `knowledge_documents` para documentos versionados con hash, metadata y frescura.
- Tabla `knowledge_chunks` para chunks ordenados por documento.
- Tabla `knowledge_symbols` para símbolos derivados asociados a documentos y chunks.
- Método `clear()` para permitir reconstrucción completa del store derivado.

Este store permanece separado de `ConversationStore`, `AuditStore` y `ExecutionStore`. No implementa FTS5, embeddings, invalidación incremental, adapters de fuentes ni compilación de contexto.

M5.6 agrega hashing e invalidación incremental mínima:

- `hash_text()` y `hash_bytes()` generan SHA-256 estable para contenido derivado.
- `document_is_current()` permite saltar fuentes sin cambios cuando versión y hash coinciden y el documento está fresco.
- `mark_document_stale()` invalida documento y chunks derivados.
- `mark_missing_documents_stale()` invalida documentos de una fuente que ya no aparecen en el conjunto activo.

La invalidación solo cambia frescura en `KnowledgeStore`; no elimina fuentes canónicas, no ejecuta adapters y no hace retrieval.

M5.7 agrega normalización y chunking determinista:

- `normalize_text()` normaliza saltos de línea, tabs, espacios finales y blancos repetidos.
- `chunk_document()` genera `KnowledgeChunk` con hash, ordinal, metadata de sección y presupuesto de tokens.
- Markdown se divide por headings.
- Python se divide por imports/prefijo de módulo y definiciones top-level `class`/`def` usando `ast`.
- Otros contenidos usan párrafos y fallback por palabras.

El chunking no lee archivos, no genera símbolos persistidos, no indexa FTS5 y no ejecuta retrieval.

M5.8 agrega metadata y símbolos derivados:

- `document_metadata()` conserva URI, tipo de fuente, versión, hash documental y lenguaje inferido.
- `infer_language()` usa extensiones conocidas sin dependencias externas.
- Los chunks incluyen metadata de provenance y, cuando aplica, `symbol_kind` / `symbol_name`.
- `symbols_for_chunks()` deriva `KnowledgeSymbol` desde chunks de Python y headings Markdown.

Los símbolos son derivados y reconstruibles. No se agregan parsers externos, FTS5, retrieval ni contexto compilado.

M5.9 agrega índice léxico local con SQLite FTS5:

- `knowledge_chunks_fts` indexa texto de chunks derivados.
- `lexical_search()` devuelve `RetrievalCandidate` con provenance de documento, chunk, versión y hash.
- La búsqueda excluye documentos/chunks stale.
- La búsqueda permite filtrar por `KnowledgeQuery.source_types` y `metadata_filters`.
- Las consultas se envían como frase escapada para evitar errores por sintaxis FTS inválida.

FTS5 sigue siendo estado derivado y reconstruible. No agrega embeddings, ranking híbrido, CLI ni integración con planner/synthesis.

M5.10 agrega CLI manual para conocimiento:

```bash
AI_ASSISTANT_WORKSPACE="$PWD" python main.py knowledge status
AI_ASSISTANT_WORKSPACE="$PWD" python main.py knowledge index README.md
AI_ASSISTANT_WORKSPACE="$PWD" python main.py knowledge rebuild docs
AI_ASSISTANT_WORKSPACE="$PWD" python main.py knowledge query blacksmith
```

La base se configura con:

```text
AI_ASSISTANT_KNOWLEDGE_DATABASE=assistant_knowledge.sqlite3
```

`index` y `rebuild` leen rutas relativas al workspace, deniegan rutas ocultas/sensibles y respetan `AI_ASSISTANT_MAX_READ_BYTES`. La CLI no es automática, no observa cambios en background y no integra resultados al runtime del agente.

M5.11 agrega el contrato de embeddings:

- `EmbeddingVector` conserva hash de texto, valores, provider, modelo y versión.
- `EmbeddingProvider` es un puerto separado de `ModelProvider`.
- `DummyEmbeddingProvider` genera vectores locales deterministas con CPU y sin dependencias externas.

No se persisten embeddings todavía, no se calcula similitud y no se integra retrieval semántico; eso queda para M5.12+.

M5.12 agrega almacenamiento local de embeddings y similitud CPU:

- `knowledge_embeddings` persiste vectores por chunk, provider, modelo, versión y dimensión.
- `save_embedding()` y `embeddings_for_chunk()` administran vectores derivados.
- `semantic_search()` calcula similitud coseno en CPU y devuelve `RetrievalCandidate` con provenance.
- La búsqueda semántica solo compara embeddings con provider/model/version/dimension compatible.
- Documentos/chunks stale quedan excluidos.

La búsqueda sigue siendo O(n) sobre SQLite para mantener el diseño local y simple. No se agrega base vectorial externa, retrieval híbrido, ranking avanzado ni contexto compilado.

M5.13 agrega `HybridRetriever`:

- Combina resultados lexicales FTS5, símbolos y semantic search.
- Deduplica por `chunk_id`.
- Excluye candidatos stale.
- Respeta `KnowledgeQuery.limit` y filtros de source type.
- Fusiona el método de retrieval cuando varias rutas encuentran el mismo chunk.

El orden actual es determinista por score y `chunk_id`; el ranking con componentes inspectables queda para M5.14.

M5.14 agrega `KnowledgeRanker`:

- Calcula `RankedCandidate` con `total_score` y componentes inspectables.
- Usa componentes deterministas `base` y `method`.
- Aplica pesos fijos por método (`symbol`, `fts5`, `semantic`).
- Excluye candidatos stale.
- Desempata de forma estable por `source_uri` y `chunk_id`.

No usa LLM reranker, no compila contexto y no modifica el `HybridRetriever` todavía.

M5.15 agrega `ContextCompiler`:

- Convierte `RankedCandidate` en `CompiledContext`.
- Carga texto desde `KnowledgeStore` y verifica provenance contra `content_hash` y `token_count`.
- Rechaza conocimiento stale o no verificable.
- Respeta `ContextBudget` de tokens, fuentes, chunks y tokens por chunk.
- Omite candidatos que exceden presupuesto sin relajar límites.

El compilador es puro sobre `KnowledgeStore`; no integra planner, synthesis ni runtime.

M5.16 integra contexto en el planner:

- `PlanningContextProvider` arma contexto de planificación desde `HybridRetriever`, `KnowledgeRanker` y `ContextCompiler`.
- `ModelBackedPlanner` recibe contexto opcional y lo envía al modelo como `compiled_context` estructurado.
- El planner sigue validando JSON no confiable con el contrato existente.
- La integración se cablea en el objective engine, no en el loop conversacional general.

No se integra synthesis ni se inyecta contexto automáticamente en `python main.py` sin subcomando `objective`.

M5.17 integra contexto en síntesis de objetivos:

- `SynthesisContextProvider` recupera contexto con la descripción del objetivo y compila `SYNTHESIS`.
- `ExecutionEngine` agrega observaciones contextuales al `ExecutionResult`.
- La evidencia no se modifica, por lo que `ObjectiveEvaluator` sigue usando solo evidencia y estados de tareas.
- La integración se mantiene en objective execution, no en el runtime conversacional general.

No se agregan métricas ni se relaja el criterio de evaluación.

M5.18 agrega observabilidad mínima de eficiencia:

- `ContextMetrics` registra candidatos recuperados, candidatos rankeados, chunks seleccionados, tokens estimados fuente, tokens compilados y `context_reduction_ratio`.
- `PlanningContextProvider` y `SynthesisContextProvider` exponen `last_metrics` y registran una línea de log por compilación de contexto.
- Las métricas son derivadas y efímeras; no crean un store nuevo ni modifican fuentes canónicas.
- No se agregan métricas de cache ni `tool_calls_avoided` porque aún no existe cache productivo ni contador causal de herramientas evitadas.

M5.19 agrega cobertura adversarial de seguridad, frescura y regresión:

- La CLI de conocimiento rechaza rutas hidden, rutas sensibles, archivos sobredimensionados y documentos no UTF-8 con errores explícitos.
- Las pruebas cubren limpieza/rebuild de `KnowledgeStore`, chunks duplicados, resultados stale léxicos y semánticos, mismatch de provenance y overflow de `ContextBudget`.
- La validación incluye pruebas de regresión de runtime, políticas de tools y execution engine de fases anteriores.

M5.20 agrega evaluación funcional manual:

- `python main.py objective --metrics "..."` muestra duración, llamadas de modelo/herramientas y métricas de contexto de planning/synthesis.
- `ExecutionEngine` mide duración total en `BudgetUsage.duration_seconds`.
- La guía `docs/phase5-functional-evaluation.md` define los escenarios para explicar por qué `ExecutionEngine` no escribe y diagnosticar fallos de scheduler.

M5.21 cierra la documentación de Phase 5:

- README, arquitectura, contexto del proyecto y guías operativas reflejan el estado implementado.
- Phase 5 queda lista para revisión humana final, no aceptada automáticamente.
- Las exclusiones siguen vigentes: memoria semántica de usuario, automatic skills, MCP, watcher daemon, network retrieval y vector DB externo.

---

## 9. Estructura recomendada del repositorio

```text
ai_assistant/
├── domain/
│   ├── __init__.py
│   ├── message.py
│   ├── session.py
│   ├── tools.py
│   └── errors.py
│
├── application/
│   ├── __init__.py
│   ├── runtime.py
│   ├── context.py
│   ├── tool_calls.py
│   └── ports/
│       ├── __init__.py
│       ├── models.py
│       ├── memory.py
│       └── tools.py
│
├── infrastructure/
│   ├── __init__.py
│   ├── models/
│   │   ├── dummy.py
│   │   ├── ollama.py
│   │   ├── openai_compatible.py
│   │   └── factory.py
│   ├── persistence/
│   │   ├── in_memory_conversation.py
│   │   └── sqlite_conversation.py
│   ├── http/
│   │   └── urllib_transport.py
│   └── config/
│       ├── settings.py
│       └── environment.py
│
├── interfaces/
│   ├── __init__.py
│   └── cli/
│       └── app.py
│
├── bootstrap/
│   ├── __init__.py
│   └── container.py
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── contract/
│   ├── smoke/
│   └── fakes/
│
├── docs/
│   ├── architecture.md
│   └── adr/
│
├── main.py
├── pyproject.toml
├── pytest.ini
├── .gitignore
└── README.md
```

---

## 10. Dependencias permitidas

La estructura por capas ya existe en el repositorio:

- `ai_assistant/domain/`: mensajes, sesiones, errores y modelos declarativos de herramientas.
- `ai_assistant/application/`: runtime, context builder, tool-call interpreter y puertos.
- `ai_assistant/infrastructure/`: adaptadores de modelo y stores de memoria.
- `ai_assistant/interfaces/`: CLI como adaptador primario.
- `ai_assistant/bootstrap/`: composition root.

Los paquetes `ai_assistant/agent/`, `ai_assistant/cli/` y
`ai_assistant/storage/` permanecen como fachadas de compatibilidad durante
Phase 1.

| Origen | Domain | Application | Infrastructure | Interfaces |
|---|---:|---:|---:|---:|
| Domain | Sí | No | No | No |
| Application | Sí | Sí | No | No |
| Infrastructure | Sí | Solo puertos | Sí | No |
| Interfaces | Sí | Sí | No idealmente | Sí |
| Bootstrap | Sí | Sí | Sí | Sí |

---

## 11. Flujo completo de una petición

```mermaid
sequenceDiagram
    actor User
    participant CLI
    participant Runtime
    participant Store
    participant Context
    participant Model
    participant Ollama

    User->>CLI: Texto
    CLI->>Runtime: respond(session_id, input)
    Runtime->>Store: get_history(session_id)
    Store-->>Runtime: list[Message]
    Runtime->>Context: build(system_prompt, history, input)
    Context-->>Runtime: messages
    Runtime->>Model: chat(messages)
    Model->>Ollama: POST /api/chat
    Ollama-->>Model: JSON response
    Model-->>Runtime: Message
    Runtime->>Store: append_many(user, assistant)
    Store-->>Runtime: success
    Runtime-->>CLI: AgentResponse
    CLI-->>User: respuesta
```

---

## 12. Persistencia

### 12.1 Esquema mínimo

```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    tool_name TEXT,
    tool_call_id TEXT,
    created_at TEXT NOT NULL
);
```

Índice:

```sql
CREATE INDEX idx_messages_session_id_id
ON messages(session_id, id);
```

### 12.2 Reglas

- El historial se filtra por `session_id`.
- El orden definitivo se basa en `id`.
- El turno usuario-asistente se persiste en una transacción.
- Si el modelo falla, no se persiste un turno incompleto.
- La base local no se incluye en Git.

---

## 13. Configuración

Fuente principal:

```text
Variables de entorno
```

Variables:

```text
AI_ASSISTANT_PROVIDER=ollama
AI_ASSISTANT_MODEL=<installed-ollama-tag>
AI_ASSISTANT_BASE_URL=http://localhost:11434
AI_ASSISTANT_DATABASE=assistant.sqlite3
AI_ASSISTANT_SESSION=default
AI_ASSISTANT_SYSTEM_PROMPT=...
AI_ASSISTANT_LOG_LEVEL=INFO
AI_ASSISTANT_REQUEST_TIMEOUT=120
AI_ASSISTANT_CONTEXT_LIMIT=4096
```

Precedencia futura:

```text
CLI args > environment > defaults
```

Phase 1 no requiere `.env`, TOML ni frameworks de configuración.

---

## 14. Logging

Biblioteca:

```text
logging
```

Salida:

```text
stderr
```

Nivel predeterminado:

```text
INFO
```

Campos recomendados:

- Provider.
- Model.
- Session ID.
- Duración.
- Estado.
- Cantidad de mensajes.
- Tipo de error.

No registrar por defecto:

- API keys.
- Prompts completos.
- Respuestas completas.
- Variables de entorno completas.
- Cuerpos HTTP completos.

---

## 15. Manejo de errores

Errores internos recomendados:

```text
ConfigurationError
ModelConnectionError
ModelNotFoundError
ModelTimeoutError
ModelProtocolError
ConversationStoreError
InvalidMessageError
InvalidSessionError
InvalidToolCallError
```

Mapeo:

```text
Ollama no disponible -> ModelConnectionError
Modelo ausente -> ModelNotFoundError
Timeout -> ModelTimeoutError
JSON inválido -> ModelProtocolError
Respuesta sin mensaje -> ModelProtocolError
SQLite error -> ConversationStoreError
```

La CLI traduce estos errores a mensajes legibles.

---

## 16. Estrategia de pruebas

Framework:

```text
pytest
```

Marcadores:

```text
unit
integration
contract
ollama
smoke
```

### Unitarias

- Runtime.
- ContextBuilder.
- Sesiones.
- Factoría.
- Mapeo de mensajes.
- Manejo de errores.

### Integración

- SQLite temporal.
- Persistencia por sesión.
- Transacciones.
- Reapertura.

### Contrato

#### Ollama nativo

- Request `/api/chat`.
- `stream=false`.
- Respuesta válida.
- Error HTTP.
- Timeout.
- JSON inválido.
- Modelo no instalado.

#### OpenAI-compatible

- Request compatible.
- Response compatible.
- Errores.
- Timeout.

### Smoke

- CLI con Dummy.
- CLI con Ollama.

### CI

Jobs recomendados:

```text
unit
integration
contract
ollama-smoke
```

Ollama real debe ejecutarse en un job separado.

---

## 17. Seguridad local-first

Phase 1 debe garantizar:

- No registrar secretos.
- No enviar datos a proveedores externos por defecto.
- No ejecutar herramientas.
- No ejecutar shell.
- No abrir puertos de red.
- No almacenar credenciales en SQLite.
- No incluir la base local en Git.

Futuras herramientas deberán incorporar:

- Lista de permisos.
- Confirmación.
- Sandbox.
- Timeouts.
- Límites de recursos.
- Auditoría.
- Separación por proceso.

---

## 18. Puntos de extensión

### Modelos

```text
ModelProvider
```

### Memoria conversacional

```text
ConversationStore
```

### Memoria semántica futura

```text
MemoryRetriever
MemoryWriter
```

### Herramientas futuras

```text
ToolCatalog
ToolCallInterpreter
ToolPolicy
ToolExecutor
```

## 18.1 Phase 2 Read-Only Tool Policy

Phase 2 is limited to read-only workspace inspection through exactly two productive tools:

- `list_directory`
- `read_file`

The model may request a tool, but authorization is deterministic application policy. Productive execution is implemented through application ports and concrete read-only executors.

Implemented invariants:

- deny by default;
- no shell, process execution, Git execution, network access or writes;
- all paths are relative to `AI_ASSISTANT_WORKSPACE`;
- external absolute paths, traversal, external symlinks, hidden paths, sensitive paths and special files are denied;
- default and hard limits are enforced for timeout, bytes, directory entries, recursion depth, path length, request payload and response payload;
- every allow, deny, success, timeout and failure outcome is audited with sanitized metadata;
- prompts, model responses and file contents are not stored in audit or logs;
- `read_file` decodes bounded bytes as UTF-8 with replacement for invalid binary sequences;
- the runtime may perform at most one tool execution round per user turn.

Implemented adapters:

- `LocalReadOnlyToolExecutor` for direct local filesystem reads after authorization.
- `UnixSocketToolExecutor` for authorized requests sent to the C toolserver over Unix domain sockets.
- C toolserver actions for `list_directory` and `read_file`, with independent path and limit validation.

The implemented ADR package is:

- ADR-016 Safe Tool Execution Pipeline
- ADR-017 Deny-by-Default Tool Policy
- ADR-018 Read-Only Tool Allowlist
- ADR-019 Workspace Confinement and Path Resolution
- ADR-020 Tool Execution Audit and Retention
- ADR-021 Tool Timeouts and Resource Limits
- ADR-022 Unix Socket Tool Executor
- ADR-023 Error and Log Redaction
- ADR-024 Bounded Single Tool Round per Turn
- ADR-025 Sensitive File Deny Policy

## 18.2 Phase 3 Controlled Development Tools

Phase 3 extends the same tool pipeline with controlled development tools while preserving deny-by-default, workspace confinement, sanitized audit and one bounded tool round per user turn.

Productive Phase 3 tools:

- `file_metadata`
- `search_text`
- `git_status`
- `git_diff`
- `run_tests`
- `build_project`
- `write`

The C toolserver is the primary productive executor. Python remains responsible for model interaction, static catalog lookup, permission derivation, policy, path prevalidation, confirmation, coordination and audit. The C process repeats critical validation before filesystem, Git or process access.

Permission and confirmation model:

| Permission | Tools | Confirmation |
|---|---|---|
| `READ_METADATA` | `file_metadata` | no |
| `READ_CONTENT` | `search_text` | no |
| `READ_REPOSITORY` | `git_status`, `git_diff` | no |
| `EXECUTE_PROJECT` | `run_tests`, `build_project` | first use |
| `WRITE_WORKSPACE` | `write` | first use |

Confirmation grants are in-memory and scoped to `session_id + workspace_id + permission`. EOF, timeout, prompt error or any answer other than literal `yes` denies the request.

Implemented safeguards:

- no model-controlled permissions;
- no dynamic tools or model-defined profiles;
- no shell, arbitrary argv, package installation or network tools;
- process tools use fixed approved profiles with controlled environment, timeout and bounded output;
- `search_text` uses bounded literal `rg` search and redacts sensitive previews;
- Git tools are read-only, bounded and disable pager/hooks/external diff behavior;
- `write` supports only bounded UTF-8 `create` and `replace`;
- writes are workspace-confined, hidden/sensitive paths and external symlinks are denied;
- C writes use temp file, flush and atomic rename with optional `expected_sha256`;
- audit stores metadata and hashes, never full file content;
- audit retention is implemented through an operator-only manual purge API with dry-run and confirmation.

Implemented ADR package:

- ADR-026 Controlled Development Tool Allowlist
- ADR-027 Permission Levels and Confirmation Grants
- ADR-028 C Toolserver as Primary Executor
- ADR-029 Preconfigured Test and Build Profiles
- ADR-030 Controlled Workspace Write Semantics
- ADR-031 Atomic Writes and Optimistic Concurrency
- ADR-032 Git Read-Only Inspection
- ADR-033 Search Text Limits and Redaction
- ADR-034 Audit Retention and Manual Purge
- ADR-035 Process Output, Timeout and Environment Limits

### Interfaces

```text
CLI
TUI
HTTP API
WebSocket
Desktop
```

### Transporte

```text
UrllibHttpTransport
Future HttpxTransport
Future UnixSocketTransport
```

---

## 19. Decisiones inmediatas

Deben completarse en Phase 1:

1. Separar capas.
2. Formalizar puertos.
3. Introducir sesiones.
4. Crear composition root.
5. Centralizar configuración.
6. Implementar Ollama nativo.
7. Migrar a pytest.
8. Normalizar errores.
9. Añadir logging.
10. Definir herramientas declarativas sin ejecución.

---

## 20. Decisiones pospuestas

- Streaming.
- Multiagente.
- RAG.
- Embeddings.
- Memoria semántica.
- Ejecución de herramientas.
- Servidor C.
- Plugins dinámicos.
- UI web.
- TUI avanzada.
- Sincronización.
- Cifrado.
- Scheduler.
- Background jobs.

---

## 21. ADR recomendados

```text
ADR-001 Ports and Adapters
ADR-002 Python Core
ADR-003 Internal Message Model
ADR-004 SQLite Persistence
ADR-005 Explicit Sessions
ADR-006 ModelProvider Port
ADR-007 Configuration at Bootstrap
ADR-008 Declarative Tools Only
ADR-009 No Agent Framework
ADR-010 Transactional Turn Persistence
ADR-011 Native Ollama Adapter
ADR-012 Minimal External Dependencies
ADR-013 Pytest Testing Strategy
ADR-014 Non-streaming Phase 1
ADR-015 Model Profiles for Limited Hardware
```
