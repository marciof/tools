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
        return -1;
    }

    if (S_ISDIR(path_stat.st_mode)) {
        Error_clear(error);
        return -1;
    }

    int file = open(path, O_RDONLY);

    if (file == -1) {
        Error_errno(error, errno);
        return -1;
    }

    Error_clear(error);
    return file;
}


static Array run(Array args, Array options, Array fds_in, Error* error) {
    if (args->length == 0) {
        Error_clear(error);
        return args;
    }

    Array new_args = Array_new(error, NULL);

    if (Error_has(error)) {
        return NULL;
    }

    for (size_t i = 0; i < args->length; ++i) {
        char* arg = (char*) args->data[i];
        int fd_in = open_file(arg, error);

        if (Error_has(error)) {
            Array_delete(new_args);
            return NULL;
        }

        if (fd_in == -1) {
            Array_add(new_args, (intptr_t) arg, error);

            if (Error_has(error)) {
                Array_delete(new_args);
                return NULL;
            }

            continue;
        }

        Array_add(fds_in, (intptr_t) fd_in, error);

        if (Error_has(error)) {
            Array_delete(new_args);
            return NULL;
        }
    }

    Error_clear(error);
    return new_args;
}


Plugin File_Plugin = {
    NULL,
    get_description,
    get_name,
    run,
};
