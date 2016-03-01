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


static Plugin_Result run(List args, List options, List fds_in, Error* error) {
    if (List_length(args) == 0) {
        Error_clear(error);
        return NO_PLUGIN_RESULT;
    }

    List new_args = List_new(error, NULL);

    if (Error_has(error)) {
        return NO_PLUGIN_RESULT;
    }

    for (size_t i = 0; i < List_length(args); ++i) {
        char* arg = (char*) List_get(args, i, NULL);
        int fd_in = open_file(arg, error);

        if (Error_has(error)) {
            List_delete(new_args, NULL);
            return NO_PLUGIN_RESULT;
        }

        if (fd_in == -1) {
            List_add(new_args, (intptr_t) arg, error);

            if (Error_has(error)) {
                List_delete(new_args, NULL);
                return NO_PLUGIN_RESULT;
            }

            continue;
        }

        List_add(fds_in, (intptr_t) fd_in, error);

        if (Error_has(error)) {
            List_delete(new_args, NULL);
            return NO_PLUGIN_RESULT;
        }
    }

    Plugin_Result result = {new_args, fds_in};
    Error_clear(error);
    return result;
}


Plugin File_Plugin = {
    NULL,
    get_description,
    get_name,
    run,
};
