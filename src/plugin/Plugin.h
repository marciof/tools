#pragma once
#include <stddef.h>
#include "../Array.h"
#include "../Error.h"

#define INPUT_NO_FD ((int) -1)

typedef struct {
    // If unnamed, `name` is set to `NULL`.
    char* name;
    int fd;
} Input;

typedef struct {
    Array* options;
    const char* (*get_description)();
    const char* (*get_name)();

    // If no plugin options are defined, `options` is `NULL`.
    void (*run)(Array* inputs, Array* options, int* output_fd, Error* error);
} Plugin;

void Input_delete(Input* input);
Input* Input_new(char* name, int fd, Error* error);
