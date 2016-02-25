#include <errno.h>
#include <poll.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>
#include "../list/Array_List.h"
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


static const char* get_description() {
    return "pipe `stdin`";
}


static const char* get_name() {
    return "pipe";
}


static List run(
        List fds_in,
        int argc,
        char* argv[],
        List options,
        Error* error) {

    List new_fds_in = List_new(Array_List, error);

    if (*error) {
        return fds_in;
    }

    Iterator it = List_iterator(fds_in, error);

    while (Iterator_has_next(it)) {
        Error discard;
        int fd_in = (int) Iterator_next(it, &discard);
        struct stat fd_in_stat;

        if (fstat(fd_in, &fd_in_stat) == -1) {
            List_delete(new_fds_in, &discard);
            Iterator_delete(it);
            *error = strerror(errno);
            return NULL;
        }

        if (S_ISDIR(fd_in_stat.st_mode)) {
            continue;
        }

        if (!S_ISFIFO(fd_in_stat.st_mode)) {
            bool has_fd_input = has_input(fd_in, error);

            if (*error) {
                List_delete(new_fds_in, &discard);
                Iterator_delete(it);
                return NULL;
            }

            if (!has_fd_input) {
                continue;
            }
        }

        List_add(new_fds_in, (intptr_t) fd_in, error);

        if (*error) {
            List_delete(new_fds_in, &discard);
            Iterator_delete(it);
            return NULL;
        }
    }

    Iterator_delete(it);
    *error = NULL;
    return new_fds_in;
}


Plugin Cat_Plugin = {
    NULL,
    get_description,
    get_name,
    run,
};
