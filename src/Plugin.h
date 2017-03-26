#pragma once
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include "Array.h"
#include "Error.h"
#include "io.h"

typedef struct Input {
    char* name;
    // If unsupported or when closed, set to `IO_NULL_FD`.
    int fd;
    intptr_t arg;
    // Calls `close` by default.
    void (*close)(struct Input*, Error* error);
} Input;

typedef struct Output {
    struct Plugin* plugin;
    intptr_t arg;
    void (*close)(struct Output*, Error* error);
    // If all data is flushed, `buffer->length` is set to `0`.
    // If `buffer` ownership is transferred to a plugin, it is set to `NULL`.
    void (*write)(struct Output*, Buffer** buffer, Error* error);
} Output;

typedef struct Plugin {
    const char* name;
    const char* description;
    bool is_enabled;
    bool (*is_available)();
    void (*run)(
        size_t nr_options,
        char* options[],
        Input* input,
        Array* outputs,
        Error* error);
} Plugin;

void Input_close(Input* input, Error* error);
void Input_close_subprocess(Input* input, Error* error);

void Output_delete(Output* output);
Output* Output_new(Plugin* plugin, Error* error);
