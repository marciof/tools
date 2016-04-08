#include <errno.h>
#include <unistd.h>
#include "io.h"

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
