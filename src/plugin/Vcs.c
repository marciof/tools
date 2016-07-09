#include "../fork_exec.h"
#include "Vcs.h"

#define EXTERNAL_BINARY "git"

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
                "--no-pager",
                "show",
                input->name,
                NULL,
            };

            int child_pid;
            input->fd = fork_exec(argv[0], argv, &child_pid, error);

            // FIXME: don't abort and don't swallow inputs
            if (ERROR_HAS(error)) {
                return;
            }

            input->arg = child_pid;
            input->close = Input_close_subprocess;
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
