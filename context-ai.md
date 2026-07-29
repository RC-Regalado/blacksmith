# Contexto del Proyecto AI Assistant

## Fin del proyecto

Este proyecto busca construir un asistente de IA local-first, modular y extensible. La meta es separar claramente la orquestación del agente, los adaptadores de modelos, la memoria conversacional, la interfaz de entrada y la futura ejecución de herramientas.

La arquitectura apunta a que el runtime del agente no dependa de un proveedor específico de modelos, de una interfaz de usuario concreta ni de la implementación final de herramientas de bajo nivel.

## Alcance actual

Fase actual: **Phase 1: Python Core**.

El foco de esta fase es tener una base funcional en Python con:

- Gateway delgado.
- Runtime de agente framework-agnostic.
- Abstracción de mensajes.
- Constructor de contexto.
- Adaptador de modelo.
- Modelo dummy para pruebas locales.
- Adaptador OpenAI-compatible estructural.
- Memoria en memoria.
- Persistencia básica en SQLite.
- CLI mínima ejecutable con `python main.py`.

No forman parte de esta fase:

- UI web o frameworks visuales.
- Integraciones externas como Telegram.
- Ejecución real de herramientas.
- Embeddings.
- Servidor C de herramientas como implementación productiva.

## Estructura actual

```text
ai_assistant/
├── agent/
│   ├── context.py
│   ├── memory.py
│   ├── message.py
│   ├── planner.py
│   ├── runtime.py
│   └── models/
│       ├── adapter.py
│       ├── dummy.py
│       ├── openai_compatible.py
│       └── provider.py
├── cli/
│   └── app.py
├── gateway/
├── storage/
│   └── sqlite_memory.py
├── tools/
└── main.py
```

También existe un `main.py` en la raíz para ejecutar la CLI con:

```bash
python main.py
```

## Estado técnico actual

### Mensajes

`Message` es una dataclass inmutable con:

- `role`
- `content`
- campos opcionales para sesión y herramientas

Valida que el contenido no esté vacío.

### Contexto

`ContextBuilder` construye la lista de mensajes que recibe el modelo:

1. Prompt de sistema.
2. Historial.
3. Nuevo input del usuario.

Valida que el input del usuario no esté vacío.

### Runtime

`AgentRuntime.respond()` implementa el flujo mínimo:

1. Lee historial desde memoria.
2. Construye contexto.
3. Llama al modelo.
4. Persiste input del usuario y respuesta.
5. Ejecuta detección stub de tool calls.
6. Devuelve la respuesta.

La ejecución real de herramientas todavía no existe, correctamente para esta fase.

### Modelos

Existe una interfaz `ModelProvider` con:

```python
chat(self, messages: list[Message]) -> Message
```

Implementaciones actuales:

- `DummyModel`: responde con `Echo: ...`.
- `OpenAICompatibleModel`: estructura llamadas HTTP tipo OpenAI Responses API.
- `ModelAdapter`: selecciona proveedor por configuración o variables de entorno.

El proveedor por defecto actual es `dummy`, adecuado para desarrollo local sin API key.

### Memoria

Hay dos stores:

- `InMemoryConversationStore`
- `SQLiteConversationStore`

SQLite usa una tabla simple `messages` con:

- `id`
- `role`
- `content`
- `created_at`

No hay embeddings ni búsqueda semántica todavía.

### CLI

La CLI crea un runtime con:

- `ContextBuilder`
- `SQLiteConversationStore("assistant.sqlite3")`
- `ModelAdapter.from_env()`
- `ToolCallDetector`

Luego entra en un loop:

```text
> user input
assistant response
```

Sale con `exit`, `quit` o EOF.

## Tests actuales

Hay pruebas para:

- Runtime básico.
- Construcción de contexto.
- Persistencia SQLite.
- Selección de adaptador de modelo.
- Framing y cliente Unix socket existentes en el repo.

El último smoke test conocido del core Python pasó con:

```bash
python -m unittest discover -s tests
```

## Riesgos y deuda actual

- El repo tiene archivos `__pycache__` y `assistant.sqlite3` trackeados; deberían salir del control de versiones.
- `ModelAdapter.from_env()` imprime el proveedor con `print(config.provider)`, lo que ensucia la salida de la CLI.
- La tabla SQLite no registra `session_id`, `tool_name` ni `tool_call_id`, aunque `Message` ya tiene esos campos opcionales.
- La memoria SQLite no tiene separación de conversaciones/sesiones.
- El detector de tool calls es solo stub, como corresponde en Phase 1.
- El adaptador OpenAI-compatible tiene estructura inicial, pero no está cubierto con pruebas de red ni contrato completo.

## Mejoras recomendadas

1. Limpiar artefactos generados del repositorio:
   - Agregar o ajustar `.gitignore`.
   - Sacar `__pycache__/`.
   - Evitar commitear `assistant.sqlite3`.

2. Quitar el `print(config.provider)` de `ModelAdapter.from_env()`.

3. Añadir soporte básico de sesión en SQLite:
   - Persistir `session_id`.
   - Filtrar historial por sesión.
   - Mantener una sesión por defecto para la CLI.

4. Definir un formato declarativo mínimo para herramientas:
   - Nombre.
   - Descripción.
   - Schema de parámetros.
   - Sin ejecución todavía.

5. Mejorar el stub de tool calls:
   - Detectar estructura explícita.
   - Devolver un plan tipado.
   - No ejecutar herramientas desde el runtime.

6. Añadir configuración simple para CLI:
   - Proveedor.
   - Modelo.
   - Ruta de SQLite.
   - Prompt de sistema.

7. Mantener el runtime pequeño:
   - El runtime debe orquestar.
   - La memoria debe persistir.
   - El modelo debe responder.
   - Las herramientas deben vivir fuera del runtime.

## Próximo paso recomendado

El siguiente cambio más útil y pequeño es limpiar el ruido de desarrollo:

1. Quitar el `print()` del adaptador.
2. Ignorar `__pycache__` y bases SQLite locales.
3. Confirmar que la CLI sigue funcionando con `DummyModel`.

Después de eso, conviene agregar sesiones a SQLite antes de crecer memoria, herramientas o modelos.
