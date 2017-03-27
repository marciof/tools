#include <errno.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
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

static size_t nr_options_per_plugin[C_ARRAY_LENGTH(plugins)] = {0, 0, 0, 0, 0};

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
        Input* input,
        int output_fd,
        Plugin* plugin,
        size_t options_length,
        char* options[],
        Error* error) {

    if (input->name == NULL) {
        if (plugin->open_default_input == NULL) {
            return false;
        }
        plugin->open_default_input(input, options_length, options, error);
    }
    else {
        if (plugin->open_named_input == NULL) {
            return false;
        }
        plugin->open_named_input(input, options_length, options, error);
    }

    if (ERROR_HAS(error)) {
        return false;
    }
    if (input->fd == IO_NULL_FD) {
        return false;
    }

    uint8_t buffer[BUFSIZ];
    ssize_t nr_read;

    while ((nr_read = read(input->fd, buffer, BUFSIZ)) > 0) {
        size_t length = (size_t) nr_read;
        uint8_t* buffer_ptr = buffer;

        while (length > 0) {
            ssize_t nr_written = write(output_fd, buffer_ptr, length);

            if (nr_written == -1) {
                Error_add(error, strerror(errno));
                return false;
            }

            buffer_ptr += nr_written;
            length -= nr_written;
        }
    }

    if ((nr_read == -1) && (errno != EIO)) {
        Error_add(error, strerror(errno));
        Error_add(error, input->name);
        return false;
    }

    input->close(input, error);

    if (ERROR_HAS(error)) {
        Error_add(error, input->name);
        return false;
    }

    return true;
}

static void flush_inputs(
        size_t inputs_length,
        char* inputs[],
        int output_fd,
        size_t max_nr_options_per_plugin,
        char* options_per_plugin[],
        Error* error) {

    for (size_t i = 0; i < inputs_length; ++i) {
        bool is_input_supported = false;

        for (size_t j = 0; j < C_ARRAY_LENGTH(plugins); ++j) {
            Plugin* plugin = plugins[j];

            if (plugin->is_enabled) {
                Input input = {
                    inputs[i],
                    IO_NULL_FD,
                    (intptr_t) NULL,
                    NULL,
                };

                is_input_supported = flush_input(
                    &input,
                    output_fd,
                    plugin,
                    nr_options_per_plugin[j],
                    options_per_plugin + j * max_nr_options_per_plugin,
                    error);

                if (ERROR_HAS(error)) {
                    Error_add(error, plugin->name);
                    return;
                }
                if (is_input_supported) {
                    break;
                }
            }
        }

        if (!is_input_supported) {
            Error_add(error, "unsupported input");
            Error_add(error, inputs[i]);
            return;
        }
    }
}

int main(int argc, char* argv[]) {
    Error error = ERROR_INITIALIZER;
    int output_fd = STDOUT_FILENO;
    char* options_per_plugin[C_ARRAY_LENGTH(plugins) * argc];

    int args_pos = parse_options(
        argc,
        argv,
        C_ARRAY_LENGTH(plugins),
        plugins,
        (size_t) argc,
        nr_options_per_plugin,
        options_per_plugin,
        &error);

    if ((args_pos < 0) || (ERROR_HAS(&error))) {
        return Error_print(&error, stderr) ? EXIT_FAILURE : EXIT_SUCCESS;
    }

    if (args_pos == argc) {
        char* input = NULL;
        flush_inputs(
            1, &input, output_fd, (size_t) argc, options_per_plugin, &error);
    }
    else {
        flush_inputs(
            (size_t) (argc - args_pos),
            argv + args_pos,
            output_fd,
            (size_t) argc,
            options_per_plugin,
            &error);
    }

    if (ERROR_HAS(&error)) {
        Error_print(&error, stderr);
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
