#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
#include "../Error.h"
#include "../io.h"
#include "File.h"

static void close_input(struct Input* input, struct Error* error) {
    if (close(input->fd) == -1) {
        Error_add_errno(error, errno);
    }
    input->fd = IO_NULL_FD;
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

    if (input->name == NULL) {
        return;
    }

    struct stat input_stat;

    if (stat(input->name, &input_stat) == -1) {
        if (errno != ENOENT) {
            Error_add_errno(error, errno);
        }
        return;
    }

    if (S_ISDIR(input_stat.st_mode)) {
        return;
    }

    int fd = open(input->name, O_RDONLY);

    if (fd == -1) {
        Error_add_errno(error, errno);
        return;
    }

    input->fd = fd;
    input->close = close_input;
    input->read = read_input;
}

struct Plugin File_Plugin = {
    "file",
    "read files",
    (intptr_t) NULL,
    is_available,
    open_input,
};
