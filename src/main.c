#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include "list/Array_List.h"
#include "Options.h"
#include "plugin/Ls_Plugin.h"
#include "plugin/Pipe_Plugin.h"
#include "std/array.h"


static Plugin* plugins[] = {
    &Cat_Plugin,
    &Ls_Plugin,
};


static void cleanup(List fds_in, Error error) {
    if (error) {
        fprintf(stderr, "%s\n", error);
    }

    Error discard;
    List_delete(fds_in, &discard);

    for (size_t i = 0; i < STATIC_ARRAY_LENGTH(plugins); ++i) {
        if (plugins[i]) {
            List_delete(plugins[i]->options, &discard);
            plugins[i] = NULL;
        }
    }
}


static List list_input_fds(Error* error) {
    List fds_in = List_new(Array_List, error);

    if (*error) {
        return NULL;
    }

    List_add(fds_in, STDIN_FILENO, error);

    if (*error) {
        Error discard;
        List_delete(fds_in, &discard);
        return NULL;
    }

    *error = NULL;
    return fds_in;
}


int main(int argc, char* argv[]) {
    Error error;
    int optind = Options_parse(
        argc, argv, plugins, STATIC_ARRAY_LENGTH(plugins), &error);

    if (error) {
        cleanup(NULL, error);
        return EXIT_FAILURE;
    }

    if (optind < 0) {
        cleanup(NULL, NULL);
        return EXIT_SUCCESS;
    }

    List fds_in = list_input_fds(&error);

    if (error) {
        cleanup(NULL, error);
        return EXIT_FAILURE;
    }

    for (size_t i = 0; i < STATIC_ARRAY_LENGTH(plugins); ++i) {
        if (plugins[i]) {
            List new_fds_in = plugins[i]->run(
                fds_in,
                argc - optind,
                argv + optind,
                plugins[i]->options,
                &error);

            if (error) {
                fprintf(stderr, "%s: %s\n", plugins[i]->get_name(), error);
                cleanup(fds_in, NULL);
                return EXIT_FAILURE;
            }

            if (new_fds_in != fds_in) {
                List_delete(fds_in, &error);
                fds_in = new_fds_in;

                if (error) {
                    cleanup(new_fds_in, error);
                    return EXIT_FAILURE;
                }
            }
        }
    }

    Iterator it = List_iterator(fds_in, &error);

    if (error) {
        cleanup(fds_in, error);
        return EXIT_FAILURE;
    }

    while (Iterator_has_next(it)) {
        Error discard;
        int fd_in = (int) Iterator_next(it, &discard);

        ssize_t nr_bytes_read;
        const int BUFFER_SIZE = 256;
        char buffer[BUFFER_SIZE + 1];

        while ((nr_bytes_read = read(fd_in, buffer, BUFFER_SIZE)) > 0) {
            buffer[nr_bytes_read] = '\0';
            fputs(buffer, stdout);
        }
    }

    Iterator_delete(it);
    cleanup(fds_in, NULL);
    return EXIT_SUCCESS;
}
