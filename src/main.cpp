#include <errno.h>
#include <map>
#include <pty.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <vector>
#include "Options.h"
#include "std/array.h"
#include "std/Error.h"


typedef struct {
    const char* (*get_name)();

    int (*run)(
        int argc,
        char* argv[],
        std::vector<char*>* options,
        Error* error);
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


int plugin_ls_run(
        int argc,
        char* argv[],
        std::vector<char*>* options,
        Error* error) {

    std::vector<char*> ls_argv;
    ls_argv.push_back((char*) "ls");

    if (options != NULL) {
        ls_argv.insert(ls_argv.end(), options->begin(), options->end());
    }

    for (int i = 0; i < argc; ++i) {
        ls_argv.push_back(argv[i]);
    }

    ls_argv.push_back(NULL);
    return exec_forkpty(ls_argv[0], ls_argv.data(), error);
}


int main(int argc, char* argv[]) {
    Error error;
    Options options = Options_parse(argc, argv, &error);

    if (error) {
        Options_delete(options);
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

        std::map<char*, std::vector<char*>, Cstring_cmp>::iterator it
            = options.plugin_options.find((char*) name);

        int output_fd = plugin->run(
            argc - options.optind,
            argv + options.optind,
            (it != options.plugin_options.end()) ? &(it->second) : NULL,
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
