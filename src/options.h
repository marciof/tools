#pragma once
#include <stdbool.h>
#include <stddef.h>
#include "Array.h"
#include "Error.h"
#include "plugin/Plugin.h"

// If a plugin is disabled, its entry in `plugins` is set to `NULL`.
// If `NULL` is returned without any `error`, it means help usage was displayed.
bool parse_options(
    int argc,
    char **argv,
    Plugin **plugins,
    size_t nr_plugins,
    Array* inputs,
    Error *error);
