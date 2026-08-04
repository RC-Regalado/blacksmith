#include "actions.h"

#include <dirent.h>
#include <errno.h>
#include <limits.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

#define MAX_PATH_CHARS 4096U
#define MAX_READ_BYTES 65536U
#define DEFAULT_READ_BYTES 16384U
#define MAX_DIRECTORY_ENTRIES 1000U
#define DEFAULT_DIRECTORY_ENTRIES 200U
#define MAX_RESPONSE_BYTES 1048576U

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

static void set_data(ActionResult *result, const char *message, char *data)
{
    if (data == NULL) {
        set_error(result, TOOLSERVER__V1__TOOL_STATUS__TOOL_STATUS_ERROR,
                  "allocation_failed", "response allocation failed");
        return;
    }
    result->status = TOOLSERVER__V1__TOOL_STATUS__TOOL_STATUS_OK;
    result->message = message;
    result->stdout_data = (uint8_t *)data;
    result->stdout_len = strlen(data);
}

static bool permission_allowed(const Toolserver__V1__ToolRequest *request)
{
    return request->requested_permission ==
           TOOLSERVER__V1__PERMISSION_LEVEL__PERMISSION_READ_ONLY;
}

static bool parse_size(const char *value, size_t fallback, size_t max, size_t *out)
{
    if (value == NULL || *value == '\0') {
        *out = fallback;
        return true;
    }
    char *end = NULL;
    unsigned long parsed = strtoul(value, &end, 10);
    if (*end != '\0' || parsed == 0UL || parsed > max) {
        return false;
    }
    *out = (size_t)parsed;
    return true;
}

static bool parse_offset(const char *value, long *out)
{
    if (value == NULL || *value == '\0') {
        *out = 0L;
        return true;
    }
    char *end = NULL;
    long parsed = strtol(value, &end, 10);
    if (*end != '\0' || parsed < 0L) {
        return false;
    }
    *out = parsed;
    return true;
}

static bool path_has_denied_component(const char *path)
{
    const char *part = path;
    while (*part != '\0') {
        size_t len = strcspn(part, "/");
        if (len == 1U && strncmp(part, ".", 1U) == 0) {
            /* allow workspace root/current-dir components */
        } else if ((len == 2U && strncmp(part, "..", 2U) == 0) ||
                   (len > 0U && part[0] == '.')) {
            return true;
        }
        part += len;
        if (*part == '/') {
            ++part;
        }
    }
    return false;
}

static bool resolve_target(const Toolserver__V1__ToolRequest *request,
                           char resolved[PATH_MAX])
{
    const char *path = arg_value(request, "path");
    if (path == NULL || *path == '\0' || path[0] == '/' ||
        strlen(path) > MAX_PATH_CHARS || path_has_denied_component(path)) {
        return false;
    }
    char workspace[PATH_MAX];
    if (request->workspace_id == NULL ||
        realpath(request->workspace_id, workspace) == NULL) {
        return false;
    }
    char joined[PATH_MAX];
    if (snprintf(joined, sizeof(joined), "%s/%s", workspace, path) >=
        (int)sizeof(joined)) {
        return false;
    }
    if (realpath(joined, resolved) == NULL) {
        return false;
    }
    size_t root_len = strlen(workspace);
    return strncmp(resolved, workspace, root_len) == 0 &&
           (resolved[root_len] == '\0' || resolved[root_len] == '/');
}

static char *append_text(char *buffer, size_t *used, size_t *capacity, const char *text)
{
    size_t len = strlen(text);
    if (*used + len + 1U > MAX_RESPONSE_BYTES) {
        return buffer;
    }
    if (*used + len + 1U > *capacity) {
        size_t next = (*capacity * 2U) + len + 1U;
        char *grown = realloc(buffer, next);
        if (grown == NULL) {
            free(buffer);
            return NULL;
        }
        buffer = grown;
        *capacity = next;
    }
    memcpy(buffer + *used, text, len + 1U);
    *used += len;
    return buffer;
}

static char *json_escape(const char *value)
{
    size_t capacity = (strlen(value) * 2U) + 3U;
    char *out = malloc(capacity);
    if (out == NULL) {
        return NULL;
    }
    size_t used = 0U;
    out[used++] = '"';
    for (const char *p = value; *p != '\0'; ++p) {
        if (*p == '"' || *p == '\\') {
            out[used++] = '\\';
        }
        out[used++] = *p;
    }
    out[used++] = '"';
    out[used] = '\0';
    return out;
}

static void handle_list_directory(const Toolserver__V1__ToolRequest *request,
                                  ActionResult *result)
{
    char target[PATH_MAX];
    size_t max_entries = 0U;
    if (!resolve_target(request, target) ||
        !parse_size(arg_value(request, "max_entries"), DEFAULT_DIRECTORY_ENTRIES,
                    MAX_DIRECTORY_ENTRIES, &max_entries)) {
        set_error(result, TOOLSERVER__V1__TOOL_STATUS__TOOL_STATUS_DENIED,
                  "path_denied", "path denied");
        return;
    }
    struct stat st;
    if (stat(target, &st) != 0 || !S_ISDIR(st.st_mode)) {
        set_error(result, TOOLSERVER__V1__TOOL_STATUS__TOOL_STATUS_INVALID_ARGUMENT,
                  "invalid_path", "path must be a directory");
        return;
    }
    DIR *dir = opendir(target);
    if (dir == NULL) {
        set_error(result, TOOLSERVER__V1__TOOL_STATUS__TOOL_STATUS_ERROR,
                  "open_failed", "directory open failed");
        return;
    }
    size_t used = 0U;
    size_t capacity = 256U;
    char *json = calloc(1U, capacity);
    json = append_text(json, &used, &capacity, "{\"entries\":[");
    if (json == NULL) {
        closedir(dir);
        set_data(result, "directory listed", NULL);
        return;
    }
    size_t count = 0U;
    bool truncated = false;
    for (struct dirent *entry = readdir(dir); entry != NULL; entry = readdir(dir)) {
        if (entry->d_name[0] == '.') {
            continue;
        }
        if (count >= max_entries) {
            truncated = true;
            break;
        }
        char child[PATH_MAX];
        if (snprintf(child, sizeof(child), "%s/%s", target, entry->d_name) >=
            (int)sizeof(child)) {
            continue;
        }
        struct stat child_st;
        if (lstat(child, &child_st) != 0) {
            continue;
        }
        char line[512];
        char *name = json_escape(entry->d_name);
        snprintf(line, sizeof(line), "%s{\"name\":%s,\"type\":\"%s\",\"size\":%ld}",
                 count == 0U ? "" : ",", name == NULL ? "\"\"" : name,
                 S_ISDIR(child_st.st_mode) ? "directory" :
                 S_ISREG(child_st.st_mode) ? "file" : "other",
                 S_ISREG(child_st.st_mode) ? (long)child_st.st_size : -1L);
        free(name);
        json = append_text(json, &used, &capacity, line);
        if (json == NULL) {
            closedir(dir);
            set_data(result, "directory listed", NULL);
            return;
        }
        ++count;
    }
    closedir(dir);
    char tail[64];
    snprintf(tail, sizeof(tail), "],\"truncated\":%s}", truncated ? "true" : "false");
    json = append_text(json, &used, &capacity, tail);
    set_data(result, "directory listed", json);
}

static void handle_file_metadata(const Toolserver__V1__ToolRequest *request,
                                 ActionResult *result)
{
    char target[PATH_MAX];
    if (!resolve_target(request, target)) {
        set_error(result, TOOLSERVER__V1__TOOL_STATUS__TOOL_STATUS_DENIED,
                  "path_denied", "path denied");
        return;
    }
    struct stat st;
    if (stat(target, &st) != 0 || (!S_ISREG(st.st_mode) && !S_ISDIR(st.st_mode))) {
        set_error(result, TOOLSERVER__V1__TOOL_STATUS__TOOL_STATUS_INVALID_ARGUMENT,
                  "invalid_path", "path must be a regular file or directory");
        return;
    }
    char *json = malloc(160U);
    if (json == NULL) {
        set_data(result, "file metadata", NULL);
        return;
    }
    if (S_ISDIR(st.st_mode)) {
        snprintf(json, 160U, "{\"type\":\"directory\",\"size\":null,\"modified_at\":%ld}",
                 (long)st.st_mtime);
    } else {
        snprintf(json, 160U, "{\"type\":\"file\",\"size\":%ld,\"modified_at\":%ld}",
                 (long)st.st_size, (long)st.st_mtime);
    }
    set_data(result, "file metadata", json);
}

static void handle_read_file(const Toolserver__V1__ToolRequest *request,
                             ActionResult *result)
{
    char target[PATH_MAX];
    long offset = 0L;
    size_t max_bytes = 0U;
    if (!resolve_target(request, target) ||
        !parse_offset(arg_value(request, "offset"), &offset) ||
        !parse_size(arg_value(request, "max_bytes"), DEFAULT_READ_BYTES,
                    MAX_READ_BYTES, &max_bytes)) {
        set_error(result, TOOLSERVER__V1__TOOL_STATUS__TOOL_STATUS_DENIED,
                  "path_denied", "path denied");
        return;
    }
    struct stat st;
    if (stat(target, &st) != 0 || !S_ISREG(st.st_mode)) {
        set_error(result, TOOLSERVER__V1__TOOL_STATUS__TOOL_STATUS_INVALID_ARGUMENT,
                  "invalid_path", "path must be a regular file");
        return;
    }
    FILE *file = fopen(target, "rb");
    if (file == NULL || fseek(file, offset, SEEK_SET) != 0) {
        if (file != NULL) {
            fclose(file);
        }
        set_error(result, TOOLSERVER__V1__TOOL_STATUS__TOOL_STATUS_ERROR,
                  "read_failed", "file read failed");
        return;
    }
    char *buffer = malloc(max_bytes + 1U);
    if (buffer == NULL) {
        fclose(file);
        set_data(result, "file read", NULL);
        return;
    }
    size_t read_count = fread(buffer, 1U, max_bytes, file);
    bool truncated = !feof(file);
    fclose(file);
    buffer[read_count] = '\0';
    char *escaped = json_escape(buffer);
    free(buffer);
    size_t size = strlen(escaped == NULL ? "\"\"" : escaped) + 96U;
    char *json = malloc(size);
    if (json == NULL) {
        free(escaped);
        set_data(result, "file read", NULL);
        return;
    }
    snprintf(json, size, "{\"content\":%s,\"bytes_read\":%zu,\"truncated\":%s}",
             escaped == NULL ? "\"\"" : escaped, read_count,
             truncated ? "true" : "false");
    free(escaped);
    set_data(result, "file read", json);
}

void handle_tool_request(const Toolserver__V1__ToolRequest *request,
                         ActionResult *result)
{
    *result = (ActionResult){0};
    result->message = "";
    result->error_code = "";
    result->error_detail = "";

    if (!permission_allowed(request)) {
        set_error(result, TOOLSERVER__V1__TOOL_STATUS__TOOL_STATUS_DENIED,
                  "permission_denied", "requested permission is not allowed");
        return;
    }
    if (strcmp(request->tool_name, "file_metadata") == 0) {
        handle_file_metadata(request, result);
        return;
    }
    if (strcmp(request->tool_name, "list_directory") == 0) {
        handle_list_directory(request, result);
        return;
    }
    if (strcmp(request->tool_name, "read_file") == 0) {
        handle_read_file(request, result);
        return;
    }
    set_error(result, TOOLSERVER__V1__TOOL_STATUS__TOOL_STATUS_NOT_FOUND,
              "tool_not_found", "unknown tool_name");
}

void free_action_result(ActionResult *result)
{
    free(result->stdout_data);
    result->stdout_data = NULL;
    result->stdout_len = 0U;
}
