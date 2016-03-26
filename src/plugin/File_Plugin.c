#include <errno.h>
#include <fcntl.h>
#include <sys/stat.h>
#include "File_Plugin.h"

static const char* get_description() {
    return "read files";
}

static const char* get_name() {
    return "file";
}

static int open_file(char* path, Error* error) {
    struct stat path_stat;

    if (stat(path, &path_stat) == -1) {
        if (errno == ENOENT) {
            Error_clear(error);
        }
        else {
            Error_errno(error, errno);
        }
        return INPUT_NO_FD;
    }

    if (S_ISDIR(path_stat.st_mode)) {
        Error_clear(error);
        return INPUT_NO_FD;
    }

    int file = open(path, O_RDONLY);

    if (file == -1) {
        Error_errno(error, errno);
        return INPUT_NO_FD;
    }

    Error_clear(error);
    return file;
}

static void run(Array* inputs, Array* options, int* output_fd, Error* error) {
    for (size_t i = 0; i < inputs->length; ++i) {
        Input* input = (Input*) inputs->data[i];

        if ((input != NULL) && (input->fd == INPUT_NO_FD)) {
            input->fd = open_file(input->name, error);

            if (Error_has(error)) {
                return;
            }
        }
    }

    Error_clear(error);
}

Plugin File_Plugin = {
    NULL,
    get_description,
    get_name,
    run,
};
