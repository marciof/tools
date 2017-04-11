#include <unistd.h>
#include "../Array.h"
#include "../io.h"
#include "../popen2.h"
#include "Vcs.h"

#define EXTERNAL_BINARY "git"

static void close_input(struct Input* input, struct Error* error) {
    popen2_close(input->fd, (pid_t) input->arg, error);
    input->fd = IO_NULL_FD;
}

static size_t read_input(
        struct Input* input, char* buffer, size_t length, struct Error* error) {

    ssize_t nr_bytes_read = read(input->fd, buffer, length * sizeof(buffer[0]));

    if (nr_bytes_read < 0) {
        // FIXME: don't ignore `EIO`
        if (errno != EIO) {
            Error_add_errno(error, errno);
        }
        return 0;
    }

    return nr_bytes_read / sizeof(buffer[0]);
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

    if (!is_input_valid(input->name, error) || Error_has(error)) {
        return;
    }

    char* exec_argv[1 + argc + 1 + 1 + 1 + 1];
    pid_t child_pid;

    exec_argv[0] = EXTERNAL_BINARY;
    exec_argv[0 + 1 + argc] = "--no-pager";
    exec_argv[0 + 1 + argc + 1] = "show";
    exec_argv[0 + 1 + argc + 1 + 1] = input->name;
    exec_argv[0 + 1 + argc + 1 + 1 + 1] = NULL;

    for (size_t i = 0; i < argc; ++i) {
        exec_argv[0 + 1 + i ] = argv[i];
    }

    int fd = popen2(
        exec_argv[0],
        exec_argv,
        true,
        IO_NULL_FD,
        IO_NULL_FD,
        &child_pid,
        error);

    if (Error_has(error)) {
        Error_add_string(error, "`" EXTERNAL_BINARY "`");
        return;
    }

    input->fd = fd;
    input->arg = (intptr_t) child_pid;
    input->close = close_input;
    input->read = read_input;
}

struct Plugin Vcs_Plugin = {
    "vcs",
    "show VCS revisions via `" EXTERNAL_BINARY "`",
    (intptr_t) NULL,
    is_available,
    open_input,
};
