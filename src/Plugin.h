#pragma once
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include "Buffer.h"
#include "Error.h"

struct Input {
    /** `NULL` when a plugin is run with no inputs to get a default one. */
    char* name;
    int fd;
    intptr_t arg;

    /** @param error `errno` `ENOENT` if the plugin is unavailable */
    void (*close)(struct Input* input, struct Error* error);

    /** @return read count, or `0` on end of input or error */
    size_t (*read)(
        struct Input* input,
        char* buffer,
        size_t length,
        struct Error* error);
};

struct Output {
    int fd;
    void (*close)(struct Output* output, struct Error* error);

    void (*write)(
        struct Output* output,
        char* buffer,
        size_t length,
        struct Error* error);
};

struct Plugin {
    char* name;
    char* description;
    bool (*is_available)(struct Plugin* plugin, struct Error* error);

    /** @param input `fd` is `IO_NULL_FD` when plugin doesn't support it */
    void (*open_input)(
        struct Plugin* plugin,
        struct Input* input,
        size_t argc,
        char* argv[],
        struct Error* error);

    /** @param output `fd` is `IO_NULL_FD` when plugin doesn't support it */
    void (*open_output)(
        struct Plugin* plugin,
        struct Output* output,
        size_t argc,
        char* argv[],
        struct Error* error);
};

struct Plugin_Setup {
    struct Plugin* plugin;
    bool is_enabled;
    size_t argc;
    char** argv;
};
