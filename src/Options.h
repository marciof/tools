#ifndef SHOW__OPTIONS_H
#define SHOW__OPTIONS_H


#include <stdbool.h>
#include "list/List.h"
#include "map/Map.h"
#include "Plugin.h"
#include "std/Error.h"


typedef struct {
    int optind;
    List disabled_plugins;
    Map plugin_options;
} Options;


void Options_delete(Options options);
List Options_get_plugin_options(Options options, const char* name);
bool Options_is_plugin_enabled(Options options, const char* name, Error* error);
Options Options_parse(int argc, char* argv[], Plugin* plugins[], Error* error);


#endif
