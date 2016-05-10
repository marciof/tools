#include <unistd.h>
#include "../Array.h"
#include "../fork_exec.h"
#include "../io.h"
#include "Ls_Plugin.h"

#define EXTERNAL_BINARY "ls"

static const char* get_description() {
    return "list directories via `" EXTERNAL_BINARY "`";
}

static const char* get_name() {
    return EXTERNAL_BINARY;
}

static void open_inputs(Array* inputs, Array* argv, size_t pos, Error* error) {
    Array_add(argv, (intptr_t) NULL, error);
    if (Error_has(error)) {
        return;
    }

    Input* input = Input_new(NULL, IO_INVALID_FD, error);
    if (Error_has(error)) {
        return;
    }

    Array_insert(inputs, (intptr_t) input, pos, error);

    if (Error_has(error)) {
        Input_delete(input);
        return;
    }

    input->fd = fork_exec((char*) argv->data[0], (char**) argv->data, error);

    if (Error_has(error)) {
        close(input->fd);
        Array_remove(inputs, pos, NULL);
        Input_delete(input);
    }
}

static Array* prepare_argv(Array* options, Error* error) {
    Array* argv = Array_new(error, EXTERNAL_BINARY, NULL);

    if (Error_has(error)) {
        return NULL;
    }

    if (options != NULL) {
        Array_extend(argv, options, error);

        if (Error_has(error)) {
            Array_delete(argv);
            return NULL;
        }
    }

    Error_clear(error);
    return argv;
}

static void run(Array* inputs, Array* options, Array* outputs, Error* error) {
    Array* argv = prepare_argv(options, error);
    size_t nr_args = 0;

    if (Error_has(error)) {
        return;
    }

    if (inputs->length == 0) {
        open_inputs(inputs, argv, inputs->length, error);
        Array_delete(argv);
        return;
    }

    for (size_t i = 0; i < inputs->length;) {
        Input* input = (Input*) inputs->data[i];

        if (input == NULL) {
            ++i;
            continue;
        }

        if ((input->name != NULL) && (input->fd == IO_INVALID_FD)) {
            Array_add(argv, (intptr_t) input->name, error);

            if (Error_has(error)) {
                Array_delete(argv);
                return;
            }

            ++nr_args;
            inputs->data[i] = (intptr_t) NULL;
            Input_delete(input);
        }
        else if (nr_args > 0) {
            open_inputs(inputs, argv, i, error);

            if (Error_has(error)) {
                Array_delete(argv);
                return;
            }

            argv->length -= nr_args + 1;
            nr_args = 0;
            ++i;
        }
        else {
            ++i;
        }
    }

    if (nr_args > 0) {
        open_inputs(inputs, argv, inputs->length, error);
    }
    else {
        Error_clear(error);
    }

    Array_delete(argv);
}

Plugin Ls_Plugin = {
    NULL,
    get_description,
    get_name,
    run,
};
