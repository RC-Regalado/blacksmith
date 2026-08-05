# C Tool Server

Servidor Unix domain socket para recibir `ToolRequest` protobuf con framing:

```text
[4 bytes length big-endian][protobuf payload]
```

La respuesta usa el mismo framing con `ToolResponse`.

## Build

Con `make`:

```sh
cd c_toolserver
make
```

Con CMake:

```sh
cmake -S c_toolserver -B c_toolserver/build
cmake --build c_toolserver/build
```

Dependencias:

- `protoc`
- `protoc-gen-c`
- `protobuf-c`

## Run

```sh
c_toolserver/build/toolserver --socket /tmp/blacksmith-toolserver.sock
```

Acciones incluidas:

- `file_metadata` con `workspace_id` y argumento `path`
- `list_directory` con `workspace_id` y argumento `path`
- `read_file` con `workspace_id`, argumento `path` y límites opcionales `offset`, `max_bytes`
- `search_text` con búsqueda literal acotada
- `git_status` con inspección read-only del repositorio
- `git_diff` con scopes `worktree` o `staged`
- `run_tests` con perfiles aprobados
- `build_project` con perfiles aprobados
- `write` con modos `create` o `replace`

`workspace_id` debe apuntar al workspace autorizado. El servidor C valida de nuevo paths relativos, traversal, symlinks externos, permisos y límites antes de leer, inspeccionar metadata, ejecutar perfiles o escribir.

Restricciones Phase 3:

- no shell ni argv definidos por el modelo;
- `run_tests` y `build_project` sólo aceptan `profile_id` registrado;
- Git es read-only, sin pager ni diff externo;
- `search_text` es literal y acotado;
- `write` sólo acepta UTF-8 acotado, paths no ocultos/no sensibles y archivos regulares;
- `write` usa archivo temporal y rename atómico;
- `expected_sha256` permite concurrencia optimista en modo `replace`;
- los resultados y errores se devuelven sanitizados.
