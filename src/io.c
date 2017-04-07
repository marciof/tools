#include <poll.h>
#include <stdlib.h>
#include <unistd.h>
#include "io.h"

void Buffer_delete(struct Buffer* buffer) {
    free(buffer);
}

struct Buffer* Buffer_new(size_t max_length, struct Error* error) {
    struct Buffer* buffer = (struct Buffer*) malloc(
        offsetof(struct Buffer, data) + sizeof(buffer->data[0]) * max_length);

    if (buffer == NULL) {
        Error_add_errno(error, errno);
        return NULL;
    }

    buffer->length = 0;
    return buffer;
}

bool io_has_input(int fd, struct Error* error) {
    struct pollfd fd_poll;

    fd_poll.fd = fd;
    fd_poll.events = POLLIN;

    int nr_fds = poll(&fd_poll, 1, 0);

    if (nr_fds == -1) {
        Error_add_errno(error, errno);
        return false;
    }

    return (nr_fds == 1) && (fd_poll.revents & POLLIN);
}

bool io_is_tty(int fd, struct Error* error) {
    bool is_tty = (isatty(fd) != 0);

    if (!is_tty && (errno != ENOTTY)) {
        Error_add_errno(error, errno);
        return false;
    }

    return is_tty;
}

void io_write(int fd, uint8_t* data, size_t nr_bytes, struct Error* error) {
    while (nr_bytes > 0) {
        ssize_t bytes_written = write(fd, data, nr_bytes);

        if (bytes_written == -1) {
            Error_add_errno(error, errno);
            return;
        }

        nr_bytes -= bytes_written;
        data += bytes_written;
    }
}
