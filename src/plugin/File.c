#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
#include "../io.h"
#include "File.h"

static void close_file(struct Input* input, Error* error) {
    if (close(input->fd) == -1) {
        ERROR_ADD_ERRNO(error, errno);
    }
    else {
        input->fd = IO_NULL_FD;
    }
}

static bool is_available() {
    return true;
}

static void open_named_input(
        struct Input* input, size_t argc, char* argv[], Error* error) {

    struct stat input_stat;

    if (stat(input->name, &input_stat) == -1) {
        if (errno != ENOENT) {
            ERROR_ADD_ERRNO(error, errno);
        }
        return;
    }

    if (S_ISDIR(input_stat.st_mode)) {
        return;
    }

    int fd = open(input->name, O_RDONLY);

    if (fd == -1) {
        ERROR_ADD_ERRNO(error, errno);
    }
    else {
        input->fd = fd;
        input->close = close_file;
    }
}

struct Plugin File_Plugin = {
    "file",
    "read files",
    is_available,
    NULL,
    open_named_input,
};
