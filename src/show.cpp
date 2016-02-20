#include <errno.h>
#include <map>
#include <pty.h>
#include <set>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <vector>
#include "std/string.h"


#define HELP_OPT "h"
#define DISABLE_PLUGIN_OPT "x:"
#define PLUGIN_OPTION_OPT "p:"

#define ALL_OPTS ( \
    HELP_OPT \
    DISABLE_PLUGIN_OPT \
    PLUGIN_OPTION_OPT \
)

#define STATIC_ARRAY_LENGTH(array) \
    (sizeof(array) / sizeof((array)[0]))


typedef struct {
    const char* (*get_name)();

    int (*run)(
        int argc,
        char* argv[],
        std::vector<char*>* options,
        char** error);
} Plugin;


struct Cstring_cmp {
    bool operator()(char* a, char* b) const {
        return strcmp(a, b) < 0;
    }
};


static char* ERROR_INVALID_OPTION = (char*) "Try '-h' for more information.";
static char* ERROR_NO_PLUGIN_NAME = (char*) "No plugin name specified.";
static char* ERROR_NO_PLUGIN_OPTION = (char*) "No plugin option specified.";


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


void parse_plugin_option(
        char* option,
        std::map<char*, std::vector<char*>, Cstring_cmp>* plugin_options,
        char** error) {

    const char PLUGIN_OPTION_SEP[] = ":";
    char* separator = strstr(option, PLUGIN_OPTION_SEP);

    bool is_option_missing = (separator == NULL)
        || (separator[STATIC_ARRAY_LENGTH(PLUGIN_OPTION_SEP) - 1] == '\0');

    if (is_option_missing) {
        *error = ERROR_NO_PLUGIN_OPTION;
        return;
    }

    size_t name_length = (separator - option);

    if (name_length == 0) {
        *error = ERROR_NO_PLUGIN_NAME;
        return;
    }

    char* name = strncopy((const char*) option, name_length, error);

    if (*error) {
        return;
    }

    char* value = separator + STATIC_ARRAY_LENGTH(PLUGIN_OPTION_SEP) - 1;

    std::map<char*, std::vector<char*>, Cstring_cmp>::iterator it
        = plugin_options->find(name);

    if (it == plugin_options->end()) {
        (*plugin_options)[name] = std::vector<char*>(1, value);
    }
    else {
        free(name);
        it->second.push_back(value);
    }

    *error = NULL;
}


int parse_options(
        int argc,
        char* argv[],
        std::set<char*, Cstring_cmp>* disabled_plugins,
        std::map<char*, std::vector<char*>, Cstring_cmp>* plugin_options,
        char** error) {

    int option;

    while ((option = getopt(argc, argv, ALL_OPTS)) != -1) {
        if (option == *DISABLE_PLUGIN_OPT) {
            disabled_plugins->insert(optarg);
        }
        else if (option == *HELP_OPT) {
            fprintf(stderr,
                "Usage: show [OPTION]... [RESOURCE]...\n"
                    "Version: 0.2.0\n"
                    "\n"
                    "Options:\n"
                    "  -%c               display this help and exit\n"
                    "  -%c PLUGIN:OPT    pass an option to a plugin\n"
                    "  -%c PLUGIN        disable plugin\n"
                    "\n"
                    "Plugins:\n"
                    "  ls               POSIX `ls` command\n",
                *HELP_OPT,
                *PLUGIN_OPTION_OPT,
                *DISABLE_PLUGIN_OPT);

            *error = NULL;
            return -1;
        }
        else if (option == *PLUGIN_OPTION_OPT) {
            parse_plugin_option(optarg, plugin_options, error);

            if (*error) {
                return -1;
            }
        }
        else {
            *error = ERROR_INVALID_OPTION;
            return -1;
        }
    }

    *error = NULL;
    return optind;
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
    std::set<char*, Cstring_cmp> disabled_plugins;
    std::map<char*, std::vector<char*>, Cstring_cmp> plugin_options;
    char* error;

    int arg_optind = parse_options(
        argc, argv, &disabled_plugins, &plugin_options, &error);

    if (error) {
        fprintf(stderr, "%s\n", error);
        return EXIT_FAILURE;
    }

    if (arg_optind < 0) {
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

        if (disabled_plugins.find((char*) name) == disabled_plugins.end()) {
            std::map<char*, std::vector<char*>, Cstring_cmp>::iterator it
                = plugin_options.find((char*) name);

            int output_fd = plugin->run(
                argc - arg_optind,
                argv + arg_optind,
                (it != plugin_options.end()) ? &(it->second) : NULL,
                &error);

            if (error) {
                if (it != plugin_options.end()) {
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

            if (it != plugin_options.end()) {
                free(it->first);
            }

            return EXIT_SUCCESS;
        }
    }

    std::map<char*, std::vector<char*>, Cstring_cmp>::iterator it
        = plugin_options.begin();

    for (; it != plugin_options.end(); ++it) {
        free(it->first);
    }

    fputs("No working enabled plugin found.\n", stderr);
    return EXIT_FAILURE;
}
