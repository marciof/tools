#include <errno.h>
#include <stdlib.h>
#include <string.h>
#include "Plugin.h"

void Input_delete(Input* input) {
    memset(input, 0, sizeof(*input));
    free(input);
}

Input* Input_new(char* name, int fd, Error* error) {
    Input* input = (Input*) malloc(sizeof(*input));

    if (input == NULL) {
        ERROR_ERRNO(error, errno);
        return NULL;
    }

    input->arg = (intptr_t) NULL;
    input->name = name;
    input->fd = fd;
    input->close = NULL;

    return input;
}

void Output_delete(Output* output) {
    memset(output, 0, sizeof(*output));
    free(output);
}

Output* Output_new(Error* error) {
    Output* output = (Output*) malloc(sizeof(*output));

    if (output == NULL) {
        ERROR_ERRNO(error, errno);
        return NULL;
    }

    return output;
}
