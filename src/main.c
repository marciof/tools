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
        false,
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
*/

/**
 * @return whether or not the input was successfully flushed
 */
static bool flush_input(
        struct Input* input,
        int output_fd,
        struct Plugin_Setup* plugin_setup,
        Error* error) {

    void (*open_input)(struct Input*, size_t, char*[], Error*)
        = (input->name == NULL)
            ? plugin_setup->plugin->open_default_input
            : plugin_setup->plugin->open_named_input;

    if (open_input == NULL) {
        return false;
    }

    open_input(input, plugin_setup->argc, plugin_setup->argv, error);

    if (ERROR_HAS(error)) {
        return false;
    }
    if (input->fd == IO_NULL_FD) {
        return false;
    }

    uint8_t buffer[BUFSIZ];
    ssize_t nr_read;

    while ((nr_read = read(input->fd, buffer, BUFSIZ)) > 0) {
        io_write(output_fd, buffer, (size_t) nr_read, error);

        if (ERROR_HAS(error)) {
            return false;
        }
    }

    if ((nr_read == -1) && (errno != EIO)) {
        ERROR_ADD_ERRNO(error, errno);
        return false;
    }

    input->close(input, error);
    return !ERROR_HAS(error);
}

static void flush_inputs(
        size_t inputs_length, char* inputs[], int output_fd, Error* error) {

    for (size_t i = 0; i < inputs_length; ++i) {
        bool is_input_supported = false;
        char* input_name = inputs[i];

        for (size_t j = 0; j < C_ARRAY_LENGTH(plugins_setup); ++j) {
            struct Plugin_Setup* plugin_setup = &plugins_setup[j];

            if (plugin_setup->is_enabled) {
                struct Input input = {
                    input_name,
                    IO_NULL_FD,
                    (intptr_t) NULL,
                    NULL,
                };

                is_input_supported = flush_input(
                    &input, output_fd, plugin_setup, error);

                if (ERROR_HAS(error)) {
                    if (input.name != NULL) {
                        ERROR_ADD_STRING(error, input.name);
                    }
                    ERROR_ADD_STRING(error, plugin_setup->plugin->name);
                    return;
                }
                if (is_input_supported) {
                    break;
                }
            }
        }

        if (!is_input_supported) {
            ERROR_ADD_STRING(error, "unsupported input");
            ERROR_ADD_STRING(error, input_name);
            return;
        }
    }
}

int main(int argc, char* argv[]) {
    Error error = ERROR_INITIALIZER;
    int output_fd = STDOUT_FILENO;
    char* plugin_argv_storage[C_ARRAY_LENGTH(plugins_setup) * (argc - 1)];

    for (size_t i = 0; i < C_ARRAY_LENGTH(plugins_setup); ++i) {
        plugins_setup[i].argv = plugin_argv_storage + i * (argc - 1);
    }

    int args_pos = parse_options(
        argc, argv, C_ARRAY_LENGTH(plugins_setup), plugins_setup, &error);

    if ((args_pos < 0) || (ERROR_HAS(&error))) {
        return Error_print(&error, stderr) ? EXIT_FAILURE : EXIT_SUCCESS;
    }

    if (args_pos == argc) {
        char* input = NULL;
        flush_inputs(1, &input, output_fd, &error);
    }
    else {
        flush_inputs(
            (size_t) (argc - args_pos), argv + args_pos, output_fd, &error);
    }

    if (ERROR_HAS(&error)) {
        Error_print(&error, stderr);
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
