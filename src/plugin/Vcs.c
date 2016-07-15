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
            Array argv;
            init_argv(&argv, &plugin->options, input->name, error);

            if (ERROR_HAS(error)) {
                return;
            }

            int child_pid;
            input->fd = fork_exec(
                (char*) argv.data[0], (char**) argv.data, &child_pid, error);

            Array_deinit(&argv);

            // FIXME: don't swallow invalid inputs
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
