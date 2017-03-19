#pragma once
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include "Error.h"

// Not to be confused with the "null device" (eg. /dev/null).
#define IO_NULL_FD ((int) -1)

// Use always as a pointer only, never by value.
typedef struct {
    size_t length;
    char data[];
} Buffer;

void Buffer_delete(Buffer* buffer);
Buffer* Buffer_new(size_t max_length, Error* error);

bool io_has_input(int fd, Error* error);
void io_write(int fd, uint8_t* data, size_t nr_bytes, Error* error);
