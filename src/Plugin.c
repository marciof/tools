#include <stdlib.h>
#include <unistd.h>
#include "Plugin.h"
#include "popen2.h"

void Input_close_subprocess(struct Input* input, Error* error) {
    if (close(input->fd) == -1) {
        ERROR_ADD_ERRNO(error, errno);
        input->fd = IO_NULL_FD;
        return;
    }

    int status = wait_subprocess((pid_t) input->arg, error);
    input->fd = IO_NULL_FD;

    if (!ERROR_HAS(error) && (status != 0)) {
        ERROR_ADD_STRING(error, "subprocess exited with an error code");
    }
}

void Output_delete(struct Output* output) {
    free(output);
}

struct Output* Output_new(struct Plugin* plugin, Error* error) {
    struct Output* output = (struct Output*) malloc(sizeof(*output));

    if (output == NULL) {
        ERROR_ADD_ERRNO(error, errno);
        return NULL;
    }

    output->plugin = plugin;
    return output;
}
