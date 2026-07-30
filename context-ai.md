# Contexto del Proyecto AI Assistant

## Fin del proyecto

Construir un asistente de IA local-first, modular, seguro y extensible.

El core de Python coordina el runtime del agente, memoria, configuración, proveedores de modelo y CLI. Las herramientas y componentes de bajo nivel deben mantenerse detrás de puertos/adaptadores y no pueden ejecutar efectos externos sin política, permisos, confirmación y auditoría.

## Phase 1 finalizada

Phase 1: Python Core está implementada, validada y aprobada.

Validación final registrada:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -q
```

Resultado: 75 tests pasaron.

## Capacidades implementadas en Phase 1

- CLI mínima con `python main.py`.
- Runtime framework-agnostic.
- Modelo interno `Message` neutral al proveedor.
- Context builder con presupuesto simple.
- Puertos explícitos para modelo y memoria.
- Providers `dummy`, Ollama nativo y OpenAI-compatible.
- Memoria en memoria.
- Persistencia SQLite transaccional.
- Sesiones explícitas.
- Configuración centralizada en bootstrap.
- Logging básico.
- Errores internos tipados.
- Tool calls declarativos sin ejecución.
- Pytest con marcadores separados.
- CI separado para core y Ollama smoke.
- Arquitectura por capas.
- ADR-001 a ADR-015 documentados como `Implemented`.

## Estructura actual

```text
ai_assistant/
|-- domain/
|-- application/
|-- infrastructure/
|-- interfaces/
|-- bootstrap/
|-- agent/      # compatibility exports
|-- cli/        # compatibility exports
|-- storage/    # compatibility exports
|-- tools/
|-- gateway/
`-- main.py
```

Responsabilidades:

- `domain`: mensajes, sesiones, errores y modelos declarativos de herramientas.
- `application`: runtime, context builder, tool-call interpreter y puertos.
- `infrastructure`: adaptadores de modelo y stores.
- `interfaces`: CLI.
- `bootstrap`: composition root y carga de configuración.
- `agent`, `cli`, `storage`: fachadas de compatibilidad.

## Ejecución

```bash
python main.py
```

Por defecto usa `AI_ASSISTANT_PROVIDER=dummy`.

Ejemplo con Ollama:

```bash
AI_ASSISTANT_PROVIDER=ollama \
AI_ASSISTANT_MODEL=gemma3:1b \
AI_ASSISTANT_REQUEST_TIMEOUT=180 \
python main.py
```

## Validación

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -q
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m unit -q
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m integration -q
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m contract -q
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m smoke -q
```

Ollama real:

```bash
AI_ASSISTANT_MODEL=gemma3:1b \
AI_ASSISTANT_REQUEST_TIMEOUT=180 \
PYTHONDONTWRITEBYTECODE=1 python -m pytest -m ollama -q
```

## Datos disponibles para Phase 2

| Área | Dato disponible | Evidencia |
|---|---|---|
| Tool calls | `ToolDefinition`, `ToolCall`, `ToolCallPlan` | `ai_assistant/domain/tools.py` |
| Interpretación | Parser JSON explícito de `tool_call` sin ejecución | `ai_assistant/application/tool_calls.py` |
| Handoff runtime | `AgentRuntime.last_tool_plan` guarda el plan detectado | `ai_assistant/application/runtime.py` |
| Permisos | Enum protobuf `PermissionLevel` | `proto/toolserver.proto` |
| Resultados | `ToolStatus`, `ToolResponse`, `ToolError`, `ToolArtifact` | `proto/toolserver.proto` |
| Transporte | Cliente Unix socket con framing protobuf | `ai_assistant/tools/unix_socket_client.py` |
| Servicio C prototipo | Acciones `noop`, `echo`, `list_tools` | `c_toolserver/README.md` |
| Seguridad base | Phase 1 prohíbe ejecución de herramientas y shell | `docs/architecture.md`, ADR-008 |
| Tests | Marcadores `unit`, `integration`, `contract`, `ollama`, `smoke` | `pytest.ini` |

## Decisiones faltantes para Phase 2

No se debe ejecutar ninguna herramienta real hasta cerrar estas decisiones:

| Decisión faltante | Motivo |
|---|---|
| Herramientas iniciales permitidas | Evita abrir una superficie genérica de ejecución. Candidato mínimo: `noop`, `echo`, `list_tools`. |
| Política de permisos | Debe mapear herramienta -> permiso máximo -> comportamiento ante denegación. |
| Confirmación humana | Debe definir cuándo la CLI pide aprobación antes de ejecutar. |
| Esquema de auditoría | Phase 2 requiere registrar request ID, sesión, herramienta, permiso, dry-run, estado, timestamps y error sanitizado. |
| Timeouts por defecto | El proto soporta timeout, pero falta default del proyecto y overrides por herramienta. |
| Límite de workspace/filesystem | Necesario antes de cualquier herramienta con lectura/escritura de archivos. |
| Redacción de errores/logs | Evita filtrar secretos, prompts completos o datos sensibles en logs. |
| ADR de ejecución de herramientas | ADR-008 solo cubre Phase 1 sin ejecución; Phase 2 necesita una decisión nueva y aprobada. |

## Gates abiertos para Phase 2

Registrados en `.agent/human-review.md`:

- `PHASE2-G1`: aprobar política exacta de seguridad de ejecución.
- `PHASE2-G2`: aprobar scope inicial de herramientas y permisos.
- `PHASE2-G3`: aprobar auditoría y retención.

## Recomendación para el primer milestone de Phase 2

No conectar todavía la salida del modelo a ejecución real.

Primer milestone recomendado:

1. Crear ADR propuesto para política de ejecución de herramientas.
2. Añadir puertos de aplicación para `ToolCatalog`, `ToolPolicy` y `ToolExecutor`.
3. Implementar solo un executor fake/dry-run para tests.
4. Documentar contrato de confirmación CLI.
5. Validar comportamiento deny-by-default.

## Limitaciones actuales

- No hay ejecución de herramientas.
- No hay embeddings, RAG ni memoria semántica.
- No hay streaming.
- No hay UI fuera de CLI.
- El servicio C de herramientas no está integrado productivamente al runtime.
- Los paquetes `agent`, `cli` y `storage` son fachadas de compatibilidad.
