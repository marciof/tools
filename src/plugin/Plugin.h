#pragma once
#include <stddef.h>
#include "../Array.h"
#include "../Error.h"


typedef struct {
    Array args;
    Array fds_in;
} Plugin_Result;


typedef struct {
    Array options;
    const char* (*get_description)();
    const char* (*get_name)();
    Plugin_Result (*run)(Array args, Array options, Array fds_in, Error* error);
} Plugin;


extern Plugin_Result NO_PLUGIN_RESULT;
