#define _POSIX_C_SOURCE 200809L
#include <errno.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include "Array.h"
#include "io.h"
#include "options.h"
#include "plugin/File_Plugin.h"
#include "plugin/Ls_Plugin.h"
#include "plugin/Pager_Plugin.h"
#include "plugin/Pipe_Plugin.h"

static Plugin* plugins[] = {
    &Pipe_Plugin,
    &File_Plugin,
    &Ls_Plugin,
    &Pager_Plugin,
};

static void cleanup(Array* inputs, Array* outputs, Error* error) {
    if (ERROR_HAS(error)) {
        fprintf(stderr, "%s\n", *error);
    }

    if (inputs != NULL) {
        for (size_t i = 0; i < inputs->length; ++i) {
            Input_delete((Input*) inputs->data[i]);
        }
        Array_delete(inputs);
    }

    if (outputs != NULL) {
        for (size_t i = 0; i < outputs->length; ++i) {
            Output* output = (Output*) outputs->data[i];

            output->close(output->arg, error);
            Output_delete(output);

            if (ERROR_HAS(error)) {
                fprintf(stderr, "%s\n", *error);
            }
        }
        Array_delete(outputs);
    }

    for (size_t i = 0; i < STATIC_ARRAY_LENGTH(plugins); ++i) {
        if (plugins[i] != NULL) {
            Array_delete(plugins[i]->options);
            plugins[i] = NULL;
        }
    }
}

static void flush_input(int input_fd, Array* outputs, Error* error) {
    const int LENGTH = 4 * 1024;
    char buffer[LENGTH];
    ssize_t bytes_read;

    while ((bytes_read = read(input_fd, buffer, LENGTH * sizeof(char))) > 0) {
        char* data = buffer;
        size_t length = (size_t) (bytes_read / sizeof(char));

        for (size_t i = 0; (i < outputs->length) && (data != NULL); ++i) {
            Output* output = (Output*) outputs->data[i];
            output->write(output->arg, &data, &length, error);

            if (ERROR_HAS(error)) {
                return;
            }
        }

        if (data != NULL) {
            io_write(STDOUT_FILENO, data, length, error);
            if (ERROR_HAS(error)) {
                return;
            }
        }
    }

    if ((bytes_read == 0) || (errno == EIO)) {
        ERROR_CLEAR(error);
    }
    else {
        ERROR_ERRNO(error, errno);
    }
}

int main(int argc, char* argv[]) {
    Error error;
    Array* inputs = parse_options(
        argc, argv, plugins, STATIC_ARRAY_LENGTH(plugins), &error);

    if (inputs == NULL) {
        cleanup(NULL, NULL, &error);
        return EXIT_SUCCESS;
    }

    Array* outputs = Array_new(&error, NULL);

    if (ERROR_HAS(&error)) {
        cleanup(inputs, NULL, &error);
        return EXIT_FAILURE;
    }

    for (size_t i = 0; i < STATIC_ARRAY_LENGTH(plugins); ++i) {
        if (plugins[i] != NULL) {
            plugins[i]->run(inputs, plugins[i]->options, outputs, &error);

            if (ERROR_HAS(&error)) {
                cleanup(inputs, outputs, &error);
                return EXIT_FAILURE;
            }
        }
    }

    for (size_t i = 0; i < inputs->length; ++i) {
        Input* input = (Input*) inputs->data[i];

        if (input != NULL) {
            int input_fd = input->fd;

            if (input_fd == IO_INVALID_FD) {
                fprintf(stderr, "Unsupported input: %s\n", input->name);
            }
            else {
                flush_input(input_fd, outputs, &error);
                close(input_fd);

                if (ERROR_HAS(&error)) {
                    cleanup(inputs, outputs, &error);
                    return EXIT_FAILURE;
                }
            }
        }
    }

    cleanup(inputs, outputs, &error);
    return EXIT_SUCCESS;
}
