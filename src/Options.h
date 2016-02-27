#pragma once
#include <stddef.h>
#include "list/List.h"
#include "plugin/Plugin.h"
#include "std/Error.h"


List Options_parse(
    int argc, char* argv[], Plugin* plugins[], size_t nr_plugins, Error* error);
