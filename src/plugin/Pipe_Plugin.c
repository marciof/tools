#include <errno.h>
#include <poll.h>
#include <stdio.h>
#include <sys/stat.h>
#include <unistd.h>
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


static Plugin_Result run(List args, List options, List fds_in, Error* error) {
    List new_fds_in = List_new(error, NULL);

    if (Error_has(error)) {
        return NO_PLUGIN_RESULT;
    }

    for (size_t i = 0; i < List_length(fds_in); ++i) {
        int fd_in = (int) List_get(fds_in, i, NULL);
        struct stat fd_in_stat;

        if (fstat(fd_in, &fd_in_stat) == -1) {
            Error_errno(error, errno);
            List_delete(new_fds_in, NULL);
            return NO_PLUGIN_RESULT;
        }

        if (S_ISDIR(fd_in_stat.st_mode)) {
            continue;
        }

        if (!S_ISFIFO(fd_in_stat.st_mode)) {
            bool has_fd_input = has_input(fd_in, error);

            if (Error_has(error)) {
                List_delete(new_fds_in, NULL);
                return NO_PLUGIN_RESULT;
            }

            if (!has_fd_input) {
                continue;
            }
        }

        List_add(new_fds_in, (intptr_t) fd_in, error);

        if (Error_has(error)) {
            List_delete(new_fds_in, NULL);
            return NO_PLUGIN_RESULT;
        }
    }

    Plugin_Result result = {args, new_fds_in};
    Error_clear(error);
    return result;
}


Plugin Pipe_Plugin = {
    NULL,
    get_description,
    get_name,
    run,
};
