#include <errno.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
#include "../io.h"
#include "../popen2.h"
#include "Dir.h"

#define EXTERNAL_BINARY "ls"

static bool close_subprocess(struct Input* input, Error* error) {
    if (close(input->fd) == -1) {
        Error_add_errno(error, errno);
        input->fd = IO_NULL_FD;
        return true;
    }

    int status = popen_wait((pid_t) input->arg, error);
    input->fd = IO_NULL_FD;

    if (Error_has_errno(error, ENOENT)) {
        Error_clear(error);
        return false;
    }

    if (!Error_has(error) && (status != 0)) {
        Error_add_string(error, "subprocess exited with an error code");
    }

    return true;
}

static bool is_available() {
    char* argv[] = {
        EXTERNAL_BINARY,
        "--version",
        NULL,
    };

    Error error = ERROR_INITIALIZER;
    int status = popen2_status(argv[0], argv, &error);
    return !Error_has(&error) && (status == 0);
}

static void open_input(
        struct Input* input, size_t argc, char* argv[], Error* error) {

    char* exec_argv[1 + argc + 1 + 1 + 1];
    pid_t child_pid;

    exec_argv[0] = EXTERNAL_BINARY;
    exec_argv[1 + argc] = "--";
    exec_argv[1 + argc + 1] = input->name;
    exec_argv[1 + argc + 1 + 1] = NULL;

    for (size_t i = 0; i < argc; ++i) {
        exec_argv[i + 1] = argv[i];
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
    }
    else {
        input->fd = fd;
        input->arg = (intptr_t) child_pid;
        input->close = close_subprocess;
    }
}

static void open_default_input(
        struct Input* input, size_t argc, char* argv[], Error* error) {

    input->name = ".";
    open_input(input, argc, argv, error);
}

static void open_named_input(
        struct Input* input, size_t argc, char* argv[], Error* error) {

    struct stat input_stat;

    if (stat(input->name, &input_stat) == -1) {
        if (errno != ENOENT) {
            Error_add_errno(error, errno);
        }
        return;
    }

    if (S_ISDIR(input_stat.st_mode)) {
        open_input(input, argc, argv, error);
    }
}

struct Plugin Dir_Plugin = {
    "dir",
    "list directories via `" EXTERNAL_BINARY "`, cwd by default",
    is_available,
    open_default_input,
    open_named_input,
};
