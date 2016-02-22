#include <errno.h>
#include <poll.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>
#include "../std/Error.h"
#include "Cat_Plugin.h"


static bool has_input(int fd_in, Error* error) {
    struct pollfd fds;

    fds.fd = fd_in;
    fds.events = POLLIN;

    int nr_fds = poll(&fds, 1, 0);

    if (nr_fds < 0) {
        *error = strerror(errno);
        return false;
    }

    *error = NULL;
    return nr_fds == 1;
}


const char* get_description() {
    return "`cat` POSIX command";
}


const char* get_name() {
    return "cat";
}


int run(int fd_in, int argc, char* argv[], List options, Error* error) {
    if (fd_in == PLUGIN_INVALID_FD_OUT) {
        *error = NULL;
        return PLUGIN_INVALID_FD_OUT;
    }

    struct stat fd_in_stat;

    if (fstat(fd_in, &fd_in_stat) == -1) {
        *error = strerror(errno);
        return PLUGIN_INVALID_FD_OUT;
    }

    if (S_ISFIFO(fd_in_stat.st_mode)) {
        *error = NULL;
        return fd_in;
    }
    else if (S_ISDIR(fd_in_stat.st_mode)) {
        *error = NULL;
        return PLUGIN_INVALID_FD_OUT;
    }

    bool is_active = has_input(fd_in, error);

    if (*error) {
        return PLUGIN_INVALID_FD_OUT;
    }
    else if (is_active) {
        *error = NULL;
        return fd_in;
    }

    *error = NULL;
    return PLUGIN_INVALID_FD_OUT;
}


Plugin Cat_Plugin = {
    NULL,
    get_description,
    get_name,
    run,
};
