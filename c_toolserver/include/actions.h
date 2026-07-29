#ifndef BLACKSMITH_ACTIONS_H
#define BLACKSMITH_ACTIONS_H

#include <stdbool.h>

#include "proto/toolserver.pb-c.h"

typedef struct ActionResult {
    Toolserver__V1__ToolStatus status;
    const char *message;
    const char *stdout_text;
    const char *error_code;
    const char *error_detail;
} ActionResult;

void handle_tool_request(const Toolserver__V1__ToolRequest *request,
                         ActionResult *result);

#endif

