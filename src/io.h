#pragma once
#include <stdbool.h>
#include <stddef.h>
#include "Error.h"

bool io_has_input(int fd, Error* error);
void io_write(int fd, char* data, size_t length, Error* error);
