#pragma once
#include "../list/List.h"
#include "../std/Error.h"


typedef struct {
    List args;
    List fds_in;
} Plugin_Result;


typedef struct {
    List options;
    const char* (*get_description)();
    const char* (*get_name)();
    Plugin_Result (*run)(List args, List options, List fds_in, Error* error);
} Plugin;


extern Plugin_Result NULL_PLUGIN_RESULT;
