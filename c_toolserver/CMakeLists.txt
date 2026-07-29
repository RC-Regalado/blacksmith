cmake_minimum_required(VERSION 3.18)

project(blacksmith_toolserver C)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

find_package(PkgConfig REQUIRED)
pkg_check_modules(PROTOBUF_C REQUIRED libprotobuf-c)
find_program(PROTOC_EXECUTABLE protoc REQUIRED)
find_program(PROTOC_GEN_C protoc-gen-c REQUIRED)

set(PROTO_FILE ${CMAKE_CURRENT_SOURCE_DIR}/../proto/toolserver.proto)
set(GENERATED_DIR ${CMAKE_CURRENT_BINARY_DIR}/generated)
set(GENERATED_C ${GENERATED_DIR}/proto/toolserver.pb-c.c)
set(GENERATED_H ${GENERATED_DIR}/proto/toolserver.pb-c.h)

add_custom_command(
    OUTPUT ${GENERATED_C} ${GENERATED_H}
    COMMAND ${CMAKE_COMMAND} -E make_directory ${GENERATED_DIR}
    COMMAND ${PROTOC_EXECUTABLE} -I${CMAKE_CURRENT_SOURCE_DIR}/.. --c_out=${GENERATED_DIR} ${PROTO_FILE}
    DEPENDS ${PROTO_FILE}
    VERBATIM
)

add_executable(toolserver
    src/actions.c
    src/framing.c
    src/main.c
    src/server.c
    ${GENERATED_C}
)

target_include_directories(toolserver PRIVATE
    include
    ${GENERATED_DIR}
    ${PROTOBUF_C_INCLUDE_DIRS}
)

target_link_libraries(toolserver PRIVATE ${PROTOBUF_C_LIBRARIES})
target_compile_definitions(toolserver PRIVATE _POSIX_C_SOURCE=200809L)
target_compile_options(toolserver PRIVATE -Wall -Wextra -Werror -pedantic)
