#include "Vcs.h"

#define EXTERNAL_BINARY "git"

static const char* Plugin_get_description() {
    return "show VCS revisions via `" EXTERNAL_BINARY "`";
}

static const char* Plugin_get_name() {
    return "vcs";
}

static void Plugin_run(
        Plugin* plugin, Array* inputs, Array* outputs, Error* error) {

    ERROR_CLEAR(error);
}

Plugin Vcs_Plugin = {
    {NULL},
    Plugin_get_description,
    Plugin_get_name,
    Plugin_run,
};
