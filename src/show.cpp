#include <errno.h>
#include <map>
#include <pty.h>
#include <set>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string>
#include <string.h>
#include <unistd.h>
#include <vector>
#include "array.h"
#include "std/string.h"


#define HELP_OPT "h"
#define DISABLE_PLUGIN_OPT "x:"
#define PLUGIN_OPTION_OPT "p:"

#define ALL_OPTS ( \
    HELP_OPT \
    DISABLE_PLUGIN_OPT \
    PLUGIN_OPTION_OPT \
)


typedef enum {
    STATUS_OK,
    STATUS_ERRNO,
    STATUS_UNSPECIFIED_PLUGIN_OPTION,
    STATUS_UNSPECIFIED_PLUGIN_NAME,
    STATUS_INVALID_OPTION
} Status;


typedef struct {
    Status (*get_name)(char** name);

    Status (*run)(
        int argc,
        char** argv,
        std::vector<char*>* options,
        int* output_fd);
} Plugin;


struct Cstring_cmp {
    bool operator()(char* a, char* b) const {
        return strcmp(a, b) < 0;
    }
};


static const char* status_string_by_code[] = {
    "Ok.",
    NULL,
    "No plugin option specified.",
    "No plugin name specified.",
    "Try '-h' for more information.",
};


const char* Status_describe(Status status) {
    return status == STATUS_ERRNO
        ? strerror(errno)
        : status_string_by_code[status];
}


Status exec_forkpty(char* file, char* argv[], int* output_fd) {
    int saved_stderr = dup(STDERR_FILENO);

    if (saved_stderr == -1) {
        return STATUS_ERRNO;
    }

    int child_out_fd;
    int child_pid = forkpty(&child_out_fd, NULL, NULL, NULL);

    if (child_pid == -1) {
        return STATUS_ERRNO;
    }
    else if (child_pid != 0) {
        *output_fd = child_out_fd;
        close(saved_stderr);
        return STATUS_OK;
    }

    if (dup2(saved_stderr, STDERR_FILENO) == -1) {
        return STATUS_ERRNO;
    }

    if (execvp(file, argv) == -1) {
        return STATUS_ERRNO;
    }
    else {
        exit(EXIT_SUCCESS);
    }
}


Status parse_plugin_option(
        char* option,
        std::map<char*, std::vector<char*>, Cstring_cmp>* plugin_options) {

    const char PLUGIN_OPTION_SEP[] = ":";
    char* separator = strstr(option, PLUGIN_OPTION_SEP);

    bool is_option_missing = (separator == NULL)
        || (separator[ARRAY_LENGTH(PLUGIN_OPTION_SEP) - 1] == '\0');

    if (is_option_missing) {
        return STATUS_UNSPECIFIED_PLUGIN_OPTION;
    }

    size_t name_length = (separator - option);

    if (name_length == 0) {
        return STATUS_UNSPECIFIED_PLUGIN_NAME;
    }

    char* name = strncopy(option, name_length);

    if (name == NULL) {
        return STATUS_ERRNO;
    }

    char* value = separator + ARRAY_LENGTH(PLUGIN_OPTION_SEP) - 1;

    std::map<char*, std::vector<char*>, Cstring_cmp>::iterator it
        = plugin_options->find(name);

    if (it == plugin_options->end()) {
        (*plugin_options)[name] = std::vector<char*>(1, value);
    }
    else {
        free(name);
        it->second.push_back(value);
    }

    return STATUS_OK;
}


Status parse_options(
        int argc,
        char* argv[],
        int* last_optind,
        std::set<std::string>* disabled_plugins,
        std::map<char*, std::vector<char*>, Cstring_cmp>* plugin_options) {

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

            *last_optind = -1;
            return STATUS_OK;
        }
        else if (option == *PLUGIN_OPTION_OPT) {
            Status status = parse_plugin_option(optarg, plugin_options);

            if (status != STATUS_OK) {
                return status;
            }
        }
        else {
            return STATUS_INVALID_OPTION;
        }
    }

    *last_optind = optind;
    return STATUS_OK;
}


Status plugin_ls_get_name(char** name) {
    *name = (char*) "ls";
    return STATUS_OK;
}


Status plugin_ls_run(
        int argc,
        char** argv,
        std::vector<char*>* options,
        int* output_fd) {

    std::vector<char*> ls_argv;
    ls_argv.push_back((char*) "ls");

    if (options != NULL) {
        ls_argv.insert(ls_argv.end(), options->begin(), options->end());
    }

    for (int i = 0; i < argc; ++i) {
        ls_argv.push_back(argv[i]);
    }

    ls_argv.push_back(NULL);
    return exec_forkpty(ls_argv[0], ls_argv.data(), output_fd);
}


int main(int argc, char* argv[]) {
    std::set<std::string> disabled_plugins;
    std::map<char*, std::vector<char*>, Cstring_cmp> plugin_options;
    int arg_optind;

    Status status = parse_options(
        argc, argv, &arg_optind, &disabled_plugins, &plugin_options);

    if (status != STATUS_OK) {
        fprintf(stderr, "%s\n", Status_describe(status));
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

    for (size_t i = 0; i < ARRAY_LENGTH(plugins); ++i) {
        Plugin* plugin = &plugins[i];
        char* name;

        status = plugin->get_name(&name);

        if (status != STATUS_OK) {
            fprintf(stderr, "%s\n", Status_describe(status));
            continue;
        }

        if (disabled_plugins.find(name) == disabled_plugins.end()) {
            int output_fd;
            std::map<char*, std::vector<char*>, Cstring_cmp>::iterator it
                = plugin_options.find(name);

            status = plugin->run(
                argc - arg_optind,
                argv + arg_optind,
                (it != plugin_options.end())
                    ? &(it->second)
                    : NULL,
                &output_fd);

            if (status != STATUS_OK) {
                fprintf(stderr, "%s\n", Status_describe(status));
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

    fputs("No working enabled plugin found.\n", stderr);
    return EXIT_FAILURE;
}
