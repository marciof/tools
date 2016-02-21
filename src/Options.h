#ifndef SHOW__OPTIONS_H
#define SHOW__OPTIONS_H


#include <stddef.h>
#include "map/Map.h"
#include "plugin/Plugin.h"
#include "std/Error.h"


typedef struct {
    int optind;
    Map plugin_options;
} Options;


void Options_delete(Options options);
List Options_get_plugin_options(Options options, const char* name);

Options Options_parse(
    int argc, char* argv[], Plugin* plugins[], size_t nr_plugins, Error* error);


#endif
