#define _POSIX_C_SOURCE 200809L
#include <errno.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include "Array.h"
#include "io.h"
#include "options.h"
#include "plugin/File.h"
#include "plugin/Pager.h"
#include "plugin/Ls.h"
#include "plugin/Pipe.h"

static Plugin* plugins[] = {
    &Pipe_Plugin,
    &File_Plugin,
    &Ls_Plugin,
    &Pager_Plugin,
};

static void cleanup(Array* inputs, Array* outputs, Error* error) {
    if (ERROR_HAS(error) && (*error != ERROR_UNSPECIFIED)) {
        fprintf(stderr, "%s\n", *error);
    }

    if (inputs != NULL) {
        for (size_t i = 0; i < inputs->length; ++i) {
            if (inputs->data[i] != (intptr_t) NULL) {
                Input_delete((Input*) inputs->data[i]);
            }
        }
        Array_deinit(inputs);
    }

    if (outputs != NULL) {
        for (size_t i = 0; i < outputs->length; ++i) {
            Output* output = (Output*) outputs->data[i];

            output->close(output, error);
            Output_delete(output);

            if (ERROR_HAS(error) && (*error != ERROR_UNSPECIFIED)) {
                fprintf(stderr, "%s\n", *error);
            }
        }
        Array_deinit(outputs);
    }

    for (size_t i = 0; i < STATIC_ARRAY_LENGTH(plugins); ++i) {
        if (plugins[i] != NULL) {
            Array_deinit(&plugins[i]->options);
            plugins[i] = NULL;
        }
    }
}

static void flush_input(int fd, Array* outputs, Error* error) {
    const int MAX_LEN = 4 * 1024;
    Buffer* buffer = Buffer_new(MAX_LEN, error);
    ssize_t bytes_read;

    if (ERROR_HAS(error)) {
        return;
    }

    while ((bytes_read = read(fd, buffer->data, MAX_LEN * sizeof(char))) > 0) {
        buffer->length = (size_t) (bytes_read / sizeof(char));
        bool has_flushed = false;

        for (size_t i = 0; i < outputs->length; ++i) {
            Output* output = (Output*) outputs->data[i];
            output->write(output, &buffer, error);

            if (ERROR_HAS(error)) {
                Buffer_delete(buffer);
                return;
            }

            if (buffer == NULL) {
                buffer = Buffer_new(MAX_LEN, error);
                if (ERROR_HAS(error)) {
                    return;
                }
                has_flushed = true;
                break;
            }

            if (buffer->length == 0) {
                has_flushed = true;
                break;
            }
        }

        if (!has_flushed) {
            io_write(STDOUT_FILENO, buffer, error);
            if (ERROR_HAS(error)) {
                Buffer_delete(buffer);
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

    Buffer_delete(buffer);
}

static bool flush_inputs(Array* inputs, Array* outputs, Error* error) {
    bool has_plugin_failed = false;

    for (size_t i = 0; i < inputs->length; ++i) {
        Input* input = (Input*) inputs->data[i];

        if (input == NULL) {
            continue;
        }

        int input_fd = input->fd;

        if (input_fd == IO_INVALID_FD) {
            has_plugin_failed = true;
            fprintf(stderr, "Unsupported input: %s\n", input->name);
            continue;
        }

        flush_input(input_fd, outputs, error);

        if (ERROR_HAS(error)) {
            return true;
        }

        if (input->close == NULL) {
            io_close(input->fd, error);
        }
        else {
            input->close(input, error);
        }

        if (ERROR_HAS(error)) {
            return true;
        }
    }

    return has_plugin_failed;
}

int main(int argc, char* argv[]) {
    Error error;
    Array inputs, outputs;

    Array_init(&inputs, &error, NULL);

    if (ERROR_HAS(&error)) {
        cleanup(NULL, NULL, &error);
        return EXIT_FAILURE;
    }

    bool has_shown_help = parse_options(
        argc, argv, plugins, STATIC_ARRAY_LENGTH(plugins), &inputs, &error);

    if (has_shown_help || ERROR_HAS(&error)) {
        cleanup(&inputs, NULL, &error);
        return has_shown_help ? EXIT_SUCCESS : EXIT_FAILURE;
    }

    Array_init(&outputs, &error, NULL);

    if (ERROR_HAS(&error)) {
        cleanup(&inputs, NULL, &error);
        return EXIT_FAILURE;
    }

    for (size_t i = 0; i < STATIC_ARRAY_LENGTH(plugins); ++i) {
        if (plugins[i] != NULL) {
            plugins[i]->run(plugins[i], &inputs, &outputs, &error);

            if (ERROR_HAS(&error)) {
                cleanup(&inputs, &outputs, &error);
                return EXIT_FAILURE;
            }
        }
    }

    bool has_plugin_failed = flush_inputs(&inputs, &outputs, &error);
    cleanup(&inputs, &outputs, &error);
    return has_plugin_failed ? EXIT_FAILURE : EXIT_SUCCESS;
}
