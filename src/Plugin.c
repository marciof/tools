#include <stdlib.h>
#include <unistd.h>
#include "Plugin.h"
#include "popen2.h"

void Input_close_subprocess(struct Input* input, Error* error) {
    if (close(input->fd) == -1) {
        Error_add_errno(error, errno);
        input->fd = IO_NULL_FD;
        return;
    }

    int status = wait_subprocess((pid_t) input->arg, error);
    input->fd = IO_NULL_FD;

    if (!Error_has(error) && (status != 0)) {
        Error_add_string(error, "subprocess exited with an error code");
    }
}

void Output_delete(struct Output* output) {
    free(output);
}

struct Output* Output_new(struct Plugin* plugin, Error* error) {
    struct Output* output = (struct Output*) malloc(sizeof(*output));

    if (output == NULL) {
        Error_add_errno(error, errno);
        return NULL;
    }

    output->plugin = plugin;
    return output;
}
