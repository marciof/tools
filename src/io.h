#pragma once
#include <stddef.h>
#include <stdint.h>
#include "Error.h"

void io_write(int fd, uint8_t* data, size_t length, Error* error);
