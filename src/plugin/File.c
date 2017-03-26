#include <errno.h>
#include <fcntl.h>
#include <string.h>
#include <sys/stat.h>
#include "../io.h"
#include "File.h"

static bool is_available() {
    return true;
}

static int open_file(char* path, Error* error) {
    struct stat path_stat;

    if (stat(path, &path_stat) == -1) {
        if (errno != ENOENT) {
            Error_add(error, strerror(errno));
        }
        return IO_NULL_FD;
    }

    if (S_ISDIR(path_stat.st_mode)) {
        return IO_NULL_FD;
    }

    int fd = open(path, O_RDONLY);

    if (fd == -1) {
        Error_add(error, strerror(errno));
        return IO_NULL_FD;
    }

    return fd;
}

static void run(
        Plugin* plugin,
        char* options[],
        Input* input,
        Array* outputs,
        Error* error) {

    /*for (size_t i = 0; i < inputs->length; ++i) {
        Input* input = (Input*) inputs->data[i];

        if ((input != NULL) && (input->fd == IO_NULL_FD)) {
            input->fd = open_file(input->name, error);

            if (ERROR_HAS(error)) {
                Error_add(error, input->name);
                return;
            }
            else if (input->fd != IO_NULL_FD) {
                input->plugin = plugin;
            }
        }
    }*/
}

Plugin File_Plugin = {
    "file",
    "read files",
    false,
    0,
    is_available,
    run,
};
