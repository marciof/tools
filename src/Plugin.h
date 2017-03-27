#pragma once
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include "Array.h"
#include "Error.h"
#include "io.h"

/** Call `close` when closing a plugin. */
#define INPUT_CLOSE_DEFAULT NULL

typedef struct Input {
    /** `NULL` when a plugin is run with no inputs to get a default one. */
    char* name;
    /** `IO_NULL_FD` if unsupported or when closed. */
    int fd;
    intptr_t arg;
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
        size_t options_length,
        char* options[],
        Input* input,
        Array* outputs,
        Error* error);
} Plugin;

void Input_close(Input* input, Error* error);
void Input_close_subprocess(Input* input, Error* error);

void Output_delete(Output* output);
Output* Output_new(Plugin* plugin, Error* error);
