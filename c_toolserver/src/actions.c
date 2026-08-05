#include "actions.h"

#include <dirent.h>
#include <errno.h>
#include <limits.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <fcntl.h>
#include <time.h>
#include <unistd.h>

#define MAX_PATH_CHARS 4096U
#define MAX_READ_BYTES 65536U
#define MAX_WRITE_BYTES 65536U
#define DEFAULT_READ_BYTES 16384U
#define MAX_DIRECTORY_ENTRIES 1000U
#define DEFAULT_DIRECTORY_ENTRIES 200U
#define MAX_RESPONSE_BYTES 1048576U
#define MAX_PROCESS_BYTES 131072U

typedef struct Sha256State {
    uint32_t state[8];
    uint64_t bit_len;
    uint8_t data[64];
    size_t data_len;
} Sha256State;

static const uint32_t SHA256_K[64] = {
    0x428a2f98U, 0x71374491U, 0xb5c0fbcfU, 0xe9b5dba5U,
    0x3956c25bU, 0x59f111f1U, 0x923f82a4U, 0xab1c5ed5U,
    0xd807aa98U, 0x12835b01U, 0x243185beU, 0x550c7dc3U,
    0x72be5d74U, 0x80deb1feU, 0x9bdc06a7U, 0xc19bf174U,
    0xe49b69c1U, 0xefbe4786U, 0x0fc19dc6U, 0x240ca1ccU,
    0x2de92c6fU, 0x4a7484aaU, 0x5cb0a9dcU, 0x76f988daU,
    0x983e5152U, 0xa831c66dU, 0xb00327c8U, 0xbf597fc7U,
    0xc6e00bf3U, 0xd5a79147U, 0x06ca6351U, 0x14292967U,
    0x27b70a85U, 0x2e1b2138U, 0x4d2c6dfcU, 0x53380d13U,
    0x650a7354U, 0x766a0abbU, 0x81c2c92eU, 0x92722c85U,
    0xa2bfe8a1U, 0xa81a664bU, 0xc24b8b70U, 0xc76c51a3U,
    0xd192e819U, 0xd6990624U, 0xf40e3585U, 0x106aa070U,
    0x19a4c116U, 0x1e376c08U, 0x2748774cU, 0x34b0bcb5U,
    0x391c0cb3U, 0x4ed8aa4aU, 0x5b9cca4fU, 0x682e6ff3U,
    0x748f82eeU, 0x78a5636fU, 0x84c87814U, 0x8cc70208U,
    0x90befffaU, 0xa4506cebU, 0xbef9a3f7U, 0xc67178f2U,
};

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

static uint32_t rotr(uint32_t value, uint32_t bits)
{
    return (value >> bits) | (value << (32U - bits));
}

static void sha256_transform(Sha256State *ctx)
{
    uint32_t w[64];
    for (size_t i = 0U; i < 16U; ++i) {
        w[i] = ((uint32_t)ctx->data[i * 4U] << 24U) |
               ((uint32_t)ctx->data[i * 4U + 1U] << 16U) |
               ((uint32_t)ctx->data[i * 4U + 2U] << 8U) |
               (uint32_t)ctx->data[i * 4U + 3U];
    }
    for (size_t i = 16U; i < 64U; ++i) {
        uint32_t s0 = rotr(w[i - 15U], 7U) ^ rotr(w[i - 15U], 18U) ^
                      (w[i - 15U] >> 3U);
        uint32_t s1 = rotr(w[i - 2U], 17U) ^ rotr(w[i - 2U], 19U) ^
                      (w[i - 2U] >> 10U);
        w[i] = w[i - 16U] + s0 + w[i - 7U] + s1;
    }
    uint32_t a = ctx->state[0], b = ctx->state[1], c = ctx->state[2];
    uint32_t d = ctx->state[3], e = ctx->state[4], f = ctx->state[5];
    uint32_t g = ctx->state[6], h = ctx->state[7];
    for (size_t i = 0U; i < 64U; ++i) {
        uint32_t s1 = rotr(e, 6U) ^ rotr(e, 11U) ^ rotr(e, 25U);
        uint32_t ch = (e & f) ^ ((~e) & g);
        uint32_t temp1 = h + s1 + ch + SHA256_K[i] + w[i];
        uint32_t s0 = rotr(a, 2U) ^ rotr(a, 13U) ^ rotr(a, 22U);
        uint32_t maj = (a & b) ^ (a & c) ^ (b & c);
        uint32_t temp2 = s0 + maj;
        h = g;
        g = f;
        f = e;
        e = d + temp1;
        d = c;
        c = b;
        b = a;
        a = temp1 + temp2;
    }
    ctx->state[0] += a; ctx->state[1] += b; ctx->state[2] += c; ctx->state[3] += d;
    ctx->state[4] += e; ctx->state[5] += f; ctx->state[6] += g; ctx->state[7] += h;
}

static void sha256_init(Sha256State *ctx)
{
    *ctx = (Sha256State){
        .state = {0x6a09e667U, 0xbb67ae85U, 0x3c6ef372U, 0xa54ff53aU,
                  0x510e527fU, 0x9b05688cU, 0x1f83d9abU, 0x5be0cd19U},
    };
}

static void sha256_update(Sha256State *ctx, const uint8_t *data, size_t len)
{
    for (size_t i = 0U; i < len; ++i) {
        ctx->data[ctx->data_len++] = data[i];
        if (ctx->data_len == 64U) {
            sha256_transform(ctx);
            ctx->bit_len += 512U;
            ctx->data_len = 0U;
        }
    }
}

static void sha256_final(Sha256State *ctx, uint8_t hash[32])
{
    size_t i = ctx->data_len;
    ctx->data[i++] = 0x80U;
    if (i > 56U) {
        while (i < 64U) {
            ctx->data[i++] = 0U;
        }
        sha256_transform(ctx);
        i = 0U;
    }
    while (i < 56U) {
        ctx->data[i++] = 0U;
    }
    ctx->bit_len += ctx->data_len * 8U;
    for (size_t j = 0U; j < 8U; ++j) {
        ctx->data[63U - j] = (uint8_t)(ctx->bit_len >> (j * 8U));
    }
    sha256_transform(ctx);
    for (size_t j = 0U; j < 8U; ++j) {
        hash[j * 4U] = (uint8_t)(ctx->state[j] >> 24U);
        hash[j * 4U + 1U] = (uint8_t)(ctx->state[j] >> 16U);
        hash[j * 4U + 2U] = (uint8_t)(ctx->state[j] >> 8U);
        hash[j * 4U + 3U] = (uint8_t)ctx->state[j];
    }
}

static void sha256_hex(const uint8_t *data, size_t len, char out[65])
{
    static const char *hex = "0123456789abcdef";
    uint8_t hash[32];
    Sha256State ctx;
    sha256_init(&ctx);
    sha256_update(&ctx, data, len);
    sha256_final(&ctx, hash);
    for (size_t i = 0U; i < 32U; ++i) {
        out[i * 2U] = hex[hash[i] >> 4U];
        out[i * 2U + 1U] = hex[hash[i] & 0x0FU];
    }
    out[64] = '\0';
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
    if (strcmp(request->tool_name, "write") == 0) {
        return request->requested_permission ==
               TOOLSERVER__V1__PERMISSION_LEVEL__PERMISSION_WORKSPACE_WRITE;
    }
    if (strcmp(request->tool_name, "run_tests") == 0 ||
        strcmp(request->tool_name, "build_project") == 0) {
        return request->requested_permission ==
               TOOLSERVER__V1__PERMISSION_LEVEL__PERMISSION_PROCESS_EXEC;
    }
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

static bool is_sensitive_name(const char *part, size_t len)
{
    return (len == 4U && strncmp(part, ".env", 4U) == 0) ||
           (len >= 4U && strncmp(part + len - 4U, ".pem", 4U) == 0) ||
           (len >= 4U && strncmp(part + len - 4U, ".key", 4U) == 0) ||
           (len >= 4U && strncmp(part + len - 4U, ".p12", 4U) == 0) ||
           (len >= 4U && strncmp(part + len - 4U, ".pfx", 4U) == 0) ||
           (len >= 11U && strncmp(part + len - 11U, ".kubeconfig", 11U) == 0) ||
           (len == 6U && strncmp(part, "id_rsa", 6U) == 0) ||
           (len == 10U && strncmp(part, "id_ed25519", 10U) == 0) ||
           (len == 16U && strncmp(part, "credentials.json", 16U) == 0) ||
           (len >= 8U && strncmp(part, "secrets.", 8U) == 0);
}

static bool path_has_sensitive_component(const char *path)
{
    const char *part = path;
    while (*part != '\0') {
        size_t len = strcspn(part, "/");
        if (is_sensitive_name(part, len)) {
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
        strlen(path) > MAX_PATH_CHARS || path_has_denied_component(path) ||
        path_has_sensitive_component(path)) {
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

static bool path_inside_workspace(const char *path, const char *workspace)
{
    size_t root_len = strlen(workspace);
    return strncmp(path, workspace, root_len) == 0 &&
           (path[root_len] == '\0' || path[root_len] == '/');
}

static bool resolve_write_target(const Toolserver__V1__ToolRequest *request,
                                 char workspace[PATH_MAX],
                                 char target[PATH_MAX],
                                 char parent[PATH_MAX])
{
    const char *path = arg_value(request, "path");
    if (path == NULL || *path == '\0' || path[0] == '/' ||
        strlen(path) > MAX_PATH_CHARS || path_has_denied_component(path) ||
        path_has_sensitive_component(path)) {
        return false;
    }
    if (request->workspace_id == NULL ||
        realpath(request->workspace_id, workspace) == NULL) {
        return false;
    }
    if (snprintf(target, PATH_MAX, "%s/%s", workspace, path) >= PATH_MAX) {
        return false;
    }
    char parent_input[PATH_MAX];
    strncpy(parent_input, target, sizeof(parent_input) - 1U);
    parent_input[sizeof(parent_input) - 1U] = '\0';
    char *slash = strrchr(parent_input, '/');
    if (slash == NULL) {
        return false;
    }
    *slash = '\0';
    if (realpath(parent_input, parent) == NULL) {
        return false;
    }
    return path_inside_workspace(parent, workspace);
}

static bool valid_sha256_hex(const char *value)
{
    if (value == NULL || strlen(value) != 64U) {
        return false;
    }
    for (size_t i = 0U; i < 64U; ++i) {
        if (!((value[i] >= '0' && value[i] <= '9') ||
              (value[i] >= 'a' && value[i] <= 'f'))) {
            return false;
        }
    }
    return true;
}

static bool valid_utf8(const unsigned char *data, size_t len)
{
    size_t i = 0U;
    while (i < len) {
        unsigned char c = data[i++];
        if (c < 0x80U) {
            continue;
        }
        size_t extra = 0U;
        if (c >= 0xC2U && c <= 0xDFU) {
            extra = 1U;
        } else if (c >= 0xE0U && c <= 0xEFU) {
            extra = 2U;
        } else if (c >= 0xF0U && c <= 0xF4U) {
            extra = 3U;
        } else {
            return false;
        }
        if (i + extra > len) {
            return false;
        }
        for (size_t j = 0U; j < extra; ++j) {
            if ((data[i++] & 0xC0U) != 0x80U) {
                return false;
            }
        }
    }
    return true;
}

static bool file_sha256_hex(const char *path, char out[65])
{
    FILE *file = fopen(path, "rb");
    if (file == NULL) {
        return false;
    }
    Sha256State ctx;
    sha256_init(&ctx);
    uint8_t buffer[4096];
    for (;;) {
        size_t count = fread(buffer, 1U, sizeof(buffer), file);
        if (count > 0U) {
            sha256_update(&ctx, buffer, count);
        }
        if (count < sizeof(buffer)) {
            if (ferror(file)) {
                fclose(file);
                return false;
            }
            break;
        }
    }
    fclose(file);
    uint8_t hash[32];
    sha256_final(&ctx, hash);
    static const char *hex = "0123456789abcdef";
    for (size_t i = 0U; i < 32U; ++i) {
        out[i * 2U] = hex[hash[i] >> 4U];
        out[i * 2U + 1U] = hex[hash[i] & 0x0FU];
    }
    out[64] = '\0';
    return true;
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
    size_t capacity = (strlen(value) * 6U) + 3U;
    char *out = malloc(capacity);
    if (out == NULL) {
        return NULL;
    }
    size_t used = 0U;
    out[used++] = '"';
    for (const char *p = value; *p != '\0'; ++p) {
        if (*p == '"' || *p == '\\') {
            out[used++] = '\\';
            out[used++] = *p;
        } else if (*p == '\n') {
            out[used++] = '\\';
            out[used++] = 'n';
        } else if (*p == '\r') {
            out[used++] = '\\';
            out[used++] = 'r';
        } else if (*p == '\t') {
            out[used++] = '\\';
            out[used++] = 't';
        } else if ((unsigned char)*p < 0x20U) {
            out[used++] = ' ';
        } else {
            out[used++] = *p;
        }
    }
    out[used++] = '"';
    out[used] = '\0';
    return out;
}

static void exec_sanitized(char *const argv[])
{
    const char *path = getenv("PATH");
    char path_env[4096];
    snprintf(path_env, sizeof(path_env), "PATH=%s", path == NULL ? "" : path);
    char *envp[] = {path_env, "PYTHONDONTWRITEBYTECODE=1", NULL};
    if (strchr(argv[0], '/') != NULL) {
        execve(argv[0], argv, envp);
        _exit(127);
    }
    char search[4096];
    strncpy(search, path == NULL ? "" : path, sizeof(search) - 1U);
    search[sizeof(search) - 1U] = '\0';
    char *save = NULL;
    for (char *dir = strtok_r(search, ":", &save); dir != NULL;
         dir = strtok_r(NULL, ":", &save)) {
        char candidate[PATH_MAX];
        if (snprintf(candidate, sizeof(candidate), "%s/%s", dir, argv[0]) >=
            (int)sizeof(candidate)) {
            continue;
        }
        execve(candidate, argv, envp);
    }
    _exit(127);
}

static char *capture_command(char *const argv[],
                             const char *cwd,
                             int timeout_seconds,
                             int *exit_code,
                             bool *timed_out,
                             bool *truncated)
{
    int pipe_fds[2];
    if (pipe(pipe_fds) != 0) {
        return NULL;
    }
    pid_t pid = fork();
    if (pid < 0) {
        close(pipe_fds[0]);
        close(pipe_fds[1]);
        return NULL;
    }
    if (pid == 0) {
        close(pipe_fds[0]);
        if (cwd != NULL) {
            (void)chdir(cwd);
        }
        dup2(pipe_fds[1], STDOUT_FILENO);
        dup2(pipe_fds[1], STDERR_FILENO);
        close(pipe_fds[1]);
        exec_sanitized(argv);
    }
    close(pipe_fds[1]);
    char *buffer = calloc(1U, MAX_PROCESS_BYTES + 1U);
    if (buffer == NULL) {
        close(pipe_fds[0]);
        kill(pid, SIGKILL);
        return NULL;
    }
    time_t deadline = time(NULL) + timeout_seconds;
    size_t used = 0U;
    int status = 0;
    for (;;) {
        char chunk[4096];
        ssize_t count = read(pipe_fds[0], chunk, sizeof(chunk));
        if (count > 0) {
            size_t copy = (size_t)count;
            if (used + copy > MAX_PROCESS_BYTES) {
                copy = MAX_PROCESS_BYTES - used;
                *truncated = true;
            }
            memcpy(buffer + used, chunk, copy);
            used += copy;
        }
        pid_t done = waitpid(pid, &status, WNOHANG);
        if (done == pid) {
            break;
        }
        if (time(NULL) > deadline) {
            kill(pid, SIGKILL);
            (void)waitpid(pid, &status, 0);
            *timed_out = true;
            break;
        }
        if (count <= 0) {
            struct timespec pause = {.tv_sec = 0, .tv_nsec = 10000000L};
            nanosleep(&pause, NULL);
        }
    }
    close(pipe_fds[0]);
    buffer[used] = '\0';
    *exit_code = WIFEXITED(status) ? WEXITSTATUS(status) : 1;
    return buffer;
}

static void handle_process_result(const Toolserver__V1__ToolRequest *request,
                                  ActionResult *result,
                                  char *const argv[],
                                  const char *cwd,
                                  const char *profile_id,
                                  int timeout_seconds)
{
    int exit_code = 0;
    bool timed_out = false;
    bool truncated = false;
    time_t started = time(NULL);
    char *output = capture_command(argv, cwd, timeout_seconds, &exit_code,
                                   &timed_out, &truncated);
    if (output == NULL) {
        set_error(result, TOOLSERVER__V1__TOOL_STATUS__TOOL_STATUS_ERROR,
                  "process_failed", "process execution failed");
        return;
    }
    char *escaped_output = json_escape(output);
    free(output);
    if (escaped_output == NULL) {
        set_data(result, "process completed", NULL);
        return;
    }
    char *json = malloc(strlen(escaped_output) + 220U);
    if (json == NULL) {
        free(escaped_output);
        set_data(result, "process completed", NULL);
        return;
    }
    snprintf(json, strlen(escaped_output) + 220U,
             "{\"profile_id\":\"%s\",\"exit_code\":%d,\"duration_ms\":%ld,"
             "\"stdout\":%s,\"stderr\":\"\",\"stdout_truncated\":%s,"
             "\"stderr_truncated\":false}",
             profile_id, exit_code, (long)((time(NULL) - started) * 1000L),
             escaped_output, truncated ? "true" : "false");
    free(escaped_output);
    if (timed_out) {
        result->status = TOOLSERVER__V1__TOOL_STATUS__TOOL_STATUS_TIMEOUT;
        result->message = "process timed out";
        result->stdout_data = (uint8_t *)json;
        result->stdout_len = strlen(json);
        result->error_code = "process_timeout";
        result->error_detail = "process timed out";
        return;
    }
    (void)request;
    set_data(result, "process completed", json);
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

static void search_file(const char *workspace,
                        const char *relative,
                        const char *query,
                        size_t max_matches,
                        char **json,
                        size_t *used,
                        size_t *capacity,
                        size_t *count)
{
    if (*count >= max_matches || path_has_denied_component(relative) ||
        path_has_sensitive_component(relative)) {
        return;
    }
    char path[PATH_MAX];
    if (snprintf(path, sizeof(path), "%s/%s", workspace, relative) >=
        (int)sizeof(path)) {
        return;
    }
    struct stat st;
    if (lstat(path, &st) != 0 || !S_ISREG(st.st_mode) || S_ISLNK(st.st_mode) ||
        st.st_size > 262144L) {
        return;
    }
    FILE *file = fopen(path, "r");
    if (file == NULL) {
        return;
    }
    char line[600];
    size_t line_no = 0U;
    while (fgets(line, sizeof(line), file) != NULL && *count < max_matches) {
        ++line_no;
        if (strstr(line, query) == NULL) {
            continue;
        }
        line[strcspn(line, "\r\n")] = '\0';
        char preview[161];
        strncpy(preview, line, sizeof(preview) - 1U);
        preview[sizeof(preview) - 1U] = '\0';
        char *path_json = json_escape(relative);
        char *preview_json = json_escape(preview);
        if (path_json == NULL || preview_json == NULL) {
            free(path_json);
            free(preview_json);
            break;
        }
        char item[1024];
        snprintf(item, sizeof(item), "%s{\"path\":%s,\"line\":%zu,\"preview\":%s}",
                 *count == 0U ? "" : ",", path_json, line_no, preview_json);
        free(path_json);
        free(preview_json);
        *json = append_text(*json, used, capacity, item);
        ++(*count);
        if (*json == NULL) {
            break;
        }
    }
    fclose(file);
}

static void search_directory(const char *workspace,
                             const char *relative,
                             const char *query,
                             size_t max_matches,
                             char **json,
                             size_t *used,
                             size_t *capacity,
                             size_t *count)
{
    if (*count >= max_matches || path_has_denied_component(relative) ||
        path_has_sensitive_component(relative)) {
        return;
    }
    char path[PATH_MAX];
    if (snprintf(path, sizeof(path), "%s/%s", workspace, relative) >=
        (int)sizeof(path)) {
        return;
    }
    DIR *dir = opendir(path);
    if (dir == NULL) {
        return;
    }
    for (struct dirent *entry = readdir(dir); entry != NULL && *count < max_matches;
         entry = readdir(dir)) {
        if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0 ||
            entry->d_name[0] == '.') {
            continue;
        }
        char child[PATH_MAX];
        const char *prefix = strcmp(relative, ".") == 0 ? "" : relative;
        if (snprintf(child, sizeof(child), "%s%s%s", prefix,
                     *prefix == '\0' ? "" : "/", entry->d_name) >=
            (int)sizeof(child)) {
            continue;
        }
        char full[PATH_MAX];
        if (snprintf(full, sizeof(full), "%s/%s", workspace, child) >=
            (int)sizeof(full)) {
            continue;
        }
        struct stat st;
        if (lstat(full, &st) != 0 || S_ISLNK(st.st_mode)) {
            continue;
        }
        if (S_ISDIR(st.st_mode)) {
            search_directory(workspace, child, query, max_matches,
                             json, used, capacity, count);
        } else if (S_ISREG(st.st_mode)) {
            search_file(workspace, child, query, max_matches, json, used,
                        capacity, count);
        }
    }
    closedir(dir);
}

static void handle_search_text(const Toolserver__V1__ToolRequest *request,
                               ActionResult *result)
{
    char target[PATH_MAX], workspace[PATH_MAX];
    const char *query = arg_value(request, "query");
    size_t max_matches = 20U;
    if (query == NULL || *query == '\0' || strlen(query) > 256U ||
        !parse_size(arg_value(request, "max_matches"), 20U, 100U, &max_matches) ||
        !resolve_target(request, target) ||
        realpath(request->workspace_id, workspace) == NULL) {
        set_error(result, TOOLSERVER__V1__TOOL_STATUS__TOOL_STATUS_DENIED,
                  "path_denied", "path denied");
        return;
    }
    size_t used = 0U, capacity = 512U, count = 0U;
    char *json = calloc(1U, capacity);
    json = append_text(json, &used, &capacity, "{\"matches\":[");
    const char *relative = arg_value(request, "path");
    struct stat st;
    if (stat(target, &st) == 0 && S_ISREG(st.st_mode)) {
        search_file(workspace, relative, query, max_matches, &json, &used, &capacity,
                    &count);
    } else {
        search_directory(workspace, relative, query, max_matches, &json, &used,
                         &capacity, &count);
    }
    char tail[64];
    snprintf(tail, sizeof(tail), "],\"truncated\":false}");
    json = append_text(json, &used, &capacity, tail);
    set_data(result, "text searched", json);
}

static void handle_git_status(const Toolserver__V1__ToolRequest *request,
                              ActionResult *result)
{
    char target[PATH_MAX];
    size_t max_entries = 200U;
    if (!resolve_target(request, target) ||
        !parse_size(arg_value(request, "max_entries"), 200U, 1000U, &max_entries)) {
        set_error(result, TOOLSERVER__V1__TOOL_STATUS__TOOL_STATUS_DENIED,
                  "path_denied", "path denied");
        return;
    }
    (void)max_entries;
    char *argv[] = {"git", "-c", "core.hooksPath=/dev/null", "-c", "core.pager=cat",
                    "status", "--porcelain=v1", NULL};
    int exit_code = 0;
    bool timed_out = false, truncated = false;
    char *output = capture_command(argv, target, 30, &exit_code, &timed_out, &truncated);
    if (output == NULL || timed_out || exit_code != 0) {
        free(output);
        set_error(result, TOOLSERVER__V1__TOOL_STATUS__TOOL_STATUS_ERROR,
                  "git_status_error", "git status failed");
        return;
    }
    char *escaped = json_escape(output);
    free(output);
    size_t size = strlen(escaped == NULL ? "\"\"" : escaped) + 80U;
    char *json = malloc(size);
    if (json == NULL) {
        free(escaped);
        set_data(result, "git status", NULL);
        return;
    }
    snprintf(json, size, "{\"repository\":\".\",\"entries_text\":%s,\"truncated\":%s}",
             escaped == NULL ? "\"\"" : escaped, truncated ? "true" : "false");
    free(escaped);
    set_data(result, "git status", json);
}

static void handle_git_diff(const Toolserver__V1__ToolRequest *request,
                            ActionResult *result)
{
    char target[PATH_MAX];
    const char *scope = arg_value(request, "scope");
    size_t max_bytes = 16384U;
    if (!resolve_target(request, target) || scope == NULL ||
        (strcmp(scope, "worktree") != 0 && strcmp(scope, "staged") != 0) ||
        !parse_size(arg_value(request, "max_bytes"), 16384U, 65536U, &max_bytes)) {
        set_error(result, TOOLSERVER__V1__TOOL_STATUS__TOOL_STATUS_DENIED,
                  "path_denied", "path denied");
        return;
    }
    char *argv_worktree[] = {"git", "-c", "core.hooksPath=/dev/null", "-c",
                             "core.pager=cat", "diff", "--no-ext-diff",
                             "--no-color", NULL};
    char *argv_staged[] = {"git", "-c", "core.hooksPath=/dev/null", "-c",
                           "core.pager=cat", "diff", "--no-ext-diff",
                           "--no-color", "--cached", NULL};
    char **argv = strcmp(scope, "staged") == 0 ? argv_staged : argv_worktree;
    int exit_code = 0;
    bool timed_out = false, truncated = false;
    char *output = capture_command(argv, target, 30, &exit_code, &timed_out, &truncated);
    if (output == NULL || timed_out || exit_code != 0) {
        free(output);
        set_error(result, TOOLSERVER__V1__TOOL_STATUS__TOOL_STATUS_ERROR,
                  "git_diff_error", "git diff failed");
        return;
    }
    output[max_bytes] = '\0';
    char *escaped = json_escape(output);
    free(output);
    size_t size = strlen(escaped == NULL ? "\"\"" : escaped) + 100U;
    char *json = malloc(size);
    if (json == NULL) {
        free(escaped);
        set_data(result, "git diff", NULL);
        return;
    }
    snprintf(json, size, "{\"repository\":\".\",\"scope\":\"%s\",\"diff\":%s,"
             "\"truncated\":%s}", scope, escaped == NULL ? "\"\"" : escaped,
             truncated ? "true" : "false");
    free(escaped);
    set_data(result, "git diff", json);
}

static void handle_profile_process(const Toolserver__V1__ToolRequest *request,
                                   ActionResult *result)
{
    char target[PATH_MAX];
    const char *profile_id = arg_value(request, "profile_id");
    if (!resolve_target(request, target) || profile_id == NULL) {
        set_error(result, TOOLSERVER__V1__TOOL_STATUS__TOOL_STATUS_DENIED,
                  "path_denied", "path denied");
        return;
    }
    if (strcmp(profile_id, "python-compile") == 0) {
        char *argv[] = {"python", "-m", "compileall", "-q", "ai_assistant",
                        "main.py", NULL};
        handle_process_result(request, result, argv, target, profile_id, 180);
        return;
    }
    if (strcmp(profile_id, "core-tests") == 0) {
        char *argv[] = {"python", "-m", "pytest", "-m",
                        "not ollama and not toolserver", "-q", NULL};
        handle_process_result(request, result, argv, target, profile_id, 120);
        return;
    }
    if (strcmp(profile_id, "c-toolserver-tests") == 0) {
        char *argv[] = {"python", "-m", "pytest", "-m", "toolserver", "-q", NULL};
        handle_process_result(request, result, argv, target, profile_id, 120);
        return;
    }
    set_error(result, TOOLSERVER__V1__TOOL_STATUS__TOOL_STATUS_DENIED,
              "unknown_profile", "unknown profile");
}

static void handle_write(const Toolserver__V1__ToolRequest *request,
                         ActionResult *result)
{
    const char *mode = arg_value(request, "mode");
    const char *content = arg_value(request, "content");
    const char *expected = arg_value(request, "expected_sha256");
    if (mode == NULL || content == NULL ||
        (strcmp(mode, "create") != 0 && strcmp(mode, "replace") != 0) ||
        (expected != NULL && !valid_sha256_hex(expected))) {
        set_error(result, TOOLSERVER__V1__TOOL_STATUS__TOOL_STATUS_INVALID_ARGUMENT,
                  "invalid_arguments", "invalid write arguments");
        return;
    }
    size_t content_len = strlen(content);
    if (content_len > MAX_WRITE_BYTES ||
        !valid_utf8((const unsigned char *)content, content_len)) {
        set_error(result, TOOLSERVER__V1__TOOL_STATUS__TOOL_STATUS_DENIED,
                  "content_denied", "content denied");
        return;
    }
    char workspace[PATH_MAX], target[PATH_MAX], parent[PATH_MAX];
    if (!resolve_write_target(request, workspace, target, parent)) {
        set_error(result, TOOLSERVER__V1__TOOL_STATUS__TOOL_STATUS_DENIED,
                  "path_denied", "path denied");
        return;
    }
    struct stat st;
    bool exists = lstat(target, &st) == 0;
    if (exists && S_ISLNK(st.st_mode)) {
        set_error(result, TOOLSERVER__V1__TOOL_STATUS__TOOL_STATUS_DENIED,
                  "path_denied", "path denied");
        return;
    }
    if (strcmp(mode, "create") == 0 && exists) {
        set_error(result, TOOLSERVER__V1__TOOL_STATUS__TOOL_STATUS_INVALID_ARGUMENT,
                  "path_exists", "path already exists");
        return;
    }
    if (strcmp(mode, "replace") == 0 && (!exists || !S_ISREG(st.st_mode))) {
        set_error(result, TOOLSERVER__V1__TOOL_STATUS__TOOL_STATUS_INVALID_ARGUMENT,
                  "invalid_path", "path must be a regular file");
        return;
    }
    char before_hash[65] = "";
    if (exists && !file_sha256_hex(target, before_hash)) {
        set_error(result, TOOLSERVER__V1__TOOL_STATUS__TOOL_STATUS_ERROR,
                  "hash_failed", "file hash failed");
        return;
    }
    if (expected != NULL && strcmp(expected, before_hash) != 0) {
        set_error(result, TOOLSERVER__V1__TOOL_STATUS__TOOL_STATUS_DENIED,
                  "hash_mismatch", "expected hash did not match");
        return;
    }
    char temp_path[PATH_MAX];
    if (snprintf(temp_path, sizeof(temp_path), "%s/.blacksmith-write.XXXXXX", parent) >=
        (int)sizeof(temp_path)) {
        set_error(result, TOOLSERVER__V1__TOOL_STATUS__TOOL_STATUS_ERROR,
                  "temp_failed", "temporary path failed");
        return;
    }
    int fd = mkstemp(temp_path);
    if (fd < 0) {
        set_error(result, TOOLSERVER__V1__TOOL_STATUS__TOOL_STATUS_ERROR,
                  "temp_failed", "temporary file failed");
        return;
    }
    size_t total = 0U;
    while (total < content_len) {
        ssize_t written = write(fd, content + total, content_len - total);
        if (written <= 0) {
            close(fd);
            unlink(temp_path);
            set_error(result, TOOLSERVER__V1__TOOL_STATUS__TOOL_STATUS_ERROR,
                      "write_failed", "file write failed");
            return;
        }
        total += (size_t)written;
    }
    if (fsync(fd) != 0 || close(fd) != 0) {
        unlink(temp_path);
        set_error(result, TOOLSERVER__V1__TOOL_STATUS__TOOL_STATUS_ERROR,
                  "write_failed", "file write failed");
        return;
    }
    int commit_status = 0;
    if (strcmp(mode, "create") == 0) {
        commit_status = link(temp_path, target);
        unlink(temp_path);
    } else {
        commit_status = rename(temp_path, target);
    }
    if (commit_status != 0) {
        unlink(temp_path);
        set_error(result, TOOLSERVER__V1__TOOL_STATUS__TOOL_STATUS_ERROR,
                  "rename_failed", "atomic rename failed");
        return;
    }
    int dir_fd = open(parent, O_RDONLY);
    if (dir_fd >= 0) {
        (void)fsync(dir_fd);
        close(dir_fd);
    }
    char after_hash[65];
    sha256_hex((const uint8_t *)content, content_len, after_hash);
    char *escaped_path = json_escape(arg_value(request, "path"));
    size_t size = strlen(escaped_path == NULL ? "\"\"" : escaped_path) + 320U;
    char *json = malloc(size);
    if (json == NULL) {
        free(escaped_path);
        set_data(result, "file written", NULL);
        return;
    }
    if (exists) {
        snprintf(json, size,
                 "{\"mode\":\"%s\",\"path\":%s,\"bytes_written\":%zu,"
                 "\"before_sha256\":\"%s\",\"after_sha256\":\"%s\"}",
                 mode, escaped_path == NULL ? "\"\"" : escaped_path, content_len,
                 before_hash, after_hash);
    } else {
        snprintf(json, size,
                 "{\"mode\":\"%s\",\"path\":%s,\"bytes_written\":%zu,"
                 "\"before_sha256\":null,\"after_sha256\":\"%s\"}",
                 mode, escaped_path == NULL ? "\"\"" : escaped_path, content_len,
                 after_hash);
    }
    free(escaped_path);
    set_data(result, "file written", json);
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
    if (strcmp(request->tool_name, "search_text") == 0) {
        handle_search_text(request, result);
        return;
    }
    if (strcmp(request->tool_name, "git_status") == 0) {
        handle_git_status(request, result);
        return;
    }
    if (strcmp(request->tool_name, "git_diff") == 0) {
        handle_git_diff(request, result);
        return;
    }
    if (strcmp(request->tool_name, "run_tests") == 0 ||
        strcmp(request->tool_name, "build_project") == 0) {
        handle_profile_process(request, result);
        return;
    }
    if (strcmp(request->tool_name, "write") == 0) {
        handle_write(request, result);
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
