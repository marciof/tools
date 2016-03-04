#include <errno.h>
#include <pty.h>
#include <stdlib.h>
#include <unistd.h>
#include "../Array.h"
#include "Ls_Plugin.h"


#define LS_PROGRAM_NAME "ls"


static int exec_forkpty(char* file, char* argv[], Error* error) {
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

    if (execvp(file, argv) == -1) {
        Error_errno(error, errno);
        return RESOURCE_NO_FD;
    }
    else {
        exit(EXIT_SUCCESS);
    }
}


static const char* get_description() {
    return "list directories via `" LS_PROGRAM_NAME "`";
}


static const char* get_name() {
    return LS_PROGRAM_NAME;
}


static void open_default_resource(Array resources, Array argv, Error* error) {
    Array_add(argv, (intptr_t) NULL, error);

    if (Error_has(error)) {
        return;
    }

    Resource resource = Resource_new(NULL, RESOURCE_NO_FD, error);

    if (Error_has(error)) {
        return;
    }

    resource->fd = exec_forkpty(
        (char*) argv->data[0], (char**) argv->data, error);

    if (Error_has(error)) {
        Resource_delete(resource);
        return;
    }

    Array_add(resources, (intptr_t) resource, error);

    if (Error_has(error)) {
        close(resource->fd);
        Resource_delete(resource);
    }
}


static void open_merge_resources(
        Array resources,
        Array argv,
        size_t next_open_resource,
        size_t nr_args,
        Error* error) {

    Array_add(argv, (intptr_t) NULL, error);

    if (Error_has(error)) {
        return;
    }

    for (size_t i = 1; i < nr_args; ++i) {
        Resource_delete((Resource)
            Array_remove(resources, next_open_resource - nr_args, NULL));
    }

    Resource resource = (Resource)
        resources->data[next_open_resource - nr_args];

    resource->name = NULL;
    resource->fd = exec_forkpty(
        (char*) argv->data[0], (char**) argv->data, error);

    if (Error_has(error)) {
        Array_remove(resources, next_open_resource - nr_args, NULL);
        Resource_delete(resource);
        return;
    }

    argv->length -= nr_args + 1;
    Error_clear(error);
}


static Array prepare_argv(Array options, Error* error) {
    Array argv = Array_new(error, LS_PROGRAM_NAME, NULL);

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
        open_default_resource(resources, argv, error);
        Array_delete(argv);
        return;
    }

    for (size_t i = 0; i < resources->length;) {
        Resource resource = (Resource) resources->data[i];

        if ((resource->name != NULL) && (resource->fd == RESOURCE_NO_FD)) {
            Array_add(argv, (intptr_t) resource->name, error);

            if (Error_has(error)) {
                Array_delete(argv);
                return;
            }

            ++nr_args;
        }
        else if (nr_args > 0) {
            open_merge_resources(resources, argv, i, nr_args, error);

            if (Error_has(error)) {
                Array_delete(argv);
                return;
            }

            i -= nr_args - 1;
            nr_args = 0;
            continue;
        }

        ++i;
    }

    if (nr_args > 0) {
        open_merge_resources(
            resources, argv, resources->length, nr_args, error);
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
