#include <errno.h>
#include <pty.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include "../list/Array_List.h"
#include "Ls_Plugin.h"


static char** create_exec_argv(
        int argc,
        char* argv[],
        List options,
        Error* error) {

    List exec_argv_list = List_literal(Array_List, error, "ls", NULL);
    Error discard;

    if (*error) {
        return NULL;
    }

    if (options != NULL) {
        List_extend(exec_argv_list, options, error);

        if (*error) {
            List_delete(exec_argv_list, &discard);
            return NULL;
        }
    }

    for (int i = 0; i <= argc; ++i) {
        List_add(exec_argv_list, (intptr_t) argv[i], error);

        if (*error) {
            List_delete(exec_argv_list, &discard);
            return NULL;
        }
    }

    char** exec_argv = (char**) List_to_array(exec_argv_list, sizeof(char*), error);
    List_delete(exec_argv_list, &discard);

    if (*error) {
        return NULL;
    }

    *error = NULL;
    return exec_argv;
}


static int exec_forkpty(char* file, char* argv[], Error* error) {
    int saved_stderr = dup(STDERR_FILENO);

    if (saved_stderr == -1) {
        *error = strerror(errno);
        return -1;
    }

    int child_fd_out;
    int child_pid = forkpty(&child_fd_out, NULL, NULL, NULL);

    if (child_pid == -1) {
        *error = strerror(errno);
        return -1;
    }
    else if (child_pid != 0) {
        close(saved_stderr);
        *error = NULL;
        return child_fd_out;
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
    return "`ls` POSIX command";
}


static const char* get_name() {
    return "ls";
}


static List run(
        List fds_in,
        int argc,
        char* argv[],
        List options,
        Error* error) {

    if ((List_length(fds_in) > 0) && (argc == 0)) {
        *error = NULL;
        return fds_in;
    }

    char** exec_ls_argv = create_exec_argv(argc, argv, options, error);

    if (*error) {
        return NULL;
    }

    int fd_out = exec_forkpty(exec_ls_argv[0], exec_ls_argv, error);
    free(exec_ls_argv);

    if (*error) {
        return NULL;
    }

    List_add(fds_in, (intptr_t) fd_out, error);

    if (*error) {
        return NULL;
    }

    return fds_in;
}


Plugin Ls_Plugin = {
    NULL,
    get_description,
    get_name,
    run,
};
