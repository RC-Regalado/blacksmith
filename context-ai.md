# Contexto del Proyecto AI Assistant

## Fin del proyecto

Construir un asistente de IA local-first, modular, seguro y extensible.

El core de Python coordina runtime, memoria, configuración, modelos, CLI y herramientas. Todo sistema externo debe vivir detrás de puertos/adaptadores. Las herramientas productivas requieren política determinística, validación de paths, límites, auditoría y errores sanitizados.

## Estado actual

Phase 1, Phase 2 y Phase 3 están implementadas y aceptadas por revisión manual.
Phase 4 está preparada con scaffolding inicial, pero no activa ejecución autónoma.

Phase 1 entregó el core Python:

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

Phase 2 entregó herramientas read-only:

- Allowlist productivo: `list_directory`, `read_file`.
- Política deny-by-default.
- Validación de workspace y paths relativos.
- Bloqueo de traversal, paths absolutos externos, symlinks externos, ocultos, sensibles y archivos especiales.
- Límites de timeout, bytes, entradas, profundidad, payload y respuesta.
- Auditoría SQLite sanitizada.
- `LocalReadOnlyToolExecutor`.
- `UnixSocketToolExecutor`.
- Toolserver C con acciones read-only.
- Un solo tool round por turno.
- Tests adversariales.

Phase 3 entregó herramientas de desarrollo controladas:

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

## Estructura actual

```text
ai_assistant/
|-- domain/
|-- application/
|-- infrastructure/
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

```bash
python main.py
```

Por defecto usa `AI_ASSISTANT_PROVIDER=dummy`.

Ejemplo con herramientas locales:

```bash
AI_ASSISTANT_TOOL_EXECUTION=true \
AI_ASSISTANT_WORKSPACE=/ruta/al/workspace \
python main.py
```

## Validación

Core sin Ollama ni C toolserver:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m "not ollama and not toolserver" -q
```

Suite completa en entorno con `protobuf-c`:

```bash
PKG_CONFIG_PATH=/home/rc-regalado/.local/lib/pkgconfig \
LD_LIBRARY_PATH=/home/rc-regalado/.local/lib \
PYTHONDONTWRITEBYTECODE=1 python -m pytest -q
```

Ollama real:

```bash
AI_ASSISTANT_MODEL=gemma3:1b \
AI_ASSISTANT_REQUEST_TIMEOUT=180 \
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m ollama -q
```

## ADRs

- ADR-001 a ADR-015: Phase 1 implementada.
- ADR-016 a ADR-025: Phase 2 implementada.
- ADR-026 a ADR-035: Phase 3 implementada.

## Datos disponibles para Phase 4

| Área | Evidencia |
|---|---|
| Tool domain models | `ai_assistant/domain/tools.py` |
| Application ports | `ai_assistant/application/ports/tools.py` |
| Static catalog | `ai_assistant/application/tool_catalog.py` |
| Deny-by-default policy | `ai_assistant/application/tool_policy.py` |
| Workspace path policy | `ai_assistant/application/path_policy.py` |
| Coordinator | `ai_assistant/application/tool_coordinator.py` |
| Audit store | `ai_assistant/infrastructure/storage/sqlite_audit.py` |
| Local executor | `ai_assistant/infrastructure/tools/local_read_only.py` |
| Unix socket executor | `ai_assistant/infrastructure/tools/unix_socket.py` |
| C toolserver | `c_toolserver/` |
| Adversarial tests | `tests/test_adversarial_security.py` |
| Phase 4 platform scaffolding | `ai_assistant/platform/` |
| Phase 4 capability roots | `ai_assistant/capabilities/` |

## Decisiones faltantes para Phase 4

- ADRs para objetivos, planes, tareas, ejecución, presupuestos, checkpoints, scheduler y evaluator.
- Si se habilitará `unrestricted_write`.
- Nuevas operaciones de filesystem: append, delete, move, rename, copy, mkdir.
- Nuevas familias de herramientas productivas y permisos.
- Persistencia de grants o revocación avanzada.
- Exportación/borrado avanzado de auditoría.
- Red, shell arbitrario, plugins dinámicos o ejecución multi-step: requieren ADR/gate nuevo.
- UI/TUI/web, streaming, embeddings, RAG y multiagente siguen fuera del alcance actual.

## Recomendaciones

- Mantener Phase 4 como ADR-first antes de conectar runtime, scheduler o capacidades.
- Reutilizar la política Phase 3 para cualquier capability nueva.
- No romper el límite de un tool round por turno sin aprobación explícita.
- Agregar perfiles fijos, no comandos arbitrarios, para cualquier build/test nuevo.
