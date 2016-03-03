#include <errno.h>
#include <poll.h>
#include <stdio.h>
#include <sys/stat.h>
#include <unistd.h>
#include "../Array.h"
#include "../Error.h"
#include "Pipe_Plugin.h"


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


static Array run(Array args, Array options, Array fds_in, Error* error) {
    int fd_in = STDIN_FILENO;
    struct stat fd_in_stat;

    if (fstat(fd_in, &fd_in_stat) == -1) {
        Error_errno(error, errno);
        return NULL;
    }

    if (S_ISDIR(fd_in_stat.st_mode)) {
        Error_clear(error);
        return args;
    }

    if (!S_ISFIFO(fd_in_stat.st_mode)) {
        bool has_fd_input = has_input(fd_in, error);

        if (Error_has(error)) {
            return NULL;
        }

        if (!has_fd_input) {
            Error_clear(error);
            return args;
        }
    }

    Array_add(fds_in, (intptr_t) fd_in, error);

    if (Error_has(error)) {
        return NULL;
    }

    Error_clear(error);
    return args;
}


Plugin Pipe_Plugin = {
    NULL,
    get_description,
    get_name,
    run,
};
