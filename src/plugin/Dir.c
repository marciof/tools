#include <errno.h>
#include <stdbool.h>
#include <string.h>
#include <unistd.h>
#include "../Array.h"
#include "../fork_exec.h"
#include "../io.h"
#include "Dir.h"

#define EXTERNAL_BINARY "ls"

static void init_argv(Array *argv, Array *options, Error *error) {
    Array_init(argv, error, EXTERNAL_BINARY, NULL);

    if (ERROR_HAS(error)) {
        return;
    }

    if (options != NULL) {
        Array_extend(argv, options, error);

        if (ERROR_HAS(error)) {
            Array_deinit(argv);
            return;
        }
    }

    Array_add(argv, argv->length, (intptr_t) "--", error);

    if (ERROR_HAS(error)) {
        Array_deinit(argv);
    }
}

static void open_inputs(
        Plugin* plugin, Array* inputs, Array* argv, size_t pos, Error* error) {

    // FIXME: `NULL` is sometimes added multiple times
    Array_add(argv, argv->length, (intptr_t) NULL, error);

    if (ERROR_HAS(error)) {
        return;
    }

    Input* input = Input_new(NULL, IO_INVALID_FD, error);

    if (ERROR_HAS(error)) {
        return;
    }

    Array_add(inputs, pos, (intptr_t) input, error);

    if (ERROR_HAS(error)) {
        Input_delete(input);
        return;
    }

    pid_t child_pid;

    int fd = fork_exec_fd(
        (char*) argv->data[0],
        (char**) argv->data,
        IO_INVALID_FD,
        IO_INVALID_FD,
        &child_pid,
        error);

    if (ERROR_HAS(error)) {
        Error_add(error, "`" EXTERNAL_BINARY "` error");
        Array_remove(inputs, pos, error);
        Input_delete(input);
    }
    else {
        input->plugin = plugin;
        input->fd = fd;
        input->arg = (intptr_t) child_pid;
        input->close = Input_close_subprocess;
    }
}

static const char* Plugin_get_description() {
    return "list directories via `" EXTERNAL_BINARY "`";
}

static const char* Plugin_get_name() {
    return "dir";
}

static void Plugin_run(
        Plugin* plugin, Array* inputs, Array* outputs, Error* error) {

    Array argv;
    size_t nr_args = 0;

    init_argv(&argv, &plugin->options, error);

    if (ERROR_HAS(error)) {
        return;
    }

    if (inputs->length == 0) {
        open_inputs(plugin, inputs, &argv, inputs->length, error);
        Array_deinit(&argv);
        return;
    }

    for (size_t i = 0; i < inputs->length;) {
        Input* input = (Input*) inputs->data[i];

        if (input == NULL) {
            ++i;
            continue;
        }

        bool does_exist = (input->fd == IO_INVALID_FD)
            && ((access(input->name, F_OK) == 0)
                && (errno != ENOENT));

        if (does_exist) {
            if (access(input->name, R_OK) == 0) {
                Array_add(&argv, argv.length, (intptr_t) input->name, error);

                if (ERROR_HAS(error)) {
                    Array_deinit(&argv);
                    return;
                }

                ++nr_args;
                inputs->data[i] = (intptr_t) NULL;
                Input_delete(input);
                continue;
            }
            else {
                Error_add(error, strerror(errno));
                Error_add(error, input->name);
                Array_deinit(&argv);
                return;
            }
        }

        if (nr_args > 0) {
            open_inputs(plugin, inputs, &argv, i, error);

            if (ERROR_HAS(error)) {
                Array_deinit(&argv);
                return;
            }

            argv.length -= nr_args + 1;
            nr_args = 0;
        }

        ++i;
    }

    if (nr_args > 0) {
        open_inputs(plugin, inputs, &argv, inputs->length, error);
    }

    Array_deinit(&argv);
}

Plugin Dir_Plugin = {
    ARRAY_NULL_INITIALIZER,
    Plugin_get_description,
    Plugin_get_name,
    Plugin_run,
};
