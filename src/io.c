#include <errno.h>
#include <poll.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
#include "io.h"

void Buffer_delete(Buffer* buffer) {
    free(buffer);
}

Buffer* Buffer_new(size_t max_length, Error* error) {
    Buffer* buffer = (Buffer*) malloc(
        offsetof(Buffer, data) + sizeof(buffer->data[0]) * max_length);

    if (buffer == NULL) {
        Error_add(error, strerror(errno));
        return NULL;
    }

    buffer->length = 0;
    return buffer;
}

bool io_has_input(int fd, Error* error) {
    struct pollfd fd_poll;

    fd_poll.fd = fd;
    fd_poll.events = POLLIN;

    int nr_fds = poll(&fd_poll, 1, 0);

    if (nr_fds == -1) {
        Error_add(error, strerror(errno));
        return false;
    }

    return (nr_fds == 1) && (fd_poll.revents & POLLIN);
}

bool io_is_tty(int fd, Error* error) {
    struct stat fd_stat;

    if (fstat(fd, &fd_stat) == -1) {
        Error_add(error, strerror(errno));
        return false;
    }

    errno = 0;

    // Check if it's a character device first to avoid `EINVAL` and `ENOTTY`.
    bool is_tty = S_ISCHR(fd_stat.st_mode) && isatty(fd);

    if (errno != 0) {
        Error_add(error, strerror(errno));
        return false;
    }

    return is_tty;
}

void io_write(int fd, uint8_t* data, size_t nr_bytes, Error* error) {
    while (nr_bytes > 0) {
        ssize_t bytes_written = write(fd, data, nr_bytes);

        if (bytes_written == -1) {
            Error_add(error, strerror(errno));
            return;
        }

        nr_bytes -= bytes_written;
        data += bytes_written;
    }
}
