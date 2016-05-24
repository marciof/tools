#include <errno.h>
#include <poll.h>
#include <stdlib.h>
#include <unistd.h>
#include "io.h"

void Buffer_delete(Buffer* buffer) {
    free(buffer);
}

Buffer* Buffer_new(size_t max_length, Error* error) {
    Buffer* buffer = (Buffer*) malloc(
        offsetof(Buffer, data) + sizeof(char) * max_length);

    if (buffer == NULL) {
        ERROR_ERRNO(error, errno);
        return NULL;
    }

    buffer->length = 0;
    return buffer;
}

void io_close(int fd, Error* error) {
    if (close(fd) == -1) {
        ERROR_ERRNO(error, errno);
    }
    else {
        ERROR_CLEAR(error);
    }
}

bool io_has_input(int fd, Error* error) {
    struct pollfd fd_poll;

    fd_poll.fd = fd;
    fd_poll.events = POLLIN;

    int nr_fds = poll(&fd_poll, 1, 0);

    if (nr_fds < 0) {
        ERROR_ERRNO(error, errno);
        return false;
    }

    ERROR_CLEAR(error);
    return (nr_fds == 1) && (fd_poll.revents & POLLIN);
}

void io_write(int fd, Buffer* buffer, Error* error) {
    size_t remaining_length = buffer->length;
    char* remaining_data = buffer->data;

    while (remaining_length > 0) {
        ssize_t bytes_written = write(
            fd, remaining_data, remaining_length * sizeof(char));

        if (bytes_written == -1) {
            ERROR_ERRNO(error, errno);
            return;
        }

        remaining_length -= bytes_written / sizeof(char);
        remaining_data += bytes_written / sizeof(char);
    }

    ERROR_CLEAR(error);
}
