#pragma once
#include <stddef.h>
#include "Array.h"
#include "Error.h"
#include "plugin/Plugin.h"


Array Options_parse(
    int argc, char* argv[], Plugin* plugins[], size_t nr_plugins, Error* error);
