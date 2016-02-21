#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include "Options.h"
#include "plugin/Ls_Plugin.h"
#include "plugin/Pipe_Plugin.h"
#include "std/array.h"


int main(int argc, char* argv[]) {
    Plugin* plugins[] = {
        &Pipe_Plugin,
        &Ls_Plugin,
    };

    Error error;
    Options options = Options_parse(
        argc, argv, plugins, STATIC_ARRAY_LENGTH(plugins), &error);

    if (error) {
        fprintf(stderr, "%s\n", error);
        return EXIT_FAILURE;
    }

    if (options.optind < 0) {
        Options_delete(options);
        return EXIT_SUCCESS;
    }

    int exit_status = EXIT_FAILURE;

    for (size_t i = 0; i < STATIC_ARRAY_LENGTH(plugins); ++i) {
        Plugin* plugin = plugins[i];

        if (!plugin) {
            continue;
        }

        const char* name = plugin->get_name();
        List plugin_options = Options_get_plugin_options(options, name);

        int output_fd = plugin->run(
            argc - options.optind,
            argv + options.optind,
            plugin_options,
            &error);

        if (error) {
            fprintf(stderr, "%s: %s\n", name, error);
            continue;
        }
        if (output_fd == PLUGIN_INVALID_FD_OUT) {
            continue;
        }

        ssize_t nr_bytes_read;
        const int BUFFER_SIZE = 256;
        char buffer[BUFFER_SIZE + 1];

        while ((nr_bytes_read = read(output_fd, buffer, BUFFER_SIZE)) > 0) {
            buffer[nr_bytes_read] = '\0';
            fputs(buffer, stdout);
        }

        exit_status = EXIT_SUCCESS;
    }

    Options_delete(options);
    return exit_status;
}
