#include "server.h"

#include "actions.h"
#include "framing.h"

#include <errno.h>
#include <signal.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/un.h>
#include <unistd.h>

static volatile sig_atomic_t should_stop = 0;

static void handle_signal(int signum)
{
    (void)signum;
    should_stop = 1;
}

static int configure_signal_handlers(void)
{
    struct sigaction action;
    memset(&action, 0, sizeof(action));
    action.sa_handler = handle_signal;

    if (sigaction(SIGINT, &action, NULL) != 0) {
        return -1;
    }
    if (sigaction(SIGTERM, &action, NULL) != 0) {
        return -1;
    }
    return 0;
}

static int create_listener(const ServerConfig *config)
{
    int fd = socket(AF_UNIX, SOCK_STREAM, 0);
    if (fd < 0) {
        perror("socket");
        return -1;
    }

    struct sockaddr_un address;
    memset(&address, 0, sizeof(address));
    address.sun_family = AF_UNIX;
    if (strlen(config->socket_path) >= sizeof(address.sun_path)) {
        fprintf(stderr, "socket path is too long\n");
        close(fd);
        return -1;
    }
    strncpy(address.sun_path, config->socket_path, sizeof(address.sun_path) - 1U);

    unlink(config->socket_path);
    if (bind(fd, (struct sockaddr *)&address, sizeof(address)) != 0) {
        perror("bind");
        close(fd);
        return -1;
    }
    if (chmod(config->socket_path, 0600) != 0) {
        perror("chmod");
        close(fd);
        return -1;
    }
    if (listen(fd, config->backlog) != 0) {
        perror("listen");
        close(fd);
        return -1;
    }
    return fd;
}

static uint8_t *pack_response(const Toolserver__V1__ToolResponse *response,
                              size_t *response_len)
{
    *response_len = toolserver__v1__tool_response__get_packed_size(response);
    uint8_t *buffer = malloc(*response_len);
    if (buffer == NULL) {
        return NULL;
    }
    toolserver__v1__tool_response__pack(response, buffer);
    return buffer;
}

static int send_response(int client_fd,
                         const Toolserver__V1__ToolRequest *request,
                         const ActionResult *result)
{
    Toolserver__V1__ToolError error = TOOLSERVER__V1__TOOL_ERROR__INIT;
    Toolserver__V1__ToolResponse response = TOOLSERVER__V1__TOOL_RESPONSE__INIT;

    response.request_id = request->request_id;
    response.status = result->status;
    response.message = (char *)result->message;
    response.stdout_data.len = strlen(result->stdout_text);
    response.stdout_data.data = (uint8_t *)result->stdout_text;
    response.exit_code = result->status == TOOLSERVER__V1__TOOL_STATUS__TOOL_STATUS_OK
                             ? 0
                             : 1;

    if (result->status != TOOLSERVER__V1__TOOL_STATUS__TOOL_STATUS_OK) {
        error.code = (char *)result->error_code;
        error.detail = (char *)result->error_detail;
        error.source = "c_toolserver";
        response.error = &error;
    }

    size_t response_len = 0;
    uint8_t *payload = pack_response(&response, &response_len);
    if (payload == NULL) {
        return -1;
    }

    FrameStatus status = write_frame(client_fd, payload, response_len);
    free(payload);
    return status == FRAME_STATUS_OK ? 0 : -1;
}

static int handle_client(int client_fd)
{
    uint8_t *payload = NULL;
    size_t payload_len = 0;
    FrameStatus frame_status = read_frame(client_fd, &payload, &payload_len);
    if (frame_status != FRAME_STATUS_OK) {
        return frame_status == FRAME_STATUS_CLOSED ? 0 : -1;
    }

    Toolserver__V1__ToolRequest *request =
        toolserver__v1__tool_request__unpack(NULL, payload_len, payload);
    free(payload);
    if (request == NULL) {
        return -1;
    }

    ActionResult result;
    handle_tool_request(request, &result);
    int status = send_response(client_fd, request, &result);
    toolserver__v1__tool_request__free_unpacked(request, NULL);
    return status;
}

int run_server(const ServerConfig *config)
{
    if (configure_signal_handlers() != 0) {
        perror("sigaction");
        return 1;
    }

    int listener_fd = create_listener(config);
    if (listener_fd < 0) {
        return 1;
    }

    while (!should_stop) {
        int client_fd = accept(listener_fd, NULL, NULL);
        if (client_fd < 0 && errno == EINTR) {
            continue;
        }
        if (client_fd < 0) {
            perror("accept");
            break;
        }
        if (handle_client(client_fd) != 0) {
            fprintf(stderr, "failed to handle client request\n");
        }
        close(client_fd);
    }

    close(listener_fd);
    unlink(config->socket_path);
    return 0;
}

