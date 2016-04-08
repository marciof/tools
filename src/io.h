#pragma once
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include "Error.h"

bool io_has_input(int fd, Error* error);
void io_write(int fd, uint8_t* data, size_t length, Error* error);
