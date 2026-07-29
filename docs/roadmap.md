# Roadmap

## 1. Objetivo

Construir un asistente de IA local-first con un núcleo Python modular, desacoplado y preparado para evolucionar hacia herramientas, interfaces adicionales y componentes de alto rendimiento.

Fase actual:

```text
Phase 1: Python Core
```

Este roadmap no introduce capacidades que pertenezcan a fases futuras antes de estabilizar:

- Runtime.
- Modelos.
- Contexto.
- Sesiones.
- Persistencia.
- Configuración.
- CLI.
- Pruebas.
- Logging.
- Manejo de errores.

---

## 2. Convenciones

### Tamaño

| Tamaño | Significado |
|---|---|
| S | Cambio pequeño y aislado |
| M | Cambio moderado con varias piezas |
| L | Cambio estructural |

### Estado

```text
[ ] Pendiente
[x] Completado
[-] Fuera de alcance
```

### Estructura de cada hito

Cada hito contiene:

- Objetivo.
- Motivación.
- Alcance.
- Fuera de alcance.
- Dependencias.
- Tareas.
- Criterios de aceptación.
- Pruebas.
- Riesgos.
- Resultado verificable.
- Commit sugerido.

---

# Phase 1: Python Core

## Milestone 1 — Higiene del repositorio

**Tamaño:** S

### Objetivo

Eliminar artefactos generados y ruido de depuración.

### Motivación

El repositorio contiene archivos que no deben versionarse y salida accidental en CLI.

### Alcance

- `.gitignore`.
- `__pycache__`.
- SQLite local.
- `print(config.provider)`.

### Fuera de alcance

- Refactor arquitectónico.
- Sesiones.
- Ollama.

### Tareas

- [ ] Eliminar `print(config.provider)`.
- [ ] Ignorar `__pycache__/`.
- [ ] Ignorar `*.pyc`.
- [ ] Ignorar `assistant.sqlite3`.
- [ ] Ignorar bases locales equivalentes.
- [ ] Retirar artefactos ya trackeados.
- [ ] Ejecutar suite existente.
- [ ] Ejecutar CLI con DummyModel.

### Criterios de aceptación

- La CLI no imprime información de depuración.
- La base local no aparece en Git.
- `__pycache__` no aparece en Git.
- El DummyModel sigue funcionando.

### Pruebas

```bash
python -m unittest discover -s tests
python main.py
```

### Riesgos

- Eliminar accidentalmente una base usada como fixture.

### Resultado verificable

Repositorio limpio y comportamiento sin cambios.

### Commit sugerido

```text
chore(repo): remove generated artifacts and debug output
```

---

## Milestone 2 — Migración a pytest

**Tamaño:** M

### Objetivo

Migrar la suite actual desde `unittest` a `pytest`.

### Motivación

Pytest facilitará fixtures, parametrización, marcadores y pruebas de integración con Ollama.

### Alcance

- Dependencia de desarrollo.
- Conversión de pruebas.
- Marcadores.
- Fixtures temporales.

### Fuera de alcance

- Pruebas Ollama reales.
- CI completo.

### Tareas

- [ ] Añadir pytest como dependencia de desarrollo.
- [ ] Crear `pytest.ini` o configuración equivalente.
- [ ] Migrar pruebas del runtime.
- [ ] Migrar pruebas de contexto.
- [ ] Migrar pruebas de SQLite.
- [ ] Migrar pruebas de factoría.
- [ ] Migrar pruebas de sockets existentes.
- [ ] Añadir fixtures temporales.
- [ ] Añadir marcadores base.

### Marcadores

```text
unit
integration
contract
ollama
smoke
```

### Criterios de aceptación

- Todas las pruebas existentes pasan con pytest.
- No depende de Ollama.
- SQLite usa archivos temporales.

### Pruebas

```bash
pytest
pytest -m unit
```

### Riesgos

- Diferencias en lifecycle entre `unittest` y pytest.
- Fixtures compartidas con estado.

### Resultado verificable

Suite ejecutable mediante pytest.

### Commit sugerido

```text
test(pytest): migrate core test suite
```

---

## Milestone 3 — Sesiones explícitas

**Tamaño:** M

### Objetivo

Separar conversaciones mediante `session_id`.

### Motivación

La memoria actual funciona como una conversación global.

### Alcance

- `session_id` string.
- Sesión CLI predeterminada.
- Persistencia entre ejecuciones.
- Filtrado SQLite.
- Store en memoria.

### Fuera de alcance

- Gestión interactiva de sesiones.
- Listado.
- Renombrado.
- Archivado.
- Eliminación avanzada.

### Tareas

- [ ] Definir `SessionId`.
- [ ] Actualizar contrato del store.
- [ ] Actualizar store en memoria.
- [ ] Añadir `session_id` a SQLite.
- [ ] Añadir índice por sesión.
- [ ] Filtrar historial.
- [ ] Mantener sesión `default`.
- [ ] Configurar `AI_ASSISTANT_SESSION`.
- [ ] Añadir pruebas de aislamiento.
- [ ] Añadir pruebas de persistencia entre ejecuciones.

### Criterios de aceptación

- Dos sesiones no comparten historial.
- La CLI usa `default`.
- Reiniciar la CLI conserva historial.
- El orden se mantiene.

### Pruebas

```bash
pytest -m unit
pytest -m integration
```

### Riesgos

- Migración de bases existentes.
- Duplicación accidental del mensaje actual.

### Resultado verificable

Memoria conversacional aislada por sesión.

### Commit sugerido

```text
feat(memory): add persistent conversation sessions
```

---

## Milestone 4 — Persistencia transaccional

**Tamaño:** S

### Objetivo

Persistir cada turno usuario-asistente de forma atómica.

### Motivación

Evitar turnos incompletos si ocurre un fallo entre escrituras.

### Alcance

- `append_many`.
- Transacción SQLite.
- Rollback ante error.

### Fuera de alcance

- WAL avanzado.
- Replicación.
- Locking distribuido.

### Tareas

- [ ] Añadir `append_many`.
- [ ] Implementar transacción SQLite.
- [ ] Implementar equivalente en memoria.
- [ ] Actualizar runtime.
- [ ] Añadir pruebas de rollback.

### Criterios de aceptación

- Usuario y asistente se escriben juntos.
- Ante error, ninguno queda persistido.
- El orden se conserva.

### Pruebas

```bash
pytest -m integration
```

### Riesgos

- Dobles commits.
- Transacciones anidadas.

### Resultado verificable

Historial consistente.

### Commit sugerido

```text
feat(storage): persist conversation turns atomically
```

---

## Milestone 5 — Puertos explícitos

**Tamaño:** M

### Objetivo

Formalizar dependencias internas.

### Motivación

Evitar acoplamiento entre runtime e infraestructura.

### Alcance

- `ModelProvider`.
- `ConversationStore`.
- Contratos tipados.
- Fakes para tests.

### Fuera de alcance

- Plugin system.
- DI framework.

### Tareas

- [ ] Crear `application/ports/models.py`.
- [ ] Crear `application/ports/memory.py`.
- [ ] Mover o adaptar interfaces actuales.
- [ ] Actualizar runtime.
- [ ] Crear fake model.
- [ ] Crear fake store.
- [ ] Añadir pruebas de contrato básicas.

### Criterios de aceptación

- Runtime no importa SQLite.
- Runtime no importa Ollama.
- Runtime no importa OpenAI.
- Tests del runtime usan fakes.

### Pruebas

```bash
pytest -m unit
```

### Riesgos

- Abstracciones demasiado generales.
- Cambios de importación amplios.

### Resultado verificable

Runtime desacoplado.

### Commit sugerido

```text
refactor(core): formalize model and memory ports
```

---

## Milestone 6 — Composition root

**Tamaño:** M

### Objetivo

Centralizar construcción e inyección de dependencias.

### Motivación

La CLI no debe actuar como contenedor de dependencias.

### Alcance

- `bootstrap/container.py`.
- Construcción de runtime.
- Selección de adaptadores.
- Configuración inyectada.

### Fuera de alcance

- Framework de DI.
- Descubrimiento dinámico.

### Tareas

- [ ] Crear `create_application`.
- [ ] Mover construcción desde CLI.
- [ ] Inyectar store.
- [ ] Inyectar provider.
- [ ] Inyectar context builder.
- [ ] Inyectar tool interpreter.
- [ ] Mantener `python main.py`.

### Criterios de aceptación

- `main.py` solo inicia la aplicación.
- CLI no importa adaptadores concretos.
- Tests pueden construir runtime con fakes.

### Pruebas

```bash
pytest -m unit
python main.py
```

### Riesgos

- Importaciones circulares.

### Resultado verificable

Grafo de dependencias explícito.

### Commit sugerido

```text
refactor(bootstrap): add explicit composition root
```

---

## Milestone 7 — Configuración centralizada

**Tamaño:** M

### Objetivo

Concentrar variables de entorno en un objeto inmutable.

### Motivación

Evitar lecturas dispersas de `os.environ`.

### Alcance

- Dataclass `AppConfig`.
- Defaults.
- Validación.
- Variables de entorno.

### Variables

```text
AI_ASSISTANT_PROVIDER
AI_ASSISTANT_MODEL
AI_ASSISTANT_BASE_URL
AI_ASSISTANT_DATABASE
AI_ASSISTANT_SESSION
AI_ASSISTANT_SYSTEM_PROMPT
AI_ASSISTANT_LOG_LEVEL
AI_ASSISTANT_REQUEST_TIMEOUT
AI_ASSISTANT_CONTEXT_LIMIT
```

### Fuera de alcance

- `.env`.
- TOML.
- YAML.
- Pydantic Settings.

### Tareas

- [ ] Crear `AppConfig`.
- [ ] Crear loader desde environment.
- [ ] Añadir defaults.
- [ ] Validar provider.
- [ ] Validar timeout.
- [ ] Validar context limit.
- [ ] Añadir tests.
- [ ] Eliminar lecturas dispersas.

### Criterios de aceptación

- Configuración se carga una vez.
- Errores inválidos son claros.
- El runtime no usa `os.environ`.

### Pruebas

```bash
pytest -m unit
```

### Riesgos

- Defaults inconsistentes.
- Variables heredadas en tests.

### Resultado verificable

Configuración predecible.

### Commit sugerido

```text
feat(config): centralize environment settings
```

---

## Milestone 8 — Logging básico

**Tamaño:** S

### Objetivo

Añadir logging técnico sin exponer datos sensibles.

### Motivación

Sustituir prints y facilitar diagnóstico.

### Alcance

- `logging`.
- stderr.
- nivel configurable.
- eventos del runtime y adaptadores.

### Fuera de alcance

- Logging JSON.
- Archivos rotativos.
- Telemetría.
- Trazas distribuidas.

### Tareas

- [ ] Configurar logging en bootstrap.
- [ ] Añadir log de provider.
- [ ] Añadir log de modelo.
- [ ] Añadir duración de requests.
- [ ] Añadir errores.
- [ ] Evitar contenido completo.
- [ ] Añadir pruebas básicas.

### Criterios de aceptación

- No existen prints técnicos.
- Nivel configurable.
- No se registran secretos.
- La CLI mantiene salida limpia.

### Pruebas

```bash
pytest -m unit
```

### Riesgos

- Duplicación de handlers.
- Logs de contenido sensible.

### Resultado verificable

Diagnóstico básico seguro.

### Commit sugerido

```text
feat(logging): add configurable runtime logging
```

---

## Milestone 9 — Errores internos tipados

**Tamaño:** M

### Objetivo

Normalizar errores de modelos, configuración y persistencia.

### Motivación

Evitar que la CLI dependa de excepciones externas.

### Alcance

- Jerarquía mínima.
- Mapeo.
- Mensajes CLI.

### Errores

```text
ConfigurationError
ModelConnectionError
ModelNotFoundError
ModelTimeoutError
ModelProtocolError
ConversationStoreError
InvalidMessageError
InvalidSessionError
```

### Tareas

- [ ] Definir errores.
- [ ] Mapear SQLite.
- [ ] Mapear HTTP.
- [ ] Mapear JSON inválido.
- [ ] Mapear modelo ausente.
- [ ] Traducir en CLI.
- [ ] Añadir pruebas.

### Criterios de aceptación

- CLI no muestra traceback en errores esperados.
- Tests validan tipo de error.
- Errores técnicos quedan en logs.

### Pruebas

```bash
pytest -m unit
pytest -m contract
```

### Riesgos

- Ocultar información útil.
- Jerarquía demasiado amplia.

### Resultado verificable

Errores consistentes.

### Commit sugerido

```text
feat(errors): normalize infrastructure failures
```

---

## Milestone 10 — Adaptador Ollama nativo

**Tamaño:** L

### Objetivo

Integrar Ollama mediante su API nativa.

### Motivación

Las primeras pruebas reales se realizarán con Ollama local.

### Alcance

- `/api/chat`.
- `stream=false`.
- Modelo configurable.
- Timeout.
- Mapeo.
- Errores.
- HTTP local.

### Fuera de alcance

- Streaming.
- Tool execution.
- Multimodalidad.
- Descarga automática de modelos.
- Gestión del daemon Ollama.

### Tareas

- [ ] Crear `OllamaModelProvider`.
- [ ] Implementar request mapper.
- [ ] Implementar response mapper.
- [ ] Usar `urllib.request`.
- [ ] Añadir timeout.
- [ ] Añadir `stream=false`.
- [ ] Traducir mensajes.
- [ ] Detectar respuesta vacía.
- [ ] Detectar modelo ausente.
- [ ] Detectar servicio no disponible.
- [ ] Registrar duración.
- [ ] Añadir pruebas unitarias.
- [ ] Añadir pruebas de contrato simuladas.
- [ ] Añadir integración real opcional.

### Request mínimo

```json
{
  "model": "<AI_ASSISTANT_MODEL>",
  "messages": [],
  "stream": false
}
```

### Criterios de aceptación

- CLI responde con Ollama.
- Modelo se selecciona por variable.
- Servicio caído genera error tipado.
- Modelo inexistente genera error tipado.
- Tests unitarios no requieren Ollama.

### Pruebas

```bash
pytest -m unit
pytest -m contract
pytest -m ollama
```

### Riesgos

- Cambios de contrato.
- Timeouts altos.
- Diferencias entre modelos.

### Resultado verificable

Proveedor Ollama operativo.

### Commit sugerido

```text
feat(ollama): add native chat provider
```

---

## Milestone 11 — Perfiles de modelo

**Tamaño:** S

### Objetivo

Documentar y configurar perfiles compatibles con 6 GB VRAM y 64 GB RAM.

### Motivación

Evitar modelos demasiado grandes como defaults.

### Perfiles

```text
development -> Gemma 4 E2B Q4
validation -> Gemma 4 E4B Q4
evaluation -> Gemma 4 12B Q4
```

### Alcance

- Documentación.
- Defaults recomendados.
- Context limit.
- Smoke tests.

### Fuera de alcance

- Selección automática según GPU.
- Benchmark framework.
- Autodescarga.
- Perfilado avanzado.

### Tareas

- [ ] Documentar perfiles.
- [ ] Definir modelo de desarrollo.
- [ ] Definir contexto 4096.
- [ ] Permitir 8192 mediante configuración.
- [ ] Añadir guía de evaluación.
- [ ] Registrar modelo activo.

### Criterios de aceptación

- El proyecto no fija un modelo en código.
- El default documentado es adecuado al hardware.
- Contexto es configurable.

### Pruebas

```bash
pytest -m smoke
```

### Riesgos

- Tags de Ollama distintos.
- Diferencias de cuantización.

### Resultado verificable

Configuración reproducible.

### Commit sugerido

```text
docs(models): define local hardware profiles
```

---

## Milestone 12 — Context budget

**Tamaño:** M

### Objetivo

Limitar historial enviado al modelo.

### Motivación

El KV cache y el contexto afectan VRAM y latencia.

### Alcance

- Límite configurable.
- Conservación de system prompt.
- Conservación de input actual.
- Selección desde mensajes recientes.

### Fuera de alcance

- Tokenizer exacto por proveedor.
- Resumen.
- Embeddings.
- Memoria semántica.

### Tareas

- [ ] Añadir `AI_ASSISTANT_CONTEXT_LIMIT`.
- [ ] Definir política simple.
- [ ] Preservar system prompt.
- [ ] Preservar input actual.
- [ ] Recorrer historial reciente.
- [ ] Añadir pruebas de orden.
- [ ] Añadir pruebas de truncamiento.

### Criterios de aceptación

- Contexto no crece sin límite.
- Mensaje actual siempre se conserva.
- Historial reciente tiene prioridad.

### Pruebas

```bash
pytest -m unit
```

### Riesgos

- Estimación aproximada.
- Cortar contexto relevante.

### Resultado verificable

Consumo de contexto controlado.

### Commit sugerido

```text
feat(context): add configurable history budget
```

---

## Milestone 13 — Adaptador OpenAI-compatible robusto

**Tamaño:** M

### Objetivo

Consolidar el adaptador existente como proveedor independiente.

### Motivación

Mantener compatibilidad con futuros proveedores.

### Alcance

- Request mapper.
- Response mapper.
- Errores.
- Timeout.
- Contrato simulado.

### Fuera de alcance

- SDK oficial.
- Streaming.
- Tools.
- Multimodalidad.

### Tareas

- [ ] Separar mapeo.
- [ ] Eliminar supuestos Ollama.
- [ ] Añadir tests de request.
- [ ] Añadir tests de response.
- [ ] Añadir timeout.
- [ ] Normalizar errores.
- [ ] Verificar provider factory.

### Criterios de aceptación

- Ollama y OpenAI-compatible son adaptadores separados.
- Ambos implementan el mismo puerto.
- Unit tests no usan red.

### Pruebas

```bash
pytest -m contract
```

### Riesgos

- Diferencias entre APIs compatibles.

### Resultado verificable

Segundo proveedor estable.

### Commit sugerido

```text
refactor(models): harden openai-compatible provider
```

---

## Milestone 14 — Herramientas declarativas

**Tamaño:** M

### Objetivo

Definir herramientas sin ejecutar efectos externos.

### Motivación

Preparar el runtime sin violar el alcance de Phase 1.

### Alcance

- `ToolDefinition`.
- `ToolCall`.
- `ToolCallInterpreter`.
- Plan tipado.

### Fuera de alcance

- `ToolExecutor`.
- Shell.
- Unix socket.
- Servidor C.
- Confirmaciones.

### Tareas

- [ ] Definir `ToolDefinition`.
- [ ] Definir `ToolCall`.
- [ ] Definir resultado de interpretación.
- [ ] Mejorar detector stub.
- [ ] Evitar ejecución.
- [ ] Añadir tests.

### Criterios de aceptación

- Runtime puede identificar una tool call.
- Ninguna herramienta se ejecuta.
- Respuesta contiene plan tipado.

### Pruebas

```bash
pytest -m unit
```

### Riesgos

- Acoplamiento a formatos de proveedor.
- Intentar soportar demasiado pronto múltiples herramientas.

### Resultado verificable

Contrato declarativo estable.

### Commit sugerido

```text
feat(tools): add declarative tool call model
```

---

## Milestone 15 — Reorganización por capas

**Tamaño:** L

### Objetivo

Alinear el repositorio con Domain, Application, Infrastructure, Interfaces y Bootstrap.

### Motivación

La estructura actual mezcla conceptos.

### Alcance

- Movimiento de archivos.
- Imports.
- Tests.
- Compatibilidad de `main.py`.

### Fuera de alcance

- Nuevas capacidades.
- Plugins.
- Frameworks.

### Tareas

- [ ] Crear `domain`.
- [ ] Crear `application`.
- [ ] Crear `infrastructure`.
- [ ] Crear `interfaces`.
- [ ] Crear `bootstrap`.
- [ ] Mover `Message`.
- [ ] Mover `ContextBuilder`.
- [ ] Mover runtime.
- [ ] Mover providers.
- [ ] Mover stores.
- [ ] Actualizar imports.
- [ ] Mantener tests verdes.
- [ ] Mantener CLI.

### Criterios de aceptación

- Domain no importa infraestructura.
- Application no importa adaptadores.
- CLI no construye dependencias.
- `python main.py` funciona.

### Pruebas

```bash
pytest
python main.py
```

### Riesgos

- Import cycles.
- Cambios grandes difíciles de revisar.

### Resultado verificable

Arquitectura visible en el repositorio.

### Commit sugerido

```text
refactor(architecture): separate core layers and adapters
```

---

## Milestone 16 — CI

**Tamaño:** M

### Objetivo

Automatizar pruebas.

### Jobs

```text
unit
integration
contract
ollama-smoke
```

### Alcance

- Python 3.12+.
- Pytest.
- SQLite.
- Ollama en job separado.

### Fuera de alcance

- GPU obligatoria.
- Modelos grandes.
- Benchmarks.

### Tareas

- [ ] Configurar entorno Python.
- [ ] Ejecutar unit.
- [ ] Ejecutar integration.
- [ ] Ejecutar contract.
- [ ] Instalar Ollama en job separado.
- [ ] Descargar modelo pequeño.
- [ ] Esperar disponibilidad.
- [ ] Ejecutar smoke.
- [ ] Cachear modelo si es viable.
- [ ] Publicar logs útiles.

### Criterios de aceptación

- Core no depende de Ollama.
- Ollama smoke es independiente.
- Fallos muestran causa clara.

### Pruebas

Pipeline completo.

### Riesgos

- Descargas lentas.
- Runners sin recursos.
- Inestabilidad del daemon.

### Resultado verificable

Validación reproducible.

### Commit sugerido

```text
ci(test): add core and ollama validation jobs
```

---

## Milestone 17 — Documentación y ADR

**Tamaño:** M

### Objetivo

Cerrar Phase 1 con decisiones explícitas.

### ADR

- [ ] ADR-001 Ports and Adapters.
- [ ] ADR-002 Python Core.
- [ ] ADR-003 Internal Message Model.
- [ ] ADR-004 SQLite Persistence.
- [ ] ADR-005 Explicit Sessions.
- [ ] ADR-006 ModelProvider Port.
- [ ] ADR-007 Configuration at Bootstrap.
- [ ] ADR-008 Declarative Tools Only.
- [ ] ADR-009 No Agent Framework.
- [ ] ADR-010 Transactional Turn Persistence.
- [ ] ADR-011 Native Ollama Adapter.
- [ ] ADR-012 Minimal External Dependencies.
- [ ] ADR-013 Pytest Strategy.
- [ ] ADR-014 Non-streaming Phase 1.
- [ ] ADR-015 Model Profiles.

### Tareas

- [ ] Actualizar README.
- [ ] Añadir diagrama.
- [ ] Documentar variables.
- [ ] Documentar pruebas.
- [ ] Documentar Ollama.
- [ ] Documentar limitaciones.
- [ ] Crear ADR.

### Criterios de aceptación

- Un nuevo desarrollador puede ejecutar el proyecto.
- Las decisiones están justificadas.
- El alcance futuro está separado.

### Resultado verificable

Phase 1 documentada.

### Commit sugerido

```text
docs(architecture): document phase one decisions
```

---

# Phase 1 Completion Criteria

La fase termina cuando:

```text
[ ] CLI ejecutable con python main.py
[ ] Dummy provider funcional
[ ] Ollama provider funcional
[ ] OpenAI-compatible provider estructuralmente estable
[ ] Sesiones persistentes
[ ] SQLite transaccional
[ ] Configuración centralizada
[ ] Logging básico
[ ] Errores tipados
[ ] Context budget
[ ] Herramientas declarativas sin ejecución
[ ] Pytest
[ ] CI separado
[ ] Arquitectura por capas
[ ] ADR documentados
[ ] Repositorio limpio
```

---

# Future Phases

## Phase 2 — Tool Execution Foundation

Objetivos futuros:

- `ToolExecutor`.
- Tool policy.
- Confirmación.
- Resultados.
- Timeout.
- Auditoría.

No iniciar hasta completar Phase 1.

## Phase 3 — Local Tool Service

Objetivos futuros:

- Proceso separado.
- Unix socket.
- Protocolo estable.
- Posible implementación en C.
- Autorización.

## Phase 4 — Additional Interfaces

Objetivos futuros:

- TUI.
- HTTP API.
- WebSocket.
- UI web.

## Phase 5 — Long-term Memory

Objetivos futuros:

- MemoryRetriever.
- MemoryWriter.
- Embeddings.
- RAG.
- Políticas de retención.

## Phase 6 — Advanced Agentic Runtime

Objetivos futuros:

- Tool loop.
- Planificación.
- Subagentes.
- Checkpoints.
- Reintentos.
- Cancelación.
- Streaming.
