#include <unistd.h>
#include "../Array.h"
#include "../fork_exec.h"
#include "../io.h"
#include "Ls_Plugin.h"

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

static const char* get_description() {
    return "list directories via `" EXTERNAL_BINARY "`";
}

static const char* get_name() {
    return EXTERNAL_BINARY;
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

    input->fd = fork_exec((char*) argv->data[0], (char**) argv->data, error);

    if (ERROR_HAS(error)) {
        close(input->fd);
        Array_remove(inputs, pos, NULL);
        Input_delete(input);
    }
}

static void run(Array* inputs, Array* options, Array* outputs, Error* error) {
    Array argv;
    size_t nr_args = 0;

    create_argv(&argv, options, error);

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

        if ((input->name != NULL) && (input->fd == IO_INVALID_FD)) {
            Array_add(&argv, argv.length, (intptr_t) input->name, error);

            if (ERROR_HAS(error)) {
                Array_deinit(&argv);
                return;
            }

            ++nr_args;
            inputs->data[i] = (intptr_t) NULL;
            Input_delete(input);
        }
        else if (nr_args > 0) {
            open_inputs(inputs, &argv, i, error);

            if (ERROR_HAS(error)) {
                Array_deinit(&argv);
                return;
            }

            argv.length -= nr_args + 1;
            nr_args = 0;
            ++i;
        }
        else {
            ++i;
        }
    }

    if (nr_args > 0) {
        open_inputs(inputs, &argv, inputs->length, error);
    }
    else {
        ERROR_CLEAR(error);
    }

    Array_deinit(&argv);
}

Plugin Ls_Plugin = {
    {NULL},
    get_description,
    get_name,
    run,
};
