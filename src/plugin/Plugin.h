#ifndef SHOW__PLUGIN_H
#define SHOW__PLUGIN_H


#include "../list/List.h"
#include "../std/Error.h"


typedef struct {
    List options;
    const char* (*get_description)();
    const char* (*get_name)();
    List (*run)(List args, List options, List fds_in, Error* error);
} Plugin;


#endif
