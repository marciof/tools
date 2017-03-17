#include <errno.h>
#include <fcntl.h>
#include <string.h>
#include <sys/stat.h>
#include "../io.h"
#include "File.h"

static int open_file(char* path, Error* error) {
    struct stat path_stat;

    if (stat(path, &path_stat) == -1) {
        if (errno != ENOENT) {
            Error_add(error, strerror(errno));
        }
        return IO_INVALID_FD;
    }

    if (S_ISDIR(path_stat.st_mode)) {
        return IO_INVALID_FD;
    }

    int fd = open(path, O_RDONLY);

    if (fd == -1) {
        Error_add(error, strerror(errno));
        return IO_INVALID_FD;
    }

    return fd;
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
                Error_add(error, input->name);
                return;
            }
            else if (input->fd != IO_INVALID_FD) {
                input->plugin = plugin;
            }
        }
    }
}

Plugin File_Plugin = {
    ARRAY_NULL_INITIALIZER,
    Plugin_get_description,
    Plugin_get_name,
    NULL,
    Plugin_run,
};
