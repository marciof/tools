#ifndef SHOW__PLUGIN_H
#define SHOW__PLUGIN_H


#include "../list/List.h"
#include "../std/Error.h"


typedef struct {
    List options;

    const char* (*get_description)();
    const char* (*get_name)();

    List (*run)(
        List fds_in,
        int argc,
        char* argv[],
        List options,
        Error* error);
} Plugin;


#endif
