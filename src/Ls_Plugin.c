#include <errno.h>
#include <pty.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include "list/Array_List.h"
#include "Ls_Plugin.h"


static int exec_forkpty(char* file, char* argv[], Error* error) {
    int saved_stderr = dup(STDERR_FILENO);

    if (saved_stderr == -1) {
        *error = strerror(errno);
        return -1;
    }

    int child_out_fd;
    int child_pid = forkpty(&child_out_fd, NULL, NULL, NULL);

    if (child_pid == -1) {
        *error = strerror(errno);
        return -1;
    }
    else if (child_pid != 0) {
        close(saved_stderr);
        *error = NULL;
        return child_out_fd;
    }

    if (dup2(saved_stderr, STDERR_FILENO) == -1) {
        *error = strerror(errno);
        return -1;
    }

    if (execvp(file, argv) == -1) {
        *error = strerror(errno);
        return -1;
    }
    else {
        exit(EXIT_SUCCESS);
    }
}


static const char* get_description() {
    return "POSIX `ls` command";
}


static const char* get_name() {
    return "ls";
}


static int run(int argc, char** argv, List options, Error* error) {
    List ls_argv = List_literal(Array_List, error, "ls", NULL);
    Error discard;

    if (*error) {
        return -1;
    }

    if (options != NULL) {
        List_extend(ls_argv, options, error);

        if (*error) {
            List_delete(ls_argv, &discard);
            return -1;
        }
    }

    for (int i = 0; i <= argc; ++i) {
        List_add(ls_argv, (intptr_t) argv[i], error);

        if (*error) {
            List_delete(ls_argv, &discard);
            return -1;
        }
    }

    char** exec_ls_argv = (char**) List_to_array(ls_argv, sizeof(char*), error);
    List_delete(ls_argv, &discard);

    if (*error) {
        return -1;
    }

    int output_fd = exec_forkpty(exec_ls_argv[0], exec_ls_argv, error);
    free(exec_ls_argv);
    return output_fd;
}


Plugin Ls_Plugin = {
    get_description,
    get_name,
    run,
};
