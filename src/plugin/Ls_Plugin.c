#include <errno.h>
#include <pty.h>
#include <stdlib.h>
#include <unistd.h>
#include "../Array.h"
#include "Ls_Plugin.h"


static Array create_exec_argv(Array args, Array options, Error* error) {
    Array argv = Array_new(error, "ls", NULL);

    if (Error_has(error)) {
        return NULL;
    }

    if (options != NULL) {
        Array_extend(argv, options, error);

        if (Error_has(error)) {
            Array_delete(argv);
            return NULL;
        }
    }

    Array_extend(argv, args, error);

    if (Error_has(error)) {
        Array_delete(argv);
        return NULL;
    }

    Array_add(argv, (intptr_t) NULL, error);

    if (Error_has(error)) {
        Array_delete(argv);
        return NULL;
    }

    Error_clear(error);
    return argv;
}


static int exec_forkpty(char* file, char* argv[], Error* error) {
    int saved_stderr = dup(STDERR_FILENO);

    if (saved_stderr == -1) {
        Error_errno(error, errno);
        return -1;
    }

    int child_fd_out;
    int child_pid = forkpty(&child_fd_out, NULL, NULL, NULL);

    if (child_pid == -1) {
        Error_errno(error, errno);
        return -1;
    }
    else if (child_pid != 0) {
        close(saved_stderr);
        Error_clear(error);
        return child_fd_out;
    }

    if (dup2(saved_stderr, STDERR_FILENO) == -1) {
        Error_errno(error, errno);
        return -1;
    }

    if (execvp(file, argv) == -1) {
        Error_errno(error, errno);
        return -1;
    }
    else {
        exit(EXIT_SUCCESS);
    }
}


static const char* get_description() {
    return "`ls` POSIX command";
}


static const char* get_name() {
    return "ls";
}


static Plugin_Result run(Array args, Array options, Array fds_in, Error* error) {
    if ((fds_in->length > 0) && (args->length == 0)) {
        Error_clear(error);
        return NO_PLUGIN_RESULT;
    }

    Array argv = create_exec_argv(args, options, error);

    if (Error_has(error)) {
        return NO_PLUGIN_RESULT;
    }

    int fd_out = exec_forkpty((char*) argv->data[0], (char**) argv->data, error);
    Array_delete(argv);

    if (Error_has(error)) {
        return NO_PLUGIN_RESULT;
    }

    Array_add(fds_in, (intptr_t) fd_out, error);

    if (Error_has(error)) {
        return NO_PLUGIN_RESULT;
    }

    Error_clear(error);
    return NO_PLUGIN_RESULT;
}


Plugin Ls_Plugin = {
    NULL,
    get_description,
    get_name,
    run,
};
