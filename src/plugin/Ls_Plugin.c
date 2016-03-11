#include <errno.h>
#include <pty.h>
#include <stdlib.h>
#include <unistd.h>
#include "../Array.h"
#include "Ls_Plugin.h"


#define EXTERNAL_BINARY "ls"


static int fork_exec_pipe(char* file, char* argv[], Error* error) {
    int read_write_fds[2];

    if (pipe(read_write_fds) == -1) {
        Error_errno(error, errno);
        return RESOURCE_NO_FD;
    }

    int child_pid = fork();

    if (child_pid == -1) {
        Error_errno(error, errno);
        return RESOURCE_NO_FD;
    }
    else if (child_pid != 0) {
        close(read_write_fds[1]);
        Error_clear(error);
        return read_write_fds[0];
    }

    if (dup2(read_write_fds[1], STDOUT_FILENO) == -1) {
        Error_errno(error, errno);
        return RESOURCE_NO_FD;
    }

    close(read_write_fds[1]);
    close(read_write_fds[0]);

    execvp(file, argv);
    Error_errno(error, errno);
    return RESOURCE_NO_FD;
}


static int fork_exec_pty(char* file, char* argv[], Error* error) {
    int saved_stderr = dup(STDERR_FILENO);

    if (saved_stderr == -1) {
        Error_errno(error, errno);
        return RESOURCE_NO_FD;
    }

    int child_fd_out;
    int child_pid = forkpty(&child_fd_out, NULL, NULL, NULL);

    if (child_pid == -1) {
        Error_errno(error, errno);
        return RESOURCE_NO_FD;
    }
    else if (child_pid != 0) {
        close(saved_stderr);
        Error_clear(error);
        return child_fd_out;
    }

    if (dup2(saved_stderr, STDERR_FILENO) == -1) {
        Error_errno(error, errno);
        return RESOURCE_NO_FD;
    }

    execvp(file, argv);
    Error_errno(error, errno);
    return RESOURCE_NO_FD;
}


static int fork_exec(char* file, char* argv[], Error* error) {
    if (isatty(STDOUT_FILENO)) {
        return fork_exec_pty(file, argv, error);
    }
    else {
        return fork_exec_pipe(file, argv, error);
    }
}


static const char* get_description() {
    return "list directories via `" EXTERNAL_BINARY "`";
}


static const char* get_name() {
    return EXTERNAL_BINARY;
}


static void open_resources(
        Array resources,
        Array argv,
        size_t pos,
        Error* error) {

    Array_add(argv, (intptr_t) NULL, error);

    if (Error_has(error)) {
        return;
    }

    Resource resource = Resource_new(NULL, RESOURCE_NO_FD, error);

    if (Error_has(error)) {
        return;
    }

    Array_insert(resources, (intptr_t) resource, pos, error);

    if (Error_has(error)) {
        Resource_delete(resource);
        return;
    }

    resource->fd = fork_exec((char*) argv->data[0], (char**) argv->data, error);

    if (Error_has(error)) {
        close(resource->fd);
        Array_remove(resources, pos, NULL);
        Resource_delete(resource);
    }
}


static Array prepare_argv(Array options, Error* error) {
    Array argv = Array_new(error, EXTERNAL_BINARY, NULL);

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

    Error_clear(error);
    return argv;
}


static void run(Array resources, Array options, Error* error) {
    Array argv = prepare_argv(options, error);
    size_t nr_args = 0;

    if (Error_has(error)) {
        return;
    }

    if (resources->length == 0) {
        open_resources(resources, argv, resources->length, error);
        Array_delete(argv);
        return;
    }

    for (size_t i = 0; i < resources->length;) {
        Resource resource = (Resource) resources->data[i];

        if (resource == NULL) {
            ++i;
            continue;
        }

        if ((resource->name != NULL) && (resource->fd == RESOURCE_NO_FD)) {
            Array_add(argv, (intptr_t) resource->name, error);

            if (Error_has(error)) {
                Array_delete(argv);
                return;
            }

            ++nr_args;
            resources->data[i] = (intptr_t) NULL;
            Resource_delete(resource);
        }
        else if (nr_args > 0) {
            open_resources(resources, argv, i, error);

            if (Error_has(error)) {
                Array_delete(argv);
                return;
            }

            argv->length -= nr_args + 1;
            nr_args = 0;
            ++i;
        }
        else {
            ++i;
        }
    }

    if (nr_args > 0) {
        open_resources(resources, argv, resources->length, error);
    }
    else {
        Error_clear(error);
    }

    Array_delete(argv);
}


Plugin Ls_Plugin = {
    NULL,
    get_description,
    get_name,
    run,
};
