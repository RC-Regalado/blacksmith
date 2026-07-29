#ifndef BLACKSMITH_FRAMING_H
#define BLACKSMITH_FRAMING_H

#include <stddef.h>
#include <stdint.h>

#define FRAME_HEADER_SIZE 4U
#define MAX_FRAME_LENGTH (64U * 1024U * 1024U)

typedef enum FrameStatus {
    FRAME_STATUS_OK = 0,
    FRAME_STATUS_CLOSED = 1,
    FRAME_STATUS_INVALID = 2,
    FRAME_STATUS_IO_ERROR = 3,
    FRAME_STATUS_NO_MEMORY = 4
} FrameStatus;

FrameStatus read_frame(int fd, uint8_t **payload, size_t *payload_len);
FrameStatus write_frame(int fd, const uint8_t *payload, size_t payload_len);

#endif

