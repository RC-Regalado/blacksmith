# Remediation Plan — Phase 5.2 Independent Adversarial Audit

Estado: OPEN — pendiente de aprobación humana para iniciar implementación. Ningún ítem de este
plan ha sido corregido todavía; este documento es la especificación de la corrección, no
evidencia de cierre.

Origen: auditoría adversarial independiente ejecutada el 2026-09-12 sobre `develop@9df190e`
(agente sin contexto de implementación previa, conforme a `AGENTS.md`). Veredicto de esa
auditoría: **NO-GO**. Este plan cubre los 5 bloqueantes y las 6 condiciones de alta severidad
que motivaron el veredicto.

Regla de gobernanza aplicable (`AGENTS.md`): la evidencia del repositorio prevalece sobre
cualquier documentación previa (ADRs marcados "Implemented", `.agent/reports/phase-5.2-final.md`,
la auditoría post-remediación anterior). Ningún hallazgo aquí fue aceptado por cita de esos
documentos; cada uno fue re-derivado y reproducido de forma independiente antes de incluirse.

## Trazabilidad

| ID | Título | Referencia de auditoría | Severidad |
|---|---|---|---|
| B-001 | Sensitive-path case bypass | BIAS-04 (+ BIAS-06 hard link) | CRITICAL |
| B-002 | Symlink protected-target write | BIAS-05 | CRITICAL |
| B-003 | Audit schema migration | BIAS-09 | CRITICAL |
| B-004 | Retrieval hardcoded project vocabulary | BIAS-01 | CRITICAL |
| B-005 | Tautological adversarial coverage | BIAS-10 | HIGH (gobernanza) |
| H-001 | Live-vs-knowledge paraphrase failure | BIAS-02 | HIGH |
| H-002 | Semantic retriever not actually wired | BIAS-03 | HIGH |
| H-003 | User text can trigger tool execution | BIAS-07 | HIGH |
| H-004 | Untrusted evidence inserted as trusted roles | BIAS-08 | HIGH |
| H-005 | Permission grant scope too broad | BIAS-17 | HIGH |
| H-006 | Redaction policy incorrect | BIAS-16 | HIGH |

Ningún ítem de este plan requiere una nueva familia de capacidad privilegiada, retrieval por
red/MCP, memoria semántica externa o clasificación basada en LLM para una decisión de política.
Donde una corrección ingenua tentaría a usar alguna de esas rutas, se marca explícitamente como
atajo prohibido en el ítem correspondiente.

---

# REMEDIATION PLAN

## B-001 Sensitive-path case bypass

- **invariant**: ningún nombre de archivo sensible (claves privadas, certificados, credenciales,
  archivos `.env`) es legible ni escribible sin importar la capitalización de su nombre o
  extensión.
- **exploit path**: `ID_RSA` (mayúsculas de `id_rsa`), `server.PEM`, `cert.Key` son aceptados y
  leídos. Reproducido contra el binario real del toolserver C: `read_file` sobre `ID_RSA` devolvió
  el contenido completo de la clave privada de prueba.
- **root cause**: `ai_assistant/application/path_policy.py:32-44,109` usa `fnmatchcase`
  (case-sensitive) contra una lista de patrones en minúsculas; `c_toolserver/src/actions.c`
  (`is_sensitive_name`) usa `strncmp`, también case-sensitive; `ai_assistant/infrastructure/
  sanitization.py:62` repite el mismo patrón. Las tres capas comparten la misma regla incorrecta,
  por lo que no hay defensa en profundidad real sobre este eje.
- **affected components**: `application/path_policy.py`, `c_toolserver/src/actions.c`
  (`is_sensitive_name`), `infrastructure/sanitization.py`.
- **proposed enforcement point**: normalizar (case-fold) el nombre de archivo y la extensión
  *antes* de la comparación contra la lista de patrones sensibles, en las tres implementaciones,
  usando una única función/constante de normalización reutilizada por Python y como referencia de
  paridad para C.
- **prohibited shortcuts**: no agregar variantes en mayúsculas a la lista de patrones (`*.PEM`,
  `*.Key`, ...) — eso es un parche que no cierra el espacio de casos (mixtos, unicode
  case-folding). No corregir solo la capa Python dejando la capa C divergente; ambas deben
  aplicar la misma normalización o la paridad declarada entre capas es falsa.
- **adversarial tests**: casos con mayúsculas, minúsculas y mezcla para cada patrón sensible
  existente (`*.pem`, `*.key`, `*.p12`, `*.pfx`, `id_rsa`, `id_ed25519`, `credentials.json`,
  `secrets.*`, `*.kubeconfig`, `.env`, `.env.*`), ejecutados contra: (a) `WorkspacePathPolicy` en
  Python, (b) el binario C real vía el executor `unix_socket` (no solo un mock), (c) el layer de
  sanitización de logs/auditoría.
- **closure evidence**: los tres tests anteriores en verde contra el binario C real (no solo
  contra un stub), más una corrida de `tests/test_adversarial_security.py` actualizada con estos
  casos, más confirmación explícita de que `MANDATORY_CASES` ("sensitive file") referencia ahora
  un test que cubre variantes de capitalización (ver B-005 para el problema estructural de ese
  archivo).

## B-002 Symlink protected-target write

- **invariant**: ninguna escritura puede terminar, directa o indirectamente vía symlink interno
  del workspace, fuera del árbol de rutas permitido; y el registro de auditoría de toda escritura
  refleja la ruta real donde ocurrió el efecto, no la ruta solicitada.
- **exploit path**: con `docs/gitdir -> ../.git` (symlink *dentro* del workspace apuntando a
  `.git/`), escribir en `docs/gitdir/pwned.txt` resultó en escritura real dentro de `.git/`.
  Reproducido contra el binario C real: el archivo apareció en `.git/pwned.txt` en el filesystem.
  El payload de éxito devuelto reporta `"path":"docs/gitdir/pwned.txt"` — la ruta señuelo, no la
  ruta real.
- **root cause**: `_validate_write` en `application/path_policy.py:132-166` valida los componentes
  de la ruta solicitada (no la resuelta) para el caso "archivo aún no existente", solo resuelve el
  padre para verificar contención dentro del workspace, y devuelve `resolved_path=str(target)`
  (la ruta *sin resolver*). `c_toolserver/src/actions.c` (`resolve_write_target`) repite la misma
  omisión. El path de lectura sí revalida componentes sobre la ruta resuelta
  (`path_policy.py:67-69`); el de escritura no — de ahí la asimetría.
- **affected components**: `application/path_policy.py` (`_validate_write`),
  `c_toolserver/src/actions.c` (`resolve_write_target`), el registro de auditoría que consume
  `resolved_path`.
- **proposed enforcement point**: `_validate_write` debe aplicar `_require_allowed_components`
  sobre `parent.relative_to(workspace)` **después** de resolver symlinks (no antes), y debe
  devolver el `resolved_path` real (post-resolución), nunca la ruta solicitada. `
  resolve_write_target` en C debe aplicar la misma revalidación sobre el padre resuelto. El
  registro de auditoría debe persistir siempre el `resolved_path` efectivo.
- **prohibited shortcuts**: no bloquear solo symlinks que apuntan *fuera* del workspace (eso ya
  existe y no cubre este caso) — el enforcement debe ser sobre componentes de ruta resuelta,
  simétrico al que ya existe para lectura. No "arreglar" solo registrando ambas rutas en el audit
  sin bloquear la escritura; el objetivo es impedir la escritura, no solo documentarla mejor.
- **adversarial tests**: symlink interno del workspace apuntando a `.git/`, a otro directorio
  sensible declarado, y a un ancestro del propio workspace; verificar denial tanto en Python como
  en el binario C real; verificar que, para cualquier escritura aceptada, el valor persistido en
  auditoría sea bit-a-bit la ruta resuelta real.
- **closure evidence**: los tests anteriores en verde contra el binario C real; inspección manual
  del filesystem tras cada intento de escritura maliciosa confirmando que no se materializó fuera
  del árbol permitido; verificación de que el finding B-005 (tests tautológicos) no pueda ocultar
  una regresión futura de este caso — el test para esto no puede ser un patrón de nombre-de-caso
  estático.

## B-003 Audit schema migration

- **invariant**: abrir una base de datos de auditoría creada por una versión anterior del sistema
  nunca debe romper la ejecución de herramientas; el esquema se actualiza (o se detecta y reporta)
  de forma explícita, nunca implícita vía `CREATE TABLE IF NOT EXISTS`.
- **exploit path**: reproducido contra la base de auditoría real y pre-Phase-5.2 del propio
  proyecto (`old/assistant_audit.sqlite3`, 178 filas): `_initialize()` no falla (es un no-op sobre
  tabla existente), pero el primer `record()` posterior falla con `OperationalError: table
  tool_audit_events has no column named interaction_id`. Como `ToolExecutionCoordinator.execute()`
  llama a `self._audit.record(...)` antes de `self._execute(context)` y sin capturar la excepción,
  **toda ejecución de herramientas queda inhabilitada de forma permanente** en cualquier
  instalación actualizada desde antes de ADR-070.
- **root cause**: `infrastructure/storage/sqlite_audit.py::_initialize` no implementa ninguna
  migración de esquema (ni `ALTER TABLE`, ni `PRAGMA user_version`, ni verificación de columnas
  existentes) — es el único store de persistencia del proyecto sin esa lógica (`sqlite_memory.py`
  sí la tiene).
- **affected components**: `infrastructure/storage/sqlite_audit.py`; potencialmente los demás
  stores SQLite (`assistant.sqlite3`, `assistant_knowledge.sqlite3`) deben auditarse con el mismo
  criterio aunque no se haya reproducido fallo en ellos todavía.
- **proposed enforcement point**: introducir un mecanismo de versión de esquema (`PRAGMA
  user_version` o tabla de metadata dedicada) en `sqlite_audit.py`, con una migración explícita
  que agregue `interaction_id` (con valor por defecto nulo/vacío para filas preexistentes) cuando
  se detecta una base en versión anterior. La migración debe ser idempotente y no destructiva.
- **prohibited shortcuts**: no resolver esto recreando o vaciando la base en caso de desajuste de
  esquema — eso destruye el historial de auditoría, que es append-only por diseño y es la fuente
  de verdad para revisión de seguridad. No silenciar la excepción de `record()` con un
  try/except que descarte el evento — el fallo debe seguir siendo fail-closed, pero la causa
  (esquema desactualizado) debe resolverse con migración, no con supresión.
- **adversarial tests**: fixture con una copia del esquema pre-ADR-070 (16 columnas menos
  `interaction_id`) cargada con filas reales o sintéticas; verificar que `_initialize()` migra el
  esquema y que `record()` subsiguiente tiene éxito sin pérdida de filas preexistentes; verificar
  idempotencia ejecutando la migración dos veces sobre la misma base.
- **closure evidence**: el test de migración anterior en verde; corrida exitosa de un flujo de
  herramientas completo contra una copia de `old/assistant_audit.sqlite3` migrada, confirmando
  que las 178 filas preexistentes siguen legibles y que nuevos eventos se insertan correctamente.

## B-004 Retrieval hardcoded project vocabulary

- **invariant**: una consulta de resumen/propósito general del proyecto en lenguaje natural debe
  recuperar los documentos de nivel superior del corpus indexado, para cualquier corpus y para
  cualquier formulación semánticamente equivalente de la pregunta — no solo para la frase exacta
  reportada como bug.
- **exploit path**: `ai_assistant/knowledge/conversation.py:11` define
  `_PROJECT_SUMMARY_TERMS = "AI Assistant README project proyecto arquitectura contexto Context
  Knowledge Engine"`, un literal con el nombre y vocabulario propio de este proyecto. Se expande
  vía OR-join en la consulta FTS solo cuando el texto contiene `{project|proyecto}` +
  `{what|que|hace|does}` sin palabras de estado-vivo. Verificado: `¿Que hace este proyecto?`
  (la frase original del bug) obtiene candidatos; `What does this repository do?`,
  `¿De qué trata este repo?`, `Dame un resumen del proyecto` y variantes similares obtienen
  `candidates=0`. Contra un corpus neutral de prueba (no este repositorio), la misma frase
  original también obtiene `candidates=0` — el fix no generaliza fuera de este repositorio.
- **root cause**: la corrección de M5.2.16-R1 codificó el síntoma reportado (una frase, este
  corpus) en vez del invariante (recuperación de documentos de resumen por estructura/tipo de
  fuente). El propio criterio de éxito citado en el cierre de fase (`candidates=12
  ranked=12 selected=12`) es producido por el mismo mecanismo que se está cuestionando —no es
  evidencia independiente.
- **affected components**: `ai_assistant/knowledge/conversation.py`
  (`_conversation_query`, `_PROJECT_SUMMARY_TERMS`), `ai_assistant/knowledge/ranking.py`
  (`KnowledgeRanker`, que no aplica piso mínimo de score).
- **proposed enforcement point**: eliminar `_PROJECT_SUMMARY_TERMS`. Si se requiere que consultas
  de resumen general funcionen, el invariante debe implementarse a nivel de ranking/selección de
  documentos por metadata estructural del corpus (p. ej. priorizar documentos raíz o de tipo
  `readme`/`overview` cuando la intención detectada es "resumen general"), nunca por lista de
  términos de un proyecto específico. Agregar un piso mínimo de relevancia en `KnowledgeRanker`
  para que "no se encontró score suficiente" sea distinguible de "se encontraron chunks
  irrelevantes".
- **prohibited shortcuts**: no ampliar la lista de términos hardcodeados con más idiomas o
  sinónimos — eso reproduce el mismo defecto a mayor escala. No introducir un clasificador basado
  en LLM para detectar "es una pregunta de resumen del proyecto" — viola la restricción de
  `AGENTS.md` de que la detección determinista nunca es LLM-based, y aquí aplicaría al mismo
  principio de políticas de retrieval. No usar retrieval por red/embeddings externos como atajo
  (prohibido por `AGENTS.md`: sin MCP/retrieval por red).
- **adversarial tests**: batería de paráfrasis en español e inglés semánticamente equivalentes a
  "¿qué hace este proyecto?" ejecutada contra (a) el índice real de este repositorio y (b) un
  corpus neutral de 3+ documentos sin relación con este proyecto; el criterio de aceptación es
  recall consistente en ambos casos, no solo en (a).
- **closure evidence**: la batería anterior con recall aceptable y sin métrica de éxito derivada
  del propio mecanismo bajo prueba; confirmación de que `candidates>0` deja de usarse como proxy
  único de "retrieval funcionó" — debe acompañarse de un score mínimo o de evidencia de que el
  chunk es relevante al tipo de pregunta.

## B-005 Tautological adversarial coverage

- **invariant**: una aserción de "cobertura adversarial obligatoria completa" debe depender de la
  existencia real de tests que ejercen el comportamiento correspondiente, no de la igualdad entre
  dos listas literales definidas en el mismo archivo.
- **exploit path**: `tests/test_adversarial_security.py` define `MANDATORY_CASES` y una variable
  local `covered`, ambas como sets literales en el mismo archivo, y afirma `covered ==
  MANDATORY_CASES`. Esta aserción es verdadera por construcción y no verifica nada sobre el
  código bajo prueba. El caso `"sensitive file"` está declarado como cubierto en este mecanismo,
  pero B-001 demuestra que el comportamiento real que ese nombre pretende representar tiene un
  bypass no detectado por el test real asociado.
- **root cause**: el mecanismo de "cobertura obligatoria" fue implementado como una lista de
  strings mantenida a mano en paralelo a los tests reales, sin ningún vínculo estructural entre
  ambos (ni introspección de tests colectados, ni fixtures compartidas, ni IDs referenciados).
- **affected components**: `tests/test_adversarial_security.py`
  (`test_m2_15_mandatory_cases_have_automated_coverage` y el test equivalente `test_m3_17_*`).
- **proposed enforcement point**: reemplazar la comparación de sets literales por introspección
  real de los tests efectivamente recolectados por pytest (p. ej. vía marcadores/IDs de test que
  referencien el caso obligatorio correspondiente, verificados con `pytest --collect-only` o un
  mecanismo equivalente), de forma que el test falle si el test real que cubre un caso obligatorio
  se elimina, se desactiva, o dejó de ejercer el comportamiento correspondiente.
- **prohibited shortcuts**: no agregar más casos a la lista `MANDATORY_CASES`/`covered` sin
  cambiar el mecanismo de verificación — eso perpetúa la misma falsa sensación de cobertura a
  mayor escala. No eliminar el test sin reemplazo — la intención original (tener una lista
  explícita de casos adversariales obligatorios) es válida y debe conservarse, solo el mecanismo
  de verificación es el defecto.
- **adversarial tests**: un caso de prueba meta que, deliberadamente, desactive o debilite un test
  real cubierto por `MANDATORY_CASES` (p. ej. comentando la aserción de `test_sensitive_file_*`) y
  confirme que el nuevo mecanismo de cobertura efectivamente falla ante esa regresión — a
  diferencia del mecanismo actual, que no la detectaría.
- **closure evidence**: el test meta anterior en verde (detecta la regresión simulada); reemplazo
  documentado de la comparación de sets literales; y opcionalmente, una nota en el propio archivo
  explicando por qué la comparación de listas planas no es suficiente, para que la reintroducción
  del patrón sea reconocible en revisión de código.

---

# HIGH CONDITIONS

## H-001 Live-vs-knowledge paraphrase failure

- **Hallazgo**: `_is_live_state()` en `ai_assistant/knowledge/retrieval_policy.py:6-31,56` decide
  si una consulta debe evitar retrieval (por tratarse de estado vivo del repositorio) exigiendo
  intersección no vacía entre la consulta y dos sets de palabras fijos (6 y 24 palabras). 9 de 10
  paráfrasis reales de "¿tengo cambios sin commitear?" fallan a enrutar correctamente (retrieval
  permitido cuando debería bloquearse), y 5 de 5 preguntas de arquitectura sobre tests/build son
  bloqueadas incorrectamente. El test que valida esta política (
  `tests/test_conversation_retrieval_policy.py`) usa exactamente las palabras de los sets como
  input, por lo que no puede detectar el problema.
- **root cause**: enrutamiento por intersección léxica fija en vez de por una decisión de
  capacidad/intención genuinamente robusta a paráfrasis.
- **proposed remediation**: rediseñar la política de enrutamiento vivo-vs-conocimiento como una
  decisión determinista pero no puramente léxica — p. ej. ampliar el vocabulario de forma
  sistemática (stemming/lematización determinista, no basada en LLM) y/o cambiar el criterio de
  "estado vivo" de intersección de palabras a un conjunto de patrones/intents estructurados
  versionados y testeados contra una batería de paráfrasis real, no contra el propio vocabulario
  de la implementación.
- **prohibited shortcuts**: no usar un clasificador LLM para esta decisión (prohibido por
  `AGENTS.md`: duplicate/progress y decisiones de política determinista nunca son LLM-based, y el
  mismo principio aplica aquí). No ampliar los sets de palabras ad hoc sin una batería de
  paráfrasis independiente que los valide.
- **acceptance evidence**: batería de paráfrasis (español/inglés) construida sin mirar el código
  de la política, con tasa de acierto documentada en ambas direcciones (falsos negativos y falsos
  positivos), reemplazando o complementando el test actual que reutiliza el vocabulario de la
  implementación.

## H-002 Semantic retriever not actually wired

- **Hallazgo**: `HybridRetriever` se construye sin `EmbeddingProvider` real en producción
  (`bootstrap/container.py:66,186`); `_semantic_search` devuelve `()` siempre. El único
  `EmbeddingProvider` existente (`infrastructure/embeddings/dummy.py`) es un hash SHA-256 sin
  propiedades semánticas. ADR-051/ADR-052 están marcados "Implemented" pero el componente que
  describen no está conectado. Adicionalmente, `_symbol_search` exige que la consulta completa
  sea substring de `"{symbol.name} {symbol.kind}"`, lo que lo inutiliza para preguntas de más de
  una palabra.
- **root cause**: la separación de puertos (ADR-052) se implementó correctamente a nivel de
  interfaz, pero ningún adapter real fue conectado en el contenedor de bootstrap; el estado
  "Implemented" del ADR no refleja que la capacidad esté activa en producción.
- **proposed remediation**: decidir explícitamente una de dos rutas y documentarla como tal: (a)
  implementar y conectar un `EmbeddingProvider` real que opere localmente (sin llamadas de red,
  conforme a la restricción de `AGENTS.md`), o (b) si no se justifica en este momento, corregir el
  estado de ADR-051/ADR-052 para reflejar que la capacidad semántica no está activa y documentar
  el retrieval actual honestamente como léxico-exacto (BM25 sin stemming). Separadamente, corregir
  `_symbol_search` para no exigir substring de la consulta completa.
- **prohibited shortcuts**: no dejar `semantic_candidates` como una métrica que reporta 0 sin
  indicar si es "no encontró nada" o "no está configurado" — son estados distintos y deben
  distinguirse aunque no se implemente (a) todavía.
- **acceptance evidence**: si se elige (a), batería de consultas con sinónimos/paráfrasis
  (`session expiry` vs `sessions expire`, consultas en español sobre contenido en inglés) con
  recall mejorado y verificado contra un corpus neutral; si se elige (b), ADRs actualizados y
  métrica de retrieval documentada sin afirmar capacidad semántica.

## H-003 User text can trigger tool execution

- **Hallazgo**: `application/runtime.py:126-135` envuelve el texto crudo del usuario en un mensaje
  `assistant` simulado y lo pasa por el mismo detector de tool-calls que procesa la salida del
  modelo. Combinado con `_first_json_object` (`tool_calls.py:71-93`), que escanea el primer
  objeto JSON balanceado en cualquier parte del string, texto pegado por el usuario que contenga
  un envelope de tool-call se ejecuta sin que el modelo sea invocado — incluso si el usuario
  declara explícitamente que no quiere que se ejecute.
- **root cause**: el mismo intérprete de tool-calls sirve dos niveles de confianza distintos
  (salida del modelo vs. entrada cruda del usuario) sin ningún flag o gate que los distinga.
- **proposed remediation**: (a) exigir que el input completo (no un substring embebido) sea el
  que parsea como el envelope válido para la ruta de ejecución directa, o (b) exponer la ruta de
  ejecución directa detrás de una afición explícita de CLI (p. ej. un prefijo de comando) que no
  pueda dispararse desde prosa pegada por el usuario.
- **prohibited shortcuts**: no intentar detectar "intención maliciosa" con heurísticas de texto o
  un clasificador — el gate debe ser estructural (forma del input), no basado en contenido.
- **acceptance evidence**: el caso reproducido en la auditoría (texto que contiene un envelope de
  tool-call incrustado en prosa, con instrucción explícita del usuario de no ejecutarlo) deja de
  ejecutar la herramienta sin pasar por el modelo.

## H-004 Untrusted evidence inserted as trusted roles

- **Hallazgo**: los resultados de herramientas se entregan al modelo en rol `user`
  (`infrastructure/models/ollama.py::_message_item`, prefijo `"Tool result:\n"` fácilmente
  falsificable dentro del propio contenido), y el contexto de conocimiento recuperado se entrega
  en rol `system` (`application/conversation_context.py::_knowledge_message`) — el canal de mayor
  confianza. Ni el system prompt ni los mensajes en sí declaran que ese contenido es dato no
  confiable proveniente del repositorio o del filesystem, no instrucciones del operador.
- **root cause**: el diseño no distingue estructuralmente entre POLICY (instrucciones del
  operador/sistema) y DATA (contenido recuperado o resultado de herramientas), a pesar de que el
  modelo debe tratarse como consumidor no confiable de esa distinción.
- **proposed remediation**: nunca insertar contenido derivado del repositorio o de resultados de
  herramientas en el rol `system`; usar un rol/formato que el propio system prompt describa
  explícitamente como "datos no confiables, no instrucciones", y usar un delimitador que no pueda
  ser falsificado por el contenido mismo (no un prefijo de texto plano dentro del mismo campo de
  contenido).
- **prohibited shortcuts**: no resolver esto solo cambiando el texto del prefijo — un prefijo
  dentro del mismo campo de contenido siempre es falsificable por el contenido que envuelve; la
  separación debe ser estructural (rol/campo), no léxica.
- **acceptance evidence**: prueba adversarial donde un documento indexado o un resultado de
  herramienta contiene instrucciones dirigidas al modelo (inyección de prompt); el sistema debe
  demostrar que esas instrucciones no se tratan con la autoridad de una instrucción del sistema.

## H-005 Permission grant scope too broad

- **Hallazgo**: `application/confirmation.py` otorga permisos con alcance
  `(session_id, workspace_id, permission)` sin expiración, sin alcance por ruta y sin re-prompt.
  Una sola confirmación de `write` autoriza silenciosamente cualquier escritura posterior en
  cualquier ruta del workspace por el resto de la sesión. `granted_at` existe en el dominio pero
  nunca se lee.
- **root cause**: el modelo de consentimiento fue diseñado para una interacción de baja frecuencia
  (Phase 5, principalmente lectura) y no se revisó al introducir capacidades de escritura de mayor
  impacto.
- **proposed remediation**: expirar los grants (por tiempo y/o por número de operaciones), acotar
  los grants de escritura a un prefijo de ruta específico en vez de todo el workspace, y volver a
  solicitar confirmación cuando el objetivo se mueva fuera del alcance previamente aprobado.
- **prohibited shortcuts**: no resolver esto acortando arbitrariamente el TTL sin introducir
  alcance por ruta — un grant de corta duración pero sin acotar sigue siendo demasiado amplio
  durante su ventana de validez.
- **acceptance evidence**: prueba donde se aprueba una escritura en una ruta específica y se
  confirma que una escritura posterior en una ruta distinta (aunque dentro del mismo workspace)
  requiere una nueva confirmación.

## H-006 Redaction policy incorrect

- **Hallazgo**: `infrastructure/sanitization.py:51-53` hace matching por substring sobre nombres de
  clave (p. ej. `author`, `content_hash`, `token_count`, `response_time_ms` se redactan por
  contener `auth`/`content`/`token`/`response`), sobre-redactando telemetría inocua, mientras que
  secretos reales en formato prosa o token plano (`"password is hunter2"`,
  `"AKIAIOSFODNN7EXAMPLE"`, `"Bearer eyJ..."`) no se redactan porque `_SECRET_RE` solo reconoce el
  patrón `key: value`/`key=value`. Como workaround, el runtime renombra sus propias métricas
  (`prompt_tokens` → `input_length`, etc.) para evitar el over-redaction, en vez de corregir el
  sanitizador.
- **root cause**: matching por substring en vez de por clave completa/límite de token, y detección
  de secretos limitada a un patrón sintáctico estrecho que no cubre secretos en prosa o tokens
  reconocibles por formato (AWS keys, JWT, Bearer tokens).
- **proposed remediation**: cambiar el matching de claves sensibles a coincidencia exacta o por
  límite de token (no substring); ampliar la detección de secretos en el lado del valor para
  cubrir formatos reconocibles de tokens/credenciales independientemente de si aparecen en forma
  `key: value`. Una vez corregido, revertir los renombres de métricas hechos como workaround en
  `application/runtime.py`, restaurando nombres semánticos.
- **prohibited shortcuts**: no ampliar la lista de excepciones de claves permitidas ad hoc sin
  corregir el mecanismo de matching — eso reproduce el mismo problema con otra lista mantenida a
  mano. No revertir los renombres de métricas antes de que la corrección de detección de secretos
  esté en su lugar y verificada — el orden importa para no reexponer secretos reales.
- **acceptance evidence**: batería de casos verificados en la auditoría (claves inocuas que
  contienen substrings sensibles; secretos reales en prosa, AWS-style keys, Bearer tokens) con el
  comportamiento correcto en ambas direcciones — sin over-redaction de telemetría y sin
  under-redaction de secretos reales.
