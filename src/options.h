#pragma once
#include <stddef.h>
#include "Error.h"
#include "Plugin.h"

/**
 * @return `argv` index of the first non-option, or negative on error or help
 */
int parse_options(
    int argc,
    char* argv[],
    size_t nr_plugins,
    struct Plugin_Setup plugins_setup[],
    Error* error);
