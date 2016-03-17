#include "Pager_Plugin.h"

#define EXTERNAL_BINARY "pager"

static const char* get_description() {
    return "page output via `" EXTERNAL_BINARY "`";
}

static const char* get_name() {
    return EXTERNAL_BINARY;
}

static void run(Array* inputs, Array* options, int* output_fd, Error* error) {
    Error_clear(error);
}

Plugin Pager_Plugin = {
    NULL,
    get_description,
    get_name,
    run,
};
