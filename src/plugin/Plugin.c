#include <errno.h>
#include <stdlib.h>
#include <string.h>
#include "Plugin.h"

void Input_delete(Input* input) {
    if (input != NULL) {
        memset(input, 0, sizeof(*input));
        free(input);
    }
}

Input* Input_new(char* name, int fd, Error* error) {
    Input* input = (Input*) malloc(sizeof(*input));

    if (input == NULL) {
        Error_errno(error, errno);
        return NULL;
    }

    input->name = name;
    input->fd = fd;

    return input;
}
