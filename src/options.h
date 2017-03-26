#pragma once
#include <stddef.h>
#include "Error.h"
#include "Plugin.h"

/**
 * @param plugin_options flat array of plugin options per plugin
 * @return `argv` index of the first argument, or negative on error or help
 */
int parse_options(
    int argc,
    char* argv[],
    size_t nr_plugins,
    Plugin* plugins[],
    char* plugin_options[],
    Error* error);
