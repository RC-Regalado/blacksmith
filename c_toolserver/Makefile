CC ?= cc
PROTOC ?= protoc
PROTOC_C_OUT ?= --c_out
PKG_CONFIG ?= pkg-config

BUILD_DIR := build
GEN_DIR := $(BUILD_DIR)/generated
PROTO_SRC := ../proto/toolserver.proto
PROTO_GEN_C := $(GEN_DIR)/proto/toolserver.pb-c.c
PROTO_GEN_H := $(GEN_DIR)/proto/toolserver.pb-c.h
TARGET := $(BUILD_DIR)/toolserver

SRC := \
	src/actions.c \
	src/framing.c \
	src/main.c \
	src/server.c

OBJ := $(patsubst src/%.c,$(BUILD_DIR)/%.o,$(SRC)) \
	$(BUILD_DIR)/toolserver.pb-c.o

CPPFLAGS += -Iinclude -I$(GEN_DIR)
CFLAGS += -std=c11 -D_POSIX_C_SOURCE=200809L -Wall -Wextra -Werror -pedantic
LDLIBS += $(shell $(PKG_CONFIG) --libs libprotobuf-c 2>/dev/null || echo -lprotobuf-c)

.PHONY: all clean proto check-deps

all: check-deps $(TARGET)

check-deps:
	@command -v $(PROTOC) >/dev/null || { echo "missing protoc"; exit 1; }
	@command -v protoc-gen-c >/dev/null || { echo "missing protoc-gen-c"; exit 1; }
	@printf '#include <protobuf-c/protobuf-c.h>\n' | $(CC) -E - >/dev/null

proto: $(PROTO_GEN_C)

$(PROTO_GEN_C) $(PROTO_GEN_H): $(PROTO_SRC)
	@mkdir -p $(GEN_DIR)
	$(PROTOC) -I.. $(PROTOC_C_OUT)=$(GEN_DIR) $(PROTO_SRC)

$(BUILD_DIR)/toolserver.pb-c.o: $(PROTO_GEN_C) $(PROTO_GEN_H)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -c $(PROTO_GEN_C) -o $@

$(BUILD_DIR)/%.o: src/%.c $(PROTO_GEN_H)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) -c $< -o $@

$(TARGET): $(OBJ)
	$(CC) $(CFLAGS) $(OBJ) $(LDLIBS) -o $@

clean:
	rm -rf $(BUILD_DIR)
