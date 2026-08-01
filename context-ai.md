# Contexto del Proyecto AI Assistant

## Fin del proyecto

Construir un asistente de IA local-first, modular, seguro y extensible.

El core de Python coordina runtime, memoria, configuración, modelos, CLI y herramientas. Todo sistema externo debe vivir detrás de puertos/adaptadores. Las herramientas productivas requieren política determinística, validación de paths, límites, auditoría y errores sanitizados.

## Estado actual

Phase 1 y Phase 2 están implementadas y listas para revisión final de Phase 2.

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

## Datos disponibles para Phase 3

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

## Decisiones faltantes para Phase 3

- Nuevas familias de herramientas productivas y sus permisos.
- Confirmaciones humanas interactivas para operaciones de mayor riesgo.
- Si el executor C será default o seguirá siendo opcional.
- Política de retención/exportación/borrado de auditoría.
- Búsqueda recursiva, Git, red, shell o escritura: requieren ADR/gate nuevo.
- UI/TUI/web, streaming, embeddings, RAG y multiagente siguen fuera del alcance actual.
