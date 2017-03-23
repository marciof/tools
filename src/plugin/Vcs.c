#include <unistd.h>
#include "../popen2.h"
#include "Vcs.h"

#define EXTERNAL_BINARY "git"

static void init_argv(Array* argv, Array* options, Error* error) {
    Array_init(argv, error,
        EXTERNAL_BINARY, "--no-pager", "show", NULL);

    if (ERROR_HAS(error)) {
        return;
    }

    if (!ARRAY_IS_NULL_INITIALIZED(options)) {
        Array_extend(argv, options, error);

        if (ERROR_HAS(error)) {
            Array_deinit(argv);
            return;
        }
    }

    Array_add(argv, argv->length, (intptr_t) "INPUT_NAME_PLACEHOLDER", error);

    if (ERROR_HAS(error)) {
        Array_deinit(argv);
        return;
    }

    Array_add(argv, argv->length, (intptr_t) NULL, error);

    if (ERROR_HAS(error)) {
        Array_deinit(argv);
    }
}

static bool is_available() {
    char* argv[] = {
        EXTERNAL_BINARY,
        "--version",
        NULL,
    };

    Error error = ERROR_INITIALIZER;
    int status = popen2_status(argv[0], argv, &error);

    return !ERROR_HAS(&error) && (status == 0);
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

    return popen2_status(args[0], args, error) == 0;
}

static void run(Plugin* plugin, Array* inputs, Array* outputs, Error* error) {
    Array argv = ARRAY_NULL_INITIALIZER;

    for (size_t i = 0; i < inputs->length; ++i) {
        Input* input = (Input*) inputs->data[i];

        if ((input == NULL) || (input->fd != IO_NULL_FD)) {
            continue;
        }

        if (!is_available()) {
            return;
        }

        bool is_valid = is_input_valid(input->name, error);

        if (ERROR_HAS(error)) {
            Error_add(error, "`" EXTERNAL_BINARY "`");
            return;
        }
        if (!is_valid) {
            continue;
        }
        if (ARRAY_IS_NULL_INITIALIZED(&argv)) {
            init_argv(&argv, &plugin->options, error);

            if (ERROR_HAS(error)) {
                return;
            }
        }

        argv.data[argv.length - 1 - 1] = (intptr_t) input->name;
        pid_t child_pid;

        int fd = popen2(
            (char*) argv.data[0],
            (char**) argv.data,
            true,
            IO_NULL_FD,
            IO_NULL_FD,
            &child_pid,
            error);

        if (ERROR_HAS(error)) {
            Error_add(error, "`" EXTERNAL_BINARY "`");
            return;
        }

        input->plugin = plugin;
        input->fd = fd;
        input->arg = child_pid;
        input->close = Input_close_subprocess;
    }

    if (!ARRAY_IS_NULL_INITIALIZED(&argv)) {
        Array_deinit(&argv);
    }
}

Plugin Vcs_Plugin = {
    ARRAY_NULL_INITIALIZER,
    "show VCS revisions via `" EXTERNAL_BINARY "`",
    "vcs",
    is_available,
    run,
};
