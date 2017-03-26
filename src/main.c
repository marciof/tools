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

/*static void cleanup(Array* outputs, Error* error) {
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
}*/

/*// Receives an optional previous `buffer` returning it or a new one when `NULL`,
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
}*/

static bool flush_input(
        Input* input,
        int output_fd,
        Plugin* plugin,
        size_t nr_options,
        char* options[],
        Error* error) {

    plugin->run(nr_options, options, input, NULL, error);

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
        return false;
    }

    Input_close(input, error);
    return !ERROR_HAS(error);
}

int main(int argc, char* argv[]) {
    Error error = ERROR_INITIALIZER;
    char* plugins_options[C_ARRAY_LENGTH(plugins) * argc];
    size_t plugins_nr_options[C_ARRAY_LENGTH(plugins)] = {0, 0, 0, 0, 0};

    int args_pos = parse_options(
        argc,
        argv,
        C_ARRAY_LENGTH(plugins),
        plugins,
        plugins_nr_options,
        plugins_options,
        &error);

    if ((args_pos < 0) || (ERROR_HAS(&error))) {
        return Error_print(&error, stderr) ? EXIT_FAILURE : EXIT_SUCCESS;
    }

    for (int i = args_pos; i < argc; ++i) {
        bool is_input_supported = false;

        Input input = {
            argv[i],
            IO_NULL_FD,
            (intptr_t) NULL,
            NULL,
        };

        for (size_t j = 0; j < C_ARRAY_LENGTH(plugins); ++j) {
            Plugin* plugin = plugins[j];

            if (plugin->is_enabled) {
                is_input_supported = flush_input(
                    &input,
                    STDOUT_FILENO,
                    plugin,
                    plugins_nr_options[j],
                    plugins_options + j * argc,
                    &error);

                if (ERROR_HAS(&error)) {
                    Error_add(&error, plugin->name);
                    Error_print(&error, stderr);
                    return EXIT_FAILURE;
                }

                if (is_input_supported) {
                    break;
                }
            }
        }

        if (!is_input_supported) {
            Error_add(&error, "unsupported input");
            Error_add(&error, input.name);
            Error_print(&error, stderr);
            return EXIT_FAILURE;
        }
    }

    return EXIT_SUCCESS;
}
