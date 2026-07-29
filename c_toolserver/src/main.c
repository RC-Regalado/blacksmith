#include "server.h"

#include <stdio.h>
#include <string.h>

static void print_usage(const char *program)
{
    fprintf(stderr, "usage: %s --socket <path>\n", program);
}

static const char *parse_socket_path(int argc, char **argv)
{
    for (int i = 1; i < argc - 1; ++i) {
        if (strcmp(argv[i], "--socket") == 0) {
            return argv[i + 1];
        }
    }
    return NULL;
}

int main(int argc, char **argv)
{
    const char *socket_path = parse_socket_path(argc, argv);
    if (socket_path == NULL) {
        print_usage(argv[0]);
        return 2;
    }

    ServerConfig config = {
        .socket_path = socket_path,
        .backlog = 8,
    };

    return run_server(&config);
}

