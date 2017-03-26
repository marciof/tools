#pragma once
#include <stddef.h>
#include "Error.h"
#include "Plugin.h"

/**
 * @return `argv` index of the first argument, or `-1` on error or help
 */
int parse_options(
    int argc,
    char* argv[],
    Plugin* plugins[],
    size_t nr_plugins,
    Error* error);
