#include "../popen2.h"
#include "Pager.h"

// Don't use `pager` as it's not available on all systems.
#define EXTERNAL_BINARY "less"

static bool is_available(struct Plugin* plugin, struct Error* error) {
    char* argv[] = {
        EXTERNAL_BINARY,
        "--version",
        NULL,
    };

    return popen2_check(argv[0], argv, error);
}

static void open_input(
        struct Plugin* plugin,
        struct Input* input,
        size_t argc,
        char* argv[],
        struct Error* error) {
}

struct Plugin Pager_Plugin = {
    "pager",
    "page output via `" EXTERNAL_BINARY "`, when needed",
    is_available,
    open_input,
};
