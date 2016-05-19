#pragma once
#include <stddef.h>
#include <stdint.h>
#include "../Array.h"
#include "../Error.h"

typedef struct Input {
    // If unnamed, `name` is set to `NULL`.
    char* name;
    int fd;
    intptr_t arg;
    void (*close)(struct Input* input, Error* error);
} Input;

typedef struct Output {
    intptr_t arg;
    void (*close)(struct Output* output, Error* error);
    // If all data is flushed, `length` is set to `0`.
    // If `data` is kept, it is set to `NULL`.
    void (*write)(
        struct Output* output, char** data, size_t* length, Error* error);
} Output;

typedef struct Plugin {
    Array options;
    const char* (*get_description)();
    const char* (*get_name)();
    // If no plugin options are defined, `options` is `NULL`.
    void (*run)(struct Plugin*, Array* inputs, Array* outputs, Error* error);
} Plugin;

void Input_delete(Input* input);
Input* Input_new(char* name, int fd, Error* error);

void Output_delete(Output* output);
Output* Output_new(Error* error);
