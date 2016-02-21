#ifndef SHOW__OPTIONS_H
#define SHOW__OPTIONS_H


#include <stddef.h>
#include "plugin/Plugin.h"
#include "std/Error.h"


int Options_parse(
    int argc, char* argv[], Plugin* plugins[], size_t nr_plugins, Error* error);


#endif
