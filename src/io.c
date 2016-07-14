#include <errno.h>
#include <poll.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include "io.h"

void Buffer_delete(Buffer* buffer) {
    free(buffer);
}

Buffer* Buffer_new(size_t max_length, Error* error) {
    Buffer* buffer = (Buffer*) malloc(
        offsetof(Buffer, data) + sizeof(char) * max_length);

    if (buffer == NULL) {
        Error_add(error, strerror(errno));
        return NULL;
    }

    buffer->length = 0;
    return buffer;
}

void io_close(int fd, Error* error) {
    if (close(fd) == -1) {
        Error_add(error, strerror(errno));
    }
}

bool io_has_input(int fd, Error* error) {
    struct pollfd fd_poll;

    fd_poll.fd = fd;
    fd_poll.events = POLLIN;

    int nr_fds = poll(&fd_poll, 1, 0);

    if (nr_fds < 0) {
        Error_add(error, strerror(errno));
        return false;
    }

    return (nr_fds == 1) && (fd_poll.revents & POLLIN);
}

void io_write(int fd, Buffer* buffer, Error* error) {
    size_t remaining_length = buffer->length;
    char* remaining_data = buffer->data;

    while (remaining_length > 0) {
        ssize_t bytes_written = write(
            fd, remaining_data, remaining_length * sizeof(char));

        if (bytes_written == -1) {
            Error_add(error, strerror(errno));
            return;
        }

        remaining_length -= bytes_written / sizeof(char);
        remaining_data += bytes_written / sizeof(char);
    }
}
