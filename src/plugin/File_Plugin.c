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
        return RESOURCE_NO_FD;
    }

    if (S_ISDIR(path_stat.st_mode)) {
        Error_clear(error);
        return RESOURCE_NO_FD;
    }

    int file = open(path, O_RDONLY);

    if (file == -1) {
        Error_errno(error, errno);
        return RESOURCE_NO_FD;
    }

    Error_clear(error);
    return file;
}


static void run(Array resources, Array options, Error* error) {
    for (size_t i = 0; i < resources->length; ++i) {
        Resource resource = (Resource) resources->data[i];

        if (resource->fd == RESOURCE_NO_FD) {
            resource->fd = open_file(resource->name, error);

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
