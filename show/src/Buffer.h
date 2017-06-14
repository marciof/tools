#pragma once
#include <stddef.h>
#include "Error.h"

/** Use always as a pointer only, never by value. */
struct Buffer {
    size_t length;
    char data[];
};

void Buffer_delete(struct Buffer* buffer);
struct Buffer* Buffer_new(size_t max_length, struct Error* error);
