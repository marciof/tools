#include <errno.h>
#include <fcntl.h>
#include <sys/stat.h>
#include "../io.h"
#include "File.h"

static int open_file(char* path, Error* error) {
    struct stat path_stat;

    if (stat(path, &path_stat) == -1) {
        if (errno == ENOENT) {
            ERROR_CLEAR(error);
        }
        else {
            ERROR_ERRNO(error, errno);
        }
        return IO_INVALID_FD;
    }

    if (S_ISDIR(path_stat.st_mode)) {
        ERROR_CLEAR(error);
        return IO_INVALID_FD;
    }

    int file = open(path, O_RDONLY);

    if (file == -1) {
        ERROR_ERRNO(error, errno);
        return IO_INVALID_FD;
    }

    ERROR_CLEAR(error);
    return file;
}

static const char* Plugin_get_description() {
    return "read files";
}

static const char* Plugin_get_name() {
    return "file";
}

static void Plugin_run(
        Plugin* plugin, Array* inputs, Array* outputs, Error* error) {

    for (size_t i = 0; i < inputs->length; ++i) {
        Input* input = (Input*) inputs->data[i];

        if ((input != NULL) && (input->fd == IO_INVALID_FD)) {
            input->fd = open_file(input->name, error);

            if (ERROR_HAS(error)) {
                return;
            }
        }
    }

    ERROR_CLEAR(error);
}

Plugin File_Plugin = {
    {NULL},
    Plugin_get_description,
    Plugin_get_name,
    Plugin_run,
};
