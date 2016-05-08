#include <errno.h>
#include <poll.h>
#include <unistd.h>
#include "io.h"

bool io_has_input(int fd, Error* error) {
    struct pollfd fd_poll;

    fd_poll.fd = fd;
    fd_poll.events = POLLIN;

    int nr_fds = poll(&fd_poll, 1, 0);

    if (nr_fds < 0) {
        Error_errno(error, errno);
        return false;
    }

    Error_clear(error);
    return (nr_fds == 1) && (fd_poll.revents & POLLIN);
}

void io_write(int fd, uint8_t* data, size_t length, Error* error) {
    while (length > 0) {
        ssize_t bytes_written = write(fd, data, length);

        if (bytes_written == -1) {
            Error_errno(error, errno);
            return;
        }

        length -= bytes_written;
        data += bytes_written;
    }

    Error_clear(error);
}
