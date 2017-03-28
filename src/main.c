#include <errno.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include "Array.h"
#include "io.h"
#include "options.h"
#include "plugin/Dir.h"
#include "plugin/File.h"
#include "plugin/Pager.h"
#include "plugin/Stdin.h"
#include "plugin/Vcs.h"

static Plugin* plugins[] = {
    &Stdin_Plugin,
    &File_Plugin,
    &Dir_Plugin,
    &Vcs_Plugin,
    &Pager_Plugin,
};

static void cleanup(Array* inputs, Array* outputs, Error* error) {
    Error_print(error, stderr);

    if (inputs != NULL) {
        for (size_t i = 0; i < inputs->length; ++i) {
            Input* input = (Input*) inputs->data[i];

            if (input == NULL) {
                continue;
            }

            if (input->fd != IO_NULL_FD) {
                Error input_error = ERROR_INITIALIZER;
                Input_close(input, &input_error);

                if (ERROR_HAS(&input_error)) {
                    Error_add(&input_error, input->plugin->name);
                    Error_print(&input_error, stderr);
                }
            }
            Input_delete(input);
        }
        Array_deinit(inputs);
    }

    if (outputs != NULL) {
        for (size_t i = 0; i < outputs->length; ++i) {
            Output* output = (Output*) outputs->data[i];
            Error output_error = ERROR_INITIALIZER;

            output->close(output, &output_error);

            if (ERROR_HAS(&output_error)) {
                Error_add(&output_error, output->plugin->name);
                Error_print(&output_error, stderr);
            }
            Output_delete(output);
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

// Receives an optional previous `buffer` returning it or a new one when `NULL`,
// so as to be able to reuse it across calls and minimize memory allocations.
static Buffer* flush_input(
        int fd, Buffer* buffer, Array* outputs, Error* error) {

    ssize_t bytes_read;

    if (buffer == NULL) {
        buffer = Buffer_new(BUFSIZ, error);

        if (ERROR_HAS(error)) {
            return NULL;
        }
    }

    while ((bytes_read = read(
            fd, buffer->data, BUFSIZ * sizeof(buffer->data[0]))) > 0) {

        buffer->length = (size_t) (bytes_read / sizeof(buffer->data[0]));
        bool has_flushed = false;

        for (size_t i = 0; i < outputs->length; ++i) {
            Output* output = (Output*) outputs->data[i];
            output->write(output, &buffer, error);

            if (ERROR_HAS(error)) {
                Error_add(error, output->plugin->name);
                return buffer;
            }

            if (buffer == NULL) {
                buffer = Buffer_new(BUFSIZ, error);

                if (ERROR_HAS(error)) {
                    Error_add(error, output->plugin->name);
                    return buffer;
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
            io_write(
                STDOUT_FILENO,
                (uint8_t*) buffer->data,
                buffer->length * sizeof(buffer->data[0]),
                error);

            if (ERROR_HAS(error)) {
                return buffer;
            }
        }
    }

    if ((bytes_read == -1) && (errno != EIO)) {
        Error_add(error, strerror(errno));
    }

    return buffer;
}

static bool flush_inputs(Array* inputs, Array* outputs, Error* error) {
    Buffer* buffer = NULL;
    bool did_succeed = true;

    for (size_t i = 0; i < inputs->length; ++i) {
        Input* input = (Input*) inputs->data[i];

        if (input == NULL) {
            continue;
        }

        if (input->fd == IO_NULL_FD) {
            Error_add(error, "Unsupported input");
            if (input->name != NULL) {
                Error_add(error, input->name);
            }
            did_succeed = false;
            break;
        }

        buffer = flush_input(input->fd, buffer, outputs, error);

        if (ERROR_HAS(error)) {
            if (input->name != NULL) {
                Error_add(error, input->name);
            }
            Error_add(error, input->plugin->name);
            did_succeed = false;
            break;
        }

        Input_close(input, error);

        if (ERROR_HAS(error)) {
            if (input->name != NULL) {
                Error_add(error, input->name);
            }
            Error_add(error, input->plugin->name);
            did_succeed = false;
            break;
        }
    }

    if (buffer != NULL) {
        Buffer_delete(buffer);
    }

    return did_succeed;
}

int main(int argc, char* argv[]) {
    Error error = ERROR_INITIALIZER;
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
        Plugin* plugin = plugins[i];

        if (plugin == NULL) {
            continue;
        }

        plugin->run(plugin, &inputs, &outputs, &error);

        if (ERROR_HAS(&error)) {
            Error_add(&error, plugin->name);
            cleanup(&inputs, &outputs, &error);
            return EXIT_FAILURE;
        }
    }

    bool did_succeed = flush_inputs(&inputs, &outputs, &error);
    cleanup(&inputs, &outputs, &error);
    return did_succeed ? EXIT_SUCCESS: EXIT_FAILURE;
}
