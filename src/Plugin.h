#pragma once
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include "Array.h"
#include "Error.h"
#include "io.h"

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
    /** `NULL` if it can't open default inputs. */
    void (*open_default_input)(
        Input* input, size_t options_length, char* options[], Error* error);
    /** `NULL` if it can't open named inputs. */
    void (*open_named_input)(
        Input* input, size_t options_length, char* options[], Error* error);
} Plugin;

void Input_close_subprocess(Input* input, Error* error);
void Output_delete(Output* output);
Output* Output_new(Plugin* plugin, Error* error);
