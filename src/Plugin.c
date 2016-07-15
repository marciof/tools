#include <errno.h>
#include <stdlib.h>
#include <string.h>
#include <sys/wait.h>
#include "Plugin.h"

void Input_close_subprocess(Input* input, Error* error) {
    io_close(input->fd, error);
    int status;

    if (ERROR_HAS(error)) {
        return;
    }

    if (waitpid((int) input->arg, &status, 0) == -1) {
        if (errno != ECHILD) {
            Error_add(error, strerror(errno));
        }
    }
    else if (WIFEXITED(status) && (WEXITSTATUS(status) != 0)) {
        Error_add(error, "Subprocess exited with an error code");
    }
}

void Input_delete(Input* input) {
    free(input);
}

Input* Input_new(char* name, int fd, Error* error) {
    Input* input = (Input*) malloc(sizeof(*input));

    if (input == NULL) {
        Error_add(error, strerror(errno));
        return NULL;
    }

    input->arg = (intptr_t) NULL;
    input->name = name;
    input->fd = fd;
    input->close = NULL;

    return input;
}

void Output_delete(Output* output) {
    free(output);
}

Output* Output_new(Error* error) {
    Output* output = (Output*) malloc(sizeof(*output));

    if (output == NULL) {
        Error_add(error, strerror(errno));
        return NULL;
    }

    return output;
}
