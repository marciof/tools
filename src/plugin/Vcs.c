#include <unistd.h>
#include "../Array.h"
#include "../popen2.h"
#include "Vcs.h"

#define EXTERNAL_BINARY "git"

static void init_argv(
        struct Array* argv, struct Array* options, struct Error* error) {

    Array_init(argv, error,
        EXTERNAL_BINARY, "--no-pager", "show", NULL);

    if (Error_has(error)) {
        return;
    }

    if (!ARRAY_IS_NULL_INITIALIZED(options)) {
        Array_extend(argv, options, error);

        if (Error_has(error)) {
            Array_deinit(argv);
            return;
        }
    }

    Array_add(argv, argv->length, (intptr_t) "INPUT_NAME_PLACEHOLDER", error);

    if (Error_has(error)) {
        Array_deinit(argv);
        return;
    }

    Array_add(argv, argv->length, (intptr_t) NULL, error);

    if (Error_has(error)) {
        Array_deinit(argv);
    }
}

static bool is_available(struct Error* error) {
    char* argv[] = {
        EXTERNAL_BINARY,
        "--version",
        NULL,
    };

    return popen2_check(argv[0], argv, error);
}

static bool is_input_valid(char* input, struct Error* error) {
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

static void open_named_input(
        struct Input* input, size_t argc, char* argv[], struct Error* error) {

    /*struct Array argv = ARRAY_NULL_INITIALIZER;

    for (size_t i = 0; i < inputs->length; ++i) {
        Input* input = (Input*) inputs->data[i];

        if ((input == NULL) || (input->fd != IO_NULL_FD)) {
            continue;
        }

        if (!is_available()) {
            return;
        }

        bool is_valid = is_input_valid(input->name, error);

        if (Error_has(error)) {
            Error_add(error, "`" EXTERNAL_BINARY "`");
            return;
        }
        if (!is_valid) {
            continue;
        }
        if (ARRAY_IS_NULL_INITIALIZED(&argv)) {
            init_argv(&argv, &plugin->options, error);

            if (Error_has(error)) {
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

        if (Error_has(error)) {
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
    }*/
}

struct Plugin Vcs_Plugin = {
    "vcs",
    "show VCS revisions via `" EXTERNAL_BINARY "`",
    is_available,
    NULL,
    open_named_input,
};
