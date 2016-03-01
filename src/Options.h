#pragma once
#include <stddef.h>
#include "Error.h"
#include "List.h"
#include "plugin/Plugin.h"


List Options_parse(
    int argc, char* argv[], Plugin* plugins[], size_t nr_plugins, Error* error);
