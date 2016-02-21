#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include "Options.h"
#include "plugin/Cat_Plugin.h"
#include "plugin/Ls_Plugin.h"
#include "std/array.h"


static void cleanup_plugins(Plugin* plugins[], size_t nr_plugins) {
    for (size_t i = 0; i < nr_plugins; ++i) {
        if (plugins[i]) {
            Error discard;
            List_delete(plugins[i]->options, &discard);
            plugins[i] = NULL;
        }
    }
}


int main(int argc, char* argv[]) {
    Error error;

    Plugin* plugins[] = {
        &Cat_Plugin,
        &Ls_Plugin,
    };

    int optind = Options_parse(
        argc, argv, plugins, STATIC_ARRAY_LENGTH(plugins), &error);

    if (error) {
        cleanup_plugins(plugins, STATIC_ARRAY_LENGTH(plugins));
        fprintf(stderr, "%s\n", error);
        return EXIT_FAILURE;
    }

    if (optind < 0) {
        cleanup_plugins(plugins, STATIC_ARRAY_LENGTH(plugins));
        return EXIT_SUCCESS;
    }

    int pipe = STDIN_FILENO;

    for (size_t i = 0; i < STATIC_ARRAY_LENGTH(plugins); ++i) {
        if (plugins[i]) {
            pipe = plugins[i]->run(
                pipe,
                argc - optind,
                argv + optind,
                plugins[i]->options,
                &error);

            if (error) {
                fprintf(stderr, "%s: %s\n", plugins[i]->get_name(), error);
                continue;
            }
        }
    }

    if (pipe == PLUGIN_INVALID_FD_OUT) {
        cleanup_plugins(plugins, STATIC_ARRAY_LENGTH(plugins));
        return EXIT_FAILURE;
    }

    ssize_t nr_bytes_read;
    const int BUFFER_SIZE = 256;
    char buffer[BUFFER_SIZE + 1];

    while ((nr_bytes_read = read(pipe, buffer, BUFFER_SIZE)) > 0) {
        buffer[nr_bytes_read] = '\0';
        fputs(buffer, stdout);
    }

    cleanup_plugins(plugins, STATIC_ARRAY_LENGTH(plugins));
    return EXIT_SUCCESS;
}
