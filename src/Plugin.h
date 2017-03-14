#pragma once
#include <stddef.h>
#include <stdint.h>
#include "Array.h"
#include "Error.h"
#include "io.h"

typedef struct Input {
    // If unsupported, `plugin` is set to `NULL`.
    struct Plugin* plugin;
    // If unnamed, `name` is set to `NULL`.
    char* name;
    // If unsupported or when closed, `fd` is set to `IO_INVALID_FD`.
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
    // If `buffer` is kept, it is set to `NULL`.
    void (*write)(struct Output*, Buffer** buffer, Error* error);
} Output;

typedef struct Plugin {
    // If no plugin options, `options` satisfies `ARRAY_IS_NULL_INITIALIZED`.
    Array options;
    const char* (*get_description)();
    const char* (*get_name)();
    // The `inputs` array is sparse, individual elements may be `NULL`.
    void (*run)(struct Plugin*, Array* inputs, Array* outputs, Error* error);
} Plugin;

void Input_close(Input* input, Error* error);
void Input_close_subprocess(Input* input, Error* error);
void Input_delete(Input* input);
Input* Input_new(char* name, int fd, Error* error);

void Output_delete(Output* output);
Output* Output_new(Plugin* plugin, Error* error);
