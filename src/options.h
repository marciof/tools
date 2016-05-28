#pragma once
#include <stdbool.h>
#include <stddef.h>
#include "Array.h"
#include "Error.h"
#include "Plugin.h"

// If a plugin is disabled, its entry in `plugins` is set to `NULL`.
// If help usage was displayed, it returns `true`.
bool parse_options(
    int argc,
    char **argv,
    Plugin **plugins,
    size_t nr_plugins,
    Array* inputs,
    Error *error);
