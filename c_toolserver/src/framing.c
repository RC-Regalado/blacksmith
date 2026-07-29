#include "framing.h"

#include <errno.h>
#include <stdlib.h>
#include <unistd.h>

static uint32_t decode_u32_be(const uint8_t bytes[FRAME_HEADER_SIZE])
{
    return ((uint32_t)bytes[0] << 24) |
           ((uint32_t)bytes[1] << 16) |
           ((uint32_t)bytes[2] << 8) |
           (uint32_t)bytes[3];
}

static void encode_u32_be(uint32_t value, uint8_t bytes[FRAME_HEADER_SIZE])
{
    bytes[0] = (uint8_t)(value >> 24);
    bytes[1] = (uint8_t)(value >> 16);
    bytes[2] = (uint8_t)(value >> 8);
    bytes[3] = (uint8_t)value;
}

static FrameStatus read_exact(int fd, uint8_t *buffer, size_t size)
{
    size_t offset = 0;
    while (offset < size) {
        ssize_t count = read(fd, buffer + offset, size - offset);
        if (count == 0) {
            return FRAME_STATUS_CLOSED;
        }
        if (count < 0 && errno == EINTR) {
            continue;
        }
        if (count < 0) {
            return FRAME_STATUS_IO_ERROR;
        }
        offset += (size_t)count;
    }
    return FRAME_STATUS_OK;
}

static FrameStatus write_exact(int fd, const uint8_t *buffer, size_t size)
{
    size_t offset = 0;
    while (offset < size) {
        ssize_t count = write(fd, buffer + offset, size - offset);
        if (count < 0 && errno == EINTR) {
            continue;
        }
        if (count < 0) {
            return FRAME_STATUS_IO_ERROR;
        }
        offset += (size_t)count;
    }
    return FRAME_STATUS_OK;
}

FrameStatus read_frame(int fd, uint8_t **payload, size_t *payload_len)
{
    uint8_t header[FRAME_HEADER_SIZE];
    FrameStatus status = read_exact(fd, header, FRAME_HEADER_SIZE);
    if (status != FRAME_STATUS_OK) {
        return status;
    }

    uint32_t length = decode_u32_be(header);
    if (length == 0U || length > MAX_FRAME_LENGTH) {
        return FRAME_STATUS_INVALID;
    }

    uint8_t *buffer = malloc(length);
    if (buffer == NULL) {
        return FRAME_STATUS_NO_MEMORY;
    }

    status = read_exact(fd, buffer, length);
    if (status != FRAME_STATUS_OK) {
        free(buffer);
        return status;
    }

    *payload = buffer;
    *payload_len = length;
    return FRAME_STATUS_OK;
}

FrameStatus write_frame(int fd, const uint8_t *payload, size_t payload_len)
{
    if (payload == NULL || payload_len == 0U || payload_len > MAX_FRAME_LENGTH) {
        return FRAME_STATUS_INVALID;
    }
    if (payload_len > UINT32_MAX) {
        return FRAME_STATUS_INVALID;
    }

    uint8_t header[FRAME_HEADER_SIZE];
    encode_u32_be((uint32_t)payload_len, header);

    FrameStatus status = write_exact(fd, header, FRAME_HEADER_SIZE);
    if (status != FRAME_STATUS_OK) {
        return status;
    }
    return write_exact(fd, payload, payload_len);
}

