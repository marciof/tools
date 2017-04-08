#include <stdio.h>
#include <sys/stat.h>
#include <unistd.h>
#include "../Error.h"
#include "../io.h"
#include "Stdin.h"

static bool close_input(struct Input* input, struct Error* error) {
    if (close(input->fd) == -1) {
        Error_add_errno(error, errno);
    }
    else {
        input->fd = IO_NULL_FD;
    }
    return true;
}

static bool is_available(struct Error* error) {
    return true;
}

static void open_default_input(
        struct Input* input, size_t argc, char* argv[], struct Error* error) {

    struct stat input_stat;

    if (fstat(STDIN_FILENO, &input_stat) == -1) {
        Error_add_errno(error, errno);
        return;
    }

    if (!S_ISFIFO(input_stat.st_mode)) {
        bool has_fd_input = io_has_input(STDIN_FILENO, error);

        if (Error_has(error) || !has_fd_input) {
            return;
        }
    }

    input->fd = STDIN_FILENO;
    input->close = close_input;
}

struct Plugin Stdin_Plugin = {
    "stdin",
    "read standard input, by default",
    is_available,
    open_default_input,
    NULL,
};
