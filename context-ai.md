# Contexto del Proyecto AI Assistant

## Fin del proyecto

Construir un asistente de IA local-first, modular, seguro y extensible. El core de Python coordina el runtime del agente, memoria, configuración, proveedores de modelo y CLI. La ejecución de herramientas de bajo nivel queda separada y fuera de Phase 1.

## Estado actual

Phase 1: Python Core está implementada y lista para revisión final.

Incluye:

- CLI mínima con `python main.py`.
- Runtime framework-agnostic.
- Modelo interno `Message` neutral al proveedor.
- Context builder con presupuesto simple.
- Puertos explícitos para modelo y memoria.
- Providers `dummy`, Ollama nativo y OpenAI-compatible.
- Memoria en memoria y persistencia SQLite transaccional.
- Sesiones explícitas.
- Configuración centralizada en bootstrap.
- Logging básico.
- Errores internos tipados.
- Tool calls declarativos sin ejecución.
- Pytest con marcadores separados.
- CI separado para core y Ollama smoke.
- Arquitectura por capas.
- ADRs de Phase 1 documentados.

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

## Ejecución

```bash
python main.py
```

Por defecto usa `AI_ASSISTANT_PROVIDER=dummy`. Para Ollama:

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

## Limitaciones conocidas

- No hay ejecución de herramientas.
- No hay embeddings, RAG ni memoria semántica.
- No hay streaming.
- No hay UI fuera de CLI.
- El servicio C de herramientas existe como trabajo separado, no integrado productivamente al runtime.
- Los paquetes `agent`, `cli` y `storage` son fachadas de compatibilidad.

## Mejoras recomendadas

1. Remover fachadas legacy cuando se acepte romper imports antiguos.
2. Diseñar Phase 2 alrededor de `ToolExecutor`, permisos y confirmación humana.
3. Definir política de auditoría antes de ejecutar herramientas.
4. Añadir migraciones explícitas si el esquema SQLite crece.
5. Medir latencia y memoria con perfiles reales de Ollama antes de elegir defaults más pesados.
