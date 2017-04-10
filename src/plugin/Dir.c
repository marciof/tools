#include <errno.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
#include "../io.h"
#include "../popen2.h"
#include "../signal2.h"
#include "Dir.h"

#define EXTERNAL_BINARY "ls"

static void close_subprocess(struct Input* input, struct Error* error) {
    popen2_close(input->fd, (pid_t) input->arg, error);
    input->fd = IO_NULL_FD;
}

static bool is_available(struct Plugin* plugin, struct Error* error) {
    char* argv[] = {
        EXTERNAL_BINARY,
        "--version",
        NULL,
    };

    return popen2_check(argv[0], argv, error);
}

static void sigchld_handler(int signum, intptr_t arg) {
}

static void open_input(
        struct Plugin* plugin,
        struct Input* input,
        size_t argc,
        char* argv[],
        struct Error* error) {

    if (!(bool) plugin->arg) {
        // signal2(SIGCHLD, (intptr_t) input, sigchld_handler, error);

        if (Error_has(error)) {
            return;
        }
        plugin->arg = (bool) true;
    }

    char* exec_argv[1 + argc + 1 + 1 + 1];
    pid_t child_pid;

    exec_argv[0] = EXTERNAL_BINARY;
    exec_argv[0 + 1 + argc] = "--";
    exec_argv[0 + 1 + argc + 1] = input->name;
    exec_argv[0 + 1 + argc + 1 + 1] = NULL;

    for (size_t i = 0; i < argc; ++i) {
        exec_argv[0 + 1 + i] = argv[i];
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
        struct Plugin* plugin,
        struct Input* input,
        size_t argc,
        char* argv[],
        struct Error* error) {

    input->name = ".";
    open_input(plugin, input, argc, argv, error);
}

static void open_named_input(
        struct Plugin* plugin,
        struct Input* input,
        size_t argc,
        char* argv[],
        struct Error* error) {

    struct stat input_stat;

    if (stat(input->name, &input_stat) == -1) {
        if (errno != ENOENT) {
            Error_add_errno(error, errno);
        }
        return;
    }

    if (S_ISDIR(input_stat.st_mode)) {
        open_input(plugin, input, argc, argv, error);
    }
}

struct Plugin Dir_Plugin = {
    "dir",
    "list directories via `" EXTERNAL_BINARY "`, cwd by default",
    (intptr_t) false, // has installed signal handler?
    is_available,
    open_default_input,
    open_named_input,
};
