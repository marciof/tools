#include <errno.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include "Plugin.h"
#include "popen2.h"

void Input_close(Input* input, Error* error) {
    if (input->close != NULL) {
        input->close(input, error);
    }
    else if (close(input->fd) == -1) {
        Error_add(error, strerror(errno));
    }

    input->fd = IO_NULL_FD;
}

void Input_close_subprocess(Input* input, Error* error) {
    if (close(input->fd) == -1) {
        Error_add(error, strerror(errno));
        input->fd = IO_NULL_FD;
        return;
    }

    int status = wait_subprocess((pid_t) input->arg, error);
    input->fd = IO_NULL_FD;

    if (ERROR_HAS(error)) {
        return;
    }

    if (status != 0) {
        Error_add(error, "Subprocess exited with an error code");
    }
}

void Output_delete(Output* output) {
    free(output);
}

Output* Output_new(Plugin* plugin, Error* error) {
    Output* output = (Output*) malloc(sizeof(*output));

    if (output == NULL) {
        Error_add(error, strerror(errno));
        return NULL;
    }

    output->plugin = plugin;
    return output;
}
