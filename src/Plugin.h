#pragma once
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include "Array.h"
#include "Error.h"
#include "io.h"

#define PLUGIN_IS_AVAILABLE_ALWAYS NULL

typedef struct Input {
    // If unsupported, set to `NULL`.
    struct Plugin* plugin;
    // If unnamed, set to `NULL`.
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
    // If no plugin options, it satisfies `ARRAY_IS_NULL_INITIALIZED`.
    Array options;
    const char* description;
    const char* name;
    // If always supported, set to `PLUGIN_IS_AVAILABLE_ALWAYS`.
    bool (*is_available)();
    // The `inputs` array is sparse, individual elements may be `NULL`.
    void (*run)(struct Plugin*, Array* inputs, Array* outputs, Error* error);
} Plugin;

void Input_close(Input* input, Error* error);
void Input_close_subprocess(Input* input, Error* error);
void Input_delete(Input* input);
Input* Input_new(char* name, int fd, Error* error);

void Output_delete(Output* output);
Output* Output_new(Plugin* plugin, Error* error);
