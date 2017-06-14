#pragma once
#include <stdbool.h>
#include <stddef.h>
#include "Error.h"

// Not to be confused with the "null device" (eg. /dev/null).
#define IO_NULL_FD ((int) -1)

bool io_has_input(int fd, struct Error* error);
bool io_is_tty(int fd, struct Error* error);
void io_write_all(int fd, void* data, size_t nr_bytes, struct Error* error);
