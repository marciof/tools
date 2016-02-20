#include <errno.h>
#include <poll.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>
#include "../std/Error.h"
#include "Pipe_Plugin.h"


static bool has_input(Error* error) {
    struct pollfd fds;

    fds.fd = STDIN_FILENO;
    fds.events = POLLIN;

    int nr_fds = poll(&fds, 1, 0);

    if (nr_fds < 0) {
        *error = strerror(errno);
        return false;
    }

    *error = NULL;
    return nr_fds == 1;
}


static bool is_being_piped_into(Error* error) {
    struct stat stats;

    if (fstat(STDIN_FILENO, &stats) == -1) {
        *error = strerror(errno);
        return false;
    }

    *error = NULL;
    return S_ISFIFO(stats.st_mode);
}


const char* get_description() {
    return "pipe `stdin` to `stdout`";
}


const char* get_name() {
    return "pipe";
}


int run(int argc, char* argv[], List options, Error* error) {
    bool is_active = is_being_piped_into(error);

    if (*error) {
        return PLUGIN_INVALID_FD_OUT;
    }
    else if (is_active) {
        *error = NULL;
        return STDIN_FILENO;
    }

    is_active = has_input(error);

    if (*error) {
        return PLUGIN_INVALID_FD_OUT;
    }
    else if (is_active) {
        *error = NULL;
        return STDIN_FILENO;
    }

    *error = NULL;
    return PLUGIN_INVALID_FD_OUT;
}


Plugin Pipe_Plugin = {
    get_description,
    get_name,
    run,
};
