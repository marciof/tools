#define _POSIX_C_SOURCE 200809L

#include <dirent.h>
#include <errno.h>
#include <poll.h>
#include <stdio.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
#include "../Array.h"
#include "../Error.h"
#include "Pipe_Plugin.h"


static char fd_dir_name[STATIC_ARRAY_LENGTH(((struct dirent*) NULL)->d_name)];


static char* get_fd_dir_path(int fd, Error* error) {
    DIR* cwd = opendir(".");

    if (cwd == NULL) {
        Error_errno(error, errno);
        return NULL;
    }

    int cwd_fd = dirfd(cwd);

    if (cwd_fd == -1) {
        Error_errno(error, errno);
        return NULL;
    }

    if (fchdir(fd) == -1) {
        Error_errno(error, errno);
        closedir(cwd);
        return NULL;
    }

    if (getcwd(fd_dir_name, STATIC_ARRAY_LENGTH(fd_dir_name)) == NULL) {
        Error_errno(error, errno);

        if (fchdir(cwd_fd) == -1) {
            Error_errno(error, errno);
        }

        closedir(cwd);
        return NULL;
    }

    if (fchdir(cwd_fd) == -1) {
        Error_errno(error, errno);
        closedir(cwd);
        return NULL;
    }

    closedir(cwd);
    Error_clear(error);
    return fd_dir_name;
}


static bool has_input(int fd_in, Error* error) {
    struct pollfd fds;

    fds.fd = fd_in;
    fds.events = POLLIN;

    int nr_fds = poll(&fds, 1, 0);

    if (nr_fds < 0) {
        Error_errno(error, errno);
        return false;
    }

    Error_clear(error);
    return nr_fds == 1;
}


static const char* get_description() {
    return "pipe `stdin`";
}


static const char* get_name() {
    return "pipe";
}


static void run(Array args, Array options, Array fds_in, Error* error) {
    int fd_in = STDIN_FILENO;
    struct stat fd_in_stat;

    if (fstat(fd_in, &fd_in_stat) == -1) {
        Error_errno(error, errno);
        return;
    }

    if (S_ISDIR(fd_in_stat.st_mode)) {
        char* path = get_fd_dir_path(fd_in, error);

        if (!Error_has(error)) {
            Array_insert(args, (intptr_t) path, 0, error);
        }

        return;
    }

    if (!S_ISFIFO(fd_in_stat.st_mode)) {
        bool has_fd_input = has_input(fd_in, error);

        if (Error_has(error)) {
            return;
        }

        if (!has_fd_input) {
            Error_clear(error);
            return;
        }
    }

    Array_add(fds_in, (intptr_t) fd_in, error);
}


Plugin Pipe_Plugin = {
    NULL,
    get_description,
    get_name,
    run,
};
