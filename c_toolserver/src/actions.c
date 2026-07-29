#include "actions.h"

#include <stddef.h>
#include <string.h>

static const char *arg_value(const Toolserver__V1__ToolRequest *request,
                             const char *key)
{
    for (size_t i = 0; i < request->n_args; ++i) {
        if (strcmp(request->args[i]->key, key) == 0) {
            return request->args[i]->value;
        }
    }
    return NULL;
}

static bool permission_allowed(const Toolserver__V1__ToolRequest *request)
{
    return request->requested_permission <=
           TOOLSERVER__V1__PERMISSION_LEVEL__PERMISSION_READ_ONLY;
}

static void set_ok(ActionResult *result, const char *message, const char *stdout_text)
{
    result->status = TOOLSERVER__V1__TOOL_STATUS__TOOL_STATUS_OK;
    result->message = message;
    result->stdout_text = stdout_text;
}

static void set_error(ActionResult *result,
                      Toolserver__V1__ToolStatus status,
                      const char *code,
                      const char *detail)
{
    result->status = status;
    result->message = detail;
    result->error_code = code;
    result->error_detail = detail;
}

void handle_tool_request(const Toolserver__V1__ToolRequest *request,
                         ActionResult *result)
{
    *result = (ActionResult){
        .status = TOOLSERVER__V1__TOOL_STATUS__TOOL_STATUS_UNSPECIFIED,
        .message = "",
        .stdout_text = "",
        .error_code = "",
        .error_detail = "",
    };

    if (request->dry_run) {
        set_ok(result, "dry-run accepted", "request validated");
        return;
    }
    if (!permission_allowed(request)) {
        set_error(result, TOOLSERVER__V1__TOOL_STATUS__TOOL_STATUS_DENIED,
                  "permission_denied", "requested permission is not allowed");
        return;
    }
    if (strcmp(request->tool_name, "noop") == 0) {
        set_ok(result, "noop completed", "");
        return;
    }
    if (strcmp(request->tool_name, "list_tools") == 0) {
        set_ok(result, "tools listed", "noop\necho\nlist_tools\n");
        return;
    }
    if (strcmp(request->tool_name, "echo") == 0) {
        const char *message = arg_value(request, "message");
        set_ok(result, "echo completed", message == NULL ? "" : message);
        return;
    }

    set_error(result, TOOLSERVER__V1__TOOL_STATUS__TOOL_STATUS_NOT_FOUND,
              "tool_not_found", "unknown tool_name");
}

