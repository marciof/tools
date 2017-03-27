#include <errno.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>
#include "../Error.h"
#include "../io.h"
#include "Stdin.h"

static bool is_available() {
    return true;
}

static void open_default_input(
        Input* input,
        size_t options_length,
        char* options[],
        Error* error) {

    struct stat fd_stat;

    if (fstat(STDIN_FILENO, &fd_stat) == -1) {
        Error_add(error, strerror(errno));
        return;
    }

    if (S_ISDIR(fd_stat.st_mode)) {
        Error_add(error, "unable to read directory");
        return;
    }

    bool has_fd_input = io_has_input(STDIN_FILENO, error);

    if (ERROR_HAS(error) || !has_fd_input) {
        return;
    }

    input->name = "<stdin>";
    input->fd = STDIN_FILENO;
}

Plugin Stdin_Plugin = {
    "stdin",
    "read standard input, by default",
    true,
    is_available,
    open_default_input,
    NULL,
};
