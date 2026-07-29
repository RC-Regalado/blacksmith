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

- `noop`
- `echo` con argumento `message`
- `list_tools`

