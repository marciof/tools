#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include "Options.h"
#include "plugin/File_Plugin.h"
#include "plugin/Ls_Plugin.h"
#include "plugin/Pipe_Plugin.h"
#include "std/array.h"


static Plugin* plugins[] = {
    &Pipe_Plugin,
    &File_Plugin,
    &Ls_Plugin,
};


static void cleanup(List args, List fds_in, Error error) {
    if (error) {
        fprintf(stderr, "%s\n", error);
    }

    List_delete(args, NULL);
    List_delete(fds_in, NULL);

    for (size_t i = 0; i < STATIC_ARRAY_LENGTH(plugins); ++i) {
        if (plugins[i]) {
            List_delete(plugins[i]->options, NULL);
            plugins[i] = NULL;
        }
    }
}


static List list_input_fds(Error* error) {
    List fds_in = List_create(error);

    if (Error_has(error)) {
        return NULL;
    }

    List_add(fds_in, STDIN_FILENO, error);

    if (Error_has(error)) {
        List_delete(fds_in, error);
        return NULL;
    }

    Error_clear(error);
    return fds_in;
}


int main(int argc, char* argv[]) {
    Error error;
    List args = Options_parse(
        argc, argv, plugins, STATIC_ARRAY_LENGTH(plugins), &error);

    if (error) {
        cleanup(NULL, NULL, error);
        return EXIT_FAILURE;
    }

    if (args == NULL) {
        cleanup(NULL, NULL, NULL);
        return EXIT_SUCCESS;
    }

    List fds_in = list_input_fds(&error);

    if (error) {
        cleanup(args, NULL, error);
        return EXIT_FAILURE;
    }

    for (size_t i = 0; i < STATIC_ARRAY_LENGTH(plugins); ++i) {
        if (plugins[i]) {
            Plugin_Result result = plugins[i]->run(
                args,
                plugins[i]->options,
                fds_in,
                &error);

            if (error) {
                fprintf(stderr, "%s: %s\n", plugins[i]->get_name(), error);
                cleanup(args, fds_in, NULL);
                return EXIT_FAILURE;
            }

            if (result.args && (result.args != args)) {
                List_delete(args, NULL);
                args = result.args;
            }

            if (result.fds_in && (result.fds_in != fds_in)) {
                List_delete(fds_in, NULL);
                fds_in = result.fds_in;
            }
        }
    }

    Iterator it = List_iterator(fds_in, &error);

    if (error) {
        cleanup(args, fds_in, error);
        return EXIT_FAILURE;
    }

    while (Iterator_has_next(it)) {
        int fd_in = (int) Iterator_next(it, NULL);
        ssize_t nr_bytes_read;
        const int BUFFER_SIZE = 256;
        char buffer[BUFFER_SIZE + 1];

        while ((nr_bytes_read = read(fd_in, buffer, BUFFER_SIZE)) > 0) {
            buffer[nr_bytes_read] = '\0';
            fputs(buffer, stdout);
        }
    }

    Iterator_delete(it);
    cleanup(args, fds_in, NULL);
    return EXIT_SUCCESS;
}
