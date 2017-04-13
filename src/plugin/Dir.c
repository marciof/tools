#include <errno.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
#include "../Error.h"
#include "../io.h"
#include "../popen2.h"
#include "../signal2.h"
#include "Dir.h"

#define EXTERNAL_BINARY "ls"

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

static bool is_directory(char* path, struct Error* error) {
    struct stat input_stat;

    if (stat(path, &input_stat) == -1) {
        if (errno != ENOENT) {
            Error_add_errno(error, errno);
        }
        return false;
    }

    return S_ISDIR(input_stat.st_mode);
}

static void sigchld_handler(int signum, intptr_t arg) {
}

static void open_input(
        struct Plugin* plugin,
        struct Input* input,
        size_t argc,
        char* argv[],
        struct Error* error) {

    if (input->name == NULL) {
        input->name = ".";
    }
    else if (!is_directory(input->name, error) || Error_has(error)) {
        return;
    }

    if (!(bool) plugin->arg) {
        // signal2(SIGCHLD, (intptr_t) input, sigchld_handler, error);

        if (Error_has(error)) {
            return;
        }
        plugin->arg = (bool) true;
    }

    char* exec_argv[1 + argc + 1 + 1 + 1];

    exec_argv[0] = EXTERNAL_BINARY;
    exec_argv[0 + 1 + argc] = "--";
    exec_argv[0 + 1 + argc + 1] = input->name;
    exec_argv[0 + 1 + argc + 1 + 1] = NULL;

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

struct Plugin Dir_Plugin = {
    "dir",
    "list directories via `" EXTERNAL_BINARY "`, cwd by default",
    (intptr_t) false, // has installed signal handler?
    is_available,
    open_input,
};
