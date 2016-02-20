#include <errno.h>
#include <map>
#include <pty.h>
#include <set>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <vector>
#include "options.h"
#include "std/array.h"


typedef struct {
    const char* (*get_name)();

    int (*run)(
        int argc,
        char* argv[],
        std::vector<char*>* options,
        char** error);
} Plugin;


int exec_forkpty(char* file, char* argv[], char** error) {
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
        char** error) {

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
    char* error;
    Options options = Options_parse(argc, argv, &error);

    if (error) {
        fprintf(stderr, "%s\n", error);
        return EXIT_FAILURE;
    }

    if (options.optind < 0) {
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

        if (options.disabled_plugins.find((char*) name) == options.disabled_plugins.end()) {
            std::map<char*, std::vector<char*>, Cstring_cmp>::iterator it
                = options.plugin_options.find((char*) name);

            int output_fd = plugin->run(
                argc - options.optind,
                argv + options.optind,
                (it != options.plugin_options.end()) ? &(it->second) : NULL,
                &error);

            if (error) {
                if (it != options.plugin_options.end()) {
                    free(it->first);
                }
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

            if (it != options.plugin_options.end()) {
                free(it->first);
            }

            return EXIT_SUCCESS;
        }
    }

    std::map<char*, std::vector<char*>, Cstring_cmp>::iterator it
        = options.plugin_options.begin();

    for (; it != options.plugin_options.end(); ++it) {
        free(it->first);
    }

    fputs("No working enabled plugin found.\n", stderr);
    return EXIT_FAILURE;
}
