#ifndef SHOW__PLUGIN_H
#define SHOW__PLUGIN_H


#include "list/List.h"
#include "std/Error.h"


typedef struct {
    const char* (*get_description)();
    const char* (*get_name)();
    int (*run)(int argc, char* argv[], List options, Error* error);
} Plugin;


#endif
