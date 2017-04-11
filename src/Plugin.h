#pragma once
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include "Array.h"
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
        struct Input* input, char* buffer, size_t length, struct Error* error);
};

struct Output {
    struct Plugin* plugin;
    intptr_t arg;
    void (*close)(struct Output* output, struct Error* error);
    // If all data is flushed, `buffer->length` is set to `0`.
    // If `buffer` ownership is transferred to a plugin, it is set to `NULL`.
    void (*write)(
        struct Output* output, struct Buffer** buffer, struct Error* error);
};

struct Plugin {
    char* name;
    char* description;
    intptr_t arg;
    bool (*is_available)(struct Plugin* plugin, struct Error* error);
    void (*open_input)(
        struct Plugin* plugin,
        struct Input* input,
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

void Output_delete(struct Output* output);
struct Output* Output_new(struct Plugin* plugin, struct Error* error);
