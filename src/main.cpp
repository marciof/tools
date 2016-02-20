#include <errno.h>
#include <pty.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include "Options.h"
#include "list/Array_List.h"
#include "list/List.h"
#include "std/array.h"
#include "std/Error.h"


typedef struct {
    const char* (*get_name)();
    int (*run)(int argc, char* argv[], List options, Error* error);
} Plugin;


int exec_forkpty(char* file, char* argv[], Error* error) {
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


const char* plugin_ls_get_name() {
    return "ls";
}


int plugin_ls_run(int argc, char* argv[], List options, Error* error) {
    List ls_argv = List_new(Array_List, error);

    if (*error) {
        return -1;
    }

    List_add(ls_argv, (intptr_t) "ls", error);
    Error discard;

    if (*error) {
        List_delete(ls_argv, &discard);
        return -1;
    }

    if (options != NULL) {
        Iterator it = List_iterator(options, error);

        if (*error) {
            List_delete(ls_argv, &discard);
            return -1;
        }

        while (Iterator_has_next(it)) {
            List_add(ls_argv, Iterator_next(it, &discard), error);

            if (*error) {
                List_delete(ls_argv, &discard);
                Iterator_delete(it);
                return -1;
            }
        }

        Iterator_delete(it);
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


int main(int argc, char* argv[]) {
    Error error;
    Options options = Options_parse(argc, argv, &error);

    if (error) {
        fprintf(stderr, "%s\n", error);
        return EXIT_FAILURE;
    }

    if (options.optind < 0) {
        Options_delete(options);
        return EXIT_SUCCESS;
    }

    Plugin plugins[] = {
        {
            plugin_ls_get_name,
            plugin_ls_run,
        },
    };

    for (size_t i = 0; i < STATIC_ARRAY_LENGTH(plugins); ++i) {
        Plugin* plugin = &plugins[i];
        const char* name = plugin->get_name();
        bool is_enabled = Options_is_plugin_enabled(options, name, &error);

        if (error) {
            Options_delete(options);
            fprintf(stderr, "%s\n", error);
            return EXIT_FAILURE;
        }

        if (!is_enabled) {
            continue;
        }

        List plugin_options = Options_get_plugin_options(options, name);

        int output_fd = plugin->run(
            argc - options.optind,
            argv + options.optind,
            plugin_options,
            &error);

        if (error) {
            Options_delete(options);
            fprintf(stderr, "%s\n", error);
            return EXIT_FAILURE;
        }

        ssize_t nr_bytes_read;
        const int BUFFER_SIZE = 256;
        char buffer[BUFFER_SIZE + 1];

        while ((nr_bytes_read = read(output_fd, buffer, BUFFER_SIZE)) > 0) {
            buffer[nr_bytes_read] = '\0';
            fputs(buffer, stdout);
        }

        Options_delete(options);
        return EXIT_SUCCESS;
    }

    Options_delete(options);
    fputs("No working enabled plugin found.\n", stderr);
    return EXIT_FAILURE;
}
