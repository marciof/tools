#include <errno.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
#include "../io.h"
#include "../popen2.h"
#include "Dir.h"

#define EXTERNAL_BINARY "ls"

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

static void run(
        size_t options_length,
        char* options[],
        Input* input,
        Array* outputs,
        Error* error) {

    if (input->name != NULL) {
        struct stat input_stat;

        if (stat(input->name, &input_stat) == -1) {
            if (errno != ENOENT) {
                Error_add(error, strerror(errno));
            }
            return;
        }
        if (!S_ISDIR(input_stat.st_mode)) {
            return;
        }
    }
    else {
        input->name = ".";
    }

    char* argv[1 + options_length + 1 + 1 + 1];

    argv[0] = EXTERNAL_BINARY;
    argv[1 + options_length] = "--";
    argv[1 + options_length + 1] = input->name;
    argv[1 + options_length + 1 + 1] = NULL;

    for (size_t i = 0; i < options_length; ++i) {
        argv[i + 1] = options[i];
    }

    pid_t child_pid;

    int fd = popen2(
        argv[0],
        argv,
        true,
        IO_NULL_FD,
        IO_NULL_FD,
        &child_pid,
        error);

    if (ERROR_HAS(error)) {
        Error_add(error, "`" EXTERNAL_BINARY "`");
    }
    else {
        input->fd = fd;
        input->arg = (intptr_t) child_pid;
        input->close = Input_close_subprocess;
    }
}

Plugin Dir_Plugin = {
    "dir",
    "list directories via `" EXTERNAL_BINARY "`",
    true,
    is_available,
    run,
};
