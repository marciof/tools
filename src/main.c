#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include "Ls_Plugin.h"
#include "Options.h"
#include "std/array.h"


int main(int argc, char* argv[]) {
    Plugin* plugins[] = {
        &Ls_Plugin,
        NULL
    };

    Error error;
    Options options = Options_parse(argc, argv, plugins, &error);

    if (error) {
        fprintf(stderr, "%s\n", error);
        return EXIT_FAILURE;
    }

    if (options.optind < 0) {
        Options_delete(options);
        return EXIT_SUCCESS;
    }

    for (size_t i = 0; i < STATIC_ARRAY_LENGTH(plugins); ++i) {
        const char* name = plugins[i]->get_name();
        bool is_enabled = Options_is_plugin_enabled(options, name, &error);

        if (error) {
            Options_delete(options);
            fprintf(stderr, "%s\n", error);
            return EXIT_FAILURE;
        }

        if (!is_enabled) {
            continue;
        }

        List plugin_options = Options_get_plugin_options(options, name);

        int output_fd = plugins[i]->run(
            argc - options.optind,
            argv + options.optind,
            plugin_options,
            &error);

        if (error) {
            Options_delete(options);
            fprintf(stderr, "%s\n", error);
            return EXIT_FAILURE;
        }

        ssize_t nr_bytes_read;
        const int BUFFER_SIZE = 256;
        char buffer[BUFFER_SIZE + 1];

        while ((nr_bytes_read = read(output_fd, buffer, BUFFER_SIZE)) > 0) {
            buffer[nr_bytes_read] = '\0';
            fputs(buffer, stdout);
        }

        Options_delete(options);
        return EXIT_SUCCESS;
    }

    Options_delete(options);
    fputs("No working enabled plugin found.\n", stderr);
    return EXIT_FAILURE;
}
