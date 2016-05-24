#pragma once
#include <stdbool.h>
#include <stddef.h>
#include "Error.h"

#define IO_INVALID_FD ((int) -1)

// Never use by value, always as a pointer.
typedef struct {
    size_t length;
    char data[];
} Buffer;

void Buffer_delete(Buffer* buffer);
Buffer* Buffer_new(size_t max_length, Error* error);

void io_close(int fd, Error* error);
void io_write(int fd, Buffer* buffer, Error* error);
bool io_has_input(int fd, Error* error);
