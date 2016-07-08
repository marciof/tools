#include <errno.h>
#include <sys/wait.h>
#include "../fork_exec.h"
#include "Vcs.h"

#define EXTERNAL_BINARY "git"

// FIXME: dup of dir
static void Input_close(Input* input, Error* error) {
    io_close(input->fd, error);

    if (!ERROR_HAS(error)) {
        int status;

        if (waitpid((int) input->arg, &status, 0) == -1) {
            ERROR_ERRNO(error, errno);
        }
        else if (WIFEXITED(status) && (WEXITSTATUS(status) != 0)) {
            ERROR_SET(error, ERROR_UNSPECIFIED);
        }
    }
}

static const char* Plugin_get_description() {
    return "show VCS revisions via `" EXTERNAL_BINARY "`";
}

static const char* Plugin_get_name() {
    return "vcs";
}

static void Plugin_run(
        Plugin* plugin, Array* inputs, Array* outputs, Error* error) {

    for (size_t i = 0; i < inputs->length; ++i) {
        Input* input = (Input*) inputs->data[i];

        if ((input != NULL) && (input->fd == IO_INVALID_FD)) {
            char* argv[] = {
                EXTERNAL_BINARY,
                "--no-pager", // FIXME: not generic
                "show",
                input->name,
                NULL,
            };

            int child_pid;
            input->fd = fork_exec(argv[0], argv, &child_pid, error);

            if (ERROR_HAS(error)) {
                return; // FIXME: don't abort
            }

            input->arg = child_pid;
            input->close = Input_close;
        }
    }

    ERROR_CLEAR(error);
}

Plugin Vcs_Plugin = {
    {NULL},
    Plugin_get_description,
    Plugin_get_name,
    Plugin_run,
};
