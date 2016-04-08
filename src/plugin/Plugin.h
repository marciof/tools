#pragma once
#include <stddef.h>
#include <stdint.h>
#include "../Array.h"
#include "../Error.h"

#define INPUT_NO_FD ((int) -1)

typedef struct {
    // If unnamed, `name` is set to `NULL`.
    char* name;
    int fd;
} Input;

typedef struct {
    intptr_t arg;
    void (*close)(intptr_t arg);

    // When `data` is flushed, it's set to `NULL`.
    void (*write)(intptr_t arg, uint8_t** data, size_t* length, Error* error);
} Output;

typedef struct {
    Array* options;
    const char* (*get_description)();
    const char* (*get_name)();

    // If no plugin options are defined, `options` is `NULL`.
    void (*run)(Array* inputs, Array* options, Array* outputs, Error* error);
} Plugin;

void Input_delete(Input* input);
Input* Input_new(char* name, int fd, Error* error);

void Output_delete(Output* output);
Output* Output_new(Error* error);
