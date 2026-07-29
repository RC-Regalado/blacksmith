#ifndef BLACKSMITH_SERVER_H
#define BLACKSMITH_SERVER_H

typedef struct ServerConfig {
    const char *socket_path;
    int backlog;
} ServerConfig;

int run_server(const ServerConfig *config);

#endif

