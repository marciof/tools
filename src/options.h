#pragma once
#include <stddef.h>
#include "Error.h"
#include "Plugin.h"

/**
 * @param options_per_plugin flat array of plugin options per plugin
 * @return `argv` index of the first argument, or negative on error or help
 */
int parse_options(
    int argc,
    char* argv[],
    size_t plugins_length,
    Plugin* plugins[],
    size_t max_nr_options_per_plugin,
    size_t nr_options_per_plugin[],
    char* options_per_plugin[],
    Error* error);
