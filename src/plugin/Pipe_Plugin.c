#include <errno.h>
#include <poll.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>
#include "../std/Error.h"
#include "Pipe_Plugin.h"


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


static bool is_being_piped_into(int fd_in, Error* error) {
    struct stat stats;

    if (fstat(fd_in, &stats) == -1) {
        *error = strerror(errno);
        return false;
    }

    *error = NULL;
    return S_ISFIFO(stats.st_mode);
}


const char* get_description() {
    return "pipe `stdin` (if any) to `stdout`";
}


const char* get_name() {
    return "pipe";
}


int run(int fd_in, int argc, char* argv[], List options, Error* error) {
    if (fd_in == PLUGIN_INVALID_FD_OUT) {
        *error = NULL;
        return fd_in;
    }

    bool is_active = is_being_piped_into(fd_in, error);

    if (*error) {
        return PLUGIN_INVALID_FD_OUT;
    }
    else if (is_active) {
        *error = NULL;
        return fd_in;
    }

    is_active = has_input(fd_in, error);

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


Plugin Pipe_Plugin = {
    get_description,
    get_name,
    run,
};
