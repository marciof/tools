#include <stdio.h>
#include <sys/stat.h>
#include <unistd.h>
#include "../Error.h"
#include "../io.h"
#include "Stdin.h"

static void close_input(struct Input* input, struct Error* error) {
}

static size_t read_input(
        struct Input* input, char* buffer, size_t length, struct Error* error) {

    ssize_t nr_bytes_read = read(input->fd, buffer, length * sizeof(buffer[0]));

    if (nr_bytes_read < 0) {
        Error_add_errno(error, errno);
        return 0;
    }

    return nr_bytes_read / sizeof(buffer[0]);
}

static bool is_available(struct Plugin* plugin, struct Error* error) {
    return true;
}

static void open_input(
        struct Plugin* plugin,
        struct Input* input,
        size_t argc,
        char* argv[],
        struct Error* error) {

    if (input->name != NULL) {
        return;
    }

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
    input->read = read_input;
}

static void open_output(
        struct Plugin* plugin,
        struct Output* output,
        size_t argc,
        char* argv[],
        struct Error* error) {
}

struct Plugin Stdin_Plugin = {
    "stdin",
    "read standard input, by default",
    is_available,
    open_input,
    open_output,
};
