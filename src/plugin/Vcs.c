#include "../fork_exec.h"
#include "Vcs.h"

#define EXTERNAL_BINARY "git"

static void init_argv(Array *argv, Array *options, char* input, Error *error) {
    Array_init(argv, error,
        EXTERNAL_BINARY, "--no-pager", "show", input, NULL);

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

    Array_add(argv, argv->length, (intptr_t) NULL, error);

    if (ERROR_HAS(error)) {
        Array_deinit(argv);
    }
}

static bool is_input_valid(char* input, Error* error) {
    char* args[] = {
        EXTERNAL_BINARY,
        "--no-pager",
        "rev-parse",
        "--quiet",
        "--verify",
        input,
        NULL,
    };

    return fork_exec_status(args[0], args, error) == 0;
}

static const char* Plugin_get_description() {
    return "show VCS revisions via `" EXTERNAL_BINARY "`";
}

static const char* Plugin_get_name() {
    return "vcs";
}

static void Plugin_run(
        Plugin* plugin, Array* inputs, Array* outputs, Error* error) {

    for (size_t i = 0; i < inputs->length; ++i) {
        Input* input = (Input*) inputs->data[i];

        if ((input != NULL) && (input->fd == IO_INVALID_FD)) {
            bool is_valid = is_input_valid(input->name, error);

            if (ERROR_HAS(error)) {
                return;
            }
            if (!is_valid) {
                continue;
            }

            Array argv;
            init_argv(&argv, &plugin->options, input->name, error);

            if (ERROR_HAS(error)) {
                return;
            }

            int child_pid;
            input->fd = fork_exec_fd(
                (char*) argv.data[0], (char**) argv.data, &child_pid, error);

            Array_deinit(&argv);

            if (ERROR_HAS(error)) {
                return;
            }

            input->arg = child_pid;
            input->close = Input_close_subprocess;
        }
    }
}

Plugin Vcs_Plugin = {
    {NULL},
    Plugin_get_description,
    Plugin_get_name,
    Plugin_run,
};
