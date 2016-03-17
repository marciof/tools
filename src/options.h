#pragma once
#include <stddef.h>
#include "Array.h"
#include "Error.h"
#include "plugin/Plugin.h"

Array* parse_options(
    int argc, char **argv, Plugin **plugins, size_t nr_plugins, Error *error);
