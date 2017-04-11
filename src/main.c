#include <stdbool.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include "io.h"
#include "options.h"
#include "plugin/Dir.h"
#include "plugin/File.h"
#include "plugin/Pager.h"
#include "plugin/Stdin.h"
#include "plugin/Vcs.h"

static struct Plugin_Setup plugins_setup[] = {
    {
        &Stdin_Plugin,
        true,
        0,
        NULL,
    },
    {
        &File_Plugin,
        true,
        0,
        NULL,
    },
    {
        &Dir_Plugin,
        true,
        0,
        NULL,
    },
    {
        &Vcs_Plugin,
        true,
        0,
        NULL,
    },
    {
        &Pager_Plugin,
        false,
        0,
        NULL,
    },
};

/*
// Receives an optional previous `buffer` returning it or a new one when `NULL`,
// so as to be able to reuse it across calls and minimize memory allocations.
static Buffer* flush_input(
        int fd, Buffer* buffer, Array* outputs, Error* error) {

    ssize_t bytes_read;

    if (buffer == NULL) {
        buffer = Buffer_new(BUFSIZ, error);

        if (Error_has(error)) {
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

            if (Error_has(error)) {
                Error_add(error, output->plugin->name);
                return buffer;
            }

            if (buffer == NULL) {
                buffer = Buffer_new(BUFSIZ, error);

                if (Error_has(error)) {
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

            if (Error_has(error)) {
                return buffer;
            }
        }
    }

    if ((bytes_read == -1) && (errno != EIO)) {
        Error_add(error, strerror(errno));
    }

    return buffer;
}
*/

/** @return `true` if the input was successfully flushed, `false` otherwise */
static bool flush_input(
        struct Input* input,
        int output_fd,
        struct Plugin_Setup* plugin_setup,
        struct Error* error) {

    plugin_setup->plugin->open_input(
        plugin_setup->plugin,
        input,
        plugin_setup->argc,
        plugin_setup->argv,
        error);

    if (Error_has(error) || (input->fd == IO_NULL_FD)) {
        return false;
    }

    while (true) {
        char buffer[BUFSIZ];
        size_t nr_read = input->read(input, buffer, BUFSIZ, error);

        if (Error_has(error)) {
            return false;
        }
        if (nr_read == 0) {
            break;
        }

        io_write_all(output_fd, buffer, nr_read, error);

        if (Error_has(error)) {
            return false;
        }
    }

    input->close(input, error);

    if (Error_has_errno(error, ENOENT)) {
        Error_clear(error);
        return false;
    }

    return !Error_has(error);
}

static void flush_inputs(
        size_t inputs_length,
        char* inputs[],
        int output_fd,
        struct Error* error) {

    for (size_t i = 0; i < inputs_length; ++i) {
        bool was_input_flushed = false;
        char* input_name = inputs[i];

        for (size_t j = 0; j < C_ARRAY_LENGTH(plugins_setup); ++j) {
            struct Plugin_Setup* plugin_setup = &plugins_setup[j];

            if (plugin_setup->is_enabled) {
                struct Input input = {
                    input_name,
                    IO_NULL_FD,
                    (intptr_t) NULL,
                    NULL,
                    NULL,
                };

                was_input_flushed = flush_input(
                    &input, output_fd, plugin_setup, error);

                if (Error_has(error)) {
                    if (input_name != NULL) {
                        Error_add_string(error, input_name);
                    }
                    Error_add_string(error, plugin_setup->plugin->name);
                    return;
                }
                if (was_input_flushed) {
                    break;
                }
            }
        }

        if (!was_input_flushed) {
            if (input_name != NULL) {
                Error_add_string(error, "unsupported input");
                Error_add_string(error, input_name);
            }
            return;
        }
    }
}

int main(int argc, char* argv[]) {
    struct Error error = ERROR_INITIALIZER;
    char* plugin_argv_storage[C_ARRAY_LENGTH(plugins_setup) * (argc - 1)];

    for (size_t i = 0; i < C_ARRAY_LENGTH(plugins_setup); ++i) {
        plugins_setup[i].argv = plugin_argv_storage + i * (argc - 1);
    }

    int args_pos = parse_options(
        argc, argv, C_ARRAY_LENGTH(plugins_setup), plugins_setup, &error);

    if ((args_pos < 0) || (Error_has(&error))) {
        return Error_print(&error, stderr) ? EXIT_FAILURE : EXIT_SUCCESS;
    }

    if (args_pos == argc) {
        char* input = NULL;
        flush_inputs(1, &input, STDOUT_FILENO, &error);
    }
    else {
        flush_inputs(
            (size_t) (argc - args_pos), argv + args_pos, STDOUT_FILENO, &error);
    }

    if (Error_has(&error)) {
        Error_print(&error, stderr);
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
