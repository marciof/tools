#pragma once
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include "Array.h"
#include "Error.h"
#include "io.h"

struct Input {
    /** `NULL` when a plugin is run with no inputs to get a default one. */
    char* name;
    /** `IO_NULL_FD` if unsupported or when closed. */
    int fd;
    intptr_t arg;
    void (*close)(struct Input* input, Error* error);
};

struct Output {
    struct Plugin* plugin;
    intptr_t arg;
    void (*close)(struct Output* output, Error* error);
    // If all data is flushed, `buffer->length` is set to `0`.
    // If `buffer` ownership is transferred to a plugin, it is set to `NULL`.
    void (*write)(struct Output* output, struct Buffer** buffer, Error* error);
};

struct Plugin {
    char* name;
    char* description;
    bool (*is_available)();
    /** `NULL` if it can't open default inputs. */
    void (*open_default_input)(
        struct Input* input, size_t argc, char* argv[], Error* error);
    /** `NULL` if it can't open named inputs. */
    void (*open_named_input)(
        struct Input* input, size_t argc, char* argv[], Error* error);
};

struct Plugin_Setup {
    struct Plugin* plugin;
    bool is_enabled;
    size_t argc;
    char** argv;
};

void Input_close_subprocess(struct Input* input, Error* error);
void Output_delete(struct Output* output);
struct Output* Output_new(struct Plugin* plugin, Error* error);
