#pragma once
#include <stddef.h>
#include "../Array.h"
#include "../Error.h"


typedef struct {
    Array options;
    const char* (*get_description)();
    const char* (*get_name)();
    Array (*run)(Array args, Array options, Array fds_in, Error* error);
} Plugin;
