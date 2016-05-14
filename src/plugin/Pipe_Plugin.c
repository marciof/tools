#define _POSIX_C_SOURCE 200809L
#include <dirent.h>
#include <errno.h>
#include <stdio.h>
#include <sys/stat.h>
#include <unistd.h>
#include "../Array.h"
#include "../Error.h"
#include "../io.h"
#include "Pipe_Plugin.h"

static char fd_dir_name[STATIC_ARRAY_LENGTH(((struct dirent*) NULL)->d_name)];

static void close_pipe(Input* input, Error* error) {
    io_close(input->fd, error);
}

static char* get_fd_dir_path(int fd, Error* error) {
    DIR* cwd = opendir(".");

    if (cwd == NULL) {
        ERROR_ERRNO(error, errno);
        return NULL;
    }

    int cwd_fd = dirfd(cwd);

    if (cwd_fd == -1) {
        ERROR_ERRNO(error, errno);
        return NULL;
    }

    if (fchdir(fd) == -1) {
        ERROR_ERRNO(error, errno);
        closedir(cwd);
        return NULL;
    }

    if (getcwd(fd_dir_name, STATIC_ARRAY_LENGTH(fd_dir_name)) == NULL) {
        ERROR_ERRNO(error, errno);

        if (fchdir(cwd_fd) == -1) {
            ERROR_ERRNO(error, errno);
        }

        closedir(cwd);
        return NULL;
    }

    if (fchdir(cwd_fd) == -1) {
        ERROR_ERRNO(error, errno);
        closedir(cwd);
        return NULL;
    }

    closedir(cwd);
    ERROR_CLEAR(error);
    return fd_dir_name;
}

static const char* get_description() {
    return "pipe input";
}

static const char* get_name() {
    return "pipe";
}

static void run(Array* inputs, Array* options, Array* outputs, Error* error) {
    int fd = STDIN_FILENO;
    struct stat fd_stat;
    Input* input;
    size_t position;

    if (fstat(fd, &fd_stat) == -1) {
        ERROR_ERRNO(error, errno);
        return;
    }

    if (S_ISFIFO(fd_stat.st_mode)) {
        input = Input_new(NULL, fd, error);
        position = 0;
    }
    else if (S_ISDIR(fd_stat.st_mode)) {
        char* path = get_fd_dir_path(fd, error);

        if (ERROR_HAS(error)) {
            return;
        }

        input = Input_new(path, IO_INVALID_FD, error);
        position = inputs->length;
    }
    else {
        bool has_fd_input = io_has_input(fd, error);

        if (ERROR_HAS(error)) {
            return;
        }

        if (!has_fd_input) {
            ERROR_CLEAR(error);
            return;
        }

        input = Input_new(NULL, fd, error);
        position = inputs->length;
    }

    if (ERROR_HAS(error)) {
        return;
    }

    input->close = close_pipe;
    Array_add(inputs, position, (intptr_t) input, error);

    if (ERROR_HAS(error)) {
        Input_delete(input);
    }
}

Plugin Pipe_Plugin = {
    {NULL},
    get_description,
    get_name,
    run,
};
