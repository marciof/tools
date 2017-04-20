#include <unistd.h>
#include "../io.h"
#include "../popen2.h"
#include "Vcs.h"

#define EXTERNAL_BINARY "git"

static void close_input(struct Input* input, struct Error* error) {
    if (input->arg != 0) {
        popen2_close(input->fd, (pid_t) input->arg, error);
    }
}

static size_t read_input(
        struct Input* input, char* buffer, size_t length, struct Error* error) {

    return popen2_read(input->fd, buffer, length, (pid_t*) &input->arg, error);
}

static bool is_available(struct Plugin* plugin, struct Error* error) {
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

    return popen2_check(args[0], args, error);
}

static void open_input(
        struct Plugin* plugin,
        struct Input* input,
        size_t argc,
        char* argv[],
        struct Error* error) {

    if (input->name == NULL) {
        input->name = "HEAD";
    }
    else if (!is_input_valid(input->name, error) || Error_has(error)) {
        return;
    }

    char* exec_argv[1 + argc + 1 + 1 + 1 + 1];

    exec_argv[0] = EXTERNAL_BINARY;
    exec_argv[0 + 1 + argc] = "--no-pager";
    exec_argv[0 + 1 + argc + 1] = "show";
    exec_argv[0 + 1 + argc + 1 + 1] = input->name;
    exec_argv[0 + 1 + argc + 1 + 1 + 1] = NULL;

    for (size_t i = 0; i < argc; ++i) {
        exec_argv[0 + 1 + i] = argv[i];
    }

    input->fd = popen2(
        exec_argv[0],
        exec_argv,
        true,
        IO_NULL_FD,
        IO_NULL_FD,
        (pid_t*) &input->arg,
        error);

    if (Error_has(error)) {
        Error_add_string(error, "`" EXTERNAL_BINARY "`");
        return;
    }

    input->close = close_input;
    input->read = read_input;
}

struct Plugin Vcs_Plugin = {
    "vcs",
    "show VCS revisions via `" EXTERNAL_BINARY "`, HEAD by default",
    is_available,
    open_input,
};
