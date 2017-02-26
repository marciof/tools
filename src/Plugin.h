#pragma once
#include <stddef.h>
#include <stdint.h>
#include "Array.h"
#include "Error.h"
#include "io.h"

typedef struct Input {
    // If unnamed, `name` is set to `NULL`.
    char* name;
    int fd;
    intptr_t arg;
    // If `NULL`, uses `io_close` by default.
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
    // If no plugin options are defined, `options` is set to `NULL`.
    Array options;
    const char* (*get_description)();
    const char* (*get_name)();
    // The `inputs` array is sparse, individual elements may be `NULL`.
    void (*run)(struct Plugin*, Array* inputs, Array* outputs, Error* error);
} Plugin;

void Input_close_subprocess(Input* input, Error* error);
void Input_delete(Input* input);
Input* Input_new(char* name, int fd, Error* error);

void Output_delete(Output* output);
Output* Output_new(Plugin* plugin, Error* error);
