#include <errno.h>
#include <stdbool.h>
#include <sys/wait.h>
#include <unistd.h>
#include "../Array.h"
#include "../fork_exec.h"
#include "../io.h"
#include "Dir.h"

#define EXTERNAL_BINARY "ls"

static void create_argv(Array* argv, Array* options, Error* error) {
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

    ERROR_CLEAR(error);
}

static void Input_close(Input* input, Error* error) {
    io_close(input->fd, error);

    if (!ERROR_HAS(error)) {
        int status;

        if (waitpid((int) input->arg, &status, 0) == -1) {
            ERROR_ERRNO(error, errno);
        }
        else if (WIFEXITED(status) && (WEXITSTATUS(status) != 0)) {
            ERROR_SET(error, ERROR_UNSPECIFIED);
        }
    }
}

static void open_inputs(Array* inputs, Array* argv, size_t pos, Error* error) {
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

    int child_pid;

    input->close = Input_close;
    input->fd = fork_exec(
        (char*) argv->data[0], (char**) argv->data, &child_pid, error);

    if (ERROR_HAS(error)) {
        Array_remove(inputs, pos, NULL);
        Input_delete(input);
    }
    else {
        input->arg = (intptr_t) child_pid;
        ERROR_CLEAR(error);
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

    create_argv(&argv, &plugin->options, error);

    if (ERROR_HAS(error)) {
        return;
    }

    if (inputs->length == 0) {
        open_inputs(inputs, &argv, inputs->length, error);
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
                || (errno != ENOENT));

        if (does_exist) {
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

        if (nr_args > 0) {
            open_inputs(inputs, &argv, i, error);

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
        open_inputs(inputs, &argv, inputs->length, error);
    }
    else {
        ERROR_CLEAR(error);
    }

    Array_deinit(&argv);
}

Plugin Dir_Plugin = {
    {NULL},
    Plugin_get_description,
    Plugin_get_name,
    Plugin_run,
};
