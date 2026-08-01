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

- `list_directory` con `workspace_id` y argumento `path`
- `read_file` con `workspace_id`, argumento `path` y límites opcionales `offset`, `max_bytes`

`workspace_id` debe apuntar al workspace autorizado. El servidor C valida de nuevo paths relativos, traversal, symlinks externos, permiso read-only y límites antes de leer.
